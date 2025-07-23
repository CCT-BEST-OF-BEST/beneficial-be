import os
from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.config.loader.config_loader import load_rag_config


def get_card_check_data():
    """카드 체크 데이터 로드"""
    try:
        # 통합된 MongoDB 클라이언트 사용
        mongo_client = get_mongo_client()
        config = load_rag_config()["collections"]["card_check"]

        # 데이터 조회
        doc = mongo_client.find_one("card_check", {})

        if not doc:
            print("⚠️ 카드 체크 데이터가 없습니다.")
            return []

        result = []
        for card in doc[config["cards_field"]]:
            result.append({
                "word": card[config["card_word_field"]],
                "meaning": card[config["card_meaning_field"]],
                "examples": card[config["card_examples_field"]]
            })

        print(f"✅ 카드 체크 데이터 로드 완료: {len(result)}개 카드")

        return result

    except Exception as e:
        print(f"❌ 카드 체크 데이터 로드 실패: {e}")
        return []


# 간단 테스트
if __name__ == "__main__":
    from pprint import pprint

    pprint(get_card_check_data())