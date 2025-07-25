import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat.chat_router import router as chat_router
from app.api.system.indexing import router as indexing_router
from app.api.learning.learning_router import router as learning_router
from app.api.learning.stage3_router import router as stage3_router
from app.common.init.initialization import get_initialization_service

# 전역 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="🎓 CCT 백엔드 API",
    version="1.0.0",
    description="""
# 초등학생 돌봄반 한국어 교육 시스템

## 시스템 개요
초등학생 돌봄반 학생들을 위한 한국어 맞춤법 교육을 위한 AI 기반 학습 시스템입니다.

## 주요 기능
- **단계별 학습**: 1단계(카드 학습) → 2단계(드래그&드롭) → 3단계(문제풀이)
- **AI 학습 도우미**: RAG 기반 맞춤법 질의응답 시스템
- **개인화 학습**: 학생별 진행도 추적 및 복습 시스템
- **적응형 복습**: 틀린 문제 자동 복습 및 뱃지 시스템

## 빠른 시작
1. **학습 시작**: `/learning/stage1/cards` - 카드 학습
2. **문제 풀이**: `/learning/stage3/next-problem` - 3단계 문제
3. **AI 도움**: `/chat/` - 맞춤법 질문하기
    """,
    openapi_tags=[
        {
            "name": "chat",
            "description": """
## AI 학습 도우미 채팅 API

### 주요 기능
- **RAG 기반 답변**: 한국어 문법/맞춤법 정확한 답변
- **초등학생 맞춤**: 쉬운 언어로 설명하는 AI
- **실시간 대화**: 학습 중 궁금한 점 즉시 해결

### 사용 시나리오
- 문제 풀이 중 헷갈리는 맞춤법 질문
- 한국어 문법 개념 설명 요청
- 학습 방법이나 팁 문의
            """
        },
        {
            "name": "learning",
            "description": """
## 단계별 학습 API

### 주요 기능
- **1단계 카드 학습**: 어휘 카드 플립 학습
- **2단계 드래그&드롭**: 인터랙티브 문제 풀이
- **이미지 서빙**: 학습용 이미지 파일 제공

### 사용 시나리오
- 단계별 순차 학습 진행
- 카드 플립 애니메이션 구현
- 드래그&드롭 인터랙션 처리
            """
        },
        {
            "name": "stage3",
            "description": """
## 3단계 문제풀이 API

### 주요 기능
- **순차 학습**: 1-5번 문제 순서대로 출제
- **적응형 복습**: 틀린 문제만 자동 복습
- **뱃지 시스템**: 학습 동기부여를 위한 뱃지
- **진행도 관리**: 개인별 학습 상태 추적
- **해당 API 를 따로 분리한 이유는 서비스 로직의 복잡도 때문에 learning 관련 API 에서 분리하였습니다.**

### 학습 알고리즘
1. **1단계**: 모든 문제 순차 학습 (1→2→3→4→5) : 정답 여부와 상관없이 5문제를 먼저 풀고
2. **2단계**: 틀린 문제만 복습 (순환 방식) : 틀린 문제들만 반복적으로 출제
3. **완료**: 모든 문제 정답 시 학습 완료
4. **복습**: 틀린 문제는 계속 복습, 맞춘 문제는 제외
5. **예시**: 1 번문제 : 정답(첫학습 -> 훌륭해요) -> 2번 문제 : 오답(첫학습 -> 잠시후복습) -> 3번 문제 : 정답 (첫핛습 -> 훌륭해요) -> 
4번 문제 : 오답 (첫학습 -> 잠시 후 복습) -> 5번 문제 : 정답 (첫학습 -> 훌륭해요) -> 다시 2번 문제 : 오답 (재도전 -> 재도전) -> 다시 4번 문제 : 정답 (재도전 -> 훌륭해요) -> 또 다시 2번 문제 : 정답 (재도전 -> 흘륭해요)
            """
        },
        {
            "name": "admin",
            "description": """
## 시스템 관리 API

### 주요 기능
- **시스템 모니터링**: 백엔드 상태 및 성능 확인
- **데이터 관리**: 학습 데이터 및 벡터 DB 관리
- **인덱싱**: PDF 문서 처리 및 검색 인덱스 생성

### 사용 시나리오
- 시스템 상태 모니터링
- 데이터베이스 문서 수 확인
- 새로운 학습 자료 추가
            """
        },
    ]
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React 개발 서버
        "http://localhost:5173",  # Vite 개발 서버
        "http://localhost:8080",  # Vue 개발 서버
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "*"  # 개발 환경에서는 모든 origin 허용 (프로덕션에서는 제거)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# Static 파일 마운트 (이미지 파일 서빙을 위해)
app.mount("/images", StaticFiles(directory="app/static/images"), name="images")


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
app.include_router(stage3_router)
app.include_router(indexing_router)


@app.get(
    "/",
    summary="시스템 기본 정보",
    description="""
## API 설명
CCT 백엔드 API의 기본 정보와 시스템 상태를 반환합니다.

## 프론트엔드 구현 가이드
- **시스템 상태 확인**: 앱 시작 시 연결 상태 점검
- **버전 정보**: API 버전 및 시스템 정보 표시

## 응답 예시
```json
{
  "message": "CCT 백엔드 API",
  "version": "1.0.0",
  "description": "초등학생 돌봄반 학생들을 위한 한국어 교육을 위한 시스템"
}
```
    """
)
def read_root():
    """시스템 기본 정보를 반환합니다."""
    return {
        "message": "CCT 백엔드 API",
        "version": "1.0.0",
        "description": "초등학생 돌봄반 학생들을 위한 한국어 교육을 위한 시스템"
    }

