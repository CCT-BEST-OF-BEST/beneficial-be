# beneficial-be/app/data/data_loader/stage3_problems_loader.py

from app.infrastructure.db.mongo.mongo_client import get_mongo_client
from app.common.logging.logging_config import get_logger

logger = get_logger(__name__)

STAGE3_DATA = {
    "_id": "stage3_problems",
    "title": "3단계 문제풀이",
    "instruction": "빈칸에 알맞은 맞춤법을 작성하세요",
    "problems": [
        # ── 차시 1: 가르치다/가르키다, 맞추다/맞히다 ──
        {
            "problem_id": 1,
            "sentence_part1": "선생님이 수학 공식을",
            "correct_answer": "가르쳐",
            "sentence_part2": "주셨다.",
            "full_sentence": "선생님이 수학 공식을 가르쳐 주셨다.",
            "explanation": "'가르치다'는 지식을 알려주는 것입니다. '가르쳐'는 '가르치-'에 '-어'가 붙은 형태예요.",
            "image": "stage3/problem_1.png",
        },
        {
            "problem_id": 2,
            "sentence_part1": "그가 손가락으로 저 건물을",
            "correct_answer": "가르켰다",
            "sentence_part2": ".",
            "full_sentence": "그가 손가락으로 저 건물을 가르켰다.",
            "explanation": "'가르키다'는 방향이나 대상을 손가락으로 지시하는 것입니다. '가르켰다'는 '가르키-'에 '-었다'가 붙은 형태예요.",
            "image": "stage3/problem_2.png",
        },
        {
            "problem_id": 3,
            "sentence_part1": "친구와 약속 시간을",
            "correct_answer": "맞췄다",
            "sentence_part2": ".",
            "full_sentence": "친구와 약속 시간을 맞췄다.",
            "explanation": "'맞추다'는 기준에 맞게 조절하는 것입니다. '맞췄다'는 '맞추-'에 '-었다'가 붙어 줄어든 형태예요.",
            "image": "stage3/problem_3.png",
        },
        {
            "problem_id": 4,
            "sentence_part1": "수수께끼를",
            "correct_answer": "맞혔다",
            "sentence_part2": ".",
            "full_sentence": "수수께끼를 맞혔다.",
            "explanation": "'맞히다'는 정답을 알아맞히는 것입니다. '맞혔다'는 '맞히-'에 '-었다'가 붙은 형태예요.",
            "image": "stage3/problem_4.png",
        },
        {
            "problem_id": 5,
            "sentence_part1": "퍼즐 조각을 제자리에",
            "correct_answer": "맞췄다",
            "sentence_part2": ".",
            "full_sentence": "퍼즐 조각을 제자리에 맞췄다.",
            "explanation": "'맞추다'는 조각을 끼워 맞추는 것입니다.",
            "image": "stage3/problem_5.png",
        },
        # ── 차시 2: 잊다/잃다, 메다/매다 ──
        {
            "problem_id": 6,
            "sentence_part1": "버스 안에서 지갑을",
            "correct_answer": "잃어버렸다",
            "sentence_part2": ".",
            "full_sentence": "버스 안에서 지갑을 잃어버렸다.",
            "explanation": "'잃다'는 가지고 있던 것이 없어지는 것입니다. '잊다'(기억을 못함)와 헷갈리지 마세요!",
            "image": "stage3/problem_6.png",
        },
        {
            "problem_id": 7,
            "sentence_part1": "숙제하는 것을 깜빡",
            "correct_answer": "잊었다",
            "sentence_part2": ".",
            "full_sentence": "숙제하는 것을 깜빡 잊었다.",
            "explanation": "'잊다'는 기억하지 못하게 되는 것입니다.",
            "image": "stage3/problem_7.png",
        },
        {
            "problem_id": 8,
            "sentence_part1": "배낭을 어깨에",
            "correct_answer": "메고",
            "sentence_part2": "산에 올랐다.",
            "full_sentence": "배낭을 어깨에 메고 산에 올랐다.",
            "explanation": "'메다'는 어깨에 걸쳐 얹는 것입니다. '매다'(묶다)와 구별하세요!",
            "image": "stage3/problem_8.png",
        },
        {
            "problem_id": 9,
            "sentence_part1": "차에 타면 안전벨트를",
            "correct_answer": "매고",
            "sentence_part2": "출발했다.",
            "full_sentence": "차에 타면 안전벨트를 매고 출발했다.",
            "explanation": "'매다'는 끈이나 줄을 묶는 것입니다.",
            "image": "stage3/problem_9.png",
        },
        {
            "problem_id": 10,
            "sentence_part1": "신발 끈을 단단히",
            "correct_answer": "매었다",
            "sentence_part2": ".",
            "full_sentence": "신발 끈을 단단히 매었다.",
            "explanation": "'매다'는 끈을 묶는 것이고, '매었다'는 '매-'에 '-었다'가 붙은 형태예요.",
            "image": "stage3/problem_10.png",
        },
        # ── 차시 3: 바라다/바래다, 부치다/붙이다 ──
        {
            "problem_id": 11,
            "sentence_part1": "꿈이 이루어지기를",
            "correct_answer": "바란다",
            "sentence_part2": ".",
            "full_sentence": "꿈이 이루어지기를 바란다.",
            "explanation": "'바라다'는 원하거나 소망하는 것입니다. '바라-'에 '-ㄴ다'가 붙으면 '바란다'예요.",
            "image": "stage3/problem_11.png",
        },
        {
            "problem_id": 12,
            "sentence_part1": "오래된 청바지 색이",
            "correct_answer": "바랬다",
            "sentence_part2": ".",
            "full_sentence": "오래된 청바지 색이 바랬다.",
            "explanation": "'바래다'는 색이 변하는 것입니다. '바라다'(소망)와 헷갈리지 마세요!",
            "image": "stage3/problem_12.png",
        },
        {
            "problem_id": 13,
            "sentence_part1": "할머니께 편지를",
            "correct_answer": "부쳤다",
            "sentence_part2": ".",
            "full_sentence": "할머니께 편지를 부쳤다.",
            "explanation": "'부치다'는 편지나 물건을 보내는 것입니다. '붙이다'(달라붙게 하다)와 구별하세요!",
            "image": "stage3/problem_13.png",
        },
        {
            "problem_id": 14,
            "sentence_part1": "봉투에 우표를",
            "correct_answer": "붙였다",
            "sentence_part2": ".",
            "full_sentence": "봉투에 우표를 붙였다.",
            "explanation": "'붙이다'는 풀이나 테이프로 달라붙게 하는 것입니다.",
            "image": "stage3/problem_14.png",
        },
        {
            "problem_id": 15,
            "sentence_part1": "어머니가 김치전을",
            "correct_answer": "부치신다",
            "sentence_part2": ".",
            "full_sentence": "어머니가 김치전을 부치신다.",
            "explanation": "'부치다'는 기름에 구워 만드는 것도 의미해요.",
            "image": "stage3/problem_15.png",
        },
        # ── 차시 4: 되다/돼, 안/않다 ──
        {
            "problem_id": 16,
            "sentence_part1": "그렇게 하면 안",
            "correct_answer": "돼",
            "sentence_part2": ".",
            "full_sentence": "그렇게 하면 안 돼.",
            "explanation": "'돼'는 '되어'의 줄임말입니다. '돼'를 '되어'로 바꿔도 말이 되면 '돼'가 맞아요!",
            "image": "stage3/problem_16.png",
        },
        {
            "problem_id": 17,
            "sentence_part1": "의사가",
            "correct_answer": "되고",
            "sentence_part2": "싶다.",
            "full_sentence": "의사가 되고 싶다.",
            "explanation": "'되다'의 어간 '되-'에 '-고'가 붙은 형태입니다.",
            "image": "stage3/problem_17.png",
        },
        {
            "problem_id": 18,
            "sentence_part1": "밥을",
            "correct_answer": "안",
            "sentence_part2": "먹었다.",
            "full_sentence": "밥을 안 먹었다.",
            "explanation": "'안'은 부사로 용언(동사/형용사) 바로 앞에 써요. '않다'는 '-지 않다' 형태로 씁니다.",
            "image": "stage3/problem_18.png",
        },
        {
            "problem_id": 19,
            "sentence_part1": "오늘은 춥지",
            "correct_answer": "않다",
            "sentence_part2": ".",
            "full_sentence": "오늘은 춥지 않다.",
            "explanation": "'-지 않다' 형태에서는 '않다'를 씁니다. '안 춥다'와 같은 의미예요.",
            "image": "stage3/problem_19.png",
        },
        {
            "problem_id": 20,
            "sentence_part1": "일이 잘",
            "correct_answer": "돼서",
            "sentence_part2": "기쁘다.",
            "full_sentence": "일이 잘 돼서 기쁘다.",
            "explanation": "'돼서'는 '되어서'의 줄임말입니다.",
            "image": "stage3/problem_20.png",
        },
        # ── 차시 5: 반드시/반듯이, 이따가/있다가 ──
        {
            "problem_id": 21,
            "sentence_part1": "약속은",
            "correct_answer": "반드시",
            "sentence_part2": "지켜야 한다.",
            "full_sentence": "약속은 반드시 지켜야 한다.",
            "explanation": "'반드시'는 '틀림없이, 꼭'의 뜻입니다. '반듯이'(반듯하게)와 구별하세요!",
            "image": "stage3/problem_21.png",
        },
        {
            "problem_id": 22,
            "sentence_part1": "자세를",
            "correct_answer": "반듯이",
            "sentence_part2": "하고 앉아라.",
            "full_sentence": "자세를 반듯이 하고 앉아라.",
            "explanation": "'반듯이'는 '비뚤어지지 않고 바르게'의 뜻입니다.",
            "image": "stage3/problem_22.png",
        },
        {
            "problem_id": 23,
            "sentence_part1": "",
            "correct_answer": "이따가",
            "sentence_part2": "같이 밥 먹자.",
            "full_sentence": "이따가 같이 밥 먹자.",
            "explanation": "'이따가'는 '조금 뒤에'라는 시간 부사입니다. '있다가'(머물다가)와 구별하세요!",
            "image": "stage3/problem_23.png",
        },
        {
            "problem_id": 24,
            "sentence_part1": "여기",
            "correct_answer": "있다가",
            "sentence_part2": "집에 갔다.",
            "full_sentence": "여기 있다가 집에 갔다.",
            "explanation": "'있다가'는 '있은 후에'라는 뜻으로, '있다'에 '-다가'가 붙은 형태입니다.",
            "image": "stage3/problem_24.png",
        },
        {
            "problem_id": 25,
            "sentence_part1": "숙제는",
            "correct_answer": "반드시",
            "sentence_part2": "해야 한다.",
            "full_sentence": "숙제는 반드시 해야 한다.",
            "explanation": "'반드시'는 '꼭'의 의미로, '반듯이'(반듯하게)와 혼동하지 마세요.",
            "image": "stage3/problem_25.png",
        },
    ],
    "total_problems": 25,
}


def load_stage3_problems():
    """3단계 문제풀이 데이터를 MongoDB에 저장"""
    try:
        mongo_client = get_mongo_client()
        collection_name = "stage3_problems"

        mongo_client.db[collection_name].drop()
        result = mongo_client.insert_one(collection_name, STAGE3_DATA)
        logger.info(f"[OK] 3단계 문제풀이 데이터 삽입 완료: {result}")
        return True

    except Exception as e:
        logger.error(f"[ERROR] 3단계 데이터 로딩 실패: {e}")
        return False


if __name__ == "__main__":
    load_stage3_problems()
