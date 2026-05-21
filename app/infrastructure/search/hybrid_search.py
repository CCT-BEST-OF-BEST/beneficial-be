from typing import List, Dict, Any
from app.infrastructure.search.bm25_retriever import get_bm25_retriever
from app.infrastructure.db.vector.vector_db import get_vector_db
from app.infrastructure.embedding.embedding_model import get_embedding_model
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

# RRF 상수: 60이 표준값 (논문 기반)
RRF_K = 60


def _reciprocal_rank_fusion(
    dense_results: List[Dict],
    sparse_results: List[tuple],
    top_k: int,
) -> List[Dict]:
    """
    Dense (ChromaDB cosine) + Sparse (BM25) 결과를 RRF로 합산한다.

    RRF score = Σ 1 / (k + rank)
    - 두 검색 결과에서 모두 상위에 있는 문서가 가장 높은 점수를 받는다.
    - 절대 유사도 값이 아닌 '순위'를 기반으로 하므로 스케일 불일치 문제가 없다.
    """
    scores: Dict[str, float] = {}
    # doc_id → (document, collection, metadata) 매핑
    doc_store: Dict[str, Dict] = {}

    # Dense 결과 반영
    for rank, item in enumerate(dense_results):
        doc_id = item["id"]
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (RRF_K + rank + 1)
        doc_store[doc_id] = item

    # Sparse (BM25) 결과 반영
    for rank, (doc_id, document, collection, bm25_score, metadata) in enumerate(
        sparse_results
    ):
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (RRF_K + rank + 1)
        if doc_id not in doc_store:
            doc_store[doc_id] = {
                "id": doc_id,
                "document": document,
                "collection": collection,
                "metadata": metadata,
                "distance": 1.0,  # BM25만 있을 경우 기본값
            }

    # RRF 점수 기준 정렬 후 top_k 반환
    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)[:top_k]

    results = []
    for doc_id in sorted_ids:
        item = doc_store[doc_id]
        item["rrf_score"] = round(scores[doc_id], 6)
        results.append(item)

    return results


class HybridSearchService:
    """
    BM25 (Sparse) + ChromaDB cosine (Dense) 하이브리드 검색.
    RRF 로 두 결과를 합산해 최종 top-k를 반환한다.
    """

    def __init__(self):
        self.vector_db = get_vector_db()
        self.embedding_model = get_embedding_model()
        self.bm25 = get_bm25_retriever()

    async def search(
        self,
        query: str,
        collection_name: str | None = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        하이브리드 검색 수행.

        Returns:
            [{"id", "document", "collection", "distance", "rrf_score"}, ...]
        """
        fetch_n = top_k * 4  # 후보군을 넉넉히 가져와 RRF 적용

        # ── Dense 검색 ──────────────────────────────────────────────
        query_embedding = await self.embedding_model.get_embedding(query)

        collections = (
            [collection_name]
            if collection_name
            else ["korean_word_problems", "card_check", "pdf_documents"]
        )

        dense_results: List[Dict] = []
        for coll_name in collections:
            collection = self.vector_db.get_collection(coll_name)
            if not collection or collection.count() == 0:
                continue

            n = min(fetch_n, collection.count())
            res = collection.query(
                query_embeddings=[query_embedding],
                n_results=n,
                include=["documents", "metadatas", "distances"],
            )

            for doc_id, doc, meta, dist in zip(
                res["ids"][0],
                res["documents"][0],
                res["metadatas"][0],
                res["distances"][0],
            ):
                dense_results.append(
                    {
                        "id": doc_id,
                        "document": doc,
                        "collection": coll_name,
                        "metadata": meta or {},
                        "distance": dist,
                    }
                )

        # 코사인 거리 기준 정렬 (낮을수록 유사)
        dense_results.sort(key=lambda x: x["distance"])

        # ── Sparse (BM25) 검색 ─────────────────────────────────────
        sparse_results = self.bm25.search(query, n_results=fetch_n)

        # collection 필터 적용
        if collection_name:
            sparse_results = [r for r in sparse_results if r[2] == collection_name]

        # ── RRF 결합 ───────────────────────────────────────────────
        final = _reciprocal_rank_fusion(dense_results, sparse_results, top_k)

        # 로그
        logger.info(
            f"🔀 하이브리드 검색 완료: dense={len(dense_results)}개, "
            f"sparse={len(sparse_results)}개 → 최종 {len(final)}개"
        )
        for i, item in enumerate(final):
            sim = round(1 - item["distance"], 4)
            logger.info(
                f"   {i+1}. [{item['collection']}] "
                f"cosine={sim:.4f} rrf={item['rrf_score']:.5f} "
                f"| {item['document'][:60]}..."
            )

        return final


# 전역 인스턴스
_hybrid_service: HybridSearchService | None = None


def get_hybrid_search_service() -> HybridSearchService:
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridSearchService()
    return _hybrid_service
