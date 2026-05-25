from app.domains.learning.schemas import Stage2SubmitResponse
from app.domains.learning.stages.stage3_schemas import Stage3AnswerRequest


def test_stage3_answer_request_model():
    request = Stage3AnswerRequest(problem_id=1, user_answer="돼")

    assert request.problem_id == 1
    assert request.user_answer == "돼"


def test_stage2_submit_response_keeps_legacy_admin_flag_for_bypass():
    response = Stage2SubmitResponse(
        problem_id=1,
        is_correct=False,
        user_answer="아무답",
        correct_answer="가르쳐",
        full_sentence="선생님이 수학 공식을 가르쳐 주셨다.",
        concept_key="가르치다/가르키다",
        is_answer_bypass_enabled=True,
        is_admin=True,
    )

    assert response.is_answer_bypass_enabled is True
    assert response.is_admin is True
