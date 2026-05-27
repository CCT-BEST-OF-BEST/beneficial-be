DEFAULT_STAGE2_LESSON_ID = "lesson_1"
LEGACY_STAGE2_LESSON_ID = "lesson1"


def find_stage2_lesson_data(
    mongo_client,
    lesson_id: str = DEFAULT_STAGE2_LESSON_ID,
) -> dict | None:
    stage2_data = mongo_client.find_one("stage2_problems", {"lesson_id": lesson_id})
    if stage2_data:
        return stage2_data

    if lesson_id == DEFAULT_STAGE2_LESSON_ID:
        return mongo_client.find_one(
            "stage2_problems",
            {"lesson_id": LEGACY_STAGE2_LESSON_ID},
        )
    return None


def find_stage2_problem_data(
    mongo_client,
    problem_id: int,
    lesson_id: str = DEFAULT_STAGE2_LESSON_ID,
) -> dict | None:
    stage2_data = find_stage2_lesson_data(mongo_client, lesson_id)
    if contains_problem(stage2_data, problem_id):
        return stage2_data

    for data in mongo_client.find_many("stage2_problems", {}):
        if contains_problem(data, problem_id):
            return data
    return None


def contains_problem(stage2_data: dict | None, problem_id: int) -> bool:
    if not stage2_data:
        return False
    return any(
        problem.get("problem_id") == problem_id
        for problem in stage2_data.get("problems", [])
    )
