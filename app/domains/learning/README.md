# Learning Domain

학습 콘텐츠, 풀이 기록, 진행도를 담당한다.

예정 구성:
- `models.py`: `LearningRecord`, `LearningProgress`, `WeakConcept`
- `schemas.py`: 학습 API 요청 및 응답
- `repository.py`: 학습 기록과 진행도 저장소 접근
- `service.py`: 정답 판정, 진행도 갱신, 약점 집계
- `router.py`: 신규 학습 API

기존 Stage 1/2/3 API는 유지하고, 내부 저장 방식을 `user_id`와 `concept_key` 중심으로 점진적으로 정리한다.
