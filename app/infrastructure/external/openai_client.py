import os
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAIClient:
    """OpenAI API 클라이언트 전용"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = "gpt-3.5-turbo"
        self.max_tokens = 500
        self.temperature = 0.7

    async def chat_completion(self, messages: List[Dict[str, str]],
                              model: str = None,
                              max_tokens: int = None,
                              temperature: float = None) -> str:
        """
        GPT API 호출만 담당

        Args:
            messages: 메시지 리스트 [{"role": "system", "content": "..."}, ...]
            model: 사용할 모델명
            max_tokens: 최대 토큰 수
            temperature: 창의성 조절 (0.0-1.0)

        Returns:
            GPT 응답 텍스트
        """
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API 호출 실패: {str(e)}")

    async def generate_response_with_context(self, prompt: str, context: str = None,
                                             system_prompt: str = None) -> str:
        """
        컨텍스트와 함께 응답 생성

        Args:
            prompt: 사용자 질문
            context: 참고할 컨텍스트
            system_prompt: 시스템 프롬프트

        Returns:
            GPT 응답
        """
        messages = []

        # 시스템 메시지
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 사용자 메시지 (컨텍스트 포함)
        if context:
            user_content = f"참고 자료:\n{context}\n\n질문: {prompt}"
        else:
            user_content = prompt

        messages.append({"role": "user", "content": user_content})

        return await self.chat_completion(messages)

    async def get_embedding(self, text: str) -> List[float]:
        """
        텍스트 임베딩 생성

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터
        """
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding

        except Exception as e:
            raise Exception(f"임베딩 생성 실패: {str(e)}")

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        배치 임베딩 생성

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            return [data.embedding for data in response.data]

        except Exception as e:
            raise Exception(f"배치 임베딩 생성 실패: {str(e)}")


def get_openai_client() -> OpenAIClient:
    """OpenAI 클라이언트 인스턴스 반환"""
    return OpenAIClient()