# 프로젝트 현황 및 다음 작업

> 최종 업데이트: 2026-05-22  
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

---

## 현재 중요한 상태

Agent MVP가 LangGraph 위에서 동작하는 단계까지 도달했다.

남은 주요 작업:
- [ ] Stage 1/2 답변도 LearningRecord에 저장 (Agent 약점 판단 데이터 풍부화)
- [ ] LangGraph 노드별 trace 로그 (디버깅)
- [ ] 앱 startup 무거움 해소 (seed/indexing/BM25를 admin API로 분리)
- [ ] `app/data/models/` → 도메인 `models.py`로 점진 이동
- [ ] `/agent/chat` 통합 smoke test (`RUN_INTEGRATION_TESTS=1`)

---

## 다음 작업 (우선순위 순)

### 우선순위 1. Stage 1/2 답변도 LearningRecord에 저장 ← 진행 중

**목표:** Agent의 약점 판단 데이터를 풍부하게 만든다. 현재는 Stage 3 답변만 저장되어 학생의 전체 학습 흐름을 보지 못한다.

**현재 상태:**
- Stage 1: `GET /learning/stage1/cards`만 존재 (submit 없음)
- Stage 2: `GET /learning/stage2/problems`만 존재 (submit 없음)
- Stage 3: 이미 `LearningRecordService.record_answer()` 연결됨

**해야 할 일:**
- `POST /learning/stage1/submit-card-check` — `(pair_id, chosen_word)` 받아서 정답 확인 + LearningRecord 저장
- `POST /learning/stage2/submit-answer` — `(problem_id, user_answer)` 받아서 정답 확인 + LearningRecord 저장
- `CONCEPT_KEY_BY_ANSWER`에 Stage 1 기본형(가르치다, 가르키다 등) 추가
- 비로그인 사용자는 정답만 반환, 로그인 시에만 LearningRecord 저장
- Stage 1/2 단위 테스트 추가

**완료 기준:**
- Stage 1/2 답변이 `LearningRecord`로 저장되고 `GET /learning/records/me`에서 조회됨
- `GET /agent/profile/me`가 Stage 1/2 오답까지 집계해 weakness profile에 포함

### 우선순위 2. LangGraph 노드별 trace 로그

**목표:** Agent 디버깅이 가능하도록 각 노드 실행 시 상태를 로깅한다.

추가할 로그:
```
[AGENT] load_context: user_id=user_1, session=sess_xxx, weak_concepts=2
[AGENT] decide_action: action=proactive_hint, target=되/돼, use_rag=True
[AGENT] rag_search: query="...", docs=3
[AGENT] generate_response: tokens=120
[AGENT] save_turn: session=sess_xxx, total_messages=5
```

비용 거의 0, 디버깅 ROI 큼.

### 우선순위 3. 앱 startup 무거움 해소

현재 startup에서 seed / vector indexing / BM25 / 가상 질문 생성이 한꺼번에 실행됨.

목표:
- startup은 connection check + router mount만
- 무거운 작업은 `POST /admin/seed`, `POST /admin/rebuild-index` 등 관리 API로 분리

### 우선순위 4. `app/data/models/` → 도메인 `models.py`로 이동

`chat_models.py`, `learning_models.py`가 도메인 schemas와 분리되어 혼재 중.
도메인 경계가 흐려져 있어 점진적으로 도메인 폴더 안으로 이동.

### 우선순위 5. `/agent/chat` 통합 smoke test

현재 `tests/test_agent_session_service.py`는 mock 기반. `RUN_INTEGRATION_TESTS=1`일 때 실제 OpenAI/Mongo로 한 흐름 도는지 검증하는 smoke test 추가.

---

## 검증 명령

```bash
pytest -q
# 현재: 32 passed, 2 skipped

python3 -c "import app.main; print('main import ok')"
```
