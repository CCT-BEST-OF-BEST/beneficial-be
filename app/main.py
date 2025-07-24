import logging
from fastapi import FastAPI
from app.api.chat.chat_router import router as chat_router
from app.api.system.indexing import router as indexing_router
from app.api.learning.learning_router import router as learning_router
from app.api.user.user_router import router as user_router
from app.common.init.initialization import get_initialization_service

# 전역 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CCT 백엔드 API",
    version="1.0.0",
    description="초등학생 돌봄반 학생들을 위한 한국어 교육을 위한 시스템",
    openapi_tags=[
        {
            "name": "chat",
            "description": "사용자 채팅 API (초등학생 돌봄반용)"
        },
        {
            "name": "learning",
            "description": "학습 진행도 및 상태 관리 API"
        },
        {
            "name": "admin",
            "description": "시스템 상태 모니터링 API (관리자용)"
        },
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
app.include_router(chat_router)
app.include_router(learning_router)
app.include_router(indexing_router)
app.include_router(user_router)


@app.get("/")
def read_root():
    """시스템 기본 정보를 반환합니다."""
    return {
        "message": "CCT 백엔드 API",
        "version": "1.0.0",
        "description": "초등학생 돌봄반 학생들을 위한 한국어 교육을 위한 시스템"
    }

