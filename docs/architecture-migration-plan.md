# 아키텍처 마이그레이션 계획

## 배경

현재 구조의 핵심 문제:
- 도메인 간 내부 구조가 불일치 (flat / sub-package / 반쪽 마이그레이션이 혼재)
- `learning/` 이 content, progress, stage3, records, practice 를 전부 포함하는 비대 도메인
- `common/data/data_loader/` 가 런타임 임포트 모듈임에도 인프라가 아닌 common에 위치
- 빈 디렉터리 스텁 (`classroom/controller/dto/`, `instruction/controller/`) 이 방치됨
- `chat/` 도메인이 `agent/` 의 반쪽짜리 래퍼로 존재

## 목표 구조

```
app/
├── main.py
│
├── common/                          # 런타임 공통 유틸만
│   ├── config/
│   │   └── loader/
│   │       └── config_loader.py
│   ├── dependency/
│   │   └── dependencies.py
│   ├── init/
│   │   └── initialization.py
│   ├── logging/
│   │   └── logging_config.py
│   └── security.py
│
├── domains/
│   ├── auth/                        # 변경 없음
│   ├── classroom/                   # repositories/ → repository.py, 빈 스텁 삭제
│   ├── content/                     # learning/content + learning/stage3 → 새 도메인
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── stage1/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── stage2/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   └── stage3/
│   │       ├── router.py
│   │       ├── schemas.py
│   │       └── service.py
│   ├── progress/                    # learning/records + practice + progress → 새 도메인
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── instruction/                 # repositories/ → repository.py, 빈 스텁 삭제
│   ├── agent/                       # chat/ 흡수
│   │   ├── graph.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── service.py
│   └── developer/                   # 변경 없음
│
├── infrastructure/
│   ├── db/
│   │   ├── mongo/
│   │   └── vector/
│   ├── embedding/
│   ├── external/
│   ├── loaders/                     # ← common/data/ 전체 이동
│   │   ├── pdfs/
│   │   │   └── korea_grammar_official.pdf
│   │   ├── card_check_loader.py
│   │   ├── classroom_loader.py
│   │   ├── content_hierarchy_loader.py
│   │   ├── hypothetical_questions_loader.py
│   │   ├── korean_word_problems_loader.py
│   │   ├── pdf_loader.py
│   │   ├── seed_mongo_loader.py
│   │   ├── stage1_cards_loader.py
│   │   ├── stage2_problems_loader.py
│   │   └── stage3_problems_loader.py
│   ├── rag/
│   └── search/
│
└── static/
    └── images/
```

## 도메인 구조 규칙

모든 도메인은 예외 없이 아래 파일 구성을 따른다.

```
{domain}/
├── router.py       # HTTP 엔드포인트 (FastAPI APIRouter)
├── service.py      # 비즈니스 로직
├── repository.py   # DB 접근
├── models.py       # MongoDB 도큐먼트 모델
└── schemas.py      # Request / Response Pydantic 스키마
```

역할별 라우터가 여럿인 경우 (`teacher_router.py`, `student_router.py`) 는 허용.
`repositories/` 서브패키지는 사용하지 않는다 — `repository.py` 단일 파일로 유지.

## 마이그레이션 단계

### Phase 1 — 저위험, 즉시 실행 가능

**목표**: 임포트 경로 변경 없이 구조 정리

1. 빈 디렉터리 삭제
   - `app/domains/classroom/controller/`
   - `app/domains/instruction/controller/`

2. `common/data/` → `infrastructure/loaders/` 이동
   - 파일 이동 후 임포트 경로 일괄 치환
   - 영향 파일: `common/init/initialization.py`, `infrastructure/search/hybrid_search.py`, `domains/developer/indexing_service.py`
   - `common/data/pdfs/` → `infrastructure/loaders/pdfs/` 함께 이동

3. `classroom/repositories/` → `classroom/repository.py` 플랫화
   - `base.py` + `mongo.py` 내용을 `repository.py` 하나로 병합
   - 임포트 경로 수정

4. `instruction/repositories/` → `instruction/repository.py` 플랫화
   - 위와 동일

### Phase 2 — 중위험, 도메인 분해

**목표**: `learning/` 비대 도메인 해체

5. `domains/content/` 신설
   - `learning/content/` 내용 이동
   - `learning/stage3/` 내용 이동 (`content/stage3/` 로)
   - `main.py` 라우터 등록 수정

6. `domains/progress/` 신설
   - `learning/records/router.py` 이동
   - `learning/practice/router.py` 이동
   - `learning/progress/router.py` 이동
   - `learning/service.py` (LearningRecordService) → `progress/service.py`
   - `learning/models.py`, `learning/repositories/` → `progress/` 로 이동

7. `domains/learning/` 삭제
   - 위 두 단계 완료 후 디렉터리 제거

### Phase 3 — 중위험, 도메인 통합

**목표**: 반쪽짜리 도메인 정리

8. `domains/chat/` → `domains/agent/` 흡수
   - `chat/router.py` 엔드포인트를 `agent/router.py` 로 병합
   - `chat/service.py` 로직을 `agent/service.py` 로 병합
   - `chat/` 디렉터리 삭제
   - `main.py` 라우터 등록 수정

## 각 Phase 완료 기준

| Phase | 완료 기준 |
|-------|-----------|
| 1 | `pytest` 전체 통과, 서버 정상 기동 |
| 2 | `learning/` 디렉터리 삭제 완료, 전체 테스트 통과 |
| 3 | `chat/` 디렉터리 삭제 완료, `/agent/chat` 엔드포인트 동작 확인 |

## 주의사항

- Phase 2, 3 작업 전 반드시 브랜치 분리
- `learning/` 분해 시 `learning/student_schemas.py` 귀속 도메인 확인 필요 (content or progress)
- `learning/repository.py` 와 `learning/repositories/` 네이밍 충돌 — Phase 2 진입 전 정리
