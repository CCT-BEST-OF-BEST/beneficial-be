"""
OpenAI 연결 통합 테스트.

기본 pytest 실행에서는 외부 API를 호출하지 않는다.
실행하려면 RUN_INTEGRATION_TESTS=1 과 OPENAI_API_KEY 를 설정한다.
"""
import os

import pytest
from dotenv import load_dotenv

load_dotenv()

if os.getenv("RUN_INTEGRATION_TESTS") != "1":
    pytest.skip(
        "OpenAI integration test requires RUN_INTEGRATION_TESTS=1",
        allow_module_level=True,
    )

if not os.getenv("OPENAI_API_KEY"):
    pytest.skip("OPENAI_API_KEY is required for this integration test", allow_module_level=True)

from app.domains.chat.service import get_chat_service


@pytest.mark.asyncio
@pytest.mark.integration
async def test_chat_with_gpt():
    chat_service = get_chat_service()
    response = await chat_service.simple_chat("맞히다와 맞추다의 차이를 짧게 알려줘")

    assert isinstance(response, str)
    assert len(response) > 0
