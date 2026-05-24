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
            "wrong_explanations": {
                "가르켰다": "네가 '가르켰다'라고 적었구나! 그건 '손가락으로 가리키다'는 뜻이라 지식을 알려주는 상황엔 안 맞아. 선생님이 공식을 '알려주는' 거니까 '가르치다 → 가르쳐'가 맞아!",
                "가르켜": "'가르켜'는 손가락으로 가리킬 때 쓰는 말이야. 지식이나 기술을 알려줄 때는 '가르치다'를 써서 '가르쳐'라고 해야 해.",
                "가르키다": "'가르키다'는 손가락으로 무언가를 가리킬 때 쓰는 말이야. 여기서는 공식을 '알려주는' 거니까 '가르치다'의 '가르쳐'가 맞아!",
            },
            "image": "stage3/problem_1.png",
        },
        {
            "problem_id": 2,
            "sentence_part1": "그가 손가락으로 저 건물을",
            "correct_answer": "가르켰다",
            "sentence_part2": ".",
            "full_sentence": "그가 손가락으로 저 건물을 가르켰다.",
            "explanation": "'가르키다'는 방향이나 대상을 손가락으로 지시하는 것입니다. '가르켰다'는 '가르키-'에 '-었다'가 붙은 형태예요.",
            "wrong_explanations": {
                "가르쳤다": "네가 '가르쳤다'라고 적었네! '가르치다'는 '지식을 알려주다'라는 뜻이라 손가락으로 가리키는 상황엔 어울리지 않아. 손가락으로 가리킬 때는 '가르키다 → 가르켰다'를 써야 해!",
                "가르쳐": "'가르쳐'는 지식을 알려줄 때 쓰는 말이야. 손가락으로 건물을 가리키는 거니까 '가르키다'의 '가르켰다'가 맞아.",
                "가르치다": "'가르치다'는 알려주는 거고, 손가락으로 가리키는 건 '가르키다'야. 그래서 '가르켰다'가 정답!",
            },
            "image": "stage3/problem_2.png",
        },
        {
            "problem_id": 3,
            "sentence_part1": "친구와 약속 시간을",
            "correct_answer": "맞췄다",
            "sentence_part2": ".",
            "full_sentence": "친구와 약속 시간을 맞췄다.",
            "explanation": "'맞추다'는 기준에 맞게 조절하는 것입니다. '맞췄다'는 '맞추-'에 '-었다'가 붙어 줄어든 형태예요.",
            "wrong_explanations": {
                "맞혔다": "'맞히다'는 수수께끼나 문제의 답을 알아낼 때 쓰는 말이야. 약속 시간은 서로 '조절해서 맞추는' 거니까 '맞추다 → 맞췄다'가 맞아!",
                "맞혀": "'맞혀'는 정답을 알아낼 때 쓰는 말이고, 시간을 서로 조절해 일치시킬 때는 '맞추다 → 맞췄다'를 써야 해.",
                "맞춰": "'맞춰'는 맞는 방향인데 형태가 살짝 달라. 과거의 일이니까 '맞췄다'로 적어야 해!",
            },
            "image": "stage3/problem_3.png",
        },
        {
            "problem_id": 4,
            "sentence_part1": "수수께끼를",
            "correct_answer": "맞혔다",
            "sentence_part2": ".",
            "full_sentence": "수수께끼를 맞혔다.",
            "explanation": "'맞히다'는 정답을 알아맞히는 것입니다. '맞혔다'는 '맞히-'에 '-었다'가 붙은 형태예요.",
            "wrong_explanations": {
                "맞췄다": "네가 '맞췄다'라고 적었네. '맞추다'는 기준에 맞게 조절할 때 쓰는 말이야. 수수께끼의 정답을 알아낼 땐 '맞히다 → 맞혔다'를 써야 해!",
                "맞춰": "'맞춰'는 시간이나 답을 서로 조절해 일치시킬 때 써. 정답을 알아내는 건 '맞히다 → 맞혔다'야.",
                "맞혀": "'맞혀'는 방향이 맞아! 다만 과거의 일이니까 '맞혔다'로 적어야 해.",
            },
            "image": "stage3/problem_4.png",
        },
        {
            "problem_id": 5,
            "sentence_part1": "퍼즐 조각을 제자리에",
            "correct_answer": "맞췄다",
            "sentence_part2": ".",
            "full_sentence": "퍼즐 조각을 제자리에 맞췄다.",
            "explanation": "'맞추다'는 조각을 끼워 맞추는 것입니다.",
            "wrong_explanations": {
                "맞혔다": "'맞히다'는 정답을 알아낼 때 쓰는 말이야. 퍼즐 조각을 끼워 넣는 건 '맞추다 → 맞췄다'를 써야 해!",
                "맞혀": "'맞혀'는 정답을 알아낼 때 쓰는 말이고, 조각을 끼우는 건 '맞추다'의 '맞췄다'야.",
                "맞춰": "'맞춰'는 방향이 맞아! 과거의 일이니까 '맞췄다'로 적어야 해.",
            },
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
            "wrong_explanations": {
                "잊어버렸다": "'잊다'는 기억이 안 날 때 쓰는 말이야. 지갑처럼 물건이 없어지는 건 '잃다 → 잃어버렸다'를 써야 해!",
                "잊었다": "'잊었다'는 기억을 못 한 거고, 물건이 없어진 건 '잃었다/잃어버렸다'야. 지갑이니까 '잃어버렸다'가 맞아.",
                "잃었다": "방향은 맞아! 다만 '완전히 사라졌다'는 느낌을 살리려고 '잃어버렸다'로 써.",
            },
            "image": "stage3/problem_6.png",
        },
        {
            "problem_id": 7,
            "sentence_part1": "숙제하는 것을 깜빡",
            "correct_answer": "잊었다",
            "sentence_part2": ".",
            "full_sentence": "숙제하는 것을 깜빡 잊었다.",
            "explanation": "'잊다'는 기억하지 못하게 되는 것입니다.",
            "wrong_explanations": {
                "잃었다": "'잃다'는 물건이 없어질 때 쓰는 말이야. 기억이 안 나는 건 '잊다 → 잊었다'를 써야 해!",
                "잃어버렸다": "'잃어버리다'는 물건이 사라진 거고, 기억이 안 나는 건 '잊다 → 잊었다'야.",
                "잊어버렸다": "방향은 맞아! 짧게 쓰려면 '잊었다'면 충분해.",
            },
            "image": "stage3/problem_7.png",
        },
        {
            "problem_id": 8,
            "sentence_part1": "배낭을 어깨에",
            "correct_answer": "메고",
            "sentence_part2": "산에 올랐다.",
            "full_sentence": "배낭을 어깨에 메고 산에 올랐다.",
            "explanation": "'메다'는 어깨에 걸쳐 얹는 것입니다. '매다'(묶다)와 구별하세요!",
            "wrong_explanations": {
                "매고": "'매다'는 끈으로 묶을 때 쓰는 말이야. 배낭을 어깨에 걸칠 때는 '메다 → 메고'를 써야 해!",
                "매다": "'매다'는 끈을 묶는 거고, 어깨에 걸치는 건 '메다 → 메고'야.",
            },
            "image": "stage3/problem_8.png",
        },
        {
            "problem_id": 9,
            "sentence_part1": "차에 타면 안전벨트를",
            "correct_answer": "매고",
            "sentence_part2": "출발했다.",
            "full_sentence": "차에 타면 안전벨트를 매고 출발했다.",
            "explanation": "'매다'는 끈이나 줄을 묶는 것입니다.",
            "wrong_explanations": {
                "메고": "'메다'는 어깨에 걸칠 때 쓰는 말이야. 안전벨트는 몸에 '묶는' 거니까 '매다 → 매고'를 써야 해!",
                "메다": "'메다'는 어깨에 걸치는 거고, 벨트나 끈을 묶는 건 '매다 → 매고'야.",
            },
            "image": "stage3/problem_9.png",
        },
        {
            "problem_id": 10,
            "sentence_part1": "신발 끈을 단단히",
            "correct_answer": "매었다",
            "sentence_part2": ".",
            "full_sentence": "신발 끈을 단단히 매었다.",
            "explanation": "'매다'는 끈을 묶는 것이고, '매었다'는 '매-'에 '-었다'가 붙은 형태예요.",
            "wrong_explanations": {
                "메었다": "'메다'는 어깨에 걸칠 때 쓰는 말이야. 신발 끈은 '묶는' 거니까 '매다 → 매었다'를 써야 해!",
                "맸다": "방향은 맞아! '매었다'를 줄여서 '맸다'로 써도 되긴 하지만, 또박또박 '매었다'로 적는 게 더 정확해.",
            },
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
            "wrong_explanations": {
                "바랜다": "'바래다'는 색이 변할 때 쓰는 말이야. 꿈을 소망하는 건 '바라다 → 바란다'를 써야 해!",
                "바랬다": "'바랬다'는 색이 흐려졌을 때 쓰는 말이고, 무언가를 원하는 건 '바라다 → 바란다'야.",
            },
            "image": "stage3/problem_11.png",
        },
        {
            "problem_id": 12,
            "sentence_part1": "오래된 청바지 색이",
            "correct_answer": "바랬다",
            "sentence_part2": ".",
            "full_sentence": "오래된 청바지 색이 바랬다.",
            "explanation": "'바래다'는 색이 변하는 것입니다. '바라다'(소망)와 헷갈리지 마세요!",
            "wrong_explanations": {
                "바랐다": "'바라다'는 무언가를 소망할 때 쓰는 말이야. 색이 흐려진 건 '바래다 → 바랬다'를 써야 해!",
                "바란다": "'바란다'는 지금 무언가를 원할 때 쓰는 말이야. 색이 변한 건 '바래다 → 바랬다'야.",
            },
            "image": "stage3/problem_12.png",
        },
        {
            "problem_id": 13,
            "sentence_part1": "할머니께 편지를",
            "correct_answer": "부쳤다",
            "sentence_part2": ".",
            "full_sentence": "할머니께 편지를 부쳤다.",
            "explanation": "'부치다'는 편지나 물건을 보내는 것입니다. '붙이다'(달라붙게 하다)와 구별하세요!",
            "wrong_explanations": {
                "붙였다": "'붙이다'는 풀이나 테이프로 달라붙게 할 때 쓰는 말이야. 편지를 보내는 건 '부치다 → 부쳤다'를 써야 해!",
                "붙이다": "'붙이다'는 달라붙게 하는 거고, 우편으로 보내는 건 '부치다 → 부쳤다'야.",
            },
            "image": "stage3/problem_13.png",
        },
        {
            "problem_id": 14,
            "sentence_part1": "봉투에 우표를",
            "correct_answer": "붙였다",
            "sentence_part2": ".",
            "full_sentence": "봉투에 우표를 붙였다.",
            "explanation": "'붙이다'는 풀이나 테이프로 달라붙게 하는 것입니다.",
            "wrong_explanations": {
                "부쳤다": "'부치다'는 편지나 물건을 보낼 때 쓰는 말이야. 우표를 봉투에 '달라붙게 하는' 건 '붙이다 → 붙였다'를 써야 해!",
                "부치다": "'부치다'는 보내는 거고, 달라붙게 하는 건 '붙이다 → 붙였다'야.",
            },
            "image": "stage3/problem_14.png",
        },
        {
            "problem_id": 15,
            "sentence_part1": "어머니가 김치전을",
            "correct_answer": "부치신다",
            "sentence_part2": ".",
            "full_sentence": "어머니가 김치전을 부치신다.",
            "explanation": "'부치다'는 기름에 구워 만드는 것도 의미해요.",
            "wrong_explanations": {
                "붙이신다": "'붙이다'는 달라붙게 할 때 쓰는 말이야. 전을 기름에 구워 만들 때는 '부치다 → 부치신다'를 써야 해!",
                "붙이다": "'붙이다'는 달라붙게 하는 거고, 기름에 구워 만드는 것도 '부치다'야. 그래서 '부치신다'가 맞아.",
            },
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
            "wrong_explanations": {
                "되": "'되'는 혼자서는 못 쓰는 말이야. '되어'로 바꿔봤을 때 자연스러우면 '돼'를 써야 해. '안 되어'가 자연스러우니까 '안 돼'가 맞아!",
                "되어": "'되어'를 줄이면 '돼'야. 짧게 '돼'로 쓰면 충분해!",
            },
            "image": "stage3/problem_16.png",
        },
        {
            "problem_id": 17,
            "sentence_part1": "의사가",
            "correct_answer": "되고",
            "sentence_part2": "싶다.",
            "full_sentence": "의사가 되고 싶다.",
            "explanation": "'되다'의 어간 '되-'에 '-고'가 붙은 형태입니다.",
            "wrong_explanations": {
                "돼고": "'돼'는 '되어'의 줄임말이야. '되어고'는 어색하지? 그래서 여기서는 '되-'에 '-고'가 붙은 '되고'가 맞아!",
                "되어고": "'되어'에 '-고'를 붙이는 건 어색해. 그냥 '되-'에 '-고'가 붙은 '되고'로 써야 해.",
            },
            "image": "stage3/problem_17.png",
        },
        {
            "problem_id": 18,
            "sentence_part1": "밥을",
            "correct_answer": "안",
            "sentence_part2": "먹었다.",
            "full_sentence": "밥을 안 먹었다.",
            "explanation": "'안'은 부사로 용언(동사/형용사) 바로 앞에 써요. '않다'는 '-지 않다' 형태로 씁니다.",
            "wrong_explanations": {
                "않": "'않'은 혼자서는 못 쓰고, 항상 '-지 않다' 형태로 써야 해. 동사 바로 앞에 짧게 부정할 때는 '안'을 써야 해!",
                "않다": "'않다'는 '먹지 않다'처럼 '-지'와 함께 쓰는 말이야. 동사 바로 앞에선 '안 먹었다'처럼 '안'을 써.",
            },
            "image": "stage3/problem_18.png",
        },
        {
            "problem_id": 19,
            "sentence_part1": "오늘은 춥지",
            "correct_answer": "않다",
            "sentence_part2": ".",
            "full_sentence": "오늘은 춥지 않다.",
            "explanation": "'-지 않다' 형태에서는 '않다'를 씁니다. '안 춥다'와 같은 의미예요.",
            "wrong_explanations": {
                "안다": "'안'은 동사 바로 앞에 쓰는 말이야. '-지' 뒤에는 '않다'를 써야 해. '춥지 않다'가 맞아!",
                "안": "'안'은 '안 춥다'처럼 동사 앞에 써. '-지' 뒤에는 '않다'를 붙여서 '춥지 않다'로 써야 해.",
            },
            "image": "stage3/problem_19.png",
        },
        {
            "problem_id": 20,
            "sentence_part1": "일이 잘",
            "correct_answer": "돼서",
            "sentence_part2": "기쁘다.",
            "full_sentence": "일이 잘 돼서 기쁘다.",
            "explanation": "'돼서'는 '되어서'의 줄임말입니다.",
            "wrong_explanations": {
                "되서": "'되서'는 잘못된 표기야! '되어서'로 바꿔봤을 때 자연스러우면 '돼서'를 써야 해. '일이 잘 되어서'가 자연스러우니까 '돼서'가 맞아.",
                "되어서": "'되어서'를 줄이면 '돼서'야. 짧게 '돼서'로 쓰면 충분해!",
            },
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
            "wrong_explanations": {
                "반듯이": "'반듯이'는 '비뚤어지지 않고 바르게'라는 뜻이야. 약속을 '꼭' 지킨다는 의미는 '반드시'를 써야 해!",
            },
            "image": "stage3/problem_21.png",
        },
        {
            "problem_id": 22,
            "sentence_part1": "자세를",
            "correct_answer": "반듯이",
            "sentence_part2": "하고 앉아라.",
            "full_sentence": "자세를 반듯이 하고 앉아라.",
            "explanation": "'반듯이'는 '비뚤어지지 않고 바르게'의 뜻입니다.",
            "wrong_explanations": {
                "반드시": "'반드시'는 '꼭, 틀림없이'라는 뜻이야. 자세를 '바르게' 한다는 의미는 '반듯이'를 써야 해!",
            },
            "image": "stage3/problem_22.png",
        },
        {
            "problem_id": 23,
            "sentence_part1": "",
            "correct_answer": "이따가",
            "sentence_part2": "같이 밥 먹자.",
            "full_sentence": "이따가 같이 밥 먹자.",
            "explanation": "'이따가'는 '조금 뒤에'라는 시간 부사입니다. '있다가'(머물다가)와 구별하세요!",
            "wrong_explanations": {
                "있다가": "'있다가'는 '어딘가에 머무르다가'라는 뜻이야. '조금 뒤에'라는 시간을 말할 때는 '이따가'를 써야 해!",
            },
            "image": "stage3/problem_23.png",
        },
        {
            "problem_id": 24,
            "sentence_part1": "여기",
            "correct_answer": "있다가",
            "sentence_part2": "집에 갔다.",
            "full_sentence": "여기 있다가 집에 갔다.",
            "explanation": "'있다가'는 '있은 후에'라는 뜻으로, '있다'에 '-다가'가 붙은 형태입니다.",
            "wrong_explanations": {
                "이따가": "'이따가'는 '조금 뒤에'라는 시간을 말할 때 써. 여기서는 '어딘가에 머물러 있다가'라는 뜻이니까 '있다가'를 써야 해!",
            },
            "image": "stage3/problem_24.png",
        },
        {
            "problem_id": 25,
            "sentence_part1": "숙제는",
            "correct_answer": "반드시",
            "sentence_part2": "해야 한다.",
            "full_sentence": "숙제는 반드시 해야 한다.",
            "explanation": "'반드시'는 '꼭'의 의미로, '반듯이'(반듯하게)와 혼동하지 마세요.",
            "wrong_explanations": {
                "반듯이": "'반듯이'는 '바르게'라는 뜻이야. 숙제를 '꼭' 해야 한다는 의미는 '반드시'를 써야 해!",
            },
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
