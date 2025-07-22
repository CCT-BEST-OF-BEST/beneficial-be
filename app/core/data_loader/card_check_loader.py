import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv() # .env 파일 로드
from app.common.config.loader.config_loader import load_rag_config

def get_card_check_data():
    # 환경 변수로부터 MONGO_URI 읽기 (.env에서 관리)
    MONGO_URI = os.getenv("MONGO_URI")
    config = load_rag_config()["collections"]["card_check"]

    client = MongoClient(MONGO_URI)
    db = client["beneficial_db"]
    # (여기선 한 세트만 있다고 가정)
    doc = db["card_check"].find_one({})

    if not doc:
        return []

    result = []
    for card in doc[config["cards_field"]]:
        result.append({
            "word": card[config["card_word_field"]],
            "meaning": card[config["card_meaning_field"]],
            "examples": card[config["card_examples_field"]]
        })
    return result

# 간단 테스트
if __name__ == "__main__":
    from pprint import pprint
    pprint(get_card_check_data())
