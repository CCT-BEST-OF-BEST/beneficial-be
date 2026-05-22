# Auth Domain

로그인과 토큰 인증을 담당한다.

예정 구성:
- `models.py`: `User`, `RefreshTokenSession`
- `schemas.py`: signup/login/refresh/me 요청 및 응답
- `repository.py`: `users`, `refresh_token_sessions` 컬렉션 접근
- `service.py`: 비밀번호 해싱, 로그인, 토큰 발급/회전/폐기
- `router.py`: `/auth/*` API

초기 목표는 Agent 학습 기록을 영속적인 `user_id`에 연결하는 것이다.
