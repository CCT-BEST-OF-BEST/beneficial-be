# 페르소나 기반 재설계 기획안

> 최종 업데이트: 2026-05-24
> 대상: 백엔드/프론트엔드 리팩토링 및 신규 기능 설계의 출발점
> 관련 문서: [API 명세](./api-spec.md) · [Agent 설계](./ai-agent-design.md) · [프로젝트 현황](./project-status.md)

이 문서는 현재 `student | admin` 두 역할 + 단일 학습 플로우로 묶여 있는 시스템을 **세 명의 실제 사용자(페르소나)** 관점으로 다시 나누는 기획안이다. 코드 변경은 이 문서 합의 후 별도 PR로 진행한다.

---

## 1. 왜 다시 정리하는가

현재 시스템은 다음 문제들이 겹쳐 있다:

- **역할이 두 개뿐(`student | admin`)이라 "교사"가 들어갈 자리가 없다.** 지금 `admin`은 사실상 개발자(시드, 인덱싱)인데, 정작 실제 운영자인 돌봄 교사가 쓸 화면·API가 없다.
- **학생이 자기 약점 프로파일을 직접 조회 가능한 구조**(`/agent/profile/me`). 돌봄반 학생(경계선 지능 포함)에겐 "내가 N번 틀렸다"는 수치 노출이 학습 동기에 역효과. 그 데이터의 진짜 수요자는 교사다.
- **콘텐츠가 정적 자산(이미지 파일)에 묶여 있음.** Stage 1 카드는 `static/images/cards/`의 PNG에 의존. 카드 한 장 추가하려면 디자인 작업 + 파일 업로드가 필요해 확장이 어렵다.
- **AI 에이전트의 활용처가 학생용 챗봇에만 한정.** 약점 분석·맞춤 문제 생성 같은 에이전트의 진짜 가치는 교사 도구에서 살아나는데, 그 통로가 없다.

---

## 2. 페르소나 정의

| 페르소나 | 누구 | 핵심 동기 | 시스템 권한 |
|---|---|---|---|
| **선생님 (Teacher)** | 돌봄반 운영 교사 | 학생별 약점 파악, 맞춤 문제 출제, 진도 관리 | 본인 담당 반의 모든 데이터 + AI 에이전트로 콘텐츠 생성 |
| **학생 (Student)** | 돌봄반 초등학생 (경계선 지능 포함) | 배정받은 문제를 풀고 모르는 건 챗봇에 물어봄 | 본인 학습 데이터(쓰기 가능) + 본인 진척도(긍정 지표만 조회) |
| **개발자 (Developer)** | 시스템 운영·유지보수 인력 | DB 시드, 벡터 인덱싱, 로그 추적, 장애 대응 | 시스템 관리 엔드포인트 전체, 모든 데이터 읽기 |

### 2.1 권한 모델

- `User.role` Literal은 `"student" | "teacher" | "developer"`로 정리한다. 기존 `"admin"`은 재단장 과정에서 `"developer"`로 리네임한다.
- 역할 부여는 [현행 화이트리스트 패턴](../app/domains/auth/whitelist.py)을 확장: `TEACHER_WHITELIST_EMAILS`, `DEVELOPER_WHITELIST_EMAILS`. DB 문서의 기존 `"admin"` 값은 마이그레이션 시 `"developer"`로 치환하거나, 인증 서비스에서 과도기적으로 `"admin"` → `"developer"`로 정규화한다.
- 개발 편의용 답안 우회는 역할과 분리한다. `ANSWER_BYPASS_WHITELIST_EMAILS`는 Stage 2 정답 검증 우회에만 쓰고, 교사/개발자 권한 판단에는 사용하지 않는다.
- 학생-교사 매핑은 Phase 1 MVP에서는 새 컬렉션 `classes`로 표현한다: `{class_id, name, teacher_id, student_ids[]}`.
- 여러 반 소속, 전학/반 이동 이력, 기간별 담당 교사 같은 요구가 생기면 `class_memberships` 컬렉션으로 분리한다. 이 문서의 1차 구현 범위에는 포함하지 않는다.

---

## 3. 페르소나별 기능 매트릭스

| 기능 | 선생님 | 학생 | 개발자 |
|---|:---:|:---:|:---:|
| 회원가입/로그인 | ✓ | ✓ | ✓ |
| 본인 반 학생 목록 조회 | ✓ | — | ✓ (전체) |
| 학생별 약점 프로파일 조회 | ✓ | — | ✓ |
| 학생별 학습기록 타임라인 | ✓ | — | ✓ |
| **AI 에이전트로 맞춤 문제 생성** | ✓ | — | — |
| 학생에게 문제 배정 | ✓ | — | — |
| 배정받은 문제 풀이 | — | ✓ | — |
| AI 챗봇(이로) 질문 | — | ✓ | — |
| 본인 진척도 조회 (긍정 지표만) | — | ✓ | — |
| Stage 1/2/3 콘텐츠 조회 | ✓ (관리용) | ✓ (풀이용) | ✓ |
| DB 시드 재적재 | — | — | ✓ |
| 벡터 인덱싱·BM25 재구축 | — | — | ✓ |
| 시스템 로그·트레이스 조회 | — | — | ✓ |

---

## 4. 선생님 (Teacher) 기능 명세

### 4.1 핵심 가치
선생님은 **AI 에이전트를 자기 도구로 쓰는 사람**이다. 학생 한 명 한 명의 약점을 자동으로 진단받고, 그 약점에 정확히 맞는 문제를 LLM으로 즉석에서 만들어 배정한다.

### 4.2 기능

#### 4.2.1 반 관리 (Phase 1)
- **반 목록 조회**: `GET /teacher/classes` — 내가 담당한 반 카드 형태로 나열
- **반 상세 (학생 목록)**: `GET /teacher/classes/{class_id}/students` — 반 학생들 + 각자 약점 요약(상위 3개 concept_key + wrong_count) + 최근 활동 시각

#### 4.2.2 학생 상세 (Phase 1)
- **학생 약점 프로파일**: `GET /teacher/students/{user_id}/profile` — 기존 `LearningRecordService.get_weakness_profile` 재사용. 정량 데이터(wrong_count, last_wrong_at, priority) 그대로 노출.
- **학생 학습기록 타임라인**: `GET /teacher/students/{user_id}/records?stage=&limit=` — 최근 N건의 LearningRecord를 시간 역순으로.

#### 4.2.3 AI 맞춤 문제 생성·배정 (Phase 2)
- **약점 기반 문제 생성**: `POST /teacher/students/{user_id}/generate-problems`
  - 요청: `{concept_key, count, difficulty?}`
  - 동작: 학생 약점 1개를 골라 LLM(gpt-4o)에게 같은 패턴의 새 예문 N개 생성 요청 → 서버 검증 → `teacher_assignments`에 `draft` 상태로 저장 → 교사 승인 시 `assigned`로 변경 → 학생 큐에 진입
  - 응답: 생성된 문제 미리보기 + 검증 결과
  - 검증: `concept_key` 허용 목록, 정답/빈칸 일치, 중복 문제 여부, 학생용 설명 난이도, JSON 스키마 유효성.
- **반 전체 일괄 생성**: `POST /teacher/classes/{class_id}/generate-problems` — 반 공통 약점 기준 일괄.
- **배정 회수/수정**: `DELETE /teacher/assignments/{assignment_id}`, `PATCH .../status`.

#### 4.2.4 반 전체 분석 (Phase 1 후반 또는 Phase 2)
- **반 공통 약점 집계**: `GET /teacher/classes/{class_id}/summary` — concept_key별 반 전체 wrong_count 합계, 참여율, 평균 진도.

### 4.3 권한 가드
`get_current_teacher` 의존성: role이 `teacher` 또는 `developer`일 때 통과. 학생 조회 시 본인 담당 반에 속한 학생인지 검증(developer는 우회).

---

## 5. 학생 (Student) 기능 명세

### 5.1 핵심 가치
학생은 **선생님이 깔아준 트랙을 따라 푸는 사람**이다. 자기 약점 데이터를 직접 보지 않으며, 모르는 게 있으면 챗봇(이로)에게 물어 해결한다.

### 5.2 기능

#### 5.2.1 학습 (현재 구조 유지)
- Stage 1 카드 학습, Stage 2 예제풀이, Stage 3 문제풀이 (기존 엔드포인트 그대로).
- **추가**: 교사가 배정한 문제가 있으면 일반 출제보다 **우선적으로** 등장 (Phase 2). 큐 비우면 기본 출제로 fallback.

#### 5.2.2 AI 챗봇 (현재 `/agent/chat` 유지)
- "이로의 설명" 통로. 오답일 때 학생 입력을 메시지에 포함시켜 맞춤 피드백 생성 (이미 적용됨).

#### 5.2.3 본인 진척도
- **변경**: 기존 `/agent/profile/me`(약점 노출)는 학생용에서 제거한다.
- 학생용 진척도는 **긍정 지표만**: 오늘 푼 문제 수, 연속 정답, 획득 뱃지, 진도율(%). 정량적 wrong_count는 빠짐.
- 새 엔드포인트: `GET /student/me/progress`.
- 교사용 약점 데이터는 `GET /teacher/students/{user_id}/profile`에서만 제공한다. 같은 URL이 role에 따라 다른 의미의 응답을 내지 않도록 한다.

### 5.3 권한 가드
모든 학생 엔드포인트는 본인 데이터에만 접근. 교사·개발자는 별도 경로(`/teacher/...`)로 접근.

---

## 6. 개발자 (Developer) 기능 명세

### 6.1 핵심 가치
개발자는 **시스템 자체를 운영하는 사람**이다. 비즈니스 데이터(학생 답·약점)는 가능한 한 건드리지 않고, 시스템 상태를 안전하게 유지한다.

### 6.2 기능 (현재 `/admin/*` 그대로 유지)
- DB 시드 적재 (`POST /admin/seed-data`)
- 벡터 인덱싱 재구축 (`POST /admin/rebuild-vector-index`)
- BM25 재구축 (`POST /admin/rebuild-bm25`)
- 가상 질문 생성 (`POST /admin/generate-hypothetical-questions`)
- **신규 추가 후보**: 트레이스 로그 조회, 사용량 통계, 에이전트 호출 모니터링 (Phase 3)

### 6.3 권한 가드
운영 환경에서는 미인증 상태인 `/admin/*`에 [api-spec.md §1.4 비고](./api-spec.md)대로 인증을 적용. role이 `developer`인 경우만 통과한다.

---

## 7. 콘텐츠 계층 구조 및 시각 자산 재설계

### 7.1 콘텐츠 계층 (단원 → 차시 → Stage)
실제 교육 콘텐츠는 다음 계층으로 조직된다:

```
단원 (Unit)         예: "1단원 헷갈리는 낱말"
  └─ 차시 (Lesson)    예: "차시 1 — 가르치다/가르키다, 맞추다/맞히다"
       ├─ Stage 1     해당 차시의 카드 학습 (단어쌍 비교)
       ├─ Stage 2     해당 차시의 예제풀이 (옵션 카드 드래그)
       └─ Stage 3     해당 차시의 문제풀이 (직접 입력)
```

**현재 코드 상태와의 갭**:
- 단원(`unit`) 개념이 데이터 모델에 **없음**. 모든 콘텐츠가 `lesson_id: "lesson1"`이라는 단일 lesson에 평면적으로 묶여 있음.
- 차시는 `stage2_problems_loader.py`·`stage3_problems_loader.py`의 **주석으로만** 표현됨 (`# ── 차시 1: 가르치다/가르키다 ──`). `problem_id`도 차시 무관하게 1~25로 흐름.
- 즉 현재 구조는 새 기획의 1단원 5차시를 **암묵적으로** 담고 있을 뿐, 단원·차시를 명시적으로 다룰 수 없음.

**필요한 변경**:
| 항목 | 변경 |
|---|---|
| 컬렉션 신설 | `units` (`unit_id, name, order, lesson_ids[]`), `lessons` (`lesson_id, unit_id, name, order, concept_keys[]`) |
| 기존 `stage1_cards`/`stage2_problems`/`stage3_problems` | **차시별 도큐먼트로 분리**. 예: `stage2_lesson_1`, `stage2_lesson_2`, `stage3_lesson_1`. 각 도큐먼트는 하나의 `lesson_id`만 가진다. |
| 문제 식별자 | 차시 안에서는 `problem_id: 1..N` 허용. 전역 식별이 필요할 때는 `problem_key = "{stage}:{lesson_id}:{problem_id}"` 사용. |
| 콘텐츠 조회 API | `GET /content/units`, `GET /content/lessons/{lesson_id}` 같은 콘텐츠 트리 조회 추가 |
| 학생 진척도 | `Stage3Progress`는 `user_id + lesson_id` 기준으로 분리. `completed_problems`/`review_problems`는 해당 lesson 내부의 `problem_id`만 담는다. |

### 7.2 현재 콘텐츠 상태와 확장 전제
- **현재 적재된 콘텐츠**: 약 2단원분 (해커톤 시연 시점에 채워 넣은 분량). 평면 구조로 흩어져 있어 단원·차시 계층 모델로 재정렬 필요.
- **재단장 후 전제**: 단원·차시 모델은 처음부터 **N단원 확장 가능**하게 설계한다. "2단원만"의 임시 제약은 두지 않음.
- 기존 콘텐츠는 단원 1·2로 마이그레이션하고, 추가 단원은 나중에 콘텐츠 기획 따라 데이터만 적재.

### 7.3 시각 자산(이미지) 의존 제거

#### 7.3.1 현재 문제
- **Stage 1 카드**: `static/images/cards/card1_front.png` 같은 정적 PNG에 의존 ([stage1_cards_loader.py](../app/data/data_loader/stage1_cards_loader.py), [content_router.py:323-377](../app/domains/learning/content_router.py#L323) 참조). 카드 쌍마다 앞/뒤 이미지 2장씩.
- **Stage 3 문제**: 각 문제마다 `image: "stage3/problem_X.png"` 1장씩, 총 25장. `_load_problems_data` → 응답에 그대로 포함.
- 콘텐츠 1개 추가 = 디자인 작업 + 이미지 파일 업로드 + 경로 수정 + 로더 재실행. **차시·단원이 늘어날수록 비선형적으로 비용 증가**.
- 텍스트만 수정해도 이미지 재생성 필요 → 운영 부담.
- AI로 이미지 생성도 가능하지만 한 장당 수십 초~분, 일관된 화풍 유지도 어려움.

#### 7.3.2 재설계 방향
백엔드는 **콘텐츠의 의미 데이터와 시각 힌트 키만** 제공하고, 프론트가 디자인 시스템(컴포넌트, 디자인 토큰, 아이콘 라이브러리)으로 시각 표현을 책임진다. 이미지 파일을 더 만들지 않는다.

즉 재단장 후 학생 학습 API는 PNG/JPG 파일 경로나 `/learning/images/...` URL을 넘기지 않는다. 백엔드는 `visual_hint`, `icon`, `accent_color` 같은 키만 내려주고, 프론트가 해당 키를 실제 아이콘·색·일러스트 컴포넌트로 매핑한다.

#### 7.3.3 새 데이터 스키마 (제안)

**Stage 1 카드**:
```python
class CardContent(BaseModel):
    word: str                    # 예: "가르치다"
    meaning: str                 # "지식이나 기술을 알려주다"
    example_sentence: str        # "선생님이 수학을 가르치다."
    pronunciation: str | None    # 발음 힌트 (옵션)
    visual_hint: str | None      # 프론트 아이콘 라이브러리 키 (예: "book", "finger-point")
    color_theme: str | None      # 프론트 디자인 토큰 키 (예: "primary", "warning")
```

**Stage 3 문제** (기존 `image` 필드 제거 → 시각 힌트 메타로 대체):
```python
class Stage3VisualHint(BaseModel):
    icon: str | None             # 아이콘 키 (예: "pencil", "envelope")
    illustration_style: str | None  # 프론트 일러스트 컴포넌트 키 (예: "thinking", "writing")
    accent_color: str | None     # 디자인 토큰 키
```
기존 `card1.front_image`/`back_image`, Stage 3의 `image` 필드는 제거 (또는 마이그레이션 기간 동안 옵션 필드로 공존).

#### 7.3.4 프론트 책임
- `visual_hint`를 프론트 아이콘 라이브러리(Lucide, Phosphor, 자체 디자인 시스템 등) 키로 매핑해 시각화.
- 카드 앞면(단어) ↔ 뒷면(뜻 + 예문) 토글, Stage 3의 상단 일러스트 영역 등은 프론트 컴포넌트가 디자인 토큰으로 렌더링.
- 텍스트만으로도 예쁘게 보이도록 타이포그래피·색채 시스템에 투자 (한 번 만들면 모든 단원·차시에 재사용).

#### 7.3.5 이점
- 콘텐츠 추가: 코드·디자인 수정 없이 DB 1줄 추가로 끝. 단원·차시 확장 비용이 일정해짐.
- 텍스트 수정: 이미지 재생성 불필요.
- 다국어 확장: 텍스트 필드만 번역.
- 프론트 디자인 변경: 백엔드 무관.
- 단원·차시 확장이 데이터 추가만으로 끝남.

#### 7.3.6 비용
- 프론트에 카드/문제 컴포넌트 + 디자인 토큰 시스템·아이콘 매핑 테이블을 한 번 만들어야 함 (1회성).
- 기존 학습한 학생의 진척도 데이터는 영향 없음(콘텐츠 메타데이터만 바뀜).
- 기존 이미지 자산은 마이그레이션 시점에 제거 (재단장 모드이므로 이중 노출·점진 전환 안 함).

---

## 8. 학습 기록과 진척도 데이터 분리

현재 `learning_records`는 학생이 답을 제출할 때마다 쌓이는 **시도 이벤트 로그**에 가깝다. 같은 학생이 같은 문제를 여러 번 풀면 여러 문서가 생기는 것이 정상이다. 이 컬렉션을 "현재 진도 상태"로 직접 쓰면 중복 시도, 복습 시도, 차시 이동이 섞여 해석이 어려워진다.

### 8.1 역할 분리

| 데이터 | 역할 | 예시 |
|---|---|---|
| `learning_records` | 모든 풀이 시도를 시간순으로 보존하는 append-only 로그 | 교사용 타임라인, 약점 집계, 최근 활동 |
| `stage_progress` 또는 `lesson_progress` | 학생의 현재 진척도 상태 | 완료 문제, 복습 큐, 진도율, 연속 정답 |
| `teacher_assignments` | 교사가 배정한 문제 큐와 상태 | draft, assigned, completed, cancelled |

### 8.2 `learning_records` 권장 스키마

```python
class LearningRecord(BaseModel):
    record_id: str
    user_id: str
    class_id: str | None
    unit_id: str | None
    lesson_id: str
    stage: Literal[1, 2, 3]
    problem_key: str              # 예: "stage1:lesson_1:pair_1"
    problem_id: str | int         # lesson 내부 ID. 기존 호환을 위해 보관 가능
    concept_key: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    attempt_no: int               # 같은 user_id + problem_key 기준 N번째 시도
    source: Literal["base", "assignment"]
    assignment_id: str | None
    created_at: datetime
```

### 8.3 인덱스와 조회

- 교사 타임라인: `{user_id: 1, created_at: -1}`
- 약점 집계: `{user_id: 1, concept_key: 1, is_correct: 1, created_at: -1}`
- 문제별 재시도 분석: `{user_id: 1, problem_key: 1, attempt_no: 1}`
- 반 집계가 필요하면 `class_id`를 기록 시점에 denormalize한다. 학생이 나중에 다른 반으로 이동해도 과거 기록의 소속 반을 보존할 수 있다.

### 8.4 설계 원칙

- `learning_records`는 수정하지 않고 계속 쌓는다. 오답을 나중에 정답으로 맞혀도 과거 오답 기록은 남긴다.
- 학생에게 보여줄 진척도는 `learning_records` 원본이 아니라 progress 컬렉션에서 만든 긍정 지표 DTO만 사용한다.
- 교사용 약점 프로파일은 `learning_records`를 집계해 만든다. 같은 문제를 반복해서 틀린 것을 약점으로 볼지, 문제별 최신 시도만 볼지는 서비스 정책으로 분리한다.
- 기존 `temp_user_id`는 레거시 호환 필드로만 유지하고, 재단장 이후 신규 기록에서는 사용하지 않는다.

---

## 9. 데이터 모델 변경 요약

| 변경 | 종류 | 우선순위 |
|---|---|---|
| `User.role` Literal을 `"student" | "teacher" | "developer"`로 정리 (`"admin"` → `"developer"` 마이그레이션) | 스키마 확장 | Phase 0 |
| `Class` 컬렉션 신설 (`class_id, name, teacher_id, student_ids[], created_at, updated_at`) | 신규 컬렉션 | Phase 1 |
| `whitelist.py`에 `TEACHER_WHITELIST_EMAILS`, `DEVELOPER_WHITELIST_EMAILS`, `ANSWER_BYPASS_WHITELIST_EMAILS` 추가 | 상수 | Phase 0 |
| `units` / `lessons` 컬렉션 신설 — 단원·차시 계층 명시화 (`unit_id`, `lesson_id` 도입) | 신규 컬렉션 | Phase 1 |
| 기존 `stage1_cards`/`stage2_problems`/`stage3_problems`를 차시별 도큐먼트로 재구성 | 파괴적 변경 | Phase 1 |
| `stage_progress`/`lesson_progress`를 `user_id + lesson_id` 기준으로 재설계 | 파괴적 변경 | Phase 1 |
| `learning_records`에 `unit_id`, `lesson_id`, `problem_key`, `attempt_no`, `source`, `assignment_id` 추가 | 스키마 확장 | Phase 1 |
| Stage 1 `card1.front_image`/`back_image` 제거, `CardContent` 스키마로 교체 | **파괴적 변경** (로더 + 라우터 + 프론트 동시 작업) | Phase 1 또는 별도 트랙 |
| Stage 3 problem의 `image` 필드 제거, `Stage3VisualHint`로 교체 | **파괴적 변경** | Phase 1 또는 별도 트랙 |
| `teacher_assignments` 컬렉션 신설 (`assignment_id, teacher_id, student_id, concept_key, problems[], status, created_at`) | 신규 컬렉션 | Phase 2 |
| Stage 3 `get_next_problem`이 `teacher_assignments` 큐를 우선 조회 | 로직 확장 | Phase 2 |

---

## 10. 백엔드 도메인 재정렬 (DDD + 페르소나 분리)

해커톤 이후 재단장이므로 도메인(비즈니스 개념)을 최상위 기준으로 삼고, 각 도메인 안에 `controller / service / repository / domain model / dto`를 모은다. 페르소나는 별도 최상위 패키지로 분리하지 않고, 각 도메인의 `controller` 안에서 라우터 prefix와 DTO로 표현한다.

### 10.1 원칙
- **도메인은 페르소나가 아니라 비즈니스 개념을 기준으로 나눈다.** `learning`이라는 한 도메인을 학생(쓰기)·교사(읽기)·개발자(집계)가 다른 권한·DTO로 접근한다. 도메인을 페르소나별로 복제하지 않는다.
- **HTTP controller도 해당 도메인 안에 둔다.** Java/Spring식 패키징처럼 `domains/learning/controller/*`, `domains/classroom/controller/*`에 라우터와 controller DTO를 배치한다.
- **페르소나는 controller의 라우터 prefix로 표현한다.** `/student/*`, `/teacher/*`, `/admin/*`은 도메인이 아니라 외부 API prefix다.
- **Repository 인터페이스 분리**로 도메인 서비스가 DB 구현에 직접 의존하지 않게 한다 (DIP). 테스트 가능성·인프라 교체 자유도 확보.
- **페르소나별 응답 DTO 분리**로 같은 도메인 엔티티라도 노출 필드를 다르게 한다 (ISP). 학생 응답에 `wrong_count`가 아예 없으면 클라이언트가 그 필드에 접근할 길이 없음 → 사고 방지.

### 10.2 새 디렉토리 구조

```
app/
  domains/
    auth/
      controller/
      domain/
      repository/
      service/

    learning/
      controller/
        content_catalog_router.py
        student_learning_router.py
        student_records_router.py
        student_progress_router.py
        student_stage3_router.py
        dto/
      domain/
      content/
      stages/
      repository/
      service/

    classroom/
      controller/
        teacher_classroom_router.py
        teacher_student_view_router.py
        dto/
      domain/
      repository/
      service/

    instruction/                    # 교사 assignment, 맞춤 문제 생성 (Phase 2)
    agent/                          # 이로 챗봇, 약점 분석
    system/                         # 시드, 인덱싱, 운영

  main.py
```

### 10.3 도메인 내부 구조 (예: `learning`)

```
domains/learning/
  controller/
    student_learning_router.py
    student_stage3_router.py
    student_records_router.py
    student_progress_router.py
    content_catalog_router.py
    dto/
      request.py
      response.py

  models.py            # 엔티티: LearningRecord, StageProblem 등 (Pydantic 도메인 모델)
  repositories/
    base.py            # LearningRecordRepository 인터페이스 (Protocol 또는 ABC)
    mongo.py           # MongoDB 구현
  services/
    record_service.py        # 학습기록 CRUD·약점 집계
    answer_service.py        # 답 채점·정답 판정
  schemas/
    common.py          # 공유 DTO
    student.py         # 학생용 응답 (긍정 지표만)
    teacher.py         # 교사용 응답 (raw counts 포함)
```

### 10.4 prefix 매핑

| prefix | 페르소나 | 호출하는 도메인 |
|---|---|---|
| `/auth/*` | 모두 | `auth` |
| `/student/learning/*` | 학생 | `learning` |
| `/student/agent/*` | 학생 | `agent` |
| `/student/me/progress` | 학생 | `learning`(긍정 지표 DTO) |
| `/teacher/classes/*` | 선생님 | `classroom` |
| `/teacher/students/*` | 선생님 | `classroom`(권한 검증) + `learning`(데이터) |
| `/teacher/instruction/*` | 선생님 | `instruction` + `agent` (Phase 2) |
| `/admin/*` | 개발자 | `system` |

기존 `/learning/*`, `/agent/*`, `/learning/stage3/*` 는 `/student/...`로 통합 리네임 (재단장이므로 호환성 부담 없음).

### 10.5 SOLID 매핑 요약

| 원칙 | 적용 |
|---|---|
| **SRP** | Router=HTTP·인증만, Service=도메인 로직, Repository=DB. 현 `Stage3Service`가 DB·로직·응답 조립을 다 하는데 분해 대상. |
| **OCP** | 새 페르소나 view 추가 = 해당 도메인의 `controller/*_router.py`와 DTO 추가. 도메인 서비스의 핵심 정책은 유지. |
| **LSP** | Repository 인터페이스에 대해 MongoDB 구현·인메모리 fake 구현이 치환 가능. 테스트에서 fake로 갈아끼움. |
| **ISP** | 페르소나별 DTO 분리로 노출 필드 차등. 응답 모델로 강제. |
| **DIP** | Router → 서비스 abstraction → repository abstraction. 모두 FastAPI `Depends`로 주입. |

### 10.6 도입할 디자인 패턴 (적정선)
- **Repository**: 모든 도메인에 적용. 인터페이스(Protocol) + Mongo 구현 분리.
- **DTO (Pydantic schemas)**: 페르소나별로 응답 모델 분리. 단순 응답은 공통 모델 공유 가능 (과적용 금지).
- **Application/Use Case service**: 라우터가 여러 도메인을 조합할 때만(예: `TeacherStudentViewUseCase`가 `classroom`+`learning` 호출). 단순 단일 도메인 호출은 라우터에서 직접.
- **Dependency Injection**: FastAPI `Depends` 활용 (이미 사용 중).

### 10.7 도입하지 않을 것
- CQRS, Event Sourcing — 데이터 흐름 규모에 맞지 않음.
- 도메인 이벤트 버스 — 동기 직접 호출로 충분.
- 모든 응답에 페르소나별 DTO 강제 — 공통으로 OK인 응답까지 분리하면 보일러플레이트만 늘어남.

---

## 11. 로드맵

선후 의존 관계 중심. 일정은 명시하지 않는다 (재단장 모드).

### Phase 0 — 도메인 재정렬 (구조 베이스)
**목표**: 후속 Phase가 올라탈 깨끗한 도메인 중심 패키지 구조를 만든다. 각 도메인 안에 controller/service/repository/model/dto를 모으고, 외부 API prefix는 controller에서 관리한다.

| 작업 | 영역 |
|---|---|
| `User.role` Literal 확장 및 `"admin"` → `"developer"` 정규화 | 백엔드 |
| `whitelist.py`에 `TEACHER_WHITELIST_EMAILS`/`DEVELOPER_WHITELIST_EMAILS`/`ANSWER_BYPASS_WHITELIST_EMAILS` 추가 | 백엔드 |
| `shared/dependencies.py`에 `get_current_student|teacher|developer` 추가 | 백엔드 |
| `domains/stage3`를 `domains/learning`에 흡수 (`controller/student_stage3_router.py`, `stages/stage3_service.py`, `stages/stage3_schemas.py`) | 백엔드 |
| 핵심 도메인부터 `repositories/base.py` + Mongo 구현 분리 (`learning`, `classroom`) | 백엔드 |
| 학생/교사용 DTO 분리 (`schemas/student.py`, `schemas/teacher.py`) — 우선 progress/profile 응답부터 | 백엔드 |
| `domains/admin` → `domains/system` 리네임 | 백엔드 |

### Phase 0.5 — 페르소나 API Prefix 전환
**목표**: 내부 정리가 끝난 뒤 외부 API 경로를 페르소나 기준으로 바꾼다. 프론트 API 클라이언트와 동시에 진행한다.

| 작업 | 영역 |
|---|---|
| 도메인 내부 `controller/` 디렉토리에 학생/교사/개발자 라우터 배치 | 백엔드 |
| `/learning/*`, `/agent/*`, `/learning/stage3/*` → `/student/...` 경로 전환 | 백엔드/프론트 |
| `/student/me/progress` 신설, 학생의 `/agent/profile/me` 접근 제거 | 백엔드/프론트 |
| `/admin/*`에 `get_current_developer` 적용 | 백엔드 |

### Phase 1 — 교사 읽기 전용 대시보드 + 콘텐츠 데이터화
**목표**: 교사가 자기 반 학생들의 약점을 한눈에 본다. 단원·차시 모델 도입. Stage 1·3 이미지 의존 제거.

선행: Phase 0.5.

| 작업 | 영역 |
|---|---|
| `classroom` 도메인: `Class` 모델, `units`/`lessons` 컬렉션, 시드(교사 1명, 반 1개, 더미 학생 몇 명) | 백엔드 |
| `learning` 도메인: stage 데이터를 차시별 도큐먼트로 재구성, 단원·차시 트리 조회 API | 백엔드 |
| `learning_records` 스키마 확장 및 신규 기록부터 `lesson_id`/`problem_key` 저장 | 백엔드 |
| `stage_progress`/`lesson_progress`를 `user_id + lesson_id` 기준으로 재설계 | 백엔드 |
| `GET /teacher/classes`, `GET /teacher/classes/{id}/students`, `GET /teacher/students/{user_id}/profile`, `GET /teacher/students/{user_id}/records` | 백엔드 |
| `get_current_teacher` + 본인 반 검증 가드 | 백엔드 |
| Stage 1 `CardContent` 스키마, Stage 3 `Stage3VisualHint` 스키마 도입, 로더 재작성, 이미지 자산 제거 | 백엔드 |
| `/teacher/dashboard`, `/teacher/students/:userId` 페이지 | 프론트 |
| 카드·문제 컴포넌트(디자인 시스템 기반) + `visual_hint` 아이콘 매핑 | 프론트 |
| 단원·차시 네비게이션 UI | 프론트 |

### Phase 2 — AI 맞춤 문제 생성·배정
**목표**: 교사가 약점 1개 지목하면 LLM이 새 문제를 만들어 학생 큐에 꽂는다.

선행: Phase 1.

| 작업 | 영역 |
|---|---|
| `instruction` 도메인: `teacher_assignments` 모델·repository·service | 백엔드 |
| LLM 문제 생성 프롬프트 설계·검증 (gpt-4o, JSON 스키마 응답) | 백엔드 |
| 생성 문제를 `draft`로 저장하고 교사 승인 시 `assigned`로 전환 | 백엔드 |
| `POST /teacher/instruction/generate-problems` (단일 학생/반 일괄) | 백엔드 |
| `learning` 도메인의 `get_next_problem`이 `instruction` 도메인의 큐를 우선 조회하도록 확장 | 백엔드 |
| 교사 페이지에 "문제 생성" UI, 생성 결과 미리보기·승인 | 프론트 |
| 학생 화면에 "선생님이 내준 문제" 뱃지·우선 노출 | 프론트 |

### Phase 3 — 운영 도구·분석
**목표**: 운영 가시성·교사 개입 도구.

선행: Phase 2.

- `system` 도메인에 트레이스 로그 조회, 사용량 통계, 에이전트 호출 모니터링 추가
- 반 전체 약점 트렌드 차트
- 교사 → 학생 메시지/격려

---

## 12. 2026-05-24 작업 기록 및 다음 작업

### 12.1 오늘 정리한 방향

- 최상위 `interfaces/` 분리 방식은 중단하고, Java/Spring식에 가까운 **도메인 내부 패키징**으로 방향을 확정했다.
- HTTP 라우터는 각 도메인의 `controller/` 아래에 둔다.
- 도메인은 비즈니스 개념 기준으로 유지한다: `auth`, `learning`, `classroom`, `agent`, `rag`, `system`.
- 페르소나는 도메인을 나누는 기준이 아니라 controller prefix와 DTO 노출 정책으로 표현한다.

### 12.2 오늘 완료한 백엔드 작업

- 역할 모델을 `student | teacher | developer`로 정리하고, 기존 `admin`은 `developer`로 정규화했다.
- whitelist를 권한용(`TEACHER`, `DEVELOPER`)과 Stage 2 답안 우회용(`ANSWER_BYPASS`)으로 분리했다.
- `domains/admin`을 `domains/system`으로 정리하고 `/admin/*`는 developer 권한으로 보호했다.
- Stage 3를 `learning` 도메인으로 흡수하고, 현재는 `domains/learning/stages/` 아래에 배치했다.
- 학생용 `GET /student/me/progress`를 추가하고, 학생의 `/agent/profile/me` 접근은 차단했다.
- `classroom` 도메인을 추가해 `classes` 컬렉션 기반 교사-학생 매핑을 표현했다.
- 교사용 읽기 API를 추가했다:
  - `GET /teacher/classes`
  - `GET /teacher/classes/{class_id}/students`
  - `GET /teacher/students/{user_id}/profile`
  - `GET /teacher/students/{user_id}/records`
- `units` / `lessons` 콘텐츠 계층과 조회 API를 추가했다.
- `learning_records` 신규 기록에 `unit_id`, `lesson_id`, `problem_key`, `problem_id`, `attempt_no`, `source`, `assignment_id`, `class_id`를 저장하도록 확장했다.
- Stage 1/3의 이미지 파일 의존을 제거하고 `visual_hint`, `color_theme`, `accent_color` 기반 응답으로 바꿨다.
- `/images` static mount와 `/learning/images/{filename}` 이미지 서빙 엔드포인트를 제거했다.
- 학생 학습 API prefix를 `/student/learning/*`로 전환했다.
- 테스트 파일을 도메인별 디렉토리로 재구성했다:
  - `tests/auth`
  - `tests/learning`
  - `tests/classroom`
  - `tests/agent`
  - `tests/rag`
  - `tests/system`
  - `tests/structure`
  - `tests/integration`

### 12.3 현재 주요 디렉토리 기준

```text
app/domains/learning/
  controller/
  content/
  stages/
  repositories/
  models.py
  schemas.py
  service.py

app/domains/classroom/
  controller/
    dto/
  repositories/
  models.py
  service.py

tests/
  agent/
  auth/
  chat/
  classroom/
  integration/
  learning/
  rag/
  structure/
  system/
```

### 12.4 검증 상태

- 도메인/라우터/서비스 중심 targeted suite: `52 passed`
- 라우트 prefix 확인: `/student/learning/*` 등록, 기존 `/learning/stage*` 미등록 확인
- 2026-05-25 재개 직후 확인: 프로젝트 venv 기준 `venv/bin/pytest -q` 전체 통과
  - `69 passed, 3 skipped`
  - 직전 기록의 `langgraph` 미설치/async 플러그인 이슈는 시스템 Python으로 실행했을 때의 환경 문제였고, `venv`에는 `langgraph`, `pytest-asyncio`가 설치되어 있다.
- 2026-05-25 이어서 작업 후 확인: `venv/bin/pytest -q`
  - `83 passed, 3 skipped`

### 12.5 다음에 이어서 할 작업

1. **현재 변경분을 의미 단위로 커밋**
   - 2026-05-25 재개 직후 기준 워킹트리가 clean이었으므로, 2026-05-24 작업분 커밋 항목은 완료된 것으로 본다.
   - 2026-05-25 이어서 작업한 `lesson_id`/Stage 3 progress/classes seed 변경분은 별도 커밋 대상으로 남아 있다.
   - 권장 커밋:
     - `refactor: 도메인 내부 controller 구조로 라우터 재배치`
     - `test: 테스트 파일을 도메인별 디렉토리로 재구성`
     - `refactor(learning): 이미지 파일 의존 제거 및 콘텐츠 구조 정리`

2. **남은 루트 파일 정리**
   - `domains/learning/service.py`를 `domains/learning/service/record_service.py`로 이동할지 결정
   - `domains/learning/schemas.py`, `student_schemas.py`를 controller DTO와 domain schema로 분리
   - `domains/learning/models.py`를 `domain/models.py`로 옮길지 결정
   - `classroom/models.py`, `classroom/service.py`도 Java식 구조에 맞춰 `domain/`, `service/` 하위로 정리할지 결정

3. **콘텐츠 데이터 구조 Phase 1 마무리**
   - Stage 1/2/3 데이터를 실제 `lesson_id` 기준 도큐먼트로 재구성
     - 완료(2026-05-25): Stage 2 로더는 `stage2_lesson_1`~`stage2_lesson_5` 도큐먼트를 삽입한다.
     - 완료(2026-05-25): Stage 3 로더는 `stage3_lesson_1`~`stage3_lesson_5` 도큐먼트를 삽입한다.
     - 완료(2026-05-25): Stage 3 서비스는 차시별 도큐먼트를 우선 조회하고, 기존 전역 `stage3_problems` 도큐먼트만 남은 환경에서는 lesson 범위로 잘라 fallback한다.
   - `lesson_1` 등 신규 lesson id와 기존 `lesson1` 호환 정리
     - 완료(2026-05-25): Stage 2 로더/API는 `lesson_1` 기준으로 전환했고, 기존 MongoDB에 `lesson1` 데이터가 남아 있어도 fallback 조회한다.
     - 완료(2026-05-25): RAG용 `korean_word_problems` 로더의 생성 ID도 `lesson_1_q1` 형태로 정규화했다.
   - `stage3_progress`를 `user_id + lesson_id` 기준으로 재설계
     - 완료(2026-05-25): `stage3_progress` 문서에 `lesson_id`를 저장하고, 조회/초기화/다음 문제/답안 제출을 `{user_id, lesson_id}` 기준으로 처리한다.
     - 완료(2026-05-25): 기존 `lesson_id` 없는 progress 문서는 기본 `lesson_1`으로 읽을 수 있도록 migration fallback을 두고, 전역 25문제 기준 데이터가 진도율을 왜곡하지 않도록 lesson 범위 문제만 남겨 정규화한다.
   - `lesson_progress` 또는 `stage_progress` 컬렉션 설계 확정
     - 결정(2026-05-25): 이번 단계에서는 새 컬렉션을 만들지 않고 기존 `stage3_progress`를 유지한다. 단, 스키마 키를 `{user_id, lesson_id}`로 확장해 향후 `lesson_progress` 통합이 필요할 때 migration 가능하게 둔다.

4. **교사/학생 데이터 연결 보강**
   - `classes` 시드 로더 추가
     - 완료(2026-05-25): `app/data/data_loader/classroom_loader.py` 추가. 기존 `classes` 데이터가 없을 때만 기본 반 매핑을 삽입하도록 비파괴적으로 동작한다.
     - 완료(2026-05-25): `InitializationService.seed_mongo_collections()`에서 `classes` 시드도 함께 수행한다.
   - 테스트용 교사 1명, 반 1개, 학생 몇 명을 초기 데이터로 넣을지 결정
     - 부분 완료(2026-05-25): 반 매핑은 `teacher_demo_1`, `student_demo_1..3` 기준으로 넣었다. 실제 `users` 계정 시드는 인증/비밀번호 정책과 연결되므로 아직 생성하지 않는다.
   - `learning_records.class_id`를 기록 시점에 실제 class에서 denormalize할지 구현
     - 완료(2026-05-25): `LearningRecordService`가 classroom repository를 선택 의존성으로 받아, 명시적 `class_id`가 없으면 학생이 속한 class를 찾아 `learning_records.class_id`에 저장한다.
     - 완료(2026-05-25): 명시적으로 전달된 `class_id`는 classroom lookup보다 우선한다.

5. **Agent 테스트 환경 이슈 해결**
   - 완료(2026-05-25): 프로젝트 venv 기준 `langgraph`, `pytest-asyncio`가 설치되어 있고 전체 테스트가 green이다.
   - 주의: 시스템 Python의 `pytest`가 아니라 `venv/bin/pytest`로 실행해야 한다.

6. **Phase 2 준비**
   - `instruction` 도메인 신설
   - `teacher_assignments` 모델/repository/service 설계
   - LLM 문제 생성 API는 `draft -> assigned -> completed/cancelled` 흐름으로 구현

---

## 13. 합의가 필요한 것

이 문서를 코드 작업으로 옮기기 전에 결정할 항목:

### 13.1 명명·경로
1. **`role` 이름**: `"admin"`을 `"developer"`로 리네임한다.
2. **`domains/admin` 폴더명**: `system`으로 리네임한다.
3. **인터페이스 prefix**: Phase 0.5에서 `/student/learning/*` 식으로 페르소나 prefix를 강제한다.

### 13.2 도메인 분리 깊이
4. **Repository 인터페이스 분리**: 우선 `learning`, `classroom`, `instruction` 핵심 도메인에 적용한다. 단순 system 작업은 과도하게 분리하지 않는다.
5. **controller 배치 방식**: 최상위 `interfaces/`는 두지 않고, 각 도메인 내부 `controller/`에 라우터를 둔다.
6. **Use Case 서비스 도입 여부**: `/teacher/students/{id}/profile`처럼 다중 도메인 조합 엔드포인트에는 use case 레이어를 둔다. 단순 단일 도메인 호출은 라우터에서 직접 서비스를 호출한다.

### 13.3 페르소나·콘텐츠
7. **학생용 진척도 응답 분리**: 새 엔드포인트 `GET /student/me/progress`를 추가한다. 기존 `/agent/profile/me`는 학생에게 제공하지 않는다.
8. **콘텐츠 구조**: stage 데이터는 차시별 도큐먼트로 쪼갠다. 전역 식별이 필요하면 `problem_key`를 사용한다.
9. **AI 생성 문제**: `draft` → 교사 승인 → `assigned` 흐름으로 간다.
10. **교사 계정 부트스트랩**: 화이트리스트 + 수동 반 시드만으로 시작 vs 교사 회원가입·반 생성 UI까지 Phase 1에 포함.
11. **신규 단원 콘텐츠**: 추가할 단원 수·주제 (별도 콘텐츠 기획 필요, 코드 작업과 병렬 진행 가능).

각 항목에 대해 결정되면 이 문서를 갱신하고 구현 PR로 진입한다.
