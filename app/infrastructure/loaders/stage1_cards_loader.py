# beneficial-be/app/common/data/data_loader/stage1_cards_loader.py

from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)


def _card(
    card_id: str,
    word: str,
    meaning: str,
    example_sentence: str,
    visual_hint: str,
    color_theme: str,
) -> dict:
    return {
        "card_id": card_id,
        "word": word,
        "meaning": meaning,
        "example_sentence": example_sentence,
        "visual_hint": visual_hint,
        "color_theme": color_theme,
    }


STAGE1_CARD_PAIRS = [
    # 차시 1: 가르치다/가르키다, 맞추다/맞히다
    {
        "_id": "pair_1",
        "pair_id": "pair_1",
        "word1": "가르치다",
        "word2": "가르키다",
        "card1": _card("card_1", "가르치다", "지식이나 기술을 알려주다", "선생님이 수학을 가르치다.", "book-open", "primary"),
        "card2": _card("card_2", "가르키다", "손가락 등으로 방향을 가리키다", "그가 건물을 가르키다.", "hand-point-up", "warning"),
        "order": 1,
    },
    {
        "_id": "pair_2",
        "pair_id": "pair_2",
        "word1": "맞추다",
        "word2": "맞히다",
        "card1": _card("card_3", "맞추다", "기준에 맞게 조절하다", "퍼즐을 제자리에 맞추다.", "puzzle", "warning"),
        "card2": _card("card_4", "맞히다", "정답을 알아맞히다", "수수께끼를 맞히다.", "target", "primary"),
        "order": 2,
    },
    # 차시 2: 잊다/잃다, 메다/매다
    {
        "_id": "pair_3",
        "pair_id": "pair_3",
        "word1": "잊다",
        "word2": "잃다",
        "card1": _card("card_5", "잊다", "기억하지 못하다", "숙제를 잊다.", "brain", "primary"),
        "card2": _card("card_6", "잃다", "가지고 있던 것이 없어지다", "지갑을 잃다.", "search-x", "warning"),
        "order": 3,
    },
    {
        "_id": "pair_4",
        "pair_id": "pair_4",
        "word1": "메다",
        "word2": "매다",
        "card1": _card("card_7", "메다", "어깨에 걸쳐 얹다", "가방을 어깨에 메다.", "backpack", "primary"),
        "card2": _card("card_8", "매다", "끈이나 줄을 묶다", "안전벨트를 매다.", "link", "warning"),
        "order": 4,
    },
    # 차시 3: 바라다/바래다, 부치다/붙이다
    {
        "_id": "pair_5",
        "pair_id": "pair_5",
        "word1": "바라다",
        "word2": "바래다",
        "card1": _card("card_9", "바라다", "원하거나 소망하다", "합격하기를 바라다.", "sparkles", "primary"),
        "card2": _card("card_10", "바래다", "색이 변하거나 희미해지다", "청바지 색이 바래다.", "palette", "warning"),
        "order": 5,
    },
    {
        "_id": "pair_6",
        "pair_id": "pair_6",
        "word1": "부치다",
        "word2": "붙이다",
        "card1": _card("card_11", "부치다", "편지나 물건을 보내다", "할머니께 편지를 부치다.", "send", "primary"),
        "card2": _card("card_12", "붙이다", "떨어지지 않게 달라붙게 하다", "봉투에 우표를 붙이다.", "paperclip", "warning"),
        "order": 6,
    },
    # 차시 4: 되다/돼다, 안/않다
    {
        "_id": "pair_7",
        "pair_id": "pair_7",
        "word1": "되다",
        "word2": "돼다",
        "card1": _card("card_13", "되다", "어떤 상태가 이루어지다", "의사가 되다.", "check-circle", "primary"),
        "card2": _card("card_14", "돼다", "'되다'와 헷갈리기 쉬운 표현", "그렇게 하면 안 돼.", "circle-alert", "warning"),
        "order": 7,
    },
    {
        "_id": "pair_8",
        "pair_id": "pair_8",
        "word1": "안",
        "word2": "않다",
        "card1": _card("card_15", "안", "동사나 형용사 앞에서 부정하다", "밥을 안 먹었다.", "minus-circle", "primary"),
        "card2": _card("card_16", "않다", "'-지 않다' 형태로 쓰다", "춥지 않다.", "ban", "warning"),
        "order": 8,
    },
    # 차시 5: 반드시/반듯이, 이따가/있다가
    {
        "_id": "pair_9",
        "pair_id": "pair_9",
        "word1": "반드시",
        "word2": "반듯이",
        "card1": _card("card_17", "반드시", "틀림없이 꼭", "약속은 반드시 지키다.", "badge-check", "primary"),
        "card2": _card("card_18", "반듯이", "비뚤어지지 않고 바르게", "자세를 반듯이 하다.", "ruler", "warning"),
        "order": 9,
    },
    {
        "_id": "pair_10",
        "pair_id": "pair_10",
        "word1": "이따가",
        "word2": "있다가",
        "card1": _card("card_19", "이따가", "조금 뒤에", "이따가 같이 밥 먹자.", "clock", "primary"),
        "card2": _card("card_20", "있다가", "머무른 뒤에", "여기 있다가 집에 갔다.", "map-pin", "warning"),
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
        logger.info(f"[OK] 1단계 카드 쌍 데이터 {len(result.inserted_ids)}개 삽입 완료")
        return True

    except Exception as e:
        logger.error(f"[ERROR] 1단계 카드 데이터 로딩 실패: {e}")
        return False


if __name__ == "__main__":
    load_stage1_cards()
