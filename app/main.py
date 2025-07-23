import logging
from fastapi import FastAPI
from app.api.chat.chat_router import router as chat_router
from app.api.system.indexing import router as indexing_router
from app.common.init.initialization import get_initialization_service

# 전역 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Beneficial RAG System",
    version="1.0.0",
    description="한국어 교육을 위한 RAG 기반 챗봇 시스템",
    openapi_tags=[
        {
            "name": "chat",
            "description": "사용자 채팅 API (프론트엔드용)"
        },
        {
            "name": "admin",
            "description": "관리자 전용 API (백엔드 개발자용)"
        },
        {
            "name": "test",
            "description": "테스트용 API (개발용)"
        }
    ]
)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행될 이벤트"""
    try:
        # 초기화 서비스를 통한 간단한 초기화
        init_service = get_initialization_service()
        result = await init_service.initialize_application()

        if result["status"] == "success":
            logger.info("🎉 애플리케이션 시작 완료!")
        else:
            logger.warning(f"⚠️ 초기화 경고: {result['message']}")

    except Exception as e:
        logger.error(f"❌ 애플리케이션 시작 실패: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행될 이벤트"""
    logger.info("🛑 Beneficial RAG System 종료 중...")


# 라우터 등록
app.include_router(chat_router, tags=["chat"])
app.include_router(indexing_router, tags=["admin"])


# 시스템 상태 확인 엔드포인트 (개발용)
@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    try:
        init_service = get_initialization_service()
        return init_service.get_system_status()
    except Exception as e:
        return {
            "status": "error",
            "message": f"상태 확인 실패: {str(e)}"
        }