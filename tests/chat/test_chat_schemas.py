from app.domains.agent.schema.schemas import ChatRequest, ChatResponse


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
