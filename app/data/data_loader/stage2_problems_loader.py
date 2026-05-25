# beneficial-be/app/data/data_loader/stage2_problems_loader.py

from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

STAGE2_INSTRUCTION = "맞춤법에 맞는 낱말 카드를 선택하세요"

STAGE2_LESSON_DATA = [
    {
        "_id": "stage2_lesson_1",
        "lesson_id": "lesson_1",
        "title": "2단계 예제풀이 - 차시 1",
        "instruction": STAGE2_INSTRUCTION,
        "answer_options": ["가르쳐", "가르켰다", "맞췄다", "맞혀"],
        "problems": [
            {
                "problem_id": 1,
                "sentence_part1": "선생님이 수학 공식을",
                "correct_answer": "가르쳐",
                "sentence_part2": "주셨다.",
                "full_sentence": "선생님이 수학 공식을 가르쳐 주셨다.",
            },
            {
                "problem_id": 2,
                "sentence_part1": "그가 손가락으로 저 건물을",
                "correct_answer": "가르켰다",
                "sentence_part2": ".",
                "full_sentence": "그가 손가락으로 저 건물을 가르켰다.",
            },
            {
                "problem_id": 3,
                "sentence_part1": "친구와 약속 시간을",
                "correct_answer": "맞췄다",
                "sentence_part2": ".",
                "full_sentence": "친구와 약속 시간을 맞췄다.",
            },
            {
                "problem_id": 4,
                "sentence_part1": "수수께끼를",
                "correct_answer": "맞혀",
                "sentence_part2": "보세요.",
                "full_sentence": "수수께끼를 맞혀 보세요.",
            },
        ],
    },
    {
        "_id": "stage2_lesson_2",
        "lesson_id": "lesson_2",
        "title": "2단계 예제풀이 - 차시 2",
        "instruction": STAGE2_INSTRUCTION,
        "answer_options": ["잃어버렸다", "잊었다", "메고", "매고"],
        "problems": [
            {
                "problem_id": 5,
                "sentence_part1": "버스 안에서 지갑을",
                "correct_answer": "잃어버렸다",
                "sentence_part2": ".",
                "full_sentence": "버스 안에서 지갑을 잃어버렸다.",
            },
            {
                "problem_id": 6,
                "sentence_part1": "숙제하는 것을 깜빡",
                "correct_answer": "잊었다",
                "sentence_part2": ".",
                "full_sentence": "숙제하는 것을 깜빡 잊었다.",
            },
            {
                "problem_id": 7,
                "sentence_part1": "배낭을 어깨에",
                "correct_answer": "메고",
                "sentence_part2": "산에 올랐다.",
                "full_sentence": "배낭을 어깨에 메고 산에 올랐다.",
            },
            {
                "problem_id": 8,
                "sentence_part1": "안전벨트를",
                "correct_answer": "매고",
                "sentence_part2": "출발했다.",
                "full_sentence": "안전벨트를 매고 출발했다.",
            },
        ],
    },
    {
        "_id": "stage2_lesson_3",
        "lesson_id": "lesson_3",
        "title": "2단계 예제풀이 - 차시 3",
        "instruction": STAGE2_INSTRUCTION,
        "answer_options": ["바란다", "바랬다", "부쳤다", "붙였다"],
        "problems": [
            {
                "problem_id": 9,
                "sentence_part1": "시험에 합격하기를",
                "correct_answer": "바란다",
                "sentence_part2": ".",
                "full_sentence": "시험에 합격하기를 바란다.",
            },
            {
                "problem_id": 10,
                "sentence_part1": "오래된 청바지 색이",
                "correct_answer": "바랬다",
                "sentence_part2": ".",
                "full_sentence": "오래된 청바지 색이 바랬다.",
            },
            {
                "problem_id": 11,
                "sentence_part1": "할머니께 편지를",
                "correct_answer": "부쳤다",
                "sentence_part2": ".",
                "full_sentence": "할머니께 편지를 부쳤다.",
            },
            {
                "problem_id": 12,
                "sentence_part1": "봉투에 우표를",
                "correct_answer": "붙였다",
                "sentence_part2": ".",
                "full_sentence": "봉투에 우표를 붙였다.",
            },
        ],
    },
    {
        "_id": "stage2_lesson_4",
        "lesson_id": "lesson_4",
        "title": "2단계 예제풀이 - 차시 4",
        "instruction": STAGE2_INSTRUCTION,
        "answer_options": ["되고", "돼", "안", "않다"],
        "problems": [
            {
                "problem_id": 13,
                "sentence_part1": "의사가",
                "correct_answer": "되고",
                "sentence_part2": "싶다.",
                "full_sentence": "의사가 되고 싶다.",
            },
            {
                "problem_id": 14,
                "sentence_part1": "그렇게 하면 안",
                "correct_answer": "돼",
                "sentence_part2": ".",
                "full_sentence": "그렇게 하면 안 돼.",
            },
            {
                "problem_id": 15,
                "sentence_part1": "밥을",
                "correct_answer": "안",
                "sentence_part2": "먹었다.",
                "full_sentence": "밥을 안 먹었다.",
            },
            {
                "problem_id": 16,
                "sentence_part1": "오늘은 춥지",
                "correct_answer": "않다",
                "sentence_part2": ".",
                "full_sentence": "오늘은 춥지 않다.",
            },
        ],
    },
    {
        "_id": "stage2_lesson_5",
        "lesson_id": "lesson_5",
        "title": "2단계 예제풀이 - 차시 5",
        "instruction": STAGE2_INSTRUCTION,
        "answer_options": ["반드시", "반듯이", "이따가", "있다가"],
        "problems": [
            {
                "problem_id": 17,
                "sentence_part1": "약속은",
                "correct_answer": "반드시",
                "sentence_part2": "지켜야 한다.",
                "full_sentence": "약속은 반드시 지켜야 한다.",
            },
            {
                "problem_id": 18,
                "sentence_part1": "자세를",
                "correct_answer": "반듯이",
                "sentence_part2": "하고 앉아라.",
                "full_sentence": "자세를 반듯이 하고 앉아라.",
            },
            {
                "problem_id": 19,
                "sentence_part1": "",
                "correct_answer": "이따가",
                "sentence_part2": "같이 밥 먹자.",
                "full_sentence": "이따가 같이 밥 먹자.",
            },
            {
                "problem_id": 20,
                "sentence_part1": "여기",
                "correct_answer": "있다가",
                "sentence_part2": "집에 갔다.",
                "full_sentence": "여기 있다가 집에 갔다.",
            },
        ],
    },
]

for lesson_data in STAGE2_LESSON_DATA:
    lesson_data["total_problems"] = len(lesson_data["problems"])

STAGE2_DATA = {
    "_id": "stage2_all",
    "lesson_id": "legacy_all",
    "title": "2단계 예제풀이",
    "instruction": STAGE2_INSTRUCTION,
    "answer_options": [
        option
        for lesson in STAGE2_LESSON_DATA
        for option in lesson["answer_options"]
    ],
    "problems": [
        problem
        for lesson in STAGE2_LESSON_DATA
        for problem in lesson["problems"]
    ],
    "total_problems": 20,
}


def load_stage2_problems():
    """2단계 예제풀이 데이터를 MongoDB에 저장"""
    try:
        mongo_client = get_mongo_client()
        collection_name = "stage2_problems"

        mongo_client.db[collection_name].drop()
        result = mongo_client.insert_many(collection_name, STAGE2_LESSON_DATA)
        logger.info(f"[OK] 2단계 예제풀이 데이터 삽입 완료: {len(result.inserted_ids)}개 차시")
        return True

    except Exception as e:
        logger.error(f"[ERROR] 2단계 데이터 로딩 실패: {e}")
        return False


if __name__ == "__main__":
    load_stage2_problems()
