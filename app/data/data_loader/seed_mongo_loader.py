from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

# ──────────────────────────────────────────────
# card_check 시드 데이터 (RAG용 어휘 카드)
# 구조: 차시별 문서, cards 배열 안에 word1/word2 쌍
# ──────────────────────────────────────────────
CARD_CHECK_SEED = [
    {
        "_id": "card_check_lesson_1",
        "lessonId": "1",
        "cards": [
            {
                "word1": "가르치다",
                "word2": "가르키다",
                "meaning1": "지식이나 기술을 알려주다",
                "meaning2": "방향이나 대상을 손가락 등으로 지시하다",
                "examples1": [
                    "선생님이 국어를 가르쳐 주셨다.",
                    "친구에게 기타 치는 법을 가르쳐 줬다.",
                    "어머니가 요리를 가르치신다.",
                ],
                "examples2": [
                    "그가 손가락으로 저 건물을 가르켰다.",
                    "화살표가 동쪽을 가르키고 있다.",
                    "선생님이 칠판의 글자를 가르켰다.",
                ],
            },
            {
                "word1": "맞추다",
                "word2": "맞히다",
                "meaning1": "어떤 기준에 맞게 조절하거나 퍼즐처럼 끼워 맞추다",
                "meaning2": "문제의 정답을 알아내거나 목표물을 적중시키다",
                "examples1": [
                    "친구와 약속 시간을 맞추다.",
                    "퍼즐 조각을 맞추다.",
                    "옷을 몸에 맞추어 입다.",
                ],
                "examples2": [
                    "수수께끼를 맞혀 보세요.",
                    "과녁을 화살로 맞혔다.",
                    "시험 문제를 모두 맞혔다.",
                ],
            },
        ],
    },
    {
        "_id": "card_check_lesson_2",
        "lessonId": "2",
        "cards": [
            {
                "word1": "잊다",
                "word2": "잃다",
                "meaning1": "기억하지 못하게 되다",
                "meaning2": "가지고 있던 것이 없어지다",
                "examples1": [
                    "친구의 이름을 잊어버렸다.",
                    "숙제하는 것을 깜빡 잊었다.",
                    "슬픔을 잊으려고 노래를 불렀다.",
                ],
                "examples2": [
                    "버스 안에서 지갑을 잃어버렸다.",
                    "길을 잃은 강아지를 발견했다.",
                    "경기에서 져서 점수를 잃었다.",
                ],
            },
            {
                "word1": "메다",
                "word2": "매다",
                "meaning1": "어깨에 걸쳐 얹다",
                "meaning2": "끈이나 줄 등을 묶다",
                "examples1": [
                    "가방을 어깨에 메고 학교에 갔다.",
                    "배낭을 메고 산에 올랐다.",
                    "카메라를 목에 메었다.",
                ],
                "examples2": [
                    "신발 끈을 단단히 매었다.",
                    "안전벨트를 매고 출발하다.",
                    "허리띠를 꽉 매었다.",
                ],
            },
        ],
    },
    {
        "_id": "card_check_lesson_3",
        "lessonId": "3",
        "cards": [
            {
                "word1": "바라다",
                "word2": "바래다",
                "meaning1": "원하거나 소망하다",
                "meaning2": "색이 변하거나, 사람을 배웅하다",
                "examples1": [
                    "시험에 합격하기를 바란다.",
                    "꿈이 이루어지기를 바랍니다.",
                    "건강하기를 바라고 있어.",
                ],
                "examples2": [
                    "오래된 청바지 색이 바랬다.",
                    "친구를 버스 정류장까지 바래다 줬다.",
                    "햇빛에 커튼이 바랬다.",
                ],
            },
            {
                "word1": "부치다",
                "word2": "붙이다",
                "meaning1": "편지나 물건을 보내다 / 기름에 구워 만들다",
                "meaning2": "풀이나 테이프로 달라붙게 하다",
                "examples1": [
                    "할머니께 편지를 부쳤다.",
                    "택배로 선물을 부치다.",
                    "어머니가 김치전을 부치신다.",
                ],
                "examples2": [
                    "봉투에 우표를 붙였다.",
                    "벽에 포스터를 붙이다.",
                    "스티커를 노트에 붙였다.",
                ],
            },
        ],
    },
    {
        "_id": "card_check_lesson_4",
        "lessonId": "4",
        "cards": [
            {
                "word1": "되다",
                "word2": "돼다",
                "meaning1": "어떤 상태가 이루어지다 (어간: 되-)",
                "meaning2": "'되어'의 줄임말, '돼' 형태로만 씀",
                "examples1": [
                    "의사가 되고 싶다.",
                    "밥이 다 됐어? (되었어?)",
                    "이렇게 하면 안 된다.",
                ],
                "examples2": [
                    "그렇게 하면 안 돼.",
                    "이제 다 됐어? → 다 돼?",
                    "일이 잘 돼서 기뻐.",
                ],
            },
            {
                "word1": "안",
                "word2": "않다",
                "meaning1": "동작이나 상태를 부정하는 부사, 용언 앞에 씀",
                "meaning2": "'-지 않다' 형태로 동사/형용사 뒤에 씀",
                "examples1": [
                    "밥을 안 먹었다.",
                    "오늘은 안 춥다.",
                    "나는 안 갈 거야.",
                ],
                "examples2": [
                    "밥을 먹지 않았다.",
                    "오늘은 춥지 않다.",
                    "나는 가지 않을 거야.",
                ],
            },
        ],
    },
    {
        "_id": "card_check_lesson_5",
        "lessonId": "5",
        "cards": [
            {
                "word1": "반드시",
                "word2": "반듯이",
                "meaning1": "틀림없이, 꼭",
                "meaning2": "비뚤어지지 않고 바르게",
                "examples1": [
                    "약속은 반드시 지켜야 한다.",
                    "숙제를 반드시 해 오세요.",
                    "반드시 성공할 거야.",
                ],
                "examples2": [
                    "자세를 반듯이 하고 앉아라.",
                    "그림을 반듯이 걸었다.",
                    "반듯이 누워서 쉬어라.",
                ],
            },
            {
                "word1": "이따가",
                "word2": "있다가",
                "meaning1": "조금 뒤에, 잠시 후에 (시간 부사)",
                "meaning2": "어떤 상태로 있은 후에",
                "examples1": [
                    "이따가 같이 밥 먹자.",
                    "이따가 전화할게.",
                    "이따가 도서관에서 보자.",
                ],
                "examples2": [
                    "여기 있다가 집에 갔다.",
                    "잠깐 있다가 떠났다.",
                    "학교에 있다가 친구를 만났다.",
                ],
            },
        ],
    },
]

# ──────────────────────────────────────────────
# korean_word_problems 시드 데이터 (RAG용 문제)
# 구조: 차시별 문서, questions 배열
# ──────────────────────────────────────────────
KOREAN_WORD_PROBLEMS_SEED = [
    {
        "_id": "kwp_lesson_1",
        "lessonId": "1",
        "option_cards": ["가르쳐", "가르켜", "맞혀", "맞춰", "맞히다", "맞추다", "가르치다", "가르키다"],
        "questions": [
            {"sentence": "선생님이 수학 공식을 ( ) 주셨다.", "answer": "가르쳐"},
            {"sentence": "친구에게 자전거 타는 법을 ( ) 줬다.", "answer": "가르쳐"},
            {"sentence": "그는 손가락으로 저 산을 ( ).", "answer": "가르켰다"},
            {"sentence": "퍼즐 조각을 제자리에 ( ) 보자.", "answer": "맞춰"},
            {"sentence": "친구와 만날 약속 시간을 ( ).", "answer": "맞췄다"},
            {"sentence": "수수께끼를 ( ) 보세요.", "answer": "맞혀"},
            {"sentence": "세 문제 중 두 개를 ( ).", "answer": "맞혔다"},
            {"sentence": "화살표가 오른쪽을 ( ) 있다.", "answer": "가르키고"},
        ],
    },
    {
        "_id": "kwp_lesson_2",
        "lessonId": "2",
        "option_cards": ["잊어버렸다", "잃어버렸다", "잊고", "잃고", "메고", "매고", "메었다", "매었다"],
        "questions": [
            {"sentence": "버스에 지갑을 ( ).", "answer": "잃어버렸다"},
            {"sentence": "숙제하는 것을 깜빡 ( ).", "answer": "잊었다"},
            {"sentence": "길을 ( ) 강아지를 발견했다.", "answer": "잃은"},
            {"sentence": "친구 이름을 ( ).", "answer": "잊어버렸다"},
            {"sentence": "배낭을 어깨에 ( ) 산에 올랐다.", "answer": "메고"},
            {"sentence": "신발 끈을 단단히 ( ).", "answer": "매었다"},
            {"sentence": "안전벨트를 ( ) 출발했다.", "answer": "매고"},
            {"sentence": "카메라를 목에 ( ) 사진을 찍었다.", "answer": "메고"},
        ],
    },
    {
        "_id": "kwp_lesson_3",
        "lessonId": "3",
        "option_cards": ["바란다", "바랬다", "바래다", "부쳤다", "붙였다", "부치다", "붙이다", "바라다"],
        "questions": [
            {"sentence": "시험에 합격하기를 ( ).", "answer": "바란다"},
            {"sentence": "오래된 청바지 색이 ( ).", "answer": "바랬다"},
            {"sentence": "친구를 버스 정류장까지 ( ) 줬다.", "answer": "바래다"},
            {"sentence": "할머니께 편지를 ( ).", "answer": "부쳤다"},
            {"sentence": "어머니가 김치전을 ( ).", "answer": "부치신다"},
            {"sentence": "봉투에 우표를 ( ).", "answer": "붙였다"},
            {"sentence": "벽에 포스터를 ( ).", "answer": "붙였다"},
            {"sentence": "햇빛에 커튼 색이 ( ).", "answer": "바랬다"},
        ],
    },
    {
        "_id": "kwp_lesson_4",
        "lessonId": "4",
        "option_cards": ["되고", "돼서", "안", "않고", "되면", "돼", "않았다", "안 됩니다"],
        "questions": [
            {"sentence": "의사가 ( ) 싶다.", "answer": "되고"},
            {"sentence": "그렇게 하면 안 ( ).", "answer": "돼"},
            {"sentence": "일이 잘 ( ) 기쁘다.", "answer": "돼서"},
            {"sentence": "밥을 ( ) 먹었다.", "answer": "안"},
            {"sentence": "오늘은 춥지 ( ).", "answer": "않다"},
            {"sentence": "나는 가지 ( ) 거야.", "answer": "않을"},
            {"sentence": "이렇게 하면 ( ).", "answer": "안 됩니다"},
            {"sentence": "숙제가 다 ( )?", "answer": "됐어"},
        ],
    },
    {
        "_id": "kwp_lesson_5",
        "lessonId": "5",
        "option_cards": ["반드시", "반듯이", "이따가", "있다가", "꼭", "바르게", "나중에", "머물다가"],
        "questions": [
            {"sentence": "약속은 ( ) 지켜야 한다.", "answer": "반드시"},
            {"sentence": "자세를 ( ) 하고 앉아라.", "answer": "반듯이"},
            {"sentence": "그림을 ( ) 걸었다.", "answer": "반듯이"},
            {"sentence": "( ) 같이 밥 먹자.", "answer": "이따가"},
            {"sentence": "( ) 전화할게.", "answer": "이따가"},
            {"sentence": "여기 ( ) 집에 갔다.", "answer": "있다가"},
            {"sentence": "학교에 ( ) 친구를 만났다.", "answer": "있다가"},
            {"sentence": "숙제는 ( ) 해야 한다.", "answer": "반드시"},
        ],
    },
]


def seed_mongo_data() -> bool:
    """card_check, korean_word_problems 컬렉션에 시드 데이터 삽입"""
    try:
        mongo_client = get_mongo_client()

        # ── card_check ──
        existing_cards = mongo_client.count_documents("card_check")
        if existing_cards == 0:
            mongo_client.insert_many("card_check", CARD_CHECK_SEED)
            logger.info(f"✅ card_check 시드 완료: {len(CARD_CHECK_SEED)}개 차시")
        else:
            logger.info(f"📊 card_check 데이터 이미 존재: {existing_cards}개")

        # ── korean_word_problems ──
        existing_problems = mongo_client.count_documents("korean_word_problems")
        if existing_problems == 0:
            mongo_client.insert_many("korean_word_problems", KOREAN_WORD_PROBLEMS_SEED)
            logger.info(f"✅ korean_word_problems 시드 완료: {len(KOREAN_WORD_PROBLEMS_SEED)}개 차시")
        else:
            logger.info(f"📊 korean_word_problems 데이터 이미 존재: {existing_problems}개")

        return True

    except Exception as e:
        logger.error(f"❌ MongoDB 시드 실패: {e}")
        return False
