# 프로젝트 현황 및 다음 작업

> 최종 업데이트: 2026-05-23 (data/models 정리 + smoke test 추가)  
> 관련 문서: [AI Agent 요구사항](./agent-requirements.md) · [AI Agent 설계](./ai-agent-design.md) · [레거시 재단장 계획](./legacy-modernization-plan.md)

---

## 프로젝트 목표

해커톤 당시 만든 레거시 FastAPI 백엔드를 **초등학생 한국어 학습 Agent + RAG 연구용 백엔드**로 재정비한다.

핵심 방향: 단순 RAG 챗봇이 아니라, 학생의 학습 기록과 대화 맥락을 보고 필요한 도움을 결정하는 **학습 Agent**를 만드는 것.

### Agent 역할 정의

- 학생의 학습 기록과 대화 맥락을 보고
- 지금 설명할지, 힌트를 줄지, 복습을 제안할지, 칭찬만 할지 결정하고
- 필요할 때 RAG를 도구로 호출하는 학습 코치

> RAG는 Agent의 중심이 아니라 "필요할 때 호출하는 도구"다.

---

## 완료된 작업

### 기반 (Phase 0~1)
- [x] 테스트 기준선 (`RUN_INTEGRATION_TESTS=1` 분리, 기본 통과)
- [x] 도메인 디렉토리 구조 (`app/domains/*`)
- [x] 인증 MVP: `/auth/signup|login|refresh|logout|me`
  - PBKDF2-HMAC-SHA256 패스워드
  - HS256 access token 자체 구현
  - refresh token rotation
  - `get_current_user` / `get_optional_current_user`

### 학습 기록 + RAG (Phase 2~3)
- [x] `LearningRecord` 도메인 (user_id, concept_key 중심)
- [x] Stage 3 답변 제출 시 LearningRecord 자동 저장
- [x] `GET /learning/records/me` — 학습 기록 조회
- [x] `GET /agent/profile/me` — 약점 프로파일 조회
- [x] `RagRetriever` + `RagService` 분리 (Agent tool 형태)

### Agent MVP (우선순위 1~3 완료)
- [x] `ChatSession`, `ChatMessage`, `AgentDecision` 모델
- [x] `ChatSessionService` (생성/조회/메시지 추가/삭제)
- [x] `AgentService` (`_decide` 의도 분류 + 흐름 오케스트레이션)
- [x] `POST /agent/chat`
- [x] `GET /agent/session/{id}`, `DELETE /agent/session/{id}`

### Stage 3 user_id 전환 (우선순위 4 완료)
- [x] `Stage3Service` MongoClient 의존성 주입
- [x] 진행도 필터를 `{"user_id": user_id}`로 변경
- [x] 비로그인 사용자는 `"anonymous"` fallback
- [x] `reset_progress(user_id)` 메서드 도입

### LangGraph 연결 (우선순위 5 완료)
- [x] `app/domains/agent/graph.py` — `AgentState` + `build_agent_graph`
- [x] 노드: `load_context → decide_action → [rag_search] → generate_response → save_turn`
- [x] `should_use_rag` 기반 conditional edge
- [x] `AgentService.chat()`이 그래프 `ainvoke`로 위임

### LangGraph 노드별 trace 로그 (완료)
- [x] 각 노드 진입 시 INFO 로그 (`[AGENT] load_context/decide_action/rag_search/generate_response/save_turn`)
- [x] `route_after_decision` DEBUG 로그
- [x] 사용자 메시지/응답 미리보기는 `_short()`로 잘라서 한 줄 유지

### `/agent/chat` 통합 smoke test (완료)
- [x] `tests/test_agent_chat_integration.py` — `RUN_INTEGRATION_TESTS=1`일 때만 활성화
- [x] signup → login → `/agent/chat` → 세션 조회 → 세션 삭제 한 흐름 검증
- [x] 실제 OpenAI / Mongo / Chroma 기준으로 LangGraph 그래프가 끝까지 도는지 확인

### `app/data/models/` 정리 (완료)
- [x] `chat_models.py` → `app/domains/chat/schemas.py`로 이동
- [x] `learning_models.py`의 Stage 3 스키마 → `app/domains/stage3/schemas.py`로 이동
- [x] 미사용 `document_models.py` 삭제
- [x] 죽은 코드(`app/domains/learning/content_service.py`의 `LearningService`)와 그것만이 의존하던 레거시 lesson 스키마(`LessonResponse`, `WordCard`, 레거시 `LearningRecord`/`SubmitAnswerRequest`/`UserProgress` 등) 일괄 삭제
- [x] `app/data/models/` 디렉토리 자체 제거

---

## 현재 중요한 상태

Agent MVP가 LangGraph 위에서 동작하고, 각 노드 흐름이 로그로 추적된다. 통합 smoke test로 실서비스 의존(OpenAI/Mongo/Chroma)까지 한 번에 검증할 수 있고, 도메인 디렉토리 구조에서 더 이상 `app/data/models/`를 거치지 않는다.

남은 주요 작업:
- [x] Stage 1/2 답변도 LearningRecord에 저장 (Agent 약점 판단 데이터 풍부화)
- [x] 앱 startup 무거움 해소 (seed/indexing/BM25를 admin API로 분리)
- [x] LangGraph 노드별 trace 로그 (디버깅)
- [x] `/agent/chat` 통합 smoke test (`RUN_INTEGRATION_TESTS=1`)
- [x] `app/data/models/` → 도메인 schemas로 이동 (+ 죽은 `LearningService` 제거)

---

## 다음 작업 (우선순위 순)

### ✅ 우선순위 1. Stage 1/2 답변도 LearningRecord에 저장 (완료)

- `POST /learning/stage1/submit-card-check` — 카드 쌍 정답 평가 + LearningRecord 저장
- `POST /learning/stage2/submit-answer` — 문제 답안 평가 + LearningRecord 저장
- `CONCEPT_KEY_BY_ANSWER`에 Stage 1 기본형 추가 → Stage 1/2/3 오답이 같은 concept_key로 묶임
- `LearningRecordService.record_stage1_card_check`, `record_stage2_answer` 메서드 추가
- 통합 동작 포함 8개 테스트 추가

### ✅ 우선순위 2. 앱 startup 무거움 해소 (완료)

기존 startup은 8단계(시드, 인덱싱, BM25, 가상 질문 생성 등)를 한꺼번에 수행해 부팅이 무거웠음.

**변경 내용:**
- `InitializationService`를 `startup_lightweight` / `seed_mongo_collections` / `rebuild_vector_index` / `rebuild_bm25_index` / `build_hypothetical_questions_index` / `full_initialization`로 분리
- 기본 startup: lightweight (의존성 init + 벡터 DB 연결 + BM25 인메모리 인덱스 빌드)
- 무거운 작업은 `/admin/*` 엔드포인트로 분리:
  - `POST /admin/initialize-all` (최초 1회)
  - `POST /admin/seed-data`
  - `POST /admin/rebuild-vector-index`
  - `POST /admin/rebuild-bm25`
  - `POST /admin/build-hypothetical-questions`
  - `GET /admin/system-status`
- `AUTO_INIT_ON_STARTUP=1` 환경변수로 기존 동작(full init) 유지 가능 — 최초 배포에 편리

### ✅ 우선순위 3. LangGraph 노드별 trace 로그 (완료)

각 노드 실행 시 INFO 로그를 남기고, 사용자 메시지/응답 미리보기는 `_short()` 헬퍼로 한 줄에 들어가게 잘라서 표시한다.

실제 출력 예시:
```
[AGENT] load_context: user_id=user_1 session=sess_xxx weak_concepts=1 recent=1 msg='되/돼 차이가 뭐야?'
[AGENT] decide_action: action=answer_with_rag target=None use_rag=True reason='사용자가 질문을 했습니다.'
[AGENT] rag_search: query='되/돼 차이가 뭐야?' context_chars=6
[AGENT] generate_response: has_rag=True response_chars=13 preview='되는 경우엔 돼를 써요!'
[AGENT] save_turn: session=sess_xxx total_messages=2 tools=['rag_search']
```

### ✅ 우선순위 4. `/agent/chat` 통합 smoke test (완료)

`tests/test_agent_chat_integration.py` 추가.
- 기본 `pytest -q`에서는 스킵 (`RUN_INTEGRATION_TESTS` 미설정 시 module-level skip)
- `RUN_INTEGRATION_TESTS=1`이면 `FastAPI TestClient`로 signup → login → `/agent/chat` → `/agent/session/{id}` GET → DELETE 한 흐름 검증
- `agent_action`, `used_tools`, `weak_concepts` 스키마와 세션에 user/assistant 메시지가 함께 저장되는지 확인

### ✅ 우선순위 5. `app/data/models/` 정리 (완료)

기존에 `app/data/models/`에 모여 있던 Pydantic 스키마를 사용 위치(도메인)로 이동시키고,
오랫동안 호출되지 않던 죽은 코드는 함께 정리했다.

- `chat_models.py` → [`app/domains/chat/schemas.py`](../app/domains/chat/schemas.py)
- `learning_models.py` 중 Stage 3 스키마 → [`app/domains/stage3/schemas.py`](../app/domains/stage3/schemas.py)
- `document_models.py` (전 영역 미사용) 삭제
- `app/domains/learning/content_service.py`의 `LearningService` 및 그것만이 의존하던 레거시 스키마(`LessonResponse`, `WordCard`, 레거시 `LearningRecord`/`SubmitAnswerRequest`/`UserProgress` 등) 삭제 — 현행 Stage 1/2/3 흐름은 모두 `LearningRecordService` 기반으로 통합되어 있음.
- `app/data/models/` 디렉토리 자체 제거

---

## 검증 명령

```bash
pytest -q
# 현재: 40 passed, 3 skipped (integration smoke 1건 포함)

# 라이브 서비스(OpenAI/Mongo/Chroma) 기준 smoke
RUN_INTEGRATION_TESTS=1 pytest tests/test_agent_chat_integration.py -q

python3 -c "import app.main; print('main import ok')"
```
