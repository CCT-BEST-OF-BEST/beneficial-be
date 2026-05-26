from app.infrastructure.db.mongo.indexes import MONGO_INDEXES, ensure_mongo_indexes


class FakeMongoClient:
    def __init__(self):
        self.created_indexes = []

    def create_index(
        self,
        collection_name,
        keys,
        unique=False,
        name=None,
        partial_filter_expression=None,
    ):
        self.created_indexes.append(
            {
                "collection_name": collection_name,
                "keys": keys,
                "unique": unique,
                "name": name,
                "partial_filter_expression": partial_filter_expression,
            }
        )
        return name


def test_mongo_index_specs_cover_learning_progress_and_assignments():
    index_names = {spec["name"] for spec in MONGO_INDEXES}

    assert "idx_learning_records_user_created_at" in index_names
    assert "idx_learning_records_user_concept_correct" in index_names
    assert "idx_learning_records_user_problem_key" in index_names
    assert "idx_stage3_progress_user_lesson_unique" in index_names
    assert "idx_teacher_assignments_student_status" in index_names
    assert "idx_teacher_assignments_class_status" in index_names
    assert "idx_teacher_assignments_teacher_created_at" in index_names


def test_ensure_mongo_indexes_creates_declared_indexes():
    mongo_client = FakeMongoClient()

    created = ensure_mongo_indexes(mongo_client)

    assert created == [spec["name"] for spec in MONGO_INDEXES]
    assert len(mongo_client.created_indexes) == len(MONGO_INDEXES)
    stage3_index = next(
        index
        for index in mongo_client.created_indexes
        if index["name"] == "idx_stage3_progress_user_lesson_unique"
    )
    assert stage3_index["unique"] is True
    assert stage3_index["partial_filter_expression"] == {"lesson_id": {"$exists": True}}
