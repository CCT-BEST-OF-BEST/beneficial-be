# 레거시 재단장 계획

> 작성일: 2026-05-22  
> 목적: 해커톤 당시 빠르게 만든 백엔드를 AI Agent/RAG 연구용 프로젝트로 재정비한다.  
> 진행 현황: [project-status.md](./project-status.md)

---

## 1. 기본 원칙

이 프로젝트는 지금 완전한 제품 백엔드라기보다 "학습 콘텐츠 + RAG 실험 + 해커톤 API"가 섞인 상태다. 그래서 한 번에 갈아엎기보다, 현재 동작 가능한 기능을 고정하고 새 구조로 조금씩 옮긴다.

원칙:
- 기존 API는 당장 삭제하지 않는다.
- 새 기능은 새 도메인 구조에만 만든다.
- 레거시 코드는 고쳐 쓰기보다 얇은 adapter로 감싼 뒤 점진적으로 교체한다.
- Agent 개발에 직접 필요한 것부터 정리한다.
- 테스트가 깨지는 상태를 먼저 수습한다.

하지 않을 것:
- 전체 폴더 구조를 한 번에 대이동
- 모든 API를 한 번에 인증 필수로 전환
- 프론트 플로우 전체 재설계
- RAG 품질 개선과 Agent 도메인 정리를 동시에 크게 진행

---

## 2. 현재 상태

### 2-1. 현재 디렉토리 구조

```text
app/
  main.py
  common/                          ← 구 app/core (이동 완료)
    security.py                    ← HS256 JWT + PBKDF2 자체 구현
    config/
      loader/config_loader.py
      schema/rag_schema.json
    dependency/dependencies.py
    init/initialization.py
    logging/logging_config.py
  domains/
    auth/                          ← 완료
      models.py / schemas.py / repository.py / service.py
      dependencies.py / router.py
    learning/                      ← 완료 (일부 미연결)
      models.py / schemas.py / repository.py / service.py
      content_service.py / content_router.py
      dependencies.py / router.py
    chat/                          ← 유지 (fallback용)
      service.py / router.py
    stage3/                        ← 부분 완료 (user_id 미연결)
      service.py / router.py
    rag/                           ← 완료
      retriever.py / service.py
      schemas.py / dependencies.py
    agent/                         ← 진행 중
      schemas.py / router.py
      ← models.py / repository.py / service.py / graph.py 미추가
    admin/
      indexing_service.py / router.py
  infrastructure/
    db/
      mongo/mongo_client.py
      vector/vector_db.py / init_vector_db.py / config/vector_db_config.py
    embedding/embedding_model.py
    external/openai_client.py
    search/
      hybrid_search.py / bm25_retriever.py
  data/
    models/
      chat_models.py / document_models.py / learning_models.py
    data_loader/
      pdf_loader.py / seed_mongo_loader.py
      stage1_cards_loader.py / stage2_problems_loader.py / stage3_problems_loader.py
      card_check_loader.py / korean_word_problems_loader.py
      hypothetical_questions_loader.py
    pdfs/korea_grammar_official.pdf
  static/images/
    cards/ / stage3/
```

### 2-2. 남아 있는 문제

- `stage3_progress`가 전역 단일 문서 → 여러 사용자가 진행도를 공유함
- `app/domains/agent/`에 `models.py`, `repository.py`, `service.py`, `graph.py` 미추가
- `app/domains/rag/router.py` 없음 (직접 호출만 가능)
- Stage 1/2가 아직 user_id 기반 기록과 완전히 연결되지 않음
- `app/data/models/`의 공유 Pydantic 모델이 도메인 schemas와 분리된 채 혼재

### 2-3. Agent 개발을 막는 부분

Agent가 필요로 하는 핵심 데이터:

```text
누가(user_id)                       ← 인증 완료
무엇을(concept_key)                  ← LearningRecord 완료
언제(created_at)                     ← 완료
어떻게 틀렸는지(user_answer, ...)    ← 완료
최근 어떤 대화를 했는지(ChatSession) ← 미구현
현재 어떤 도움을 줘야 하는지(AgentDecision) ← 미구현
```

---

## 3. 목표 구조

최종적으로 아래 구조에 가깝게 정리한다.

```text
app/
  main.py
  common/                          ← 현재와 동일, 유지
    security.py
    config/
    dependency/
    init/
    logging/
  domains/
    auth/                          ← 완료
    learning/                      ← 완료 (stage3 user_id 연결 필요)
    chat/                          ← 유지 (fallback)
    stage3/                        ← user_id 기준으로 재정비 필요
    rag/                           ← 완료 (router 추가 선택)
    agent/                         ← 진행 중
      models.py                    ← ChatSession, ChatMessage, AgentDecision
      repository.py
      service.py                   ← ChatSessionService
      graph.py                     ← LangGraph (Phase 5에서 추가)
      schemas.py
      router.py
    admin/                         ← 유지
  infrastructure/                  ← 현재와 동일, 유지
    db/
      mongo/
      vector/
    embedding/
    external/
    search/
  data/                            ← 현재와 동일, 유지
    models/
    data_loader/
    pdfs/
  static/                          ← 유지
```

---

## 4. 재단장 순서

### ✅ Phase 0. 기준선 세우기 (완료)

- [x] `pytest` 수집 실패 해결
- [x] 누락 dependency 정리
- [x] 죽은 레거시 테스트 격리 (`RUN_INTEGRATION_TESTS=1`로 분리)
- [x] `.env.example` 추가
- [x] `app/legacy/` 삭제

완료 기준 달성:
- 기본 `pytest` 통과 (17 passed, 2 skipped)
- 외부 API 테스트는 명시적으로 skip

---

### ✅ Phase 1. 인증 도메인 추가 (완료)

- [x] `User`, `RefreshTokenSession` 모델 추가
- [x] access/refresh token 발급 (HS256, PBKDF2)
- [x] `get_current_user` / `get_optional_current_user` dependency
- [x] refresh token rotation

완료된 API:

| Method | Path | 상태 |
|--------|------|------|
| `POST` | `/auth/signup` | ✅ |
| `POST` | `/auth/login` | ✅ |
| `POST` | `/auth/refresh` | ✅ |
| `POST` | `/auth/logout` | ✅ |
| `GET` | `/auth/me` | ✅ |

---

### ✅ Phase 2. 학습 기록 + RAG 도구화 (완료)

- [x] `LearningRecord` (`user_id`, `concept_key`, `user_answer`, `correct_answer`)
- [x] Stage 3 답변 제출 시 로그인 사용자 학습 기록 자동 저장
- [x] `WeaknessProfileService` (`concept_key`별 오답 집계)
- [x] `GET /learning/records/me` — 학습 기록 조회
- [x] `GET /agent/profile/me` — 약점 프로파일 조회
- [x] `RagRetriever` + `RagService` 분리 (기존 `ChatService` 연결)

미완료:
- [ ] Stage 3 `stage3_progress` → user_id 기준 전환 (Phase 2.5로 처리)

---

### 🔲 Phase 2.5. Stage 3 progress → user_id 기준 전환

목표: 여러 사용자가 동일 문서를 공유하는 전역 progress 제거.

작업:
- `stage3_progress` 문서에 `user_id` 필드 추가
- 조회/업데이트 쿼리를 `{"user_id": user_id}`로 변경
- 비로그인 사용자는 `temp_user_id` fallback 유지 여부 결정

완료 기준:
- 사용자 A와 B가 서로 다른 Stage 3 진행도를 유지한다.

---

### 🔲 Phase 3. Agent MVP — ChatSession + AgentDecision

목표: Agent가 대화 기억과 판단 모델을 가지게 한다.

추가할 파일:
```
app/domains/agent/models.py       ← ChatSession, ChatMessage, AgentDecision
app/domains/agent/repository.py  ← MongoDB CRUD
app/domains/agent/service.py     ← ChatSessionService
app/domains/agent/schemas.py     ← 업데이트 (AgentChatRequest/Response)
app/domains/agent/router.py      ← 업데이트 (/agent/chat, /agent/session/*)
tests/agent/test_session_service.py
```

추가할 모델:

```python
class ChatMessage(BaseModel):
    role: str                    # "user" | "assistant"
    content: str
    agent_action: Optional[str]
    target_concept: Optional[str]
    used_tools: List[str]
    created_at: datetime

class ChatSession(BaseModel):
    session_id: str
    user_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    last_agent_action: Optional[str]
    last_intervention_at: Optional[datetime]

class AgentDecision(BaseModel):
    action: Literal[
        "answer_with_rag",
        "proactive_hint",
        "encourage",
        "small_talk",
        "ask_followup"
    ]
    target_concept: Optional[str]
    should_use_rag: bool
    reason: str
```

추가할 API:

| Method | Path | 역할 |
|--------|------|------|
| `POST` | `/agent/chat` | Agent와 대화 (메인) |
| `GET` | `/agent/session/{session_id}` | 대화 기록 조회 |
| `DELETE` | `/agent/session/{session_id}` | 세션 초기화 |

`/agent/chat` 흐름 (LangGraph 없이 service flow):

```text
POST /agent/chat
  → current_user 확인
  → session 로드/생성
  → learning records / weakness profile 조회
  → message intent 판단
  → AgentDecision 생성
  → 필요하면 RagService 호출
  → 응답 생성
  → turn 저장
  → response 반환
```

응답 예시:

```json
{
  "session_id": "...",
  "response": "...",
  "agent_action": "proactive_hint",
  "target_concept": "되/돼",
  "used_tools": ["rag_search"],
  "weak_concepts": ["되/돼"]
}
```

완료 기준:
- Agent 응답에 `agent_action`, `target_concept`, `session_id` 포함
- 동일 사용자에게 대화 기억과 약점 프로파일이 연결됨

---

### 🔲 Phase 4. LangGraph 연결

목표: Phase 3 service flow를 그래프 노드로 분리한다.

추가할 파일:
```
app/domains/agent/graph.py
```

노드 구성:

```text
load_context
  → classify_intent
  → evaluate_weakness
  → decide_action
  → maybe_rag_search
  → generate_response
  → save_turn
```

완료 기준:
- 그래프 실행 결과와 기존 service flow 결과가 동등하다.
- 노드별 단위 테스트가 가능하다.

---

## 5. 남길 것과 버릴 것

### 남길 것

| 대상 | 현재 위치 | 이유 |
|------|-----------|------|
| Stage 1/2/3 학습 콘텐츠 API | `domains/learning/`, `domains/stage3/` | Agent 약점 판단의 원천 데이터 |
| ChromaDB 데이터 | `infrastructure/db/vector/` | RAG 연구 자산 |
| `HybridSearchService` | `infrastructure/search/hybrid_search.py` | 검색 실험의 핵심 |
| PDF/카드/문제 data loader | `data/data_loader/` | 공식 맞춤법 근거 데이터 |
| 기존 `/chat` | `domains/chat/` | 비교/fallback 용도 |
| `app/data/models/` 공유 모델 | `data/models/` | 인프라 레이어 공유 타입 |

### 정리할 것

| 대상 | 처리 방향 |
|------|-----------|
| 전역 `stage3_progress` 단일 문서 | user_id 기준으로 전환 (Phase 2.5) |
| `temp_user_id` 중심 로직 | 로그인 사용자는 user_id 기준으로 전환, 비로그인만 fallback 유지 |
| `app/data/models/` 중 도메인 모델과 중복되는 것 | 도메인 `models.py`로 이동 후 점진적 정리 |

---

## 6. 앱 시작 흐름 정리

현재 startup에서 너무 많은 일이 일어난다.

```text
현재:
  dependency init / vector DB init / Mongo seed
  auto indexing / stage data loading / BM25 build
  hypothetical question generation
```

목표:

```text
startup:
  - Mongo connection check
  - vector DB connection check
  - router mount

manual/admin (POST /admin/*):
  - seed data
  - rebuild vector index
  - rebuild BM25
  - generate hypothetical questions
```

---

## 7. 테스트 전략

| 종류 | 설명 | 기본 실행 포함 |
|------|------|---------------|
| unit | 순수 로직, 모델, 정책 테스트 | 포함 |
| service | Mongo/Chroma를 mock 또는 test DB로 검증 | 일부 포함 |
| integration | OpenAI, 실제 Mongo, 실제 Chroma 호출 | `RUN_INTEGRATION_TESTS=1`일 때만 |

다음 추가할 테스트:
1. `tests/agent/test_session_service.py` — `ChatSessionService` CRUD
2. `tests/test_agent_decision.py` — `AgentDecision` 판단 로직
3. `tests/test_stage3_user_progress.py` — user_id 기준 진행도 격리

---

## 8. 판단 기준

리팩토링 중 판단이 헷갈리면 아래 기준으로 결정한다.

1. Agent가 학생 상태를 더 잘 이해하는 데 도움이 되는가?
2. RAG 실험을 더 명확하게 비교/평가할 수 있게 하는가?
3. 기존 학습 플로우를 불필요하게 깨지 않는가?
4. 테스트 가능한 단위로 쪼개지는가?
5. 앱 시작과 API 요청의 책임이 분리되는가?
