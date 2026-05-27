from app.domains.content.service.catalog_service import ContentCatalogService


class FakeContentCatalogRepository:
    def find_units(self):
        return [
            {
                "unit_id": "unit_1",
                "name": "1단원",
                "order": 1,
                "lesson_ids": ["lesson_2", "lesson_1"],
            }
        ]

    def find_lessons(self):
        return [
            {
                "lesson_id": "lesson_1",
                "unit_id": "unit_1",
                "name": "차시 1",
                "order": 1,
                "concept_keys": ["A/B"],
                "stage_ids": [1, 2, 3],
            },
            {
                "lesson_id": "lesson_2",
                "unit_id": "unit_1",
                "name": "차시 2",
                "order": 2,
                "concept_keys": ["C/D"],
                "stage_ids": [1, 2, 3],
            },
        ]

    def find_lessons_by_unit(self, unit_id):
        return [
            lesson
            for lesson in self.find_lessons()
            if lesson["unit_id"] == unit_id
        ]

    def find_lesson_by_id(self, lesson_id):
        return next(
            (
                lesson
                for lesson in self.find_lessons()
                if lesson["lesson_id"] == lesson_id
            ),
            None,
        )


def test_list_units_with_lessons_respects_unit_lesson_order():
    service = ContentCatalogService(FakeContentCatalogRepository())

    units = service.list_units_with_lessons()

    assert units[0][0].unit_id == "unit_1"
    assert [lesson.lesson_id for lesson in units[0][1]] == ["lesson_2", "lesson_1"]


def test_get_lesson_returns_none_when_missing():
    service = ContentCatalogService(FakeContentCatalogRepository())

    assert service.get_lesson("lesson_1").name == "차시 1"
    assert service.get_lesson("missing") is None
