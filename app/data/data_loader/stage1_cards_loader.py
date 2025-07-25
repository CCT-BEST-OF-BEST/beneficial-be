# beneficial-be/app/data/data_loader/stage1_cards_loader.py

from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

def load_stage1_cards():
    """1단계 카드 데이터를 MongoDB에 저장"""
    try:
        mongo_client = get_mongo_client()
        collection_name = "stage1_cards"
        
        # 기존 컬렉션 삭제 (개발용)
        mongo_client.db[collection_name].drop()
        
        # 8개 카드 데이터 (이미지 경로만)
        cards_data = [
            {
                "_id": "card_1",
                "card_id": "card_1",
                "front_image": "/images/cards/card1_front.png",
                "back_image": "/images/cards/card1_back.png",
                "order": 1
            },
            {
                "_id": "card_2", 
                "card_id": "card_2",
                "front_image": "/images/cards/card2_front.png",
                "back_image": "/images/cards/card2_back.png",
                "order": 2
            },
            {
                "_id": "card_3",
                "card_id": "card_3", 
                "front_image": "/images/cards/card3_front.png",
                "back_image": "/images/cards/card3_back.png",
                "order": 3
            },
            {
                "_id": "card_4",
                "card_id": "card_4",
                "front_image": "/images/cards/card4_front.png",
                "back_image": "/images/cards/card4_back.png",
                "order": 4
            },
            {
                "_id": "card_5",
                "card_id": "card_5",
                "front_image": "/images/cards/card5_front.png", 
                "back_image": "/images/cards/card5_back.png",
                "order": 5
            },
            {
                "_id": "card_6",
                "card_id": "card_6",
                "front_image": "/images/cards/card6_front.png",
                "back_image": "/images/cards/card6_back.png",
                "order": 6
            },
            {
                "_id": "card_7",
                "card_id": "card_7",
                "front_image": "/images/cards/card7_front.png",
                "back_image": "/images/cards/card7_back.png",
                "order": 7
            },
            {
                "_id": "card_8",
                "card_id": "card_8",
                "front_image": "/images/cards/card8_front.png",
                "back_image": "/images/cards/card8_back.png",
                "order": 8
            }
        ]
        
        # 데이터 삽입
        result = mongo_client.insert_many(collection_name, cards_data)
        logger.info(f"✅ 1단계 카드 데이터 {len(result.inserted_ids)}개 삽입 완료")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 1단계 카드 데이터 로딩 실패: {e}")
        return False

if __name__ == "__main__":
    load_stage1_cards() 