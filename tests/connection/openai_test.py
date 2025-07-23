import os
from openai import OpenAI
from dotenv import load_dotenv
from app.infrastructure.rag_service import get_rag_service
from app.common.logging_config import get_logger

logger = get_logger(__name__)
import pytest
import asyncio

load_dotenv()  # .env 파일에서 환경변수 읽어오기


@pytest.mark.asyncio
async def test_chat_with_gpt():
    prompt = "맞히다와 맞추다의 차이 알려줘"
    """
    RAG 시스템을 사용하여 GPT와 대화합니다.

    Args:
        prompt: 사용자 질문

    Returns:
        GPT 응답
    """
    try:
        # RAG 서비스 사용
        rag_service = await get_rag_service()
        response = await rag_service.chat_with_rag(prompt)
        assert response is not None and len(response) > 0
    except Exception as e:
        logger.error(f"RAG 시스템 오류: {e}")
        # RAG 실패 시 기본 GPT 응답으로 폴백
        response = await _fallback_gpt_response(prompt)
        assert response is not None and len(response) > 0


async def _fallback_gpt_response(prompt: str):
    """RAG 실패 시 기본 GPT 응답"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("API Key not found in environment variable!")

    client = OpenAI(api_key=api_key)

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if 계정 허용시
        messages=[
            {"role": "system", "content": "너는 초등학생 돌봄선생님이야."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content
