# beneficial-be/app/data/data_loader/stage2_problems_loader.py

from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

def load_stage2_problems():
    """2단계 예제풀이 데이터를 MongoDB에 저장"""
    try:
        mongo_client = get_mongo_client()
        collection_name = "stage2_problems"
        
        # 기존 컬렉션 삭제 (개발용)
        mongo_client.db[collection_name].drop()
        
        # 2단계 문제 데이터
        stage2_data = {
            "_id": "stage2_lesson1",
            "lesson_id": "lesson1",
            "title": "2단계 예제풀이",
            "instruction": "맞춤법에 맞는 낱말 카드를 선택하세요",
            "answer_options": [
                "가르쳐", "맞힐", "바라는", "가르켰", "맞춰", "잊지", "바랐", "잊으려고"
            ],
            "problems": [
                {
                    "problem_id": 1,
                    "sentence_part1": "왜 화가 났는지",
                    "correct_answer": "가르쳐",
                    "sentence_part2": "줘",
                    "full_sentence": "왜 화가 났는지 가르쳐 줘"
                },
                {
                    "problem_id": 2,
                    "sentence_part1": "개념을 알아야만",
                    "correct_answer": "맞힐",
                    "sentence_part2": "수 있는 문제다",
                    "full_sentence": "개념을 알아야만 맞힐 수 있는 문제다"
                },
                {
                    "problem_id": 3,
                    "sentence_part1": "슬픔을",
                    "correct_answer": "잊으려고",
                    "sentence_part2": "노력 중이에요",
                    "full_sentence": "슬픔을 잊으려고 노력 중이에요"
                },
                {
                    "problem_id": 4,
                    "sentence_part1": "새해에는",
                    "correct_answer": "바라는",
                    "sentence_part2": "모든 일들이 이루어지기를 빌겠습니다",
                    "full_sentence": "새해에는 바라는 모든 일들이 이루어지기를 빌겠습니다"
                },
                {
                    "problem_id": 5,
                    "sentence_part1": "유진이는 손가락으로 오른쪽을",
                    "correct_answer": "가르켰",
                    "sentence_part2": "다",
                    "full_sentence": "유진이는 손가락으로 오른쪽을 가르켰다"
                },
                {
                    "problem_id": 6,
                    "sentence_part1": "여행을 가기 위해 친구와 일정을",
                    "correct_answer": "맞춰",
                    "sentence_part2": "보았다",
                    "full_sentence": "여행을 가기 위해 친구와 일정을 맞춰 보았다"
                },
                {
                    "problem_id": 7,
                    "sentence_part1": "차에 타면 안전벨트 매는 것을",
                    "correct_answer": "잊지",
                    "sentence_part2": "마",
                    "full_sentence": "차에 타면 안전벨트를 매는 것을 잊지 마"
                },
                {
                    "problem_id": 8,
                    "sentence_part1": "용돈이 오르기를 간절히",
                    "correct_answer": "바랐",
                    "sentence_part2": "다",
                    "full_sentence": "용돈이 오르기를 간절히 바랐다"
                }
            ],
            "total_problems": 8
        }
        
        # 데이터 삽입
        result = mongo_client.insert_one(collection_name, stage2_data)
        logger.info(f"✅ 2단계 예제풀이 데이터 삽입 완료: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 2단계 데이터 로딩 실패: {e}")
        return False

if __name__ == "__main__":
    load_stage2_problems() 