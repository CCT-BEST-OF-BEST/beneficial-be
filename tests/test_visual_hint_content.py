from app.domains.learning.content_router import _stage1_pair_response
from app.domains.learning.stage3_service import Stage3Service


def test_stage1_card_response_removes_image_paths():
    pair = {
        "pair_id": "pair_1",
        "word1": "가르치다",
        "word2": "가르키다",
        "card1": {
            "card_id": "card_1",
            "front_image": "/images/cards/card1_front.png",
            "back_image": "/images/cards/card1_back.png",
        },
        "card2": {
            "card_id": "card_2",
            "front_image": "/images/cards/card2_front.png",
            "back_image": "/images/cards/card2_back.png",
        },
        "order": 1,
    }

    response = _stage1_pair_response(pair)
    data = response.model_dump()

    assert "front_image" not in data["card1"]
    assert "back_image" not in data["card1"]
    assert data["card1"]["visual_hint"] == "book-open"
    assert data["card2"]["visual_hint"] == "hand-point-up"


class FakeMongoClient:
    def find_one(self, collection_name, filter_dict):
        if collection_name != "stage3_problems":
            return None
        return {
            "_id": "stage3_problems",
            "instruction": "빈칸에 알맞은 맞춤법을 작성하세요",
            "total_problems": 1,
            "problems": [
                {
                    "problem_id": 1,
                    "sentence_part1": "선생님이 수학 공식을",
                    "correct_answer": "가르쳐",
                    "sentence_part2": "주셨다.",
                    "full_sentence": "선생님이 수학 공식을 가르쳐 주셨다.",
                    "explanation": "설명",
                    "image": "stage3/problem_1.png",
                }
            ],
        }


def test_stage3_problem_response_uses_visual_hint_not_image_path():
    service = Stage3Service(FakeMongoClient())

    response = service.get_problems()
    problem = response.problems[0].model_dump()

    assert "image" not in problem
    assert problem["visual_hint"] == "book-open"
    assert problem["accent_color"] == "primary"
