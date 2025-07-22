import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class EmbeddingModel:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        임베딩 모델 초기화

        Args:
            model_name: 사용할 임베딩 모델명
        """
        self.model_name = model_name
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # OpenAI API 키가 있으면 OpenAI 사용, 없으면 sentence-transformers 사용
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
            self.use_openai = True
            print("🔑 OpenAI 임베딩 모델 사용")
        else:
            self.model = SentenceTransformer(model_name)
            self.use_openai = False
            print(f"🤖 Sentence Transformers 모델 사용: {model_name}")

    async def get_embedding(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩합니다.

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터
        """
        if self.use_openai:
            try:
                response = await self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"OpenAI 임베딩 실패: {e}")
                # OpenAI 실패 시 sentence-transformers로 폴백
                return self.model.encode(text).tolist()
        else:
            return self.model.encode(text).tolist()

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트를 임베딩합니다.

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        if self.use_openai:
            try:
                response = await self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=texts
                )
                return [data.embedding for data in response.data]
            except Exception as e:
                print(f"OpenAI 임베딩 실패: {e}")
                # OpenAI 실패 시 sentence-transformers로 폴백
                return self.model.encode(texts).tolist()
        else:
            return self.model.encode(texts).tolist()


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
                doc_text = f"문제 {question['number']}: {question['sentence']} 정답: {question['answer']}"

                documents.append({
                    "id": f"question_{question['number']}",
                    "text": doc_text,
                    "metadata": {
                        "type": "question",
                        "number": str(question['number']),  # int를 str로 변환
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
                        "card_index": str(i),  # int를 str로 변환
                        "content": card,
                        "collection": collection_type
                    }
                })

        elif collection_type == "card_check":
            # 카드 체크 데이터 처리
            for i, card in enumerate(data):
                doc_text = f"단어: {card['word']} 의미: {card['meaning']}"
                if card.get('examples'):
                    # 리스트를 문자열로 변환
                    examples_str = ", ".join(card['examples'])
                    doc_text += f" 예시: {examples_str}"

                documents.append({
                    "id": f"card_{i}",
                    "text": doc_text,
                    "metadata": {
                        "type": "card",
                        "word": card['word'],
                        "meaning": card['meaning'],
                        "examples": ", ".join(card.get('examples', [])),  # 리스트를 문자열로 변환
                        "collection": collection_type
                    }
                })

        return documents


# 전역 임베딩 모델 인스턴스
embedding_model = None


def get_embedding_model():
    """전역 임베딩 모델 인스턴스를 반환합니다."""
    global embedding_model
    if embedding_model is None:
        embedding_model = EmbeddingModel()
    return embedding_model