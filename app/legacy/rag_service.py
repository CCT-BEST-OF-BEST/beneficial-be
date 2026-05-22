# from typing import List, Dict, Any
# from app.infrastructure.db.vector.vector_db import get_vector_db
# from app.infrastructure.embedding.embedding_model import get_embedding_model
# from app.data.data_loader.korean_word_problems_loader import get_korean_word_problems
# from app.data.data_loader.card_check_loader import get_card_check_data
# import os
# from openai import OpenAI
# from dotenv import load_dotenv
#
# load_dotenv()
#
# class RAGService:
#     def __init__(self):
#         """RAG 서비스 초기화"""
#         self.vector_db = get_vector_db()
#         self.embedding_model = get_embedding_model()
#         self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
#     async def initialize(self):
#         # 데이터가 벡터 DB에 없으면 자동으로 인덱싱
#         await self._ensure_data_indexed()
#
#     async def async_init(self):
#         # 데이터가 벡터 DB에 없으면 자동으로 인덱싱
#         await self._ensure_data_indexed()
#         """RAG 서비스 초기화"""
#         self.vector_db = get_vector_db()
#         self.embedding_model = get_embedding_model()
#         self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
#     async def _ensure_data_indexed(self):
#         """데이터가 벡터 DB에 인덱싱되어 있는지 확인하고, 없으면 자동 인덱싱"""
#         try:
#             # 각 컬렉션의 문서 수 확인
#             korean_collection = self.vector_db.get_collection("korean_word_problems")
#             card_collection = self.vector_db.get_collection("card_check")
#
#             korean_count = korean_collection.count() if korean_collection else 0
#             card_count = card_collection.count() if card_collection else 0
#
#             print(f"🔎 현재 인덱싱된 문서: korean_word_problems={korean_count}, card_check={card_count}")
#
#             # 데이터가 없으면 자동 인덱싱
#             if korean_count == 0:
#                 print("🔎 한국어 단어 문제 데이터 자동 인덱싱 중...")
#                 await self._index_korean_word_problems()
#
#             if card_count == 0:
#                 print("🔎 카드 체크 데이터 자동 인덱싱 중...")
#                 await self._index_card_check_data()
#
#         except Exception as e:
#             print(f"[WARN] 데이터 인덱싱 확인 중 오류: {e}")
#
#     async def _index_korean_word_problems(self):
#         """한국어 단어 문제 데이터를 벡터 DB에 인덱싱"""
#         try:
#             data = get_korean_word_problems()
#             if not data:
#                 return
#
#             documents = self.embedding_model.prepare_documents_for_indexing(data, "korean_word_problems")
#
#             texts = [doc["text"] for doc in documents]
#             ids = [doc["id"] for doc in documents]
#             metadatas = [doc["metadata"] for doc in documents]
#
#             embeddings = await self.embedding_model.get_embeddings(texts)
#
#             collection = self.vector_db.get_collection("korean_word_problems")
#             collection.add(
#                 embeddings=embeddings,
#                 documents=texts,
#                 ids=ids,
#                 metadatas=metadatas
#             )
#             print(f"[OK] 한국어 단어 문제 {len(documents)}개 문서 인덱싱 완료")
#
#         except Exception as e:
#             print(f"[ERROR] 한국어 단어 문제 인덱싱 실패: {e}")
#
#     async def _index_card_check_data(self):
#         """카드 체크 데이터를 벡터 DB에 인덱싱"""
#         try:
#             data = get_card_check_data()
#             if not data:
#                 return
#
#             documents = self.embedding_model.prepare_documents_for_indexing(data, "card_check")
#
#             texts = [doc["text"] for doc in documents]
#             ids = [doc["id"] for doc in documents]
#             metadatas = [doc["metadata"] for doc in documents]
#
#             embeddings = await self.embedding_model.get_embeddings(texts)
#
#             collection = self.vector_db.get_collection("card_check")
#             collection.add(
#                 embeddings=embeddings,
#                 documents=texts,
#                 ids=ids,
#                 metadatas=metadatas
#             )
#             print(f"[OK] 카드 체크 {len(documents)}개 문서 인덱싱 완료")
#
#         except Exception as e:
#             print(f"[ERROR] 카드 체크 인덱싱 실패: {e}")
#
#     async def search_relevant_documents(self, query: str, collection_name: str = None, top_k: int = 3) -> List[
#         Dict[str, Any]]:
#         """
#         질문과 관련된 문서를 검색합니다. - 사용자 질문과 관련된 문서를 벡터 검색으로 찾기
#
#         Args:
#             query: 검색할 질문
#             collection_name: 검색할 컬렉션명 (None이면 모든 컬렉션)
#             top_k: 반환할 문서 수
#
#         Returns:
#             관련 문서 리스트
#         """
#         try:
#             # 질문을 임베딩 - 사용자 질문을 임베딩으로 변환
#             query_embedding = await self.embedding_model.get_embedding(query)
#
#             results = []
#
#             # 검색할 컬렉션 결정
#             if collection_name:
#                 # 특정 컬렉션에서만 검색
#                 collection = self.vector_db.get_collection(collection_name)
#                 if collection:
#                     search_results = collection.query(
#                         query_embeddings=[query_embedding],
#                         n_results=top_k
#                     )
#
#                     for i in range(len(search_results['documents'][0])):
#                         results.append({
#                             'document': search_results['documents'][0][i],
#                             'metadata': search_results['metadatas'][0][i],
#                             'distance': search_results['distances'][0][i],
#                             'collection': collection_name
#                         })
#             else:
#                 # 모든 컬렉션에서 검색
#                 collections = ["korean_word_problems", "card_check"]
#
#                 # 각 컬렉션에서 유사도 검색 실행
#                 for coll_name in collections:
#                     collection = self.vector_db.get_collection(coll_name)
#                     if collection:
#
#                         # ChromaDB 에서 코사인 유사도 검색
#                         search_results = collection.query(
#                             query_embeddings=[query_embedding],
#                             n_results=top_k
#                         )
#
#                         # 검색 결과 포맷팅
#                         for i in range(len(search_results['documents'][0])):
#                             results.append({
#                                 'document': search_results['documents'][0][i],
#                                 'metadata': search_results['metadatas'][0][i],
#                                 'distance': search_results['distances'][0][i],
#                                 'collection': coll_name
#                             })
#
#             # 거리순으로 정렬 (가까울수록 관련성 높음)
#             # 전체 결과를 유사도 순으로 정렬
#             results.sort(key=lambda x: x['distance'])
#
#             return results[:top_k]  # 상위 top_k개 문서만 반환
#
#         except Exception as e:
#             print(f"[ERROR] 문서 검색 실패: {e}")
#             return []
#
#     async def chat_with_rag(self, prompt: str, collection_name: str = None, top_k: int = 3) -> str:
#         """
#         RAG를 사용하여 GPT와 대화합니다.
#
#         Args:
#             prompt: 사용자 질문
#             collection_name: 검색할 컬렉션명
#             top_k: 참조할 문서 수
#
#         Returns:
#             GPT 응답
#         """
#         try:
#             # 1. 관련 문서 검색
#             relevant_docs = await self.search_relevant_documents(prompt, collection_name, top_k)
#
#             # 2. 컨텍스트 구성
#             context = self._build_context(relevant_docs)
#
#             # 3. GPT에 전달할 메시지 구성
#             system_message = """너는 초등학생 돌봄선생님이야.
# 주어진 참고 자료를 바탕으로 정확하고 친근하게 답변해줘.
# 참고 자료에 없는 내용은 일반적인 지식으로 답변하되,
# 참고 자료가 있으면 그것을 우선적으로 활용해줘."""
#
#             user_message = f"""참고 자료:
# {context}
#
# 질문: {prompt}"""
#
#             # 4. GPT 호출
#             response = await self.openai_client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": system_message},
#                     {"role": "user", "content": user_message}
#                 ],
#                 max_tokens=500,
#                 temperature=0.7
#             )
#
#             return response.choices[0].message.content
#
#         except Exception as e:
#             print(f"[ERROR] RAG 채팅 실패: {e}")
#             return f"죄송합니다. 오류가 발생했습니다: {str(e)}"
#
#     def _build_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
#         """검색된 문서들을 컨텍스트로 구성합니다."""
#         if not relevant_docs:
#             return "참고 자료가 없습니다."
#
#         context_parts = []
#         for i, doc in enumerate(relevant_docs, 1):
#             context_parts.append(f"{i}. {doc['document']}")
#
#         return "\n".join(context_parts)
#
#
# # 전역 RAG 서비스 인스턴스
# rag_service = None
#
#
# async def get_rag_service():
#     """전역 RAG 서비스 인스턴스를 비동기적으로 반환하고 초기화합니다."""
#     global rag_service
#     if rag_service is None:
#         rag_service = RAGService()
#         await rag_service.initialize()
#     return rag_service