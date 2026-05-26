# 페르소나 기반 UI 플로우

> 최종 업데이트: 2026-05-25  
> 관련 문서: [페르소나 기반 재설계 기획안](./persona-based-redesign.md), [API 명세](./api-spec.md)

이 문서는 페르소나 기반 재설계 이후 프론트엔드가 가져야 할 화면 구조와 사용자 흐름만 정리한다. 핵심 전제는 **학생은 학습 경험 중심**, **선생님은 AI 수업 준비/배정 중심**, **개발자는 운영 관리 중심**이다.

---

## 1. 전체 IA

```text
로그인
 ├─ 학생
 │   └─ /student
 │       ├─ 오늘의 학습
 │       ├─ 단원/차시 선택
 │       ├─ Stage 1 카드 학습
 │       ├─ Stage 2 예제 풀이
 │       ├─ Stage 3 직접 입력 문제
 │       ├─ 선생님이 준비한 복습
 │       ├─ 이로에게 물어보기
 │       └─ 내 진척도
 │
 ├─ 선생님
 │   └─ /teacher
 │       ├─ AI 수업 준비
 │       │   ├─ 반 분석
 │       │   ├─ 학생별 약점 확인
 │       │   ├─ AI 문제 생성
 │       │   ├─ 초안 검토/수정
 │       │   └─ 배정 관리
 │       ├─ 내 반
 │       ├─ 학생 기록
 │       └─ 콘텐츠 미리보기
 │
 └─ 개발자
     └─ /admin
         ├─ 시스템 상태
         ├─ 시드 데이터 적재
         ├─ 벡터 인덱싱
         ├─ BM25 재구축
         └─ 가상 질문 생성
```

---

## 2. 공통 진입 흐름

```text
/login
 ├─ access token 발급
 ├─ /auth/me로 role 확인
 └─ role별 홈으로 이동
     ├─ student   -> /student
     ├─ teacher   -> /teacher
     └─ developer -> /admin
```

역할별 홈은 서로 다른 목적을 가진다.

| 역할 | 첫 화면 목표 |
|---|---|
| 학생 | 바로 오늘 풀 학습으로 들어간다. |
| 선생님 | 오늘 어떤 학생에게 어떤 복습을 줄지 판단한다. |
| 개발자 | 시스템 데이터와 인덱싱 상태를 점검한다. |

---

## 3. 학생 UI 플로우

학생 UI는 약점/오답 횟수 같은 정량 진단을 직접 보여주지 않는다. 대신 진행률, 오늘 푼 문제 수, 연속 정답, 뱃지처럼 긍정 지표만 보여준다.

### 3.1 학생 홈

```text
/student

오늘의 학습
 ├─ 이어 풀 차시
 ├─ 진행률
 ├─ 오늘 푼 문제 수
 ├─ 연속 정답
 ├─ 획득 뱃지
 └─ [학습 시작]

선생님이 준비한 복습
 ├─ 배정된 문제가 있으면 노출
 └─ 없으면 숨김 또는 빈 상태
```

사용 API:

```text
GET /student/me/progress
GET /student/learning/assignments
```

### 3.2 단원/차시 선택

```text
/student/learning

1단원 헷갈리는 낱말
 ├─ lesson_1: 가르치다/가르키다, 맞추다/맞히다
 ├─ lesson_2: 잊다/잃다, 메다/매다
 ├─ lesson_3: 바라다/바래다, 부치다/붙이다
 ├─ lesson_4: 되다/돼, 안/않다
 └─ lesson_5: 반드시/반듯이, 이따가/있다가
```

사용 API:

```text
GET /content/units
GET /content/lessons/{lesson_id}
```

### 3.3 차시 학습 흐름

```text
/student/learning/{lesson_id}

Stage 1 카드 학습
 → Stage 2 예제 풀이
 → Stage 3 직접 입력
 → 결과/칭찬
 → 이로에게 질문
```

Stage는 한 화면 안에서 stepper로 표현해도 되고, 라우트를 나눠도 된다.

```text
/student/learning/{lesson_id}/stage-1
/student/learning/{lesson_id}/stage-2
/student/learning/{lesson_id}/stage-3
```

### 3.4 Stage 1 카드 학습

백엔드는 이미지 URL을 내려주지 않는다. 프론트는 `visual_hint`, `color_theme`를 디자인 시스템의 아이콘/색상으로 매핑한다.

```text
┌──────────────┐      flip      ┌────────────────────┐
│ book-open    │   ─────────▶   │ 뜻/예문             │
│ 가르치다     │                │ 지식이나 기술을...   │
└──────────────┘                └────────────────────┘
```

사용 API:

```text
GET  /student/learning/stage1/cards
POST /student/learning/stage1/submit-card-check
```

### 3.5 Stage 2 예제 풀이

```text
선생님이 수학 공식을 [      ] 주셨다.

[가르쳐] [가르켰다] [맞췄다] [맞혀]
```

학생은 보기 카드를 선택하거나 드래그한다. 제출 후 정답 여부와 완성 문장을 보여준다.

사용 API:

```text
GET  /student/learning/stage2/problems?lesson_id=lesson_1
POST /student/learning/stage2/submit-answer?lesson_id=lesson_1
```

### 3.6 Stage 3 직접 입력

```text
차시 1 - Stage 3
문제 2 / 5

선생님이 수학 공식을 [        ] 주셨다.

[제출]
```

사용 API:

```text
GET  /student/learning/stage3/next-problem?lesson_id=lesson_1
POST /student/learning/stage3/submit-answer?lesson_id=lesson_1
GET  /student/learning/stage3/progress?lesson_id=lesson_1
POST /student/learning/stage3/reset-progress?lesson_id=lesson_1
```

### 3.7 선생님이 준비한 복습

학생에게는 “AI가 만든 문제”보다 “선생님이 준비한 복습”으로 보여준다.

```text
오늘 선생님이 준비한 복습
 └─ 되/돼 복습 5문제

[복습 시작]
```

향후 출제 우선순위:

```text
1. assigned 상태의 teacher_assignments 문제 조회
2. 아직 안 푼 배정 문제가 있으면 먼저 출제
3. 없으면 기본 stage3_problems에서 출제
```

### 3.8 이로 챗봇

```text
/student/iro

학생 질문
 ├─ "왜 여기서는 돼예요?"
 └─ "되랑 돼가 헷갈려요"

이로 응답
 ├─ 짧은 설명
 ├─ 예문
 └─ 다시 풀어볼 힌트
```

사용 API:

```text
POST   /agent/chat
GET    /agent/session/{session_id}
DELETE /agent/session/{session_id}
```

---

## 4. 선생님 UI 플로우

선생님 UI는 단순 조회 대시보드가 아니라 **AI 수업 준비 작업대**가 중심이다. 핵심 흐름은 “반/학생 선택 → 약점 확인 → AI 문제 생성 → 초안 검토 → 배정”이다.

### 4.1 선생님 홈

```text
/teacher

AI 수업 준비
 ├─ 오늘 확인할 반
 ├─ 최근 오답이 많은 학생
 ├─ 공통 약점 concept
 └─ [AI로 복습 만들기]

내 반
 └─ 담당 반 목록

최근 배정
 ├─ draft
 ├─ assigned
 └─ completed
```

사용 API:

```text
GET /teacher/classes
GET /teacher/instruction/assignments
```

### 4.2 반 목록

```text
/teacher/classes

┌─────────────────────┐
│ 돌봄 한국어 1반      │
│ 학생 3명             │
│ 최근 활동            │
└─────────────────────┘
```

사용 API:

```text
GET /teacher/classes
```

### 4.3 반 상세

```text
/teacher/classes/{class_id}

┌────────────────────────────────────┐
│ 돌봄 한국어 1반                     │
│ 학생 3명 · 오늘 풀이 · 공통 약점     │
└────────────────────────────────────┘

┌──────────────────────┐ ┌──────────────────────┐
│ AI 반 분석            │ │ 학생 목록              │
│ 공통 약점: 되/돼       │ │ 민준 · 서연 · 지우       │
│ 추천: 복습 문제 생성   │ │ 학생별 약점 요약        │
│ [AI로 문제 만들기]     │ │                      │
└──────────────────────┘ └──────────────────────┘
```

사용 API:

```text
GET /teacher/classes/{class_id}/students
```

### 4.4 학생 상세

```text
/teacher/students/{user_id}

약점 프로파일
 ├─ 되/돼: 오답 4회
 ├─ 안/않다: 오답 3회
 └─ 맞추다/맞히다: 오답 2회

학습 기록 타임라인
 ├─ Stage 3 lesson_4 문제 16 오답
 ├─ Stage 2 lesson_4 문제 13 정답
 └─ ...

[AI로 맞춤 문제 만들기]
```

사용 API:

```text
GET /teacher/students/{user_id}/profile
GET /teacher/students/{user_id}/records?stage=3&limit=50
```

### 4.5 AI 문제 생성

```text
/teacher/instruction/generate

대상
[반 전체] [특정 학생]

선택된 대상
돌봄 한국어 1반 / 민준

AI 분석
이 학생은 '되/돼'와 '안/않다'에서 오답이 반복됩니다.
짧은 직접 입력 문제 5개를 추천합니다.

생성 조건
개념: 되/돼
문제 수: 5
난이도: 쉬움
문제 유형: 빈칸 직접 입력

[AI 문제 생성]
```

사용 API:

```text
POST /teacher/instruction/generate-problems
```

응답에는 draft assignment와 문제별 검증 결과가 함께 온다. 프론트는 `validation_results`에서 실패 사유가 있는 문제를 교사에게 보여주고, `assignment.problems`의 검증 통과 문제를 초안 검토 화면에 렌더링한다.

### 4.6 초안 검토/수정

```text
AI가 만든 문제 초안

1. 숙제가 다 [      ]?
정답: 됐어
설명: '됐어'는 '되었어'의 줄임말이에요.
[수정] [삭제]

검증 결과
 - concept_key 일치
 - 정답/빈칸 일치
 - 기존 문제와 중복 없음
 - 학생용 설명 길이 적절

[초안 저장] [학생에게 배정]
```

사용 API:

```text
POST  /teacher/instruction/assignments/draft
PATCH /teacher/instruction/assignments/{assignment_id}/assign
```

### 4.7 배정 관리

```text
/teacher/instruction/assignments

필터
[전체] [초안] [배정됨] [완료] [취소]

배정 목록
 ├─ 민준 · 되/돼 · draft
 ├─ 돌봄 한국어 1반 · 안/않다 · assigned
 └─ 서연 · 맞추다/맞히다 · completed
```

사용 API:

```text
GET   /teacher/instruction/assignments?status=draft
PATCH /teacher/instruction/assignments/{assignment_id}/assign
PATCH /teacher/instruction/assignments/{assignment_id}/cancel
PATCH /teacher/instruction/assignments/{assignment_id}/complete
```

상태 흐름:

```text
draft -> assigned -> completed
draft -> cancelled
assigned -> cancelled
```

---

## 5. 개발자 UI 플로우

개발자 UI는 학생/교사 워크플로우와 분리된 운영 도구다.

```text
/admin
 ├─ 시스템 상태
 ├─ Mongo seed 적재
 ├─ Chroma vector index 재구축
 ├─ BM25 재구축
 └─ 가상 질문 생성
```

사용 API:

```text
GET  /admin/system-status
POST /admin/initialize-all
POST /admin/seed-data
POST /admin/rebuild-vector-index
POST /admin/rebuild-bm25
POST /admin/build-hypothetical-questions
POST /admin/indexing/pdf
GET  /admin/indexing/status
```

운영 화면에서는 실행 버튼마다 확인 모달과 실행 결과 로그를 보여준다. 특히 `initialize-all`, `rebuild-vector-index`, `build-hypothetical-questions`는 비용과 시간이 들 수 있으므로 실수 클릭을 막아야 한다.

---

## 6. 프론트엔드 구현 우선순위

1. 학생 기본 학습 UI
   - 단원/차시 선택
   - Stage 1/2/3
   - 학생 긍정 진척도

2. 선생님 읽기 전용 대시보드
   - 내 반
   - 학생 목록
   - 학생 약점/기록

3. 선생님 AI 수업 준비
   - AI 분석 패널
   - 문제 생성 화면
   - 초안 검토/수정
   - 배정 관리

4. 개발자 운영 화면
   - 시스템 상태
   - seed/indexing 관리
