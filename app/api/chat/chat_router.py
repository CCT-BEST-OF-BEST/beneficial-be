from fastapi import APIRouter, HTTPException
from app.api.chat.service.chat_service import get_chat_service
from app.data.models.chat_models import ChatRequest, ChatResponse, ChatStatusResponse
from app.common.logging.logging_config import get_logger

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post(
    "/", 
    response_model=ChatResponse, 
    summary="AI 학습 도우미 채팅",
    description="""
## API 설명
초등학생 돌봄반 학생들을 위한 AI 학습 도우미와 대화합니다.
RAG(Retrieval-Augmented Generation) 시스템을 사용하여 한국어 문법과 맞춤법에 대한 정확한 답변을 제공합니다.

## 프론트엔드 구현 가이드
- **로딩 처리**: 응답 대기 시간 동안 로딩 인디케이터 표시
- **에러 처리**: 네트워크 오류 시 사용자에게 알림
- **추천 질문**: 자주 묻는 질문 버튼으로 사용자 편의성 증대

## 요청 예시
```json
{
  "prompt": "맞춤법이 헷갈려요"
}
```

## 응답 예시
```json
{
  "status": "success",
  "prompt": "맞춤법이 헷갈려요",
  "response": "맞춤법에 대해 쉽게 설명해드릴게요! 맞춤법은 말을 쓸 때 맞는 글자로 쓰는 법칙이에요. 예를 들어 '가르치다'와 '가르키다'는 다른 뜻이에요. '가르치다'는 '교육하다'는 뜻이고, '가르키다'는 '지시하다'는 뜻이에요. 이런 차이를 알고 쓰는 것이 맞춤법이에요!",
  "collection_used": "all",
  "top_k": 5
}
```

## 사용 시나리오
- 문제 풀이 중 궁금한 점 질문
- 한국어 문법 개념 설명 요청
- 맞춤법 확인 및 학습 도움
    """
)
async def chat_with_rag(request: ChatRequest):
    """
    RAG 시스템을 사용하여 GPT와 대화합니다. (초등학생 돌봄반용)

    Args:
        request: 채팅 요청 (질문만 필요)

    Returns:
        GPT 응답
    """
    try:
        # 내부 기본값 설정
        top_k = 5
        collection_name = None  # 전체 컬렉션 검색
        
        logger.info(f"📨 채팅 요청 수신: '{request.prompt}' (top_k={top_k})")
        
        chat_service = get_chat_service()
        response = await chat_service.chat_with_rag(
            prompt=request.prompt,
            collection_name=collection_name,
            top_k=top_k
        )

        logger.info(f"✅ 채팅 응답 완료: {len(response)}자")
        
        return ChatResponse(
            status="success",
            prompt=request.prompt,
            response=response,
            collection_used=collection_name or "all",
            top_k=top_k
        )
    except Exception as e:
        logger.error(f"❌ 채팅 요청 실패: {e}")
        raise HTTPException(status_code=500, detail=f"채팅 실패: {str(e)}")


@router.get(
    "/status", 
    summary="채팅 시스템 상태 확인",
    description="""
## API 설명
채팅 시스템의 현재 상태와 데이터베이스 정보를 확인합니다.
백엔드 개발자나 시스템 관리자를 위한 모니터링 API입니다.

## 프론트엔드 구현 가이드
- **관리자 대시보드**: 시스템 상태 및 컬렉션별 통계 표시
- **상태 표시**: 시스템 활성화 상태를 시각적으로 표현
- **문서 수 표시**: 각 컬렉션의 문서 개수 확인

## 응답 예시
```json
{
  "status": "success",
  "chat_system": "active",
  "rag_system": "available",
  "collections": {
    "korean_word_problems": {
      "document_count": 15,
      "status": "available"
    },
    "card_check": {
      "document_count": 8,
      "status": "available"
    },
    "pdf_documents": {
      "document_count": 1250,
      "status": "available"
    }
  }
}
```

## 주의사항
- **관리자 전용**: 일반 사용자는 접근 불필요
- **민감 정보**: 시스템 내부 정보 포함
- **빈도 제한**: 과도한 호출 시 성능 영향 가능
    """
)
async def get_chat_status():
    """채팅 시스템 상태를 확인합니다. (시스템 모니터링용)"""
    try:
        chat_service = get_chat_service()
        vector_db = chat_service.vector_db

        # 각 컬렉션의 문서 수 확인 (PDF 컬렉션 포함)
        collections_info = {}
        for collection_name in ["korean_word_problems", "card_check", "pdf_documents"]:
            collection = vector_db.get_collection(collection_name)
            if collection:
                collections_info[collection_name] = {
                    "document_count": collection.count(),
                    "status": "available"
                }
            else:
                collections_info[collection_name] = {
                    "document_count": 0,
                    "status": "not_available"
                }

        return ChatStatusResponse(
            status="success",
            chat_system="active",
            rag_system="available",
            collections=collections_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")