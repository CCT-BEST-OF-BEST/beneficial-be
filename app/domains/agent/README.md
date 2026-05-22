# Agent Domain

학생 상태를 바탕으로 어떤 도움을 줄지 결정하는 AI Agent를 담당한다.

예정 구성:
- `models.py`: `AgentDecision`, `AgentTurn`, `ChatSession`
- `schemas.py`: `/agent/chat`, `/agent/profile/me` 요청 및 응답
- `service.py`: Agent MVP 흐름
- `graph.py`: LangGraph 연결
- `router.py`: `/agent/*` API

RAG는 이 도메인의 중심이 아니라 필요할 때 호출하는 도구다.
