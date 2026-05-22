# Domains

새 기능은 도메인 중심으로 이곳에 추가한다.

원칙:
- router는 HTTP 입출력만 담당한다.
- service는 비즈니스 규칙을 담당한다.
- repository는 MongoDB 같은 저장소 접근을 담당한다.
- schemas는 API request/response DTO를 담당한다.
- models는 도메인 내부 모델을 담당한다.

기존 `app/api`, `app/data`, `app/infrastructure`는 바로 이동하지 않는다. 새 도메인부터 이 구조를 따른다.
