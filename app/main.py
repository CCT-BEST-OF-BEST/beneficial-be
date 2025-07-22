import logging
from fastapi import FastAPI

# 라우터 import (실제 존재하는 파일들만)
from app.api.chat.chat_bot import router as chat_router
from app.api.system.indexing import router as indexing_router

# 기존 테스트 함수들
from tests.connection.db_conntction_test import mongo_test
from tests.connection.openai_test import test_chat_with_gpt

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
    logger.info("🚀 Beneficial RAG System 시작 중...")

    # 벡터 DB 및 RAG 서비스 초기화
    try:
        from app.core.vector_db import initialize_vector_db
        from app.core.rag_service import get_rag_service

        vector_db = initialize_vector_db()
        logger.info("✅ 벡터 DB 초기화 완료")

        await get_rag_service()
        logger.info("✅ RAG 서비스 초기화 완료")

    except Exception as e:
        logger.warning(f"⚠️ 서비스 초기화 실패: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행될 이벤트"""
    logger.info("🛑 Beneficial RAG System 종료 중...")


# 라우터 등록 (실제 존재하는 파일들만)
app.include_router(chat_router, tags=["chat"])
app.include_router(indexing_router, tags=["admin"])


# 기존 테스트 엔드포인트 (개발용)
@app.get("/", tags=["test"])
def read_root():
    return {
        "message": "Hello, Hackathon!",
        "system": "Beneficial RAG System",
        "version": "1.0.0"
    }


@app.get("/test-db", tags=["test"])
def test_db_connection():
    result = mongo_test()
    return result


@app.get("/test-gpt", tags=["test"])
async def test_gpt(prompt: str = "맞히다와 맞추다의 차이 알려줘"):
    result = await test_chat_with_gpt(prompt)
    return {"result": result}