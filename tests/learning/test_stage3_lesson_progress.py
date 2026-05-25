from app.domains.learning.stages.stage3_service import Stage3Service


class FakeMongoClient:
    def __init__(self):
        self.collections = {
            "stage3_problems": [
                {
                    "_id": "stage3_problems",
                    "title": "3단계 문제풀이",
                    "instruction": "빈칸에 알맞은 맞춤법을 작성하세요",
                    "total_problems": 10,
                    "problems": [
                        {
                            "problem_id": idx,
                            "sentence_part1": "앞",
                            "correct_answer": "정답",
                            "sentence_part2": "뒤",
                            "full_sentence": "앞 정답 뒤",
                            "explanation": "설명",
                        }
                        for idx in range(1, 11)
                    ],
                }
            ],
            "stage3_progress": [],
        }

    def find_one(self, collection_name, filter_dict):
        for document in self.collections.get(collection_name, []):
            if self._matches(document, filter_dict):
                return document
        return None

    def insert_one(self, collection_name, document):
        self.collections.setdefault(collection_name, []).append(dict(document))
        return "inserted"

    def update_one(self, collection_name, filter_dict, update_dict):
        document = self.find_one(collection_name, filter_dict)
        if not document:
            return False
        document.update(update_dict)
        return True

    def delete_one(self, collection_name, filter_dict):
        documents = self.collections.get(collection_name, [])
        for index, document in enumerate(documents):
            if self._matches(document, filter_dict):
                del documents[index]
                return True
        return False

    def _matches(self, document, filter_dict):
        for key, value in filter_dict.items():
            if isinstance(value, dict) and "$exists" in value:
                exists = key in document
                if exists != value["$exists"]:
                    return False
                continue
            if document.get(key) != value:
                return False
        return True


def test_stage3_problem_list_is_filtered_by_lesson():
    service = Stage3Service(FakeMongoClient())

    response = service.get_problems(lesson_id="lesson_2")

    assert response.lesson_id == "lesson_2"
    assert response.total_problems == 5
    assert [problem.problem_id for problem in response.problems] == [6, 7, 8, 9, 10]


def test_stage3_progress_is_scoped_by_user_and_lesson():
    mongo_client = FakeMongoClient()
    service = Stage3Service(mongo_client)

    lesson_1 = service.get_progress("student_1", lesson_id="lesson_1").progress
    lesson_2 = service.get_progress("student_1", lesson_id="lesson_2").progress

    assert lesson_1.lesson_id == "lesson_1"
    assert lesson_2.lesson_id == "lesson_2"
    assert len(mongo_client.collections["stage3_progress"]) == 2


def test_stage3_next_problem_uses_lesson_local_sequence():
    service = Stage3Service(FakeMongoClient())

    problem = service.get_next_problem("student_1", lesson_id="lesson_2")

    assert problem["problem_id"] == 6
    assert problem["badge"] == "첫학습"


def test_stage3_submit_answer_records_progress_in_inferred_lesson():
    mongo_client = FakeMongoClient()
    service = Stage3Service(mongo_client)

    response = service.submit_answer(6, "오답", user_id="student_1")
    progress = service.get_progress("student_1", lesson_id="lesson_2").progress

    assert response.problem_id == 6
    assert progress.lesson_id == "lesson_2"
    assert progress.wrong_count == 1
    assert progress.review_problems == [6]


def test_stage3_legacy_progress_is_normalized_to_default_lesson():
    mongo_client = FakeMongoClient()
    mongo_client.collections["stage3_progress"].append(
        {
            "user_id": "student_1",
            "total_problems": 10,
            "completed_problems": [1, 2, 6],
            "review_problems": [3, 7],
            "current_problem_id": 7,
            "next_problem_index": 3,
        }
    )
    service = Stage3Service(mongo_client)

    progress = service.get_progress("student_1", lesson_id="lesson_1").progress

    assert progress.lesson_id == "lesson_1"
    assert progress.total_problems == 5
    assert progress.completed_problems == [1, 2]
    assert progress.review_problems == [3]
    assert progress.current_problem_id is None
