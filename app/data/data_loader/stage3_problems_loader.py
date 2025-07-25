# beneficial-be/app/data/data_loader/stage3_problems_loader.py

from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

def load_stage3_problems():
    """3단계 문제풀이 데이터를 MongoDB에 저장"""
    try:
        mongo_client = get_mongo_client()
        collection_name = "stage3_problems"
        
        # 기존 컬렉션 삭제 (개발용)
        mongo_client.db[collection_name].drop()
        
        # 3단계 문제 데이터 (실제 문제에 맞게 단순화)
        stage3_data = {
            "_id": "stage3_problems",
            "title": "3단계 문제풀이",
            "instruction": "빈칸에 알맞은 맞춤법을 작성하세요",
            "problems": [
                {
                    "problem_id": 1,
                    "sentence_part1": "차에 타면 안전벨트를 매는 것을",
                    "correct_answer": "잊지",
                    "sentence_part2": "마!",
                    "full_sentence": "차에 타면 안전벨트를 매는 것을 잊지 마!",
                    "explanation": "잊지: '잊다'의 어간 '잊-'에 '-지'가 붙은 형태로, '잊지 말아라'의 준말입니다.",
                    "image": "stage3/problem_1.png"
                },
                {
                    "problem_id": 2,
                    "sentence_part1": "용돈이 오르기를 간절히",
                    "correct_answer": "바랐",
                    "sentence_part2": "다.",
                    "full_sentence": "용돈이 오르기를 간절히 바랐다.",
                    "explanation": "바랐: '바라다'의 어간 '바라-'에 '-었'이 붙은 형태로, 과거의 희망을 나타냅니다.",
                    "image": "stage3/problem_2.png"
                },
                {
                    "problem_id": 3,
                    "sentence_part1": "유진이는 손가락으로 오른쪽을",
                    "correct_answer": "가르켰",
                    "sentence_part2": "다.",
                    "full_sentence": "유진이는 손가락으로 오른쪽을 가르켰다.",
                    "explanation": "가르켰: '가르키다'의 어간 '가르키-'에 '-었'이 붙은 형태로, '가르키다'는 '지시하다'의 의미입니다.",
                    "image": "stage3/problem_3.png"
                },
                {
                    "problem_id": 4,
                    "sentence_part1": "가원이는 가방을",
                    "correct_answer": "메고",
                    "sentence_part2": "학교에 갔다",
                    "full_sentence": "가원이는 가방을 메고 학교에 갔다",
                    "explanation": "메고: '메다'의 어간 '메-'에 '-고'가 붙은 형태로, '메다'는 '어깨에 걸치다'의 의미입니다.",
                    "image": "stage3/problem_4.png"
                },
                {
                    "problem_id": 5,
                    "sentence_part1": "지훈이 허리띠를",
                    "correct_answer": "매고",
                    "sentence_part2": "있다.",
                    "full_sentence": "지훈이 허리띠를 매고 있다.",
                    "explanation": "매고: '매다'의 어간 '매-'에 '-고'가 붙은 형태로, '매다'는 '묶다'의 의미입니다.",
                    "image": "stage3/problem_5.png"
                }
            ],
            "total_problems": 5
        }
        
        # 데이터 삽입
        result = mongo_client.insert_one(collection_name, stage3_data)
        logger.info(f"✅ 3단계 문제풀이 데이터 삽입 완료: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 3단계 데이터 로딩 실패: {e}")
        return False

if __name__ == "__main__":
    load_stage3_problems() 