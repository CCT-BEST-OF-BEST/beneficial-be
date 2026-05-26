from app.infrastructure.rag.retriever import RagRetriever
from app.infrastructure.rag.service import RagService


def get_rag_service(openai_client=None) -> RagService:
    return RagService(retriever=RagRetriever(), openai_client=openai_client)
