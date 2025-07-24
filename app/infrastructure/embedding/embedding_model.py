import os
import asyncio
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer
from openai import AsyncOpenAI
from dotenv import load_dotenv
from app.common.logging.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)


class EmbeddingModel:
    def __init__(self, model_name: str = "jhgan/ko-sroberta-multitask"):
        """
        임베딩 모델 초기화

        Args:
            model_name: 사용할 임베딩 모델명
                - OpenAI: "text-embedding-3-small", "text-embedding-3-large"
                - Local: "jhgan/ko-sroberta-multitask" (한국어 전용), "sentence-transformers/all-MiniLM-L6-v2"
        """
        self.model_name = model_name
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # 환경 변수에서 배치 크기와 워커 수 설정
        self.batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "50"))
        self.max_workers = int(os.getenv("MAX_WORKERS", "4"))

        # ThreadPoolExecutor 초기화
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

        # OpenAI API 키가 있으면 OpenAI 사용, 없으면 sentence-transformers 사용
        if self.openai_api_key:
            self.client = AsyncOpenAI(api_key=self.openai_api_key)
            self.use_openai = True
            logger.info("🔑 OpenAI 임베딩 모델 사용 (비동기)")
        else:
            self.model = SentenceTransformer(model_name)
            self.use_openai = False
            logger.info(f"🤖 Sentence Transformers 모델 사용: {model_name}")

    async def get_embedding(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩합니다.

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터
        """
        embeddings = await self.get_embeddings([text])
        return embeddings[0] if embeddings else []

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트를 배치로 나누어 임베딩합니다.

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        if not texts:
            return []

        if self.use_openai:
            return await self._get_openai_embeddings_batch(texts)
        else:
            return await self._get_local_embeddings_batch(texts)

    async def _get_openai_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """OpenAI API 배치 처리"""
        all_embeddings = []

        # 텍스트를 배치로 나누어 처리
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]

            try:
                response = await self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=batch_texts
                )
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)

                # API 호출 간격 조절 (rate limit 방지)
                if i + self.batch_size < len(texts):
                    await asyncio.sleep(0.1)

                logger.debug(f"OpenAI 임베딩 진행률: {min(i + self.batch_size, len(texts))}/{len(texts)}")

            except Exception as e:
                logger.error(f"OpenAI 배치 임베딩 실패 (배치 {i // self.batch_size + 1}): {e}")
                # 폴백으로 로컬 모델 사용
                fallback_embeddings = await self._get_local_embeddings_batch(batch_texts)
                all_embeddings.extend(fallback_embeddings)

        return all_embeddings

    async def _get_local_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """로컬 모델 배치 처리 (ThreadPoolExecutor 사용)"""
        loop = asyncio.get_event_loop()

        async def process_batch(batch_texts):
            return await loop.run_in_executor(
                self.executor,
                lambda: self.model.encode(batch_texts, show_progress_bar=False).tolist()
            )

        all_embeddings = []

        # 텍스트를 배치로 나누어 처리
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = await process_batch(batch_texts)
            all_embeddings.extend(batch_embeddings)

            logger.debug(f"로컬 임베딩 진행률: {min(i + self.batch_size, len(texts))}/{len(texts)}")

        return all_embeddings

    def prepare_documents_for_indexing(self, data: Dict[str, Any], collection_type: str) -> List[Dict[str, Any]]:
        """
        데이터를 벡터 DB 인덱싱용으로 변환합니다.

        Args:
            data: 원본 데이터
            collection_type: 컬렉션 타입 ('korean_word_problems' 또는 'card_check')

        Returns:
            인덱싱용 문서 리스트
        """
        documents = []

        if collection_type == "korean_word_problems":
            # 한국어 단어 문제 데이터 처리
            questions = data.get("questions", [])
            option_cards = data.get("option_cards", [])

            # 문제별로 문서 생성
            for question in questions:
                # ID 필드가 있으면 사용, 없으면 기본 ID 생성
                question_id = question.get('id', f"question_{question['number']}")
                doc_text = f"문제 {question['number']}: {question['sentence']} 정답: {question['answer']}"

                documents.append({
                    "id": question_id,
                    "text": doc_text,
                    "metadata": {
                        "type": "question",
                        "number": str(question['number']),
                        "sentence": question['sentence'],
                        "answer": question['answer'],
                        "collection": collection_type
                    }
                })

            # 옵션 카드별로 문서 생성
            for i, card in enumerate(option_cards):
                documents.append({
                    "id": f"option_card_{i}",
                    "text": card,
                    "metadata": {
                        "type": "option_card",
                        "card_index": str(i),
                        "content": card,
                        "collection": collection_type
                    }
                })

        elif collection_type == "card_check":
            # 카드 체크 데이터 처리
            for i, card in enumerate(data):
                doc_text = f"단어: {card['word']} 의미: {card['meaning']}"
                if card.get('examples'):
                    examples_str = ", ".join(card['examples'])
                    doc_text += f" 예시: {examples_str}"

                documents.append({
                    "id": f"card_{i}",
                    "text": doc_text,
                    "metadata": {
                        "type": "card",
                        "word": card['word'],
                        "meaning": card['meaning'],
                        "examples": ", ".join(card.get('examples', [])),
                        "collection": collection_type
                    }
                })

        elif collection_type == "pdf_documents":  # 신규 추가
            # PDF 문서 데이터는 이미 전처리된 상태로 들어옴
            for doc in data:
                documents.append({
                    "id": doc["id"],
                    "text": doc["text"],
                    "metadata": doc["metadata"]
                })

        return documents

    def __del__(self):
        """소멸자에서 ThreadPoolExecutor 정리"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# 전역 임베딩 모델 인스턴스
embedding_model = None


def get_embedding_model():
    """전역 임베딩 모델 인스턴스를 반환합니다."""
    global embedding_model
    if embedding_model is None:
        embedding_model = EmbeddingModel()
    return embedding_model