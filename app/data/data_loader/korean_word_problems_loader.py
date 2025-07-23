import os
from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.config.loader.config_loader import load_rag_config


def get_korean_word_problems():
    """한국어 단어 문제 데이터 로드"""
    try:
        # 통합된 MongoDB 클라이언트 사용
        mongo_client = get_mongo_client()
        config = load_rag_config()["collections"]["korean_word_problems"]

        # 데이터 조회
        doc = mongo_client.find_one("korean_word_problems", {})

        if not doc:
            print("⚠️ 한국어 단어 문제 데이터가 없습니다.")
            return {}

        # option_cards, questions 파싱
        option_cards = doc.get(config["option_cards_field"], [])
        questions_raw = doc.get(config["questions_field"], [])

        questions = []
        for q in questions_raw:
            questions.append({
                "number": q[config["question_number_field"]],
                "sentence": q[config["question_sentence_field"]],
                "answer": q[config["question_answer_field"]]
            })

        print(f"✅ 한국어 단어 문제 데이터 로드 완료: 문제 {len(questions)}개, 옵션 카드 {len(option_cards)}개")

        return {
            "option_cards": option_cards,
            "questions": questions
        }

    except Exception as e:
        print(f"❌ 한국어 단어 문제 데이터 로드 실패: {e}")
        return {}


# 간단 테스트
if __name__ == "__main__":
    from pprint import pprint

    pprint(get_korean_word_problems())