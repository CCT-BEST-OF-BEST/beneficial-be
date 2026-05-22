from typing import Any, Dict, List, Optional

from app.domains.rag.schemas import RagDocument
from app.infrastructure.search.hybrid_search import get_hybrid_search_service


class RagRetriever:
    def __init__(self, hybrid_search=None):
        self.hybrid_search = hybrid_search or get_hybrid_search_service()

    async def search(
        self,
        query: str,
        collection_name: Optional[str] = None,
        top_k: int = 5,
    ) -> List[RagDocument]:
        raw_results = await self.hybrid_search.search(
            query=query,
            collection_name=collection_name,
            top_k=top_k,
        )
        return [self._to_document(item) for item in raw_results]

    def _to_document(self, item: Dict[str, Any]) -> RagDocument:
        metadata = item.get("metadata") or {}
        doc_text = metadata.get("original_text") or item.get("document", "")
        return RagDocument(
            document=doc_text,
            metadata=metadata,
            distance=item.get("distance", 1.0),
            collection=item.get("collection", "unknown"),
            rrf_score=item.get("rrf_score", 0.0),
        )
