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

### 문서 정리
- `docs/agent-requirements.md`
- `docs/ai-agent-design.md`
- `docs/legacy-modernization-plan.md`

정리한 방향:
- 기존 API를 바로 삭제하지 않는다.
- 새 기능은 `app/domains/*` 아래 도메인 중심으로 만든다.
- 기존 `app/api`, `app/data`, `app/infrastructure`는 점진적으로 대체한다.

### 테스트 기준선 복구
- 기본 pytest가 깨지지 않게 정리
- OpenAI/RAG 실호출 테스트는 `RUN_INTEGRATION_TESTS=1`일 때만 실행되도록 분리
- 현재 기준: `17 passed, 2 skipped`

### 도메인 구조 추가
```
app/domains/auth        ← 완료
app/domains/learning    ← 완료
app/domains/rag         ← 완료
app/domains/agent       ← 일부 완료 (프로파일 조회만)
```

기존 구조는 아직 유지:
```
app/api / app/data / app/infrastructure / app/common
```

### 인증 MVP 완료
| Method | Path | 상태 |
|--------|------|------|
| `POST` | `/auth/signup` | ✅ |
| `POST` | `/auth/login` | ✅ |
| `POST` | `/auth/refresh` | ✅ |
| `POST` | `/auth/logout` | ✅ |
| `GET` | `/auth/me` | ✅ |

구현 내용:
- `User`, `RefreshTokenSession` MongoDB 모델
- PBKDF2-HMAC-SHA256 비밀번호 해시
- HS256 access token (자체 구현, 외부 라이브러리 없음)
- refresh token 서버 저장 및 rotation
- `get_current_user` / `get_optional_current_user` dependency

핵심 파일:
- `app/common/security.py`
- `app/domains/auth/models.py`, `schemas.py`, `repository.py`, `service.py`, `dependencies.py`, `router.py`

### 학습 기록 도메인 완료

Agent가 읽을 수 있는 학습 기록 형태 추가.

핵심 모델 (`LearningRecord`):
```
user_id / temp_user_id / stage / question_id / concept_key
user_answer / correct_answer / is_correct / created_at
```

- Stage 3 답변 제출 시 로그인 사용자가 있으면 `learning_records`에 자동 저장

### 학습 기록 조회 API 완료
| Method | Path | 역할 |
|--------|------|------|
| `GET` | `/learning/records/me` | 로그인 사용자 학습 기록 목록 조회 |

### Agent 약점 프로파일 API 완료
| Method | Path | 역할 |
|--------|------|------|
| `GET` | `/agent/profile/me` | `concept_key`별 오답 횟수·우선순위 반환 |

### RAG 도구화 완료

기존 `/chat` 중심 RAG를 Agent가 호출할 수 있는 tool 형태로 분리.

```
RagRetriever  → HybridSearchService 래퍼
RagService.search()  → 검색 결과 + context 생성
RagService.answer()  → RAG 기반 응답 생성
```

- 기존 `ChatService`는 새 `RagService`를 사용하도록 연결

### 로그 정리
- 이모지 제거
- 로그 레벨을 `[INFO]`, `[WARN]`, `[ERROR]` 형식으로 변경

---

## 현재 중요한 상태

**Agent 본체는 아직 없다.**

완료된 것은 Agent가 사용할 재료들:
- [x] user_id 기반 인증
- [x] 학습 기록 저장
- [x] 학습 기록 조회
- [x] 약점 프로파일 조회
- [x] RAG tool 서비스

아직 남은 주요 레거시:
- [ ] Stage 3 progress가 아직 전역 `_id: "stage3_progress"` 단일 문서
- [ ] Stage 1/2가 아직 user_id 기반 기록과 완전히 연결되지 않음
- [ ] ChatSession 없음
- [ ] AgentDecision 없음
- [ ] `/agent/chat` 없음
- [ ] LangGraph 연결 없음

---

## 다음 작업 (우선순위 순)

### 우선순위 1. ChatSession 도메인 추가

**목표:** Agent가 대화 기억을 가질 수 있게 한다.

추가할 모델:
```python
class ChatSession(BaseModel):
    session_id: str
    user_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    last_agent_action: Optional[str]
    last_intervention_at: Optional[datetime]

class ChatMessage(BaseModel):  # AgentTurn 역할
    role: str          # "user" | "assistant"
    content: str
    agent_action: Optional[str]
    target_concept: Optional[str]
    used_tools: List[str]
    created_at: datetime
```

추가할 서비스 (`ChatSessionService`):
- `create_session`
- `get_session`
- `append_message`
- `get_recent_messages`
- `update_last_agent_action`

추가할 API:
```
GET    /agent/session/{session_id}
DELETE /agent/session/{session_id}
```

추가할 파일:
```
app/domains/agent/models.py
app/domains/agent/repository.py
app/domains/agent/service.py
app/domains/agent/schemas.py   ← 업데이트
app/domains/agent/router.py    ← 업데이트
tests/test_agent_session_service.py
```

### 우선순위 2. AgentDecision 모델 추가

**목표:** Agent가 "무엇을 할지"를 명시적으로 결정하게 한다.

```python
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

이 모델이 있으면 디버깅과 테스트가 쉬워진다.

### 우선순위 3. `/agent/chat` MVP 구현

처음에는 LangGraph 없이 service flow로 구현한다.

흐름:
```
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

### 우선순위 4. Stage 3 progress를 user_id 기준으로 변경

현재 전역 `_id: "stage3_progress"` 단일 문서 → 여러 사용자가 쓰면 진행도가 섞임.

해야 할 것:
- `stage3_progress` 문서에 `user_id` 추가
- 조회/업데이트 필터를 `{"user_id": user_id}`로 변경
- 비로그인 사용자는 legacy fallback 유지 여부 결정

### 우선순위 5. LangGraph 연결

Agent MVP가 service flow로 동작한 뒤 아래 node로 분리한다:

```
load_context → classify_intent → evaluate_weakness
→ decide_action → maybe_rag_search → generate_response → save_turn
```

---

## 검증 명령

```bash
pytest -q
# 예상: 17 passed, 2 skipped

python3 -c "import app.main; print('main import ok')"
# 예상: main import ok
```
