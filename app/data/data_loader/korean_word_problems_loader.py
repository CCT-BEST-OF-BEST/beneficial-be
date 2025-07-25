from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.config.loader.config_loader import load_rag_config
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)


def get_korean_word_problems():
    """한국어 단어 문제 데이터 로드"""
    try:
        # 통합된 MongoDB 클라이언트 사용
        mongo_client = get_mongo_client()
        config = load_rag_config()["collections"]["korean_word_problems"]

        # 데이터 조회 - 모든 문서 가져오기
        docs = mongo_client.find_many("korean_word_problems")

        if not docs:
            logger.warning("⚠️ 한국어 단어 문제 데이터가 없습니다.")
            return {}

        all_questions = []
        all_option_cards = []

        # 각 차시별 데이터 처리
        for doc in docs:
            lesson_id = doc.get("lessonId", "0")
            option_cards = doc.get("option_cards", [])
            questions = doc.get("questions", [])
            
            # 문제 데이터 처리
            for idx, q in enumerate(questions, 1):
                # 차시별로 고유한 ID 생성 (예: lesson1_q1, lesson2_q1, ...)
                question_id = f"lesson{lesson_id}_q{idx}"
                all_questions.append({
                    "id": question_id,  # 고유 ID 추가
                    "number": idx,
                    "sentence": q.get("sentence", ""),
                    "answer": q.get("answer", "")
                })
            
            all_option_cards.extend(option_cards)

        logger.info(f"✅ 한국어 단어 문제 데이터 로드 완료: 문제 {len(all_questions)}개, 옵션 카드 {len(all_option_cards)}개")

        return {
            "option_cards": all_option_cards,
            "questions": all_questions
        }

    except Exception as e:
        logger.error(f"❌ 한국어 단어 문제 데이터 로드 실패: {e}")
        return {}


# 간단 테스트
if __name__ == "__main__":
    from pprint import pprint

    pprint(get_korean_word_problems())