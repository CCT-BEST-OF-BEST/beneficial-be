from typing import Optional

from app.domains.rag.retriever import RagRetriever
from app.domains.rag.schemas import RagDocument, RagSearchResult


class RagService:
    def __init__(self, retriever: RagRetriever, openai_client=None):
        self.retriever = retriever
        self.openai_client = openai_client

    async def search(
        self,
        query: str,
        collection_name: Optional[str] = None,
        top_k: int = 5,
    ) -> RagSearchResult:
        documents = await self.retriever.search(query, collection_name, top_k)
        context = self.build_context(documents)
        return RagSearchResult(query=query, documents=documents, context=context)

    async def answer(
        self,
        query: str,
        system_prompt: str,
        collection_name: Optional[str] = None,
        top_k: int = 5,
    ) -> str:
        if self.openai_client is None:
            raise ValueError("RagService.answer requires an OpenAI client")

        search_result = await self.search(query, collection_name, top_k)
        return await self.openai_client.generate_response_with_context(
            prompt=query,
            context=search_result.context,
            system_prompt=system_prompt,
        )

    def build_context(self, documents: list[RagDocument]) -> str:
        if not documents:
            return "참고 자료가 없습니다."

        context_parts = []
        for index, doc in enumerate(documents, 1):
            similarity = round(1 - doc.distance, 4)
            if doc.collection == "card_check":
                label = "카드"
            elif doc.collection == "korean_word_problems":
                label = "문제"
            elif doc.collection == "pdf_documents":
                label = "PDF"
            else:
                label = "기타"
            context_parts.append(
                f"{index}. [{label}] 유사도: {similarity} - {doc.document}"
            )

        return "\n".join(context_parts)
