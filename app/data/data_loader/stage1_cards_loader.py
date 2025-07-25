# beneficial-be/app/data/data_loader/stage1_cards_loader.py

from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

def load_stage1_cards():
    """1단계 카드 데이터를 MongoDB에 저장 (쌍 그룹 구조)"""
    try:
        mongo_client = get_mongo_client()
        collection_name = "stage1_cards"
        
        # 기존 컬렉션 삭제 (개발용)
        mongo_client.db[collection_name].drop()
        
        # 2개 카드 쌍 데이터
        card_pairs_data = [
            {
                "_id": "pair_1",
                "pair_id": "pair_1",
                "word1": "가르치다",
                "word2": "가르키다",
                "card1": {
                    "card_id": "card_1",
                    "front_image": "/images/cards/card1_front.png",
                    "back_image": "/images/cards/card1_back.png"
                },
                "card2": {
                    "card_id": "card_2",
                    "front_image": "/images/cards/card2_front.png",
                    "back_image": "/images/cards/card2_back.png"
                },
                "order": 1
            },
            {
                "_id": "pair_2",
                "pair_id": "pair_2", 
                "word1": "맞추다",
                "word2": "맞히다",
                "card1": {
                    "card_id": "card_3",
                    "front_image": "/images/cards/card3_front.png",
                    "back_image": "/images/cards/card3_back.png"
                },
                "card2": {
                    "card_id": "card_4",
                    "front_image": "/images/cards/card4_front.png",
                    "back_image": "/images/cards/card4_back.png"
                },
                "order": 2
            }
        ]
        
        # 데이터 삽입
        result = mongo_client.insert_many(collection_name, card_pairs_data)
        logger.info(f"✅ 1단계 카드 쌍 데이터 {len(result.inserted_ids)}개 삽입 완료")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 1단계 카드 데이터 로딩 실패: {e}")
        return False

if __name__ == "__main__":
    load_stage1_cards() 