from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.config.loader.config_loader import load_rag_config
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)


def get_card_check_data():
    """카드 체크 데이터 로드"""
    try:
        # 통합된 MongoDB 클라이언트 사용
        mongo_client = get_mongo_client()
        config = load_rag_config()["collections"]["card_check"]

        # 데이터 조회 - 모든 문서 가져오기
        docs = mongo_client.find_many("card_check")

        if not docs:
            logger.warning("⚠️ 카드 체크 데이터가 없습니다.")
            return []

        result = []
        # 각 차시별 데이터 처리
        for doc in docs:
            cards = doc.get("cards", [])
            
            # 각 카드 데이터 처리
            for idx, card in enumerate(cards, 1):
                result.append({
                    "word": f"{card.get('word1', '')}/{card.get('word2', '')}",
                    "meaning": f"{card.get('meaning1', '')} | {card.get('meaning2', '')}",
                    "examples": card.get('examples1', []) + card.get('examples2', [])
                })

        logger.info(f"✅ 카드 체크 데이터 로드 완료: {len(result)}개 카드")

        return result

    except Exception as e:
        logger.error(f"❌ 카드 체크 데이터 로드 실패: {e}")
        return []


# 간단 테스트
if __name__ == "__main__":
    from pprint import pprint

    pprint(get_card_check_data())