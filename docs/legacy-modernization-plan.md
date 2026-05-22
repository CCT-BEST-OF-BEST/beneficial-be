# 레거시 재단장 계획

> 작성일: 2026-05-22  
> 목적: 해커톤 당시 빠르게 만든 백엔드를 AI Agent/RAG 연구용 프로젝트로 재정비한다.

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

## 2. 현재 문제

### 2-1. 도메인 경계가 흐림

현재 파일 구조는 겉으로는 나뉘어 있지만 실제 책임은 섞여 있다.

```text
app/api              # router와 일부 비즈니스 로직
app/data             # 모델, seed loader, 정적 데이터 로딩 혼재
app/infrastructure  # DB, OpenAI, embedding, search
app/common          # dependency/init/logging
app/legacy          # 사실상 죽은 RAG 코드
```

문제:
- `learning_service.py`와 `stage3_service.py`가 서로 다른 방식으로 진행도를 관리한다.
- `temp_user_id`, `stage3_progress`, `UserProgress`가 하나의 사용자 상태로 연결되지 않는다.
- MongoDB 접근이 서비스 내부에서 직접 일어난다.
- 앱 시작 시 seed, vector indexing, BM25, 가상 질문 생성이 한꺼번에 실행된다.
- 테스트가 현재 코드와 맞지 않아 수집 단계에서 실패한다.

### 2-2. Agent 개발을 막는 부분

Agent가 필요로 하는 핵심 데이터는 아래다.

```text
누가(user_id)
무엇을(concept_key)
언제(created_at)
어떻게 틀렸는지(user_answer, correct_answer)
최근 어떤 대화를 했는지(chat session)
현재 어떤 도움을 줘야 하는지(agent decision)
```

현재 레거시는 이 데이터를 안정적으로 제공하지 못한다. 그래서 Agent 구현보다 먼저 사용자/학습기록/세션 도메인을 정리해야 한다.

---

## 3. 목표 구조

최종적으로는 아래에 가깝게 정리한다.

```text
app/
  main.py
  core/
    config.py
    security.py
    logging.py
    dependencies.py
  domains/
    auth/
      models.py
      schemas.py
      repository.py
      service.py
      router.py
    learning/
      models.py
      schemas.py
      repository.py
      service.py
      router.py
    agent/
      models.py
      schemas.py
      service.py
      graph.py
      router.py
    rag/
      schemas.py
      retriever.py
      service.py
      router.py
  infrastructure/
    db/
      mongo.py
      vector.py
    ai/
      openai_client.py
      embedding.py
    search/
      bm25.py
      hybrid.py
  data/
    loaders/
    seeds/
```

단, 이 구조로 바로 옮기지 않는다. 새 도메인을 만들 때부터 이 구조를 따른다.

현재 적용 상태:
- `app/core` 패키지 골격 추가
- `app/domains/auth` 패키지 골격 추가
- `app/domains/auth` 인증 MVP 구현 (`/auth/signup`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`)
- `app/domains/learning` 패키지 골격 추가
- `app/domains/learning` 학습 기록 MVP 구현 (`LearningRecord`, `concept_key`, 약점 프로파일 집계)
- `app/domains/agent` 패키지 골격 추가
- `app/domains/rag` 패키지 골격 추가
- `app/domains/rag` RAG tool MVP 구현 (`RagRetriever`, `RagService`)
- 기존 `app/api`, `app/data`, `app/infrastructure` 코드는 아직 이동하지 않음

---

## 4. 재단장 순서

### Phase 0. 기준선 세우기

목표: 현재 프로젝트가 어디까지 깨져 있는지 명확히 한다.

작업:
- `pytest` 수집 실패 해결
- 누락 dependency 정리
- 죽은 레거시 테스트 격리 또는 삭제
- `.env.example` 추가
- README에 현재 실행 조건 정리

완료 기준:
- 최소한 `pytest`가 수집 단계에서 실패하지 않는다.
- 외부 API가 필요한 테스트는 명시적으로 skip 된다.
- 로컬 실행에 필요한 환경 변수가 문서화된다.

우선 처리할 파일:
- `requirements.txt`
- `tests/connection/openai_test.py`
- `tests/test_rag_system.py`
- `app/legacy/rag_service.py`

### Phase 1. 인증 도메인 추가

목표: `temp_user_id` 중심 구조에서 `user_id` 중심 구조로 넘어갈 기반을 만든다.

작업:
- `auth` 도메인 추가
- `User`, `RefreshTokenSession` 모델 추가
- access/refresh token 발급
- 현재 사용자 조회 dependency 추가
- refresh token rotation 구현

새 API:

| Method | Path |
|---|---|
| `POST` | `/auth/signup` |
| `POST` | `/auth/login` |
| `POST` | `/auth/refresh` |
| `POST` | `/auth/logout` |
| `GET` | `/auth/me` |

완료 기준:
- 로그인한 사용자의 `user_id`를 API dependency에서 얻을 수 있다.
- 기존 학습 API를 아직 건드리지 않아도 된다.

### Phase 2. 학습 기록 도메인 정리

목표: Agent가 사용할 수 있는 학습 이력을 만든다.

작업:
- `LearningRecord`를 `user_id`, `concept_key`, `user_answer`, `correct_answer` 중심으로 정리
- Stage 3 진행도에 `user_id` 추가
- `stage3_progress` 단일 문서 구조 제거
- `WeaknessProfileService` 추가
- 기존 Stage 1/2/3 API는 유지하되 내부 저장 방식을 정리

완료 기준:
- 같은 사용자가 푼 문제만 해당 사용자의 기록으로 집계된다.
- `GET /agent/profile/me`를 만들 수 있을 정도로 약점 집계가 가능하다.

### Phase 3. RAG를 도구화

목표: RAG를 독립 채팅 기능이 아니라 Agent가 호출하는 tool로 만든다.

작업:
- 기존 `ChatService`에서 RAG 검색/응답 생성을 분리
- `RagRetriever`와 `RagAnswerService`로 역할 분리
- `HybridSearchService`는 유지하되 정책 정리
- `/chat`은 legacy-compatible endpoint로 유지

정리할 정책:
- 검색 대상 컬렉션 우선순위
- top_k 기본값
- 유사도/거리 threshold
- BM25 단독 후보 허용 여부
- PDF context가 너무 쉽게 상위로 올라오는 문제

완료 기준:
- Agent 서비스가 `rag_tool.search(query, user_context)` 형태로 호출할 수 있다.
- 기존 `/chat`도 새 RAG service를 사용한다.

### Phase 4. Agent MVP 추가

목표: LangGraph 전이라도 Agent의 판단 모델을 먼저 만든다.

작업:
- `AgentDecision` 모델 추가
- `ChatSessionService` 추가
- `/agent/chat` 추가
- 질문이면 RAG 사용
- 질문이 아니고 약점 개입 조건이면 proactive hint 생성
- 모든 turn 저장

초기 흐름:

```text
POST /agent/chat
-> auth user 확인
-> session 로드/생성
-> weakness profile 로드
-> intent 판단
-> action 결정
-> 필요한 경우 RAG 호출
-> 응답 생성
-> turn 저장
```

완료 기준:
- Agent 응답에 `agent_action`, `target_concept`, `session_id`가 포함된다.
- 동일 사용자에게 대화 기억과 약점 프로파일이 연결된다.

### Phase 5. LangGraph 연결

목표: MVP Agent 흐름을 그래프로 옮긴다.

작업:
- 기존 Agent service의 단계를 LangGraph node로 분리
- `load_context`, `classify_intent`, `evaluate_weakness`, `decide_action`, `maybe_rag_search`, `generate_response`, `save_turn`
- trace/debug 로그 추가

완료 기준:
- 그래프 실행 결과와 기존 Agent service 결과가 동등하다.
- node별 테스트가 가능하다.

---

## 5. 남길 것과 버릴 것

### 남길 것

| 대상 | 이유 |
|---|---|
| Stage 1/2/3 학습 콘텐츠 | Agent 약점 판단의 원천 데이터 |
| ChromaDB 데이터 | RAG 연구 자산 |
| HybridSearchService | 검색 실험의 핵심 |
| PDF loader | 공식 맞춤법 근거 데이터 |
| 기존 `/chat` | 비교/fallback 용도 |

### 버리거나 격리할 것

| 대상 | 처리 |
|---|---|
| `app/legacy/rag_service.py` | 삭제 후보. 당장은 import되지 않게 테스트 정리 |
| OpenAI 실호출 테스트 | 기본 테스트에서 제외하고 integration test로 분리 |
| 앱 시작 시 무거운 자동 작업 | 관리 API 또는 명령어로 분리 |
| 전역 `stage3_progress` | 사용자별 progress로 교체 |
| `temp_user_id` 중심 API | 호환용으로만 유지 후 단계적 제거 |

---

## 6. 앱 시작 흐름 정리

현재 startup에서 너무 많은 일이 일어난다.

```text
dependency init
vector DB init
Mongo seed
auto indexing
stage data loading
BM25 build
hypothetical question generation
```

목표:

```text
startup:
  - config validation
  - Mongo connection check
  - vector DB connection check
  - router mount

manual/admin:
  - seed data
  - rebuild vector index
  - rebuild BM25
  - generate hypothetical questions
```

이렇게 나눠야 서버 부팅이 예측 가능해진다.

---

## 7. 테스트 전략

테스트를 세 종류로 나눈다.

| 종류 | 설명 | 기본 실행 포함 |
|---|---|---|
| unit | 순수 로직, 모델, 정책 테스트 | 포함 |
| service | Mongo/Chroma를 mock 또는 test DB로 검증 | 일부 포함 |
| integration | OpenAI, 실제 Mongo, 실제 Chroma 호출 | 기본 제외 |

우선순위:
1. `MongoClient.upsert_one` 같은 공통 유틸 테스트
2. auth token 발급/검증 테스트
3. `WeaknessProfileService` 집계 테스트
4. Stage 3 사용자별 진행도 테스트
5. Agent decision 테스트
6. RAG 검색 smoke test

---

## 8. 첫 커밋 후보

가장 먼저 할 만한 작은 작업 묶음:

1. `requirements.txt`에 누락 dependency 추가
2. 깨진 레거시 테스트 skip 또는 제거
3. `MongoClient.upsert_one` 추가
4. `docs` 정리 문서 추가
5. `/auth` 도메인 뼈대 추가

이 정도가 첫 커밋으로 적당하다. 동작을 크게 바꾸지 않으면서 다음 작업의 기반을 만든다.

---

## 9. 판단 기준

리팩토링 중 판단이 헷갈리면 아래 기준으로 결정한다.

1. Agent가 학생 상태를 더 잘 이해하는 데 도움이 되는가?
2. RAG 실험을 더 명확하게 비교/평가할 수 있게 하는가?
3. 기존 학습 플로우를 불필요하게 깨지 않는가?
4. 테스트 가능한 단위로 쪼개지는가?
5. 앱 시작과 API 요청의 책임이 분리되는가?
