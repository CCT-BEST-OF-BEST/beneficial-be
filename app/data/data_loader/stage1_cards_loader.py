# beneficial-be/app/data/data_loader/stage1_cards_loader.py

from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

STAGE1_CARD_PAIRS = [
    # 차시 1: 가르치다/가르키다, 맞추다/맞히다
    {
        "_id": "pair_1",
        "pair_id": "pair_1",
        "word1": "가르치다",
        "word2": "가르키다",
        "card1": {"card_id": "card_1", "front_image": "/images/cards/card1_front.png", "back_image": "/images/cards/card1_back.png"},
        "card2": {"card_id": "card_2", "front_image": "/images/cards/card2_front.png", "back_image": "/images/cards/card2_back.png"},
        "order": 1,
    },
    {
        "_id": "pair_2",
        "pair_id": "pair_2",
        "word1": "맞추다",
        "word2": "맞히다",
        "card1": {"card_id": "card_3", "front_image": "/images/cards/card3_front.png", "back_image": "/images/cards/card3_back.png"},
        "card2": {"card_id": "card_4", "front_image": "/images/cards/card4_front.png", "back_image": "/images/cards/card4_back.png"},
        "order": 2,
    },
    # 차시 2: 잊다/잃다, 메다/매다
    {
        "_id": "pair_3",
        "pair_id": "pair_3",
        "word1": "잊다",
        "word2": "잃다",
        "card1": {"card_id": "card_5", "front_image": "/images/cards/card5_front.png", "back_image": "/images/cards/card5_back.png"},
        "card2": {"card_id": "card_6", "front_image": "/images/cards/card6_front.png", "back_image": "/images/cards/card6_back.png"},
        "order": 3,
    },
    {
        "_id": "pair_4",
        "pair_id": "pair_4",
        "word1": "메다",
        "word2": "매다",
        "card1": {"card_id": "card_7", "front_image": "/images/cards/card7_front.png", "back_image": "/images/cards/card7_back.png"},
        "card2": {"card_id": "card_8", "front_image": "/images/cards/card8_front.png", "back_image": "/images/cards/card8_back.png"},
        "order": 4,
    },
    # 차시 3: 바라다/바래다, 부치다/붙이다
    {
        "_id": "pair_5",
        "pair_id": "pair_5",
        "word1": "바라다",
        "word2": "바래다",
        "card1": {"card_id": "card_9", "front_image": "/images/cards/card9_front.png", "back_image": "/images/cards/card9_back.png"},
        "card2": {"card_id": "card_10", "front_image": "/images/cards/card10_front.png", "back_image": "/images/cards/card10_back.png"},
        "order": 5,
    },
    {
        "_id": "pair_6",
        "pair_id": "pair_6",
        "word1": "부치다",
        "word2": "붙이다",
        "card1": {"card_id": "card_11", "front_image": "/images/cards/card11_front.png", "back_image": "/images/cards/card11_back.png"},
        "card2": {"card_id": "card_12", "front_image": "/images/cards/card12_front.png", "back_image": "/images/cards/card12_back.png"},
        "order": 6,
    },
    # 차시 4: 되다/돼다, 안/않다
    {
        "_id": "pair_7",
        "pair_id": "pair_7",
        "word1": "되다",
        "word2": "돼다",
        "card1": {"card_id": "card_13", "front_image": "/images/cards/card13_front.png", "back_image": "/images/cards/card13_back.png"},
        "card2": {"card_id": "card_14", "front_image": "/images/cards/card14_front.png", "back_image": "/images/cards/card14_back.png"},
        "order": 7,
    },
    {
        "_id": "pair_8",
        "pair_id": "pair_8",
        "word1": "안",
        "word2": "않다",
        "card1": {"card_id": "card_15", "front_image": "/images/cards/card15_front.png", "back_image": "/images/cards/card15_back.png"},
        "card2": {"card_id": "card_16", "front_image": "/images/cards/card16_front.png", "back_image": "/images/cards/card16_back.png"},
        "order": 8,
    },
    # 차시 5: 반드시/반듯이, 이따가/있다가
    {
        "_id": "pair_9",
        "pair_id": "pair_9",
        "word1": "반드시",
        "word2": "반듯이",
        "card1": {"card_id": "card_17", "front_image": "/images/cards/card17_front.png", "back_image": "/images/cards/card17_back.png"},
        "card2": {"card_id": "card_18", "front_image": "/images/cards/card18_front.png", "back_image": "/images/cards/card18_back.png"},
        "order": 9,
    },
    {
        "_id": "pair_10",
        "pair_id": "pair_10",
        "word1": "이따가",
        "word2": "있다가",
        "card1": {"card_id": "card_19", "front_image": "/images/cards/card19_front.png", "back_image": "/images/cards/card19_back.png"},
        "card2": {"card_id": "card_20", "front_image": "/images/cards/card20_front.png", "back_image": "/images/cards/card20_back.png"},
        "order": 10,
    },
]


def load_stage1_cards():
    """1단계 카드 데이터를 MongoDB에 저장 (쌍 그룹 구조)"""
    try:
        mongo_client = get_mongo_client()
        collection_name = "stage1_cards"

        mongo_client.db[collection_name].drop()
        result = mongo_client.insert_many(collection_name, STAGE1_CARD_PAIRS)
        logger.info(f"✅ 1단계 카드 쌍 데이터 {len(result.inserted_ids)}개 삽입 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 1단계 카드 데이터 로딩 실패: {e}")
        return False


if __name__ == "__main__":
    load_stage1_cards()
