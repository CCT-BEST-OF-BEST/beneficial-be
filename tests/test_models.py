from app.domains.chat.schemas import ChatRequest, ChatResponse
from app.domains.learning.stage3_schemas import Stage3AnswerRequest


def test_chat_request_model():
    request = ChatRequest(prompt="맞히다와 맞추다의 차이를 알려줘")

    assert request.prompt == "맞히다와 맞추다의 차이를 알려줘"


def test_chat_response_model():
    response = ChatResponse(
        status="success",
        prompt="안녕",
        response="안녕!",
        collection_used="all",
        top_k=5,
    )

    assert response.status == "success"
    assert response.collection_used == "all"
    assert response.top_k == 5


def test_stage3_answer_request_model():
    request = Stage3AnswerRequest(problem_id=1, user_answer="돼")

    assert request.problem_id == 1
    assert request.user_answer == "돼"
