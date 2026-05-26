# Domains

새 기능은 도메인 중심으로 이곳에 추가한다. 도메인 안에서는 기능 단위 vertical slice를 우선한다.

원칙:
- router는 HTTP 입출력만 담당하며, 가능하면 해당 기능 패키지 옆에 둔다.
- service는 비즈니스 규칙을 담당한다.
- repository는 MongoDB 같은 저장소 접근을 담당한다.
- schemas는 API request/response DTO를 담당한다.
- models는 도메인 내부 모델을 담당한다.

RAG처럼 비즈니스 도메인보다 기술 기능에 가까운 코드는 `app/infrastructure`에 둔다.
seed/fixture 성격의 공통 데이터 로더는 `app/common/data`에 둔다.
