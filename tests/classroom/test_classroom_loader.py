from app.common.data.data_loader import classroom_loader


class FakeMongoClient:
    def __init__(self, existing_count=0):
        self.existing_count = existing_count
        self.inserted = []

    def count_documents(self, collection_name):
        assert collection_name == "classes"
        return self.existing_count

    def insert_many(self, collection_name, documents):
        assert collection_name == "classes"
        self.inserted.extend(documents)
        return True


def test_load_classrooms_inserts_default_class_when_empty(monkeypatch):
    mongo_client = FakeMongoClient(existing_count=0)
    monkeypatch.setattr(classroom_loader, "get_mongo_client", lambda: mongo_client)

    assert classroom_loader.load_classrooms() is True

    assert len(mongo_client.inserted) == 1
    assert mongo_client.inserted[0]["class_id"] == "class_demo_1"
    assert mongo_client.inserted[0]["teacher_id"] == "teacher_demo_1"
    assert mongo_client.inserted[0]["student_ids"]
    assert "created_at" in mongo_client.inserted[0]


def test_load_classrooms_does_not_overwrite_existing_data(monkeypatch):
    mongo_client = FakeMongoClient(existing_count=1)
    monkeypatch.setattr(classroom_loader, "get_mongo_client", lambda: mongo_client)

    assert classroom_loader.load_classrooms() is True

    assert mongo_client.inserted == []
