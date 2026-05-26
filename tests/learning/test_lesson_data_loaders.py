from app.common.data.data_loader.stage2_problems_loader import STAGE2_LESSON_DATA
from app.common.data.data_loader.stage3_problems_loader import STAGE3_LESSON_DATA


def test_stage2_loader_defines_lesson_scoped_documents():
    assert [doc["lesson_id"] for doc in STAGE2_LESSON_DATA] == [
        "lesson_1",
        "lesson_2",
        "lesson_3",
        "lesson_4",
        "lesson_5",
    ]
    assert [problem["problem_id"] for problem in STAGE2_LESSON_DATA[1]["problems"]] == [
        5,
        6,
        7,
        8,
    ]
    assert STAGE2_LESSON_DATA[1]["total_problems"] == 4


def test_stage3_loader_defines_lesson_scoped_documents():
    assert [doc["lesson_id"] for doc in STAGE3_LESSON_DATA] == [
        "lesson_1",
        "lesson_2",
        "lesson_3",
        "lesson_4",
        "lesson_5",
    ]
    assert [problem["problem_id"] for problem in STAGE3_LESSON_DATA[2]["problems"]] == [
        11,
        12,
        13,
        14,
        15,
    ]
    assert STAGE3_LESSON_DATA[2]["total_problems"] == 5
