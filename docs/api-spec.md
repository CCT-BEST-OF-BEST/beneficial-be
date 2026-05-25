# Beneficial Backend API 명세서

> 최종 업데이트: 2026-05-25
> 대상: 프론트엔드 / 프론트 에이전트의 리팩토링 작업
> 관련 문서: [페르소나 기반 재설계 기획안](./persona-based-redesign.md) · [페르소나 기반 UI 플로우](./persona-ui-flow.md)

이 문서는 백엔드가 노출하는 모든 HTTP 엔드포인트의 **요청/응답 스키마**, **인증 요구사항**, **에러 케이스**를 정리한다. 코드 상의 권위 있는 HTTP 정의는 각 도메인의 `controller/` 라우터이고, 도메인 스키마는 `app/domains/**/schemas.py`에 있다.

---

## 1. 개요

### 1.1 베이스 URL
- 로컬 개발: `http://localhost:8000`
- 라우터 prefix가 곧 도메인 경로다 (전역 prefix 없음). 예: `/auth/login`, `/agent/chat`, `/student/learning/stage3/next-problem`.

### 1.2 인증 모델
| 요소 | 위치 | 비고 |
| --- | --- | --- |
| Access token | `Authorization: Bearer <jwt>` 헤더 | HS256, 30분 만료 |
| Refresh token | `refresh_token` 쿠키 (`HttpOnly`, path=`/auth`) **또는** request body | 14일 만료, rotation 적용 |

- 보호 엔드포인트 (`Depends(get_current_user)`): access token 없거나 만료 시 `401`.
- 헬스 체크(`GET /`)를 제외한 **모든 서비스 엔드포인트는 로그인 필수**다. `/admin/*`는 developer 권한이 필요하다.

### 1.3 공통 응답 규약
- 성공 응답은 각 엔드포인트가 명시한 Pydantic 모델 형태 (대부분 JSON).
- 에러 응답은 FastAPI 기본 포맷:
  ```json
  { "detail": "사람이 읽을 수 있는 에러 메시지" }
  ```
- 흔히 쓰이는 상태 코드: `200`, `201`, `204`, `400`, `401`, `404`, `409`, `500`.

### 1.4 도메인 한눈에 보기
| Prefix | 도메인 | 인증 |
| --- | --- | --- |
| `/` | 시스템 메타 정보 (`GET /`만) | — |
| `/auth` | 회원가입 / 로그인 / 세션 | 일부 보호 (`/me`) |
| `/agent` | 학습 코치 Agent (LangGraph) | 전부 보호 |
| `/student/learning` | Stage 1·2 컨텐츠 + 시각 힌트 | 전부 보호 |
| `/student/learning/records` | 학습 기록 조회 | 보호 |
| `/student/learning/stage3` | Stage 3 문제풀이 | 전부 보호 |
| `/student/me` | 학생용 긍정 진척도 | student 보호 |
| `/content` | 단원·차시 콘텐츠 트리 | 전부 보호 |
| `/teacher/classes` | 교사 담당 반/학생 조회 | teacher/developer 보호 |
| `/teacher/students` | 교사용 학생 약점/기록 조회 | teacher/developer 보호 |
| `/teacher/instruction` | 교사용 문제 초안/배정 관리 | teacher/developer 보호 |
| `/chat` | 단발 RAG 채팅 (Agent와 별개) | 전부 보호 |
| `/admin` | 시스템 관리, 시드/인덱싱 | developer 보호 |

### 1.5 시스템 메타
**`GET /`** — 인증 불필요. 헬스 체크/버전 확인용.
```json
{
  "message": "CCT 백엔드 API",
  "version": "1.0.0",
  "description": "초등학생 돌봄반 학생들을 위한 한국어 교육을 위한 시스템"
}
```

또한 FastAPI가 자동으로 `GET /docs` (Swagger UI)와 `GET /openapi.json`을 노출한다.

---

## 2. 인증 흐름 (Auth · `/auth`)

| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| POST | `/auth/signup` | — | 회원가입 |
| POST | `/auth/login` | — | 로그인, 토큰 페어 발급 |
| POST | `/auth/refresh` | refresh token | access token 재발급 + refresh rotation |
| POST | `/auth/logout` | refresh token | 서버 측 refresh 무효화 + 쿠키 삭제 |
| GET | `/auth/me` | access token | 현재 사용자 정보 |

### 2.1 `POST /auth/signup`
**Request body**
```json
{
  "email": "string (5~255자)",
  "password": "string (8~128자)",
  "display_name": "string (1~50자)"
}
```
**Response 201** (`UserResponse`)
```json
{ "user_id": "u_xxx", "email": "...", "display_name": "...", "role": "student" }
```
**Errors**
- `409` 이미 가입된 이메일
- `400` 기타 검증 실패

### 2.2 `POST /auth/login`
**Request body**
```json
{ "email": "...", "password": "..." }
```
**Response 200** (`AuthTokenResponse`)
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "<opaque>",
  "user": { "user_id": "...", "email": "...", "display_name": "...", "role": "student" }
}
```
- `refresh_token`은 응답 본문과 함께 `Set-Cookie: refresh_token=...; HttpOnly; Path=/auth; SameSite=Lax; Max-Age=1209600` 도 같이 설정된다.
- **Errors**: `401` 자격 증명 불일치.

### 2.3 `POST /auth/refresh`
**Request**: body의 `{ "refresh_token": "..." }` **또는** `refresh_token` 쿠키 중 하나가 있어야 함.
**Response 200**: `AuthTokenResponse` (새 access + 새 refresh, 기존 refresh는 무효화)
**Errors**: `401` refresh가 없거나 만료/회수됨.

### 2.4 `POST /auth/logout`
**Request**: body 또는 쿠키의 refresh token. 없으면 그냥 쿠키만 삭제.
**Response 200**: `{ "message": "로그아웃되었습니다." }`

### 2.5 `GET /auth/me`
**Headers**: `Authorization: Bearer <access_token>`
**Response 200**: `UserResponse` (위와 동일)
**Errors**: `401` 토큰 없음/만료/유효하지 않음.

---

## 3. 학습 Agent (`/agent`)

LangGraph 기반 학습 코치. 모든 엔드포인트가 `get_current_user`로 보호된다.

| Method | Path | 설명 |
| --- | --- | --- |
| POST | `/agent/chat` | Agent에게 메시지 전송 → action 결정 + (선택적) RAG + LLM 응답 |
| GET | `/agent/session/{session_id}` | 세션의 전체 메시지 히스토리 조회 |
| DELETE | `/agent/session/{session_id}` | 세션 삭제 |
| GET | `/agent/profile/me` | 학습 기록 기반 약점 프로파일 |

### 3.1 `POST /agent/chat`
**Request body** (`AgentChatRequest`)
```json
{
  "session_id": "string | null",
  "message": "string"
}
```
- `session_id`가 `null`이면 새 세션을 만들어 반환한다.

**Response 200** (`AgentChatResponse`)
```json
{
  "session_id": "sess_xxx",
  "response": "GPT가 생성한 자연어 응답",
  "agent_action": "answer_with_rag | proactive_hint | encourage | small_talk | ask_followup",
  "target_concept": "되/돼 | null",
  "used_tools": ["rag_search"],
  "weak_concepts": ["가르치다/가르키다", "되/돼"]
}
```
- `agent_action`: 그래프가 결정한 행동 유형.
- `target_concept`: `proactive_hint`일 때 보조 설명 대상 (없으면 `null`).
- `used_tools`: 이번 턴에서 호출된 도구. 현재는 `"rag_search"` 한 종류.
- `weak_concepts`: 현재 사용자의 상위 약점 concept_key 목록 (UI 보조용).

### 3.2 `GET /agent/session/{session_id}`
**Response 200** (`ChatSessionResponse`)
```json
{
  "session_id": "sess_xxx",
  "user_id": "u_xxx",
  "messages": [
    {
      "role": "user | assistant",
      "content": "메시지 본문",
      "agent_action": "answer_with_rag | null",
      "target_concept": "되/돼 | null",
      "used_tools": ["rag_search"],
      "created_at": "ISO-8601"
    }
  ],
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "last_agent_action": "answer_with_rag | null"
}
```
**Errors**: `404` 세션 없음 또는 다른 사용자 소유.

### 3.3 `DELETE /agent/session/{session_id}`
**Response**: `204 No Content`
**Errors**: `404` 세션 없음 또는 다른 사용자 소유.

### 3.4 `GET /agent/profile/me`
학생은 이 엔드포인트를 호출할 수 없다. 학생 화면에는 정량 약점 대신 `GET /student/me/progress`의 긍정 지표만 노출한다. 교사는 `/teacher/students/{user_id}/profile`에서 담당 학생의 약점 프로파일을 조회한다.

**Response 200** (`AgentProfileResponse`)
```json
{
  "user_id": "u_xxx",
  "weak_concepts": [
    {
      "concept_key": "되/돼",
      "wrong_count": 3,
      "last_wrong_at": "ISO-8601",
      "priority": 0.87
    }
  ]
}
```
- `priority`가 큰 순서로 정렬되어 옴.

---

## 4. 학습 컨텐츠 (`/student/learning`)

Stage 1 (카드 학습) · Stage 2 (드래그&드롭) 컨텐츠.
이미지 파일 경로는 내려주지 않고, 프론트가 아이콘/컴포넌트로 매핑할 시각 힌트만 제공한다.

### 4.0 콘텐츠 계층 (`/content`)

| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/content/units` | 보호 | 단원과 하위 차시 목록 |
| GET | `/content/lessons/{lesson_id}` | 보호 | 단일 차시 상세 |

`GET /content/units` 응답 예시:

```json
{
  "units": [
    {
      "unit_id": "unit_1",
      "name": "1단원 헷갈리는 낱말",
      "order": 1,
      "lessons": [
        {
          "lesson_id": "lesson_1",
          "unit_id": "unit_1",
          "name": "가르치다/가르키다, 맞추다/맞히다",
          "order": 1,
          "concept_keys": ["가르치다/가르키다", "맞추다/맞히다"],
          "stage_ids": [1, 2, 3]
        }
      ]
    }
  ],
  "total_count": 1
}
```

| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/student/learning/stage1/cards` | 보호 | Stage 1 카드 쌍 목록 |
| POST | `/student/learning/stage1/submit-card-check` | 보호 | Stage 1 답안 확인 |
| GET | `/student/learning/stage2/problems` | 보호 | Stage 2 문제 + 답안 풀 |
| POST | `/student/learning/stage2/submit-answer` | 보호 | Stage 2 답안 제출 |

> 모든 답안 제출 결과는 `LearningRecord`에 저장되어 Agent의 약점 분석에 반영된다.

### 4.1 `GET /student/learning/stage1/cards`
**Response 200** (`Stage1CardsResponse`)
```json
{
  "success": true,
  "total_pairs": 2,
  "card_pairs": [
    {
      "pair_id": "pair_1",
      "word1": "가르치다",
      "word2": "가르키다",
      "card1": {
        "card_id": "card_1",
        "word": "가르치다",
        "meaning": "지식이나 기술을 알려주다",
        "example_sentence": "선생님이 수학을 가르치다.",
        "visual_hint": "book-open",
        "color_theme": "primary"
      },
      "card2": {
        "card_id": "card_2",
        "word": "가르키다",
        "meaning": "손가락 등으로 방향을 가리키다",
        "example_sentence": "그가 건물을 가르키다.",
        "visual_hint": "hand-point-up",
        "color_theme": "warning"
      },
      "order": 1
    }
  ]
}
```
- `word1`이 **항상** 맞춤법상 정답인 단어다.

### 4.2 `POST /student/learning/stage1/submit-card-check`
**Request** (`Stage1SubmitRequest`)
```json
{ "pair_id": "pair_1", "chosen_word": "가르치다" }
```
**Response 200** (`Stage1SubmitResponse`)
```json
{
  "pair_id": "pair_1",
  "is_correct": true,
  "chosen_word": "가르치다",
  "correct_word": "가르치다",
  "concept_key": "가르치다/가르키다"
}
```
**Errors**: `404` pair_id 없음.

### 4.3 `GET /student/learning/stage2/problems`
**Response 200** (`Stage2ProblemsResponse`)
```json
{
  "success": true,
  "lesson_id": "lesson_1",
  "title": "2단계 예제풀이",
  "instruction": "맞춤법에 맞는 낱말 카드를 선택하세요",
  "total_problems": 4,
  "answer_options": ["가르쳐", "가르켜", "맞혀", "맞춰", "..."],
  "problems": [
    { "problem_id": 1, "sentence_part1": "선생님이 수학 공식을", "sentence_part2": "주셨다." }
  ]
}
```
- `correct_answer`와 `full_sentence`는 응답에 포함되지 않는다 (정답 노출 방지). 채점은 `POST /student/learning/stage2/submit-answer`가 담당하며 제출 시점에 둘 다 함께 돌려준다.

### 4.4 `POST /student/learning/stage2/submit-answer`
**Request** (`Stage2SubmitRequest`)
```json
{ "problem_id": 1, "user_answer": "가르쳐" }
```
**Response 200** (`Stage2SubmitResponse`)
```json
{
  "problem_id": 1,
  "is_correct": true,
  "user_answer": "가르쳐",
  "correct_answer": "가르쳐",
  "full_sentence": "선생님이 수학 공식을 가르쳐 주셨다.",
  "concept_key": "가르치다/가르키다"
}
```
**Errors**: `404` lesson 데이터 / problem_id 없음.

## 5. 학생 진척도 (`/student/me`)

| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/student/me/progress` | student 보호 | 본인 긍정 진척도 |

### 5.1 `GET /student/me/progress`

학생에게는 오답 횟수나 약점 우선순위를 직접 노출하지 않는다.

**Response 200** (`StudentProgressResponse`)
```json
{
  "today_solved_count": 3,
  "total_solved_count": 20,
  "streak_correct_count": 4,
  "progress_rate": 60,
  "badges": ["첫 학습 시작", "연속 정답"]
}
```

## 6. 학습 기록 (`/student/learning/records`)

| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/student/learning/records/me` | 보호 | 본인 학습 기록 전체 |

### 6.1 `GET /student/learning/records/me`
**Response 200** (`LearningRecordsResponse`)
```json
{
  "records": [
    {
      "user_id": "u_xxx",
      "temp_user_id": null,
      "stage": 2,
      "question_id": "stage2:lesson_1:1",
      "unit_id": "unit_1",
      "lesson_id": "lesson_1",
      "problem_key": "stage2:lesson_1:1",
      "problem_id": 1,
      "attempt_no": 1,
      "source": "base",
      "assignment_id": null,
      "class_id": "class_demo_1",
      "concept_key": "가르치다/가르키다",
      "user_answer": "가르켰",
      "correct_answer": "가르쳐",
      "is_correct": false,
      "created_at": "ISO-8601"
    }
  ],
  "total_count": 1
}
```

---

## 7. Stage 3 (`/student/learning/stage3`)

Stage 3는 "순차 학습 → 틀린 문제만 순환 복습" 알고리즘으로 별도 진행도(`stage3_progress`)를 갖는다.
모든 엔드포인트가 로그인 필수이며, 진행도는 로그인한 사용자의 `user_id` 별로 저장된다.

| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/student/learning/stage3/problems` | 보호 | 전체 문제 목록 (관리/디버그용) |
| GET | `/student/learning/stage3/next-problem` | 보호 | 다음 출제할 문제 1건 |
| POST | `/student/learning/stage3/submit-answer` | 보호 | 답안 제출 + 진행도 갱신 |
| GET | `/student/learning/stage3/progress` | 보호 | 진행도 조회 |
| POST | `/student/learning/stage3/reset-progress` | 보호 | 진행도 초기화 |

### 7.1 `GET /student/learning/stage3/problems`
**Response 200** (`Stage3ProblemsResponse`)
```json
{
  "success": true,
  "lesson_id": "lesson_1",
  "title": null,
  "instruction": "...",
  "total_problems": 5,
  "problems": [
    {
      "problem_id": 1,
      "sentence_part1": "...",
      "sentence_part2": "...",
      "visual_hint": "book-open",
      "accent_color": "primary",
      "badge": null
    }
  ]
}
```

### 7.2 `GET /student/learning/stage3/next-problem`
**Response 200** (dict, 두 케이스)
- 진행 중:
  ```json
  {
    "success": true,
    "problem": {
      "problem_id": 2,
      "sentence_part1": "...",
      "sentence_part2": "...",
      "visual_hint": "book-open",
      "accent_color": "primary",
      "badge": "재도전 | 첫학습 | null"
    },
    "is_completed": false
  }
  ```
- 모두 완료:
  ```json
  { "success": true, "message": "모든 문제를 완료했습니다!", "is_completed": true }
  ```
- 학습 알고리즘:
  1. **순차 학습** (1→5): 정답/오답 상관없이 한 번씩 시도
  2. **복습 학습**: 모든 문제 시도 후 틀린 문제만 순환 출제
  3. **완료**: 복습 문제까지 모두 정답 시 `is_completed: true`

### 7.3 `POST /student/learning/stage3/submit-answer`
**Request** (`Stage3AnswerRequest`)
```json
{ "problem_id": 1, "user_answer": "돼" }
```
**Response 200** (`Stage3AnswerResponse`)
```json
{
  "success": true,
  "problem_id": 1,
  "is_correct": true,
  "user_answer": "돼",
  "correct_answer": "돼",
  "explanation": "...",
  "full_sentence": "...",
  "status": "correct | wrong | review | completed",
  "badge": "훌륭해요 | 잠시후복습 | null"
}
```

### 7.4 `GET /student/learning/stage3/progress`
**Response 200** (`Stage3ProgressResponse`)
```json
{
  "success": true,
  "progress": {
    "total_problems": 5,
    "correct_count": 3,
    "wrong_count": 2,
    "review_problems": [2, 4],
    "completed_problems": [1, 3, 5],
    "current_problem_id": 2,
    "next_problem_index": 6,
    "review_problem_index": 0
  },
  "is_completed": false
}
```

### 7.5 `POST /student/learning/stage3/reset-progress`
**Response 200**: `{ "success": true, "message": "진행도가 초기화되었습니다." }`

---

## 8. 교사 API (`/teacher`)

교사 API는 `teacher` 또는 `developer` 권한이 필요하다. 교사는 본인이 담당한 반/학생 데이터만 조회하거나 배정할 수 있고, developer는 운영 목적으로 우회 가능하다.

### 8.1 반/학생 조회

| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/teacher/classes` | teacher/developer | 담당 반 목록 |
| GET | `/teacher/classes/{class_id}/students` | teacher/developer | 반 학생 목록 + 약점 요약 |
| GET | `/teacher/students/{user_id}/profile` | teacher/developer | 학생 약점 프로파일 |
| GET | `/teacher/students/{user_id}/records` | teacher/developer | 학생 학습 기록 |

`GET /teacher/classes` 응답 예시:

```json
{
  "classes": [
    {
      "class_id": "class_demo_1",
      "name": "돌봄 한국어 1반",
      "teacher_id": "teacher_demo_1",
      "student_count": 3
    }
  ],
  "total_count": 1
}
```

`GET /teacher/classes/{class_id}/students` 응답 예시:

```json
{
  "class_id": "class_demo_1",
  "students": [
    {
      "user_id": "student_demo_1",
      "email": "student1@example.com",
      "display_name": "민준",
      "weak_concepts": ["되/돼", "안/않다"],
      "recent_activity_at": "ISO-8601"
    }
  ],
  "total_count": 1
}
```

`GET /teacher/students/{user_id}/records` query:

| Query | 타입 | 설명 |
| --- | --- | --- |
| `stage` | `int | null` | 특정 Stage만 필터 |
| `limit` | `int` | 기본 50, 최대 200 |

### 8.2 문제 초안/배정 관리 (`/teacher/instruction`)

| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| POST | `/teacher/instruction/assignments/draft` | teacher/developer | 문제 초안 assignment 생성 |
| GET | `/teacher/instruction/assignments` | teacher/developer | assignment 목록 |
| PATCH | `/teacher/instruction/assignments/{assignment_id}/assign` | teacher/developer | draft를 assigned로 전환 |
| PATCH | `/teacher/instruction/assignments/{assignment_id}/cancel` | teacher/developer | draft/assigned 취소 |
| PATCH | `/teacher/instruction/assignments/{assignment_id}/complete` | teacher/developer | assigned를 completed로 전환 |

상태 흐름:

```text
draft -> assigned -> completed
draft -> cancelled
assigned -> cancelled
```

`POST /teacher/instruction/assignments/draft` 요청 예시:

```json
{
  "target_type": "student",
  "class_id": "class_demo_1",
  "student_id": "student_demo_1",
  "unit_id": "unit_1",
  "lesson_id": "lesson_4",
  "stage": 3,
  "concept_key": "되/돼",
  "problems": [
    {
      "type": "fill_blank",
      "sentence_part1": "숙제가 다",
      "correct_answer": "됐어",
      "sentence_part2": "?",
      "full_sentence": "숙제가 다 됐어?",
      "explanation": "'됐어'는 '되었어'의 줄임말이에요.",
      "visual_hint": "pencil",
      "accent_color": "primary",
      "validation_status": "pending"
    }
  ],
  "generation_context": {
    "reason": "최근 되/돼 오답 반복"
  }
}
```

응답은 `AssignmentResponse`이며 `assignment_id`, `status`, `problems[].problem_key`, `created_at` 등을 포함한다.

현재 구현 범위는 생성된 문제를 draft로 저장하고 배정 상태를 관리하는 것이다. OpenAI를 호출해 문제 초안을 직접 만드는 `POST /teacher/instruction/generate-problems`는 다음 작업으로 남아 있다.

---

## 9. RAG 채팅 (`/chat`)

> Agent와 별개로 존재하는 **단발 RAG 질의응답** API. 세션·약점 분석 없이 한 번의 질문에 대한 답만 돌려준다. 로그인 필수.

| Method | Path | 인증 | 설명 |
| --- | --- | --- | --- |
| POST | `/chat/` | 보호 | RAG 기반 GPT 응답 |
| GET | `/chat/status` | 보호 | RAG/Chat 시스템 상태 |

### 9.1 `POST /chat/`
**Request** (`ChatRequest`)
```json
{ "prompt": "맞춤법이 헷갈려요" }
```
**Response 200** (`ChatResponse`)
```json
{
  "status": "success",
  "prompt": "맞춤법이 헷갈려요",
  "response": "...",
  "collection_used": "all",
  "top_k": 5
}
```
- 내부 기본값으로 `top_k=5`, 모든 컬렉션 검색.

### 9.2 `GET /chat/status`
**Response 200** (`ChatStatusResponse`)
```json
{
  "status": "success",
  "chat_system": "active",
  "rag_system": "available",
  "collections": {
    "korean_word_problems": { "document_count": 15, "status": "available" },
    "card_check": { "document_count": 8, "status": "available" },
    "pdf_documents": { "document_count": 1250, "status": "available" }
  }
}
```

---

## 10. 관리자 / 인덱싱 (`/admin`)

> developer 권한 필요.
> 평상시 startup은 lightweight 모드라 시드/인덱싱은 이 엔드포인트들로 트리거한다.

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/admin/system-status` | ChromaDB 컬렉션 상태 |
| POST | `/admin/initialize-all` | 최초 배포 시 1회 — 시드 + 벡터 인덱싱 + BM25 + 가상 질문 생성 |
| POST | `/admin/seed-data` | MongoDB에 Stage 1·2·3 시드 적재 |
| POST | `/admin/rebuild-vector-index` | ChromaDB 전체 컬렉션 재인덱싱 + BM25 |
| POST | `/admin/rebuild-bm25` | BM25 인메모리 인덱스만 재구축 |
| POST | `/admin/build-hypothetical-questions` | OpenAI로 가상 질문 생성 (**API 비용 발생**) |
| POST | `/admin/indexing/pdf` | PDF 문서만 재인덱싱 |
| GET | `/admin/indexing/status` | `system-status`의 호환용 별칭 |

모든 엔드포인트는 dict 형태의 결과를 반환한다 (스키마 정의 없음). 대체로 `{ "status": "success", ... }` 형태이고 실패 시 `500`.

---

## 11. 공통 데이터 타입

### 11.1 Agent action
| 값 | 의미 |
| --- | --- |
| `answer_with_rag` | 질문에 대한 직접 답변 + RAG 호출 |
| `proactive_hint` | 약점 개념을 자연스럽게 끼워서 설명 |
| `encourage` | 칭찬/격려 위주 |
| `small_talk` | 가벼운 잡담 |
| `ask_followup` | 추가 질문으로 맥락 보강 |

### 11.2 concept_key
"`가르치다/가르키다`", "`되/돼`"처럼 슬래시로 두 단어를 묶은 문자열. Stage 1·2·3 답안이 같은 concept_key로 묶여서 Agent의 약점 분석에 쓰인다.

### 11.3 Stage3 badge
| 값 | 의미 |
| --- | --- |
| `첫학습` | 한 문제를 처음 푼 직후 |
| `훌륭해요` | 정답 처리됨 |
| `잠시후복습` | 오답으로 복습 큐에 들어감 |
| `재도전` | 복습 단계에서 다시 출제됨 |

### 11.4 user_id
- `auth/signup`에서 발급되는 `"u_..."` 형태. 모든 학습/채팅 엔드포인트가 로그인 필수이므로 항상 이 형태로만 들어온다.

---

## 12. 에러 처리 가이드

1. **401 처리**: access token 만료 시 자동으로 `/auth/refresh` → 원래 요청 재시도 패턴을 권장. refresh도 401이면 로그인 페이지로.
2. **404**: 자원 없음 또는 다른 사용자 소유. 사용자에게 "찾을 수 없음" 표시.
3. **409**: 회원가입 중복 이메일 — 폼 인라인 에러로 표시.
4. **500**: 백엔드 로그 확인 필요. UI에서는 "잠시 후 다시 시도해주세요" 정도로.

---

## 13. 빠른 확인 명령

```bash
# 서버 기동 (기본 lightweight)
uvicorn app.main:app --reload

# 최초 1회: 시드/인덱싱 모두 수행
curl -X POST http://localhost:8000/admin/initialize-all \
  -H "Authorization: Bearer <developer_access_token>"

# 시스템 상태
curl http://localhost:8000/admin/system-status \
  -H "Authorization: Bearer <developer_access_token>"

# Swagger UI (자동 생성된 OpenAPI 문서)
open http://localhost:8000/docs
```

> 이 명세서와 코드가 충돌할 경우 **코드가 권위 있다**. 변경이 누락된 경우 PR 시 본 문서도 같이 갱신한다.
