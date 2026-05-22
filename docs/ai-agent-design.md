# 학습형 AI Agent 설계 문서

> 작성일: 2026-05-22  
> 목표: 초등학생 맞춤형 한국어 학습 AI Agent (Auth + RAG + LangGraph)
> 선행 문서: [AI Agent 요구사항 정리](./agent-requirements.md)

---

## 1. 핵심 목표

> "AI가 학생이 뭘 모르는지 파악하고, 먼저 말을 걸어 보완해주는 학습 도우미"

| 기존 채팅 시스템 | 목표 Agent 시스템 |
|---|---|
| 질문하면 RAG로 답변 | 오답 패턴 감지 → AI가 먼저 개입 |
| 대화 기억 없음 | MongoDB 세션으로 대화 연속성 유지 |
| 모든 학생 동일 답변 | 개인 약점 프로파일 기반 맞춤 답변 |
| 수동형 (학생 주도) | 능동형 (AI가 약점 감지 시 선제 안내) |
| 임시 사용자 ID | 로그인 기반 user_id로 학습 이력 연결 |

---

## 2. 전체 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (학생)                        │
│  채팅 입력 → POST /agent/chat  (session_id, user_id, msg) │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              LangGraph Agent (핵심 두뇌)                  │
│                                                          │
│  ┌──────────┐    ┌───────────┐    ┌──────────────────┐  │
│  │  ROUTER  │───▶│ EXPLAINER │───▶│ RESPONSE_BUILDER │  │
│  │(의도 분류)│    │(RAG 검색) │    │(개인화 응답 생성) │  │
│  └────┬─────┘    └───────────┘    └──────────────────┘  │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────┐    ┌───────────┐                          │
│  │ PROACTIVE│    │ ENCOURAGER│                          │
│  │(약점 개입)│    │(격려/칭찬) │                          │
│  └──────────┘    └───────────┘                          │
└────────────────────────┬────────────────────────────────┘
                         │ Tools
         ┌───────────────┼────────────────┐
         │               │                │
┌────────▼───────┐ ┌─────▼──────┐ ┌──────▼──────┐
│  ChromaDB      │ │  MongoDB   │ │  MongoDB    │
│  (RAG 검색)    │ │ (약점 프로파일)│ │ (채팅 세션) │
│  hybrid_search │ │ LearningRecord│ │ ChatSession │
└────────────────┘ └────────────┘ └─────────────┘
```

---

## 3. LangGraph 상태 머신

```
START
  │
  ▼
[load_context]          ← MongoDB에서 세션 히스토리 + 약점 프로파일 로드
  │
  ▼
[router]                ← 입력 의도 분류
  │
  ├─── 질문 감지 ──────▶ [rag_search] ──▶ [explain] ──▶ [build_response]
  │
  ├─── 오답/약점 감지 ─▶ [proactive_hint] ──────────▶ [build_response]
  │
  └─── 일반 대화 ──────▶ [small_talk] ───────────────▶ [build_response]
                                                              │
                                                              ▼
                                                      [save_session]
                                                              │
                                                              ▼
                                                            END
```

### 각 노드 역할

| 노드 | 역할 |
|---|---|
| `load_context` | 인증된 user_id와 session_id로 대화 히스토리 조회, 오답 개념 집계 |
| `router` | 학생 메시지 의도 분류 (질문 / 일반 대화) + 약점 개입 여부 결정 |
| `rag_search` | 질문 + 약점 키워드로 하이브리드 검색 (기존 HybridSearchService 재사용) |
| `explain` | 검색된 문서로 맞춤 설명 생성 |
| `proactive_hint` | 약점 단어 감지 시 AI가 먼저 관련 설명 제안 |
| `build_response` | 대화 히스토리 + 컨텍스트 + 약점 프로파일 → 최종 GPT 응답 |
| `save_session` | 이번 턴 대화를 MongoDB에 저장 |

---

## 4. 새로운 데이터 모델

### 4-1. ChatSession (MongoDB)

```python
class ChatMessage(BaseModel):
    role: str                    # "user" | "assistant"
    content: str
    timestamp: datetime

class ChatSession(BaseModel):
    session_id: str              # UUID
    user_id: str                 # 인증된 사용자 ID
    temp_user_id: Optional[str]  # 마이그레이션/개발용 호환 필드
    messages: List[ChatMessage]  # 대화 히스토리
    created_at: datetime
    updated_at: datetime
```

### 4-2. StudentWeaknessProfile (집계 뷰)

```python
# LearningRecord에서 실시간 집계 (별도 저장 X)
class StudentWeaknessProfile(BaseModel):
    user_id: str
    weak_words: List[str]        # 2회 이상 틀린 단어들
    wrong_count_by_word: Dict[str, int]  # {"되/돼": 3, "맞추다/맞히다": 2}
    last_wrong_at: Dict[str, datetime]
```

### 4-3. AgentChatRequest / AgentChatResponse

```python
class AgentChatRequest(BaseModel):
    session_id: Optional[str]    # None이면 새 세션 생성
    message: str

class AgentChatResponse(BaseModel):
    session_id: str
    response: str
    agent_action: str            # "explained" | "proactive_hint" | "small_talk"
    weak_words_detected: List[str]  # 이번 턴에서 감지된 약점 단어
```

---

## 5. 약점 감지 로직

```
LearningRecord에서 집계:
  - 같은 question_id를 2회 이상 틀린 경우
  - is_correct=False가 연속으로 나온 경우
  - review_date가 지났는데 재학습 안 한 경우

→ weak_words 목록 생성
```

### 능동 개입 트리거 조건

```python
# router 노드에서 판단
should_intervene = (
    len(weak_words) > 0                          # 약점 단어 존재
    and turns_since_last_hint >= 3               # 3턴 이상 개입 안 한 경우
    and current_message_is_not_question          # 학생이 질문 중이 아닐 때
)
```

---

## 6. 개인화 시스템 프롬프트 예시

```
너는 초등학생 돌봄 선생님이야.

[학생 정보]
- 이름: user_id 기반 프로필명 (예: 학생3)
- 최근 틀린 단어: 되다/돼다 (3회), 맞추다/맞히다 (2회)
- 오늘 학습한 단계: 2단계까지 완료

[대화 방침]
- 학생이 자유롭게 대화하다가 틀린 단어 관련 주제가 나오면 자연스럽게 설명해줘
- 3턴 이상 약점 단어 언급이 없으면 "아, 근데 아까 되/돼 부분 같이 한번 볼까?" 처럼 먼저 제안해
- 칭찬을 자주 하고, 어려운 말은 쓰지 마
```

---

## 7. API 엔드포인트 설계

| Method | Path | 설명 |
|---|---|---|
| `POST` | `/agent/chat` | 에이전트와 대화 (메인 엔드포인트) |
| `GET` | `/agent/session/{session_id}` | 세션 히스토리 조회 |
| `DELETE` | `/agent/session/{session_id}` | 세션 초기화 |
| `GET` | `/agent/profile/me` | 내 약점 프로파일 조회 |

---

## 8. 구현 순서 (Phase)

### Phase 1 — 기반 인프라 (1~2일)
- [ ] 로그인/토큰 인증 (`/auth/signup`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`)
- [ ] `ChatSession` MongoDB 컬렉션 및 CRUD
- [ ] `StudentWeaknessProfile` 집계 서비스
- [ ] LangGraph 패키지 설치 및 기본 그래프 뼈대

### Phase 2 — 핵심 노드 구현 (2~3일)
- [ ] `load_context` 노드: 세션 + 약점 로드
- [ ] `router` 노드: 의도 분류 + 개입 여부 결정
- [ ] `rag_search` 노드: 기존 HybridSearchService 연결
- [ ] `build_response` 노드: 개인화 프롬프트 생성
- [ ] `save_session` 노드: MongoDB 저장

### Phase 3 — 능동 개입 (1~2일)
- [ ] `proactive_hint` 노드: 약점 기반 선제 안내
- [ ] 개입 빈도 조절 (3턴 룰)
- [ ] 자연스러운 전환 문구 프롬프트 튜닝

### Phase 4 — API & 통합 (1일)
- [ ] `/agent/chat` 엔드포인트
- [ ] 기존 `/chat` 엔드포인트와 공존
- [ ] 통합 테스트

---

## 9. 기술 스택 추가

```
기존: FastAPI + ChromaDB + MongoDB + OpenAI API
추가: langgraph + langchain-core + langchain-openai
```

```bash
pip install langgraph langchain-core langchain-openai
```

---

## 10. 미결 사항

- [ ] `temp_user_id` 발급 방식: 현재 프론트엔드가 어떻게 관리하는지 확인 필요
- [ ] 로그인 도입 후 기존 `temp_user_id` 데이터를 `user_id`와 어떻게 매핑할지 결정 필요
- [ ] 세션 만료 정책: 몇 시간 후 자동 종료?
- [ ] 약점 기준: 2회 틀림 vs 3회 틀림 기준 결정 필요
