"""
인덱싱 타임 가상 질문 생성 (Hypothetical Questions Augmentation)

각 문서에 대해 GPT로 초등학생이 물어볼 법한 예상 질문 3개를 생성하고,
원본 문서와 함께 ChromaDB에 별도 벡터로 저장한다.

검색 시 쿼리가 '가상 질문 벡터'와 매칭되면 원본 문서 내용을 LLM에 전달한다.
→ 구어체 질문 ↔ 정의 형태 문서의 비대칭 검색 문제 해결
"""

import asyncio
from typing import List, Dict, Any
import chromadb
from dotenv import load_dotenv
import os

from app.infrastructure.embedding.embedding_model import EmbeddingModel
from app.common.logging.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)

try:
    from openai import AsyncOpenAI
except ModuleNotFoundError:
    AsyncOpenAI = None

QUESTIONS_SUFFIX = "_questions"  # 가상 질문 컬렉션 접미사
N_QUESTIONS = 3                  # 문서당 생성 질문 수

# 생성 완료된 컬렉션 추적 (hybrid_search에서 readiness 확인용)
_ready_question_collections: set[str] = set()


def is_question_collection_ready(collection_name: str) -> bool:
    """해당 _questions 컬렉션의 생성이 완료되었는지 반환"""
    return collection_name in _ready_question_collections

SYSTEM_PROMPT = """너는 초등학생 대상 한국어 맞춤법 교육 챗봇의 검색 시스템을 개선하는 전문가야.
주어진 교육 자료에 대해 초등학생이 실제로 물어볼 법한 자연스러운 구어체 질문을 만들어줘.
질문은 짧고 구체적으로, 줄바꿈으로 구분해서 딱 {n}개만 출력해."""


async def _generate_questions(
    openai_client,
    document: str,
    n: int = N_QUESTIONS,
) -> List[str]:
    """GPT로 문서에 대한 예상 질문 n개 생성"""
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT.format(n=n),
                },
                {
                    "role": "user",
                    "content": f"다음 자료를 보고 초등학생이 물어볼 질문 {n}개를 만들어줘:\n\n{document}",
                },
            ],
            max_tokens=200,
            temperature=0.7,
        )
        raw = response.choices[0].message.content or ""
        questions = [
            line.strip().lstrip("0123456789.-) ")
            for line in raw.strip().splitlines()
            if line.strip()
        ]
        return questions[:n]
    except Exception as e:
        logger.error(f"✗ 가상 질문 생성 실패: {e}")
        return []


async def build_hypothetical_questions(
    chroma_client: chromadb.PersistentClient,
    embedding_model: EmbeddingModel,
    collection_names: List[str] | None = None,
) -> None:
    """
    지정된 컬렉션의 모든 문서에 대해 가상 질문을 생성하고
    {collection_name}_questions 컬렉션에 저장한다.
    이미 생성된 문서는 스킵한다.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("[WARN] OPENAI_API_KEY 없음 → 가상 질문 생성 스킵")
        return
    if AsyncOpenAI is None:
        logger.warning("[WARN] openai 패키지 없음 → 가상 질문 생성 스킵")
        return

    openai_client = AsyncOpenAI(api_key=api_key)
    targets = collection_names or ["card_check", "korean_word_problems", "pdf_documents"]

    for coll_name in targets:
        q_coll_name = coll_name + QUESTIONS_SUFFIX

        try:
            src_col = chroma_client.get_collection(coll_name)
        except Exception:
            logger.warning(f"[WARN] 컬렉션 없음: {coll_name}")
            continue

        # 가상 질문 컬렉션 (없으면 생성)
        q_col = chroma_client.get_or_create_collection(
            q_coll_name,
            metadata={"hnsw:space": "cosine"},
        )

        # 이미 생성된 original_id 목록
        existing = q_col.get(include=[])
        existing_ids = set(existing["ids"])

        src_data = src_col.get(include=["documents", "metadatas"])
        total = len(src_data["ids"])
        new_count = 0
        processed = 0

        # 이미 모든 문서가 처리된 경우 바로 완료 처리
        already_done = all(
            any(eid.startswith(f"hq_{doc_id}_") for eid in existing_ids)
            for doc_id in src_data["ids"]
        )
        if already_done:
            logger.info(f"⏭ [{coll_name}] 가상 질문 이미 생성됨 (총 {q_col.count()}개) → 스킵")
            _ready_question_collections.add(q_coll_name)
            continue

        logger.info(f"[WRITE] [{coll_name}] 가상 질문 생성 시작: {total}개 문서")

        for doc_id, document, metadata in zip(
            src_data["ids"], src_data["documents"], src_data["metadatas"]
        ):
            # 이미 처리된 문서 스킵
            if any(eid.startswith(f"hq_{doc_id}_") for eid in existing_ids):
                processed += 1
                continue

            questions = await _generate_questions(openai_client, document)
            if not questions:
                processed += 1
                continue

            # 질문 임베딩 후 저장
            embeddings = await embedding_model.get_embeddings(questions)
            q_ids = [f"hq_{doc_id}_{i}" for i in range(len(questions))]
            q_metas = [
                {
                    "original_id": doc_id,
                    "original_text": document,
                    "collection": coll_name,
                    "question_index": i,
                }
                for i in range(len(questions))
            ]

            q_col.add(
                ids=q_ids,
                embeddings=embeddings,
                documents=questions,
                metadatas=q_metas,
            )
            new_count += len(questions)
            processed += 1

            logger.info(f"   [{coll_name}] 진행: {processed}/{total} | 최근 질문: {questions[0][:40]}...")

            # API rate limit 방지
            await asyncio.sleep(0.3)

        _ready_question_collections.add(q_coll_name)
        logger.info(
            f"[OK] [{coll_name}] 가상 질문 생성 완료: "
            f"{new_count}개 추가 (총 {q_col.count()}개) → 검색 활성화"
        )
