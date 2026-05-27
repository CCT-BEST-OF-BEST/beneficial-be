import asyncio

from app.infrastructure.rag.schemas import RagDocument
from app.infrastructure.rag.service import RagService


class FakeRetriever:
    async def search(self, query, collection_name=None, top_k=5):
        return [
            RagDocument(
                document="단어: 되/돼 의미: 돼는 되어의 줄임말",
                collection="card_check",
                distance=0.2,
                metadata={"word": "되/돼"},
                rrf_score=0.03,
            )
        ]


def test_build_context_formats_documents():
    service = RagService(retriever=FakeRetriever())

    context = service.build_context(
        [
            RagDocument(
                document="문제 1: 그렇게 하면 안 ( ). 정답: 돼",
                collection="korean_word_problems",
                distance=0.25,
            )
        ]
    )

    assert "[문제]" in context
    assert "정답: 돼" in context
    assert "유사도: 0.75" in context


def test_search_returns_documents_and_context():
    service = RagService(retriever=FakeRetriever())

    result = asyncio.run(service.search("되와 돼의 차이"))

    assert result.query == "되와 돼의 차이"
    assert len(result.documents) == 1
    assert "되/돼" in result.context
