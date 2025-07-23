from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Document(BaseModel):
    """문서 기본 모델"""
    id: str = Field(..., description="문서 ID")
    text: str = Field(..., description="문서 텍스트")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="문서 메타데이터")


class KoreanWordProblem(BaseModel):
    """한국어 단어 문제 모델"""
    id: str = Field(..., description="문제 ID")
    question: str = Field(..., description="문제 내용")
    answer: str = Field(..., description="정답")
    explanation: Optional[str] = Field(None, description="설명")
    difficulty: Optional[str] = Field(None, description="난이도")
    category: Optional[str] = Field(None, description="카테고리")


class CardCheckData(BaseModel):
    """카드 체크 데이터 모델"""
    id: str = Field(..., description="카드 ID")
    title: str = Field(..., description="카드 제목")
    content: str = Field(..., description="카드 내용")
    category: Optional[str] = Field(None, description="카테고리")
    tags: Optional[List[str]] = Field(None, description="태그")


class IndexingResult(BaseModel):
    """인덱싱 결과 모델"""
    status: str = Field(..., description="인덱싱 상태")
    message: str = Field(..., description="결과 메시지")
    indexed_count: Optional[int] = Field(None, description="인덱싱된 문서 수")
    total_collections: Optional[int] = Field(None, description="전체 컬렉션 수")
    successful_collections: Optional[int] = Field(None, description="성공한 컬렉션 수")
    results: Optional[Dict[str, Any]] = Field(None, description="상세 결과")


class CollectionInfo(BaseModel):
    """컬렉션 정보 모델"""
    name: str = Field(..., description="컬렉션명")
    document_count: int = Field(..., description="문서 수")
    status: str = Field(..., description="상태")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")