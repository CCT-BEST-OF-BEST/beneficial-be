# AI Agent 요구사항 정리

> 작성일: 2026-05-22  
> 목적: 현재 백엔드/프론트 기능 중 무엇을 유지하고, 무엇을 줄이고, 무엇을 Agent 중심으로 리팩토링할지 결정한다.  
> 관련 문서: [레거시 재단장 계획](./legacy-modernization-plan.md)

---

## 1. 현재 판단

현재 시스템은 크게 세 가지 기능으로 나뉜다.

| 영역 | 현재 상태 | 판단 |
|---|---|---|
| 단계별 학습 | Stage 1 카드, Stage 2 문제, Stage 3 순환 복습 API 존재 | 유지하되 사용자별 상태 관리로 정리 |
| RAG 채팅 | `/chat`에서 검색 후 GPT 응답 | 유지하되 Agent의 도구로 격하 |
| 학습 기록/개인화 | `LearningRecord`, `UserProgress`, `stage3_progress`가 분산됨 | Agent 도입 전 도메인 정리 필요 |
| 사용자 인증 | 해커톤 당시 로그인 없이 `temp_user_id` 중심 | 정식 `User` 도메인과 토큰 인증 추가 |

Agent의 핵심은 "RAG를 잘 호출하는 것"이 아니라 "학생 상태를 보고 지금 어떤 도움을 줄지 결정하는 것"이다.

로그인 기능은 제품 완성도를 위한 부가 기능이기도 하지만, Agent 관점에서는 더 중요하다. Agent가 장기 기억, 약점 프로파일, 복습 이력, 세션 기록을 안정적으로 연결하려면 임시 사용자 ID가 아니라 영속적인 `user_id`가 필요하다.

---

## 2. 가져갈 기능

### 2-1. 학습 콘텐츠

아래 데이터는 Agent의 판단 근거가 되므로 유지한다.

| 기능 | 유지 이유 |
|---|---|
| Stage 1 카드 학습 | 학생이 어떤 단어쌍을 학습했는지 추적 가능 |
| Stage 2 예제 풀이 | 오답 개념을 수집하기 좋음 |
| Stage 3 순환 복습 | "약점 반복 노출"이라는 Agent 개입 근거와 잘 맞음 |
| 맞춤법 PDF / 카드 / 문제 벡터 데이터 | Agent가 설명할 때 쓰는 지식 도구 |

### 2-2. RAG 검색

RAG는 버리지 않는다. 다만 역할을 바꾼다.

```text
기존:
사용자 질문 -> RAG -> GPT 답변

변경:
Agent가 필요하다고 판단한 경우 -> RAG tool 호출 -> 응답 생성에 사용
```

유지할 것:
- `HybridSearchService`
- `ChromaDB` 컬렉션
- PDF/카드/문제 데이터 인덱싱
- 가상 질문 기반 검색 개선 방향

정리할 것:
- 검색 결과 임계값 정책
- BM25 단독 후보를 제거할지 여부
- Agent 응답에 들어갈 context 개수와 우선순위

### 2-3. 기존 `/chat`

초기에는 유지한다.

이유:
- 기존 프론트 기능을 바로 깨지 않기 위함
- Agent 응답과 기존 RAG 응답을 비교하기 쉬움
- fallback 엔드포인트로 사용할 수 있음

단, 장기적으로는 `/chat`을 주력 기능으로 두지 않는다.

---

## 3. 버리거나 뒤로 미룰 기능

### 3-1. 처음부터 완전한 LangGraph Agent 만들기

초기 MVP에서는 미룬다.

이유:
- 현재 도메인 데이터가 아직 Agent가 쓰기 좋은 형태가 아님
- `LearningRecord`, `UserProgress`, `stage3_progress`가 서로 연결되지 않음
- 사용자별 Stage 3 진행도가 분리되어 있지 않음

우선은 아래 순서가 맞다.

```text
도메인 정리 -> 세션/약점 집계 -> Agent 결정 모델 -> LangGraph 연결
```

### 3-2. Cross-Encoder 리랭커

검색 품질 개선에는 도움이 되지만 Agent MVP의 필수 기능은 아니다.

미루는 이유:
- 모델 추가로 배포/성능 부담이 커짐
- 현재 더 급한 문제는 "검색 품질"보다 "학생 상태를 일관되게 저장하는 것"

### 3-3. AI가 완전히 자율적으로 먼저 말 걸기

초기에는 제한한다.

현실적인 MVP:
- 학생이 채팅을 보냈을 때 약점 힌트를 섞어준다.
- 학생이 문제를 틀린 직후 짧은 설명을 제안한다.
- 세션 진입 시 복습 필요 개념을 안내한다.

나중에 할 것:
- 백그라운드 이벤트 기반 선제 메시지
- 푸시 알림
- 장기 학습 스케줄링

---

## 4. 리팩토링 대상

### 4-1. 사용자/인증 도메인

해커톤 버전의 `temp_user_id`는 유지하되, 앞으로의 기준 식별자는 `user_id`로 바꾼다.

초기 인증 방식:
- 이메일/비밀번호 회원가입
- 로그인 시 access token + refresh token 발급
- access token은 짧게 유지
- refresh token은 더 길게 유지하되 서버에 저장하고 재발급 시 회전
- 로그아웃 시 refresh token 폐기

초기에는 소셜 로그인, 이메일 인증, 비밀번호 재설정, 보호자 계정은 미룬다. 주 목적은 AI Agent와 RAG 파이프라인 학습이므로 인증은 "Agent 데이터를 사용자별로 안정적으로 묶는 최소 기능"으로 잡는다.

필요한 모델 방향:

```python
class User(BaseModel):
    user_id: str
    email: str
    password_hash: str
    display_name: str
    role: Literal["student", "admin"] = "student"
    created_at: datetime
    updated_at: datetime

class RefreshTokenSession(BaseModel):
    session_id: str
    user_id: str
    refresh_token_hash: str
    user_agent: Optional[str]
    ip_address: Optional[str]
    expires_at: datetime
    revoked_at: Optional[datetime]
    created_at: datetime
```

토큰 정책 초안:

| 토큰 | 저장 위치 | 만료 | 용도 |
|---|---|---|---|
| Access Token | 프론트 메모리 또는 앱 상태 | 15~30분 | API 인증 |
| Refresh Token | HttpOnly Secure Cookie 권장 | 7~14일 | access token 재발급 |

MongoDB 컬렉션:
- `users`
- `refresh_token_sessions`

인증 API:

| Method | Path | 역할 |
|---|---|---|
| `POST` | `/auth/signup` | 회원가입 |
| `POST` | `/auth/login` | 로그인, 토큰 발급 |
| `POST` | `/auth/refresh` | access token 재발급 |
| `POST` | `/auth/logout` | refresh token 폐기 |
| `GET` | `/auth/me` | 현재 사용자 조회 |

Agent/학습 API는 장기적으로 `temp_user_id`를 직접 받지 않고 인증된 `user_id`를 사용한다.

전환 전략:

```text
1단계: 기존 temp_user_id 유지 + user_id 필드 추가
2단계: 로그인 사용자는 user_id 기준으로 기록 저장
3단계: 비로그인/개발용 요청만 temp_user_id 허용
4단계: Agent API는 user_id 기준으로 완전 전환
```

### 4-2. 학습 기록 도메인

현재 Agent가 쓰기에 부족한 점:
- 문제 ID와 약점 개념이 분리되어 있지 않음
- 오답 답변과 정답 답변이 표준 형태로 저장되지 않음
- Stage 3 진행도가 사용자별로 분리되지 않음

필요한 모델 방향:

```python
class LearningRecord(BaseModel):
    user_id: str
    temp_user_id: Optional[str]  # 마이그레이션/개발용 호환 필드
    stage: int
    question_id: str
    concept_key: str          # 예: "되/돼", "맞추다/맞히다"
    user_answer: str
    correct_answer: str
    is_correct: bool
    created_at: datetime
```

Agent는 `question_id`보다 `concept_key`를 중심으로 학생 약점을 판단한다.

### 4-3. 약점 프로파일 서비스

새 서비스가 필요하다.

```text
WeaknessProfileService
  - user_id 기준 LearningRecord 집계
  - concept_key별 오답 횟수 계산
  - 최근 오답 개념 반환
  - 개입 우선순위 계산
```

응답 예시:

```json
{
  "user_id": "user_123",
  "weak_concepts": [
    {
      "concept_key": "되/돼",
      "wrong_count": 3,
      "last_wrong_at": "2026-05-22T13:00:00",
      "priority": 0.91
    }
  ]
}
```

### 4-4. 채팅 세션 서비스

Agent는 대화 기억이 필요하다.

```text
ChatSessionService
  - 세션 생성
  - 메시지 append
  - 최근 N턴 조회
  - 마지막 Agent 개입 시점 조회
  - 세션 만료 처리
```

초기 정책:
- 최근 10턴만 Agent prompt에 사용
- 전체 메시지는 MongoDB에 저장
- 세션 만료는 우선 24시간

### 4-5. Agent 결정 모델

LLM 응답을 바로 만들기 전에, 먼저 Agent가 할 행동을 명시한다.

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

---

## 5. 백엔드 MVP 범위

### Phase A. 도메인 정리

필수:
- `User`, `RefreshTokenSession` 모델 추가
- `/auth/signup`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me` 추가
- `LearningRecord` 저장 필드 정리
- Stage 3 진행도에 `user_id` 추가
- `MongoClient.upsert_one` 또는 upsert 가능한 update 메서드 추가
- 테스트 수집 실패 해결

하지 않을 것:
- LangGraph 도입
- 복잡한 리랭커
- 푸시형 선제 알림
- 소셜 로그인
- 이메일 인증/비밀번호 재설정

### Phase B. Agent 기반 API 추가

새 API:

| Method | Path | 역할 |
|---|---|---|
| `POST` | `/agent/chat` | Agent와 대화 |
| `GET` | `/agent/session/{session_id}` | 대화 기록 조회 |
| `GET` | `/agent/profile/me` | 내 약점 프로파일 조회 |

기존 API:

| Path | 처리 |
|---|---|
| `/chat` | 유지, fallback 또는 비교용 |
| `/learning/stage1/cards` | 유지 |
| `/learning/stage2/problems` | 유지 |
| `/learning/stage3/*` | 사용자별 진행도로 리팩토링 |

### Phase C. LangGraph 연결

도메인이 정리된 뒤 도입한다.

초기 그래프:

```text
START
-> load_context
-> classify_intent
-> evaluate_weakness
-> decide_action
-> maybe_rag_search
-> generate_response
-> save_turn
-> END
```

---

## 6. 프론트엔드 변경 방향

### 6-1. 유지할 화면

| 화면 | 판단 |
|---|---|
| Stage 1 카드 화면 | 유지 |
| Stage 2 문제 화면 | 유지 |
| Stage 3 문제/복습 화면 | 유지 |
| 채팅 화면 | Agent 채팅으로 교체 또는 병행 |

### 6-2. 추가할 상태

프론트는 최소한 아래 값을 관리해야 한다.

```text
access_token
session_id
current_stage
last_agent_action
weak_concepts_summary
```

### 6-3. 채팅 UI 변경

기존 채팅 UI:

```text
입력 -> /chat -> 답변 표시
```

Agent 채팅 UI:

```text
입력 + session_id + Authorization: Bearer {access_token}
-> /agent/chat
-> response, agent_action, weak_words_detected 표시
```

프론트에서 구분하면 좋은 `agent_action`:

| action | UI 처리 |
|---|---|
| `answer_with_rag` | 일반 답변 |
| `proactive_hint` | 약점 힌트 말풍선 또는 학습 제안 |
| `encourage` | 짧은 칭찬/피드백 |
| `ask_followup` | 선택 버튼 또는 후속 질문 |

### 6-4. 문제 풀이 화면 변경

문제 제출 후 Agent 개입을 연결할 수 있다.

초기 방식:

```text
POST /learning/stage3/submit-answer
-> 정답/오답 결과 표시
-> 오답이면 "AI 설명 보기" 버튼 노출
-> 버튼 클릭 시 /agent/chat 호출
```

나중 방식:

```text
POST /learning/stage3/submit-answer
-> 백엔드가 agent_suggestion을 함께 반환
```

초기에는 버튼 방식이 안전하다. 기존 문제풀이 흐름을 덜 흔든다.

### 6-5. 로그인 UI 추가

초기 프론트는 최소 화면만 추가한다.

필수:
- 회원가입 화면
- 로그인 화면
- 로그아웃 버튼
- 앱 시작 시 `/auth/me`로 로그인 상태 복원
- access token 만료 시 `/auth/refresh` 호출

초기에는 사용자를 "학생" 하나로 본다. 보호자/교사/관리자 UI는 뒤로 미룬다.

---

## 7. 이번 스프린트 결정안

이번 단계에서는 아래만 한다.

1. 기존 학습 기능은 유지한다.
2. RAG는 Agent의 도구로 유지한다.
3. 로그인과 토큰 기반 인증을 추가한다.
4. Stage 3 진행도와 학습 기록을 사용자별/개념별로 정리한다.
5. `/agent/chat`은 새로 만들되 기존 `/chat`은 유지한다.
6. 프론트는 로그인 후 Agent 채팅을 붙일 준비만 한다.
7. LangGraph는 도메인 모델과 서비스가 정리된 뒤 붙인다.

명시적으로 하지 않을 것:

- 모든 채팅 기능을 한 번에 Agent로 교체
- 완전 자동 선제 발화
- Cross-Encoder 리랭커
- 프론트 전체 플로우 재설계
- 장기 학습 스케줄러
- 소셜 로그인
- 보호자/교사 권한 모델

---

## 8. 남은 질문

결정이 필요한 질문:

1. `temp_user_id`는 프론트에서 생성할지, 백엔드에서 발급할지?
2. 약점 기준은 같은 `concept_key` 2회 오답으로 볼지, 3회 오답으로 볼지?
3. Agent가 문제 풀이 직후 자동으로 설명을 붙일지, "AI 설명 보기" 버튼으로 시작할지?
4. 세션 만료는 24시간으로 충분한지?
5. 기존 `/chat`은 언제 제거할지, 계속 fallback으로 둘지?
6. refresh token 만료 기간은 7일과 14일 중 무엇으로 할지?
7. access token을 프론트 메모리에만 둘지, localStorage를 허용할지?
