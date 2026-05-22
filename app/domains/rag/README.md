# RAG Domain

검색과 근거 기반 응답 생성을 담당한다.

예정 구성:
- `schemas.py`: 검색 결과와 근거 문서 DTO
- `retriever.py`: Hybrid/BM25/Vector 검색을 감싼 도구 인터페이스
- `service.py`: RAG 응답 생성
- `router.py`: legacy-compatible `/chat` 또는 실험용 RAG API

기존 `HybridSearchService`, ChromaDB, PDF 인덱스는 유지하되 Agent가 호출하기 쉬운 tool 형태로 감싼다.
