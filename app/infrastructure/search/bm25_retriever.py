import re
from typing import List, Tuple, Dict, Any
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

try:
    from rank_bm25 import BM25Okapi
except ModuleNotFoundError:
    BM25Okapi = None


def _tokenize_korean(text: str) -> List[str]:
    """
    한국어 텍스트를 토큰화한다.
    - 공백 기준 어절 분리
    - 한국어 글자 단위 바이그램 추가 (형태소 변형 커버)
      예) "되다" → ["되다", "되다", "되", "다"]
          "되와" → ["되와", "되", "와"]
    """
    # 특수문자 제거 후 어절 분리
    clean = re.sub(r"[^\w가-힣a-zA-Z0-9]", " ", text)
    words = [w for w in clean.split() if w]

    tokens = list(words)

    # 한국어 단어에 대해 글자 바이그램 추가
    for word in words:
        korean_chars = re.sub(r"[^가-힣]", "", word)
        if len(korean_chars) >= 2:
            for i in range(len(korean_chars) - 1):
                tokens.append(korean_chars[i : i + 2])
        # 단일 글자도 추가 (받침 없는 조사 붙은 형태 처리)
        for ch in korean_chars:
            tokens.append(ch)

    return tokens


class BM25Retriever:
    """
    ChromaDB 전체 문서를 대상으로 BM25 키워드 검색을 수행한다.
    서버 시작 시 모든 컬렉션의 문서를 로드해 인메모리 인덱스를 구축한다.
    """

    def __init__(self):
        self._bm25: BM25Okapi | None = None
        self._corpus: List[str] = []
        self._doc_ids: List[str] = []
        self._collections: List[str] = []
        self._metadatas: List[Dict[str, Any]] = []

    def build_index(self, vector_db) -> None:
        """ChromaDB 전체 컬렉션에서 문서를 로드해 BM25 인덱스를 구축한다."""
        if BM25Okapi is None:
            logger.warning("[WARN] BM25 인덱스: rank_bm25 패키지가 없어 비활성화합니다")
            return

        self._corpus = []
        self._doc_ids = []
        self._collections = []
        self._metadatas = []

        collection_names = ["card_check", "korean_word_problems", "pdf_documents"]

        for coll_name in collection_names:
            collection = vector_db.get_collection(coll_name)
            if not collection or collection.count() == 0:
                continue

            result = collection.get(include=["documents", "metadatas"])
            for doc_id, doc, meta in zip(
                result["ids"], result["documents"], result["metadatas"]
            ):
                self._corpus.append(doc)
                self._doc_ids.append(doc_id)
                self._collections.append(coll_name)
                self._metadatas.append(meta or {})

        if not self._corpus:
            logger.warning("[WARN] BM25 인덱스: 문서 없음")
            return

        tokenized = [_tokenize_korean(doc) for doc in self._corpus]
        self._bm25 = BM25Okapi(tokenized)
        logger.info(f"[OK] BM25 인덱스 구축 완료: {len(self._corpus)}개 문서")

    def search(
        self, query: str, n_results: int = 20
    ) -> List[Tuple[str, str, str, float, Dict]]:
        """
        BM25 검색 수행.

        Returns:
            (doc_id, document, collection_name, bm25_score, metadata) 리스트
        """
        if self._bm25 is None or not self._corpus:
            return []

        tokens = _tokenize_korean(query)
        scores = self._bm25.get_scores(tokens)

        top_n = min(n_results, len(scores))
        top_indices = scores.argsort()[::-1][:top_n]

        return [
            (
                self._doc_ids[i],
                self._corpus[i],
                self._collections[i],
                float(scores[i]),
                self._metadatas[i],
            )
            for i in top_indices
            if scores[i] > 0  # 점수 0 이하 제외
        ]


# 전역 인스턴스
_bm25_retriever: BM25Retriever | None = None


def get_bm25_retriever() -> BM25Retriever:
    global _bm25_retriever
    if _bm25_retriever is None:
        _bm25_retriever = BM25Retriever()
    return _bm25_retriever
