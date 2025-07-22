import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
from app.common.config.loader.config_loader import load_rag_config

def get_korean_word_problems():
    MONGO_URI = os.getenv("MONGO_URI")
    config = load_rag_config()["collections"]["korean_word_problems"]

    client = MongoClient(MONGO_URI)
    db = client["beneficial_db"]
    doc = db["korean_word_problems"].find_one({})

    if not doc:
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

    return {
        "option_cards": option_cards,
        "questions": questions
    }

# 간단 테스트
if __name__ == "__main__":
    from pprint import pprint
    pprint(get_korean_word_problems())
