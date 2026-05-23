"""
/agent/chat 통합 smoke test.

실제 OpenAI / Mongo / Chroma를 사용해 LangGraph 파이프라인이 끝까지 도는지 확인한다.

실행 조건:
- RUN_INTEGRATION_TESTS=1
- OPENAI_API_KEY, MongoDB, Chroma가 사용 가능한 환경
"""
import os
import uuid

import pytest

if os.getenv("RUN_INTEGRATION_TESTS") != "1":
    pytest.skip(
        "Agent chat integration test requires RUN_INTEGRATION_TESTS=1 and "
        "live OpenAI / Mongo / Chroma services.",
        allow_module_level=True,
    )

from fastapi.testclient import TestClient

from app.main import app


def _signup_and_login(client: TestClient) -> tuple[str, str]:
    """고유 사용자를 만들고 access token + user_id를 반환."""
    email = f"smoke_{uuid.uuid4().hex[:10]}@test.local"
    password = "smoke-pass-1234"
    display_name = "smoke"

    signup = client.post(
        "/auth/signup",
        json={"email": email, "password": password, "display_name": display_name},
    )
    assert signup.status_code == 201, signup.text
    user_id = signup.json()["user_id"]

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text
    return login.json()["access_token"], user_id


def test_agent_chat_smoke_full_pipeline():
    """signup → login → /agent/chat 한 번 호출 → 세션 조회 → 정리."""
    with TestClient(app) as client:
        access_token, user_id = _signup_and_login(client)
        headers = {"Authorization": f"Bearer {access_token}"}

        chat_resp = client.post(
            "/agent/chat",
            headers=headers,
            json={"message": "되와 돼는 어떻게 다른가요?"},
        )
        assert chat_resp.status_code == 200, chat_resp.text
        body = chat_resp.json()

        # 그래프가 끝까지 돌고 응답 스키마가 채워졌는지 확인
        assert body["session_id"]
        assert isinstance(body["response"], str) and body["response"].strip()
        assert body["agent_action"] in {
            "answer_with_rag",
            "proactive_hint",
            "encourage",
            "small_talk",
            "ask_followup",
        }
        assert isinstance(body["used_tools"], list)
        assert isinstance(body["weak_concepts"], list)

        session_id = body["session_id"]

        # 세션이 실제로 저장되어 user/assistant 메시지가 들어있는지 확인
        session_resp = client.get(f"/agent/session/{session_id}", headers=headers)
        assert session_resp.status_code == 200, session_resp.text
        session = session_resp.json()
        assert session["user_id"] == user_id
        roles = [m["role"] for m in session["messages"]]
        assert "user" in roles and "assistant" in roles

        # 정리
        delete_resp = client.delete(f"/agent/session/{session_id}", headers=headers)
        assert delete_resp.status_code == 204
