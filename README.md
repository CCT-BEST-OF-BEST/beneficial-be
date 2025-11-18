# 🇰🇷 이로운 (Beneficial) - AI 기반 초등 돌봄반 한국어 교육 플랫폼

> RAG(Retrieval-Augmented Generation) 기술을 활용하여 초등학생에게 맞춤형 한국어 학습 경험을 제공하는 백엔드 시스템입니다.
<img width="1341" height="750" alt="image" src="https://github.com/user-attachments/assets/06d0b964-6564-40f8-95d1-176027fac10a" />

---

## 📅 프로젝트 소개
**이로운(Beneficial)** 은 초등학생 돌봄 교실 내 한국어 교육 격차를 해소하기 위해 개발되었습니다.
단순한 주입식 교육이 아닌, **AI 튜터와의 실시간 대화**와 **3단계 게이미피케이션 학습**을 통해 아이들이 스스로 흥미를 느끼고 학습할 수 있도록 돕습니다.

---

## 🛠 Tech Stack

### AI & Backend
- **Framework**: FastAPI (Asynchronous Web Framework)
- **LLM**: OpenAI GPT-3.5/4 Turbo
- **Vector DB**: ChromaDB (On-premise Vector Store)
- **Embedding**: OpenAI text-embedding-ada-002 / Custom Models
- **Architecture**: RAG (Retrieval-Augmented Generation) Pipeline

### Infrastructure
- **Container**: Docker
- **CI/CD**: GitHub Actions (Deploy workflow)

---

## ✨ Key Features (핵심 기능)

### 1. RAG 기반 AI 학습 튜터 (AI Tutor)
<img width="1179" height="772" alt="image" src="https://github.com/user-attachments/assets/f48b92bf-4ccd-41cd-9278-6b8827be2ef9" />

- **초등학생 맞춤 페르소나**: "친절한 돌봄 선생님" 시스템 프롬프트 적용 (반말/존댓말 모드, 격려 멘트)
- **문맥 인식 답변**: `VectorDB`에서 유사도가 높은 교육 자료(PDF, 카드 데이터)를 검색(Retrieval)하여 할루시네이션 없는 정확한 맞춤법/문법 설명 제공
- **실시간 질의응답**: 학습 도중 모르는 단어나 문법을 물어보면 즉시 답변

### 2. 3단계 적응형 학습 시스템 (Adaptive Learning)
<img width="833" height="623" alt="image" src="https://github.com/user-attachments/assets/36b2f929-1c21-4bc6-b814-d6d041d276aa" />

- **Stage 1 (어휘 학습)**: 플래시 카드를 통한 시각적 어휘 습득
- **Stage 2 (인터랙티브)**: 드래그 앤 드롭(Drag & Drop)을 활용한 능동적 문제 풀이
- **Stage 3 (실전 & 복습)**: **'오답 순환 알고리즘'** 적용
    - 틀린 문제는 잠시 후 다시 출제되는 반복 학습 루틴(Spaced Repetition) 구현
    - 모든 문제를 맞힐 때까지 끝나지 않는 완전 학습 지향

### 3. 자동화된 지식 인덱싱 (Auto Indexing)
- **PDF 문서 처리**: 교육용 PDF 교재를 업로드하면 자동으로 텍스트를 추출하고 청킹(Chunking)하여 벡터 데이터베이스에 임베딩 저장
- **검색 최적화**: 사용자 질문 의도에 따라 검색 컬렉션(`korean_word_problems`, `card_check`) 자동 분기 처리

---

## 💁🏻 System Architecture
<img width="1362" height="750" alt="image" src="https://github.com/user-attachments/assets/c682241b-efd6-4ea7-8d02-2f4c6b950528" />

---

## 🔥 Technical Deep Dive: RAG System Implementation
<img width="937" height="489" alt="image" src="https://github.com/user-attachments/assets/e77ae7cb-abd1-4c63-be48-80d5e9ab27b0" />

<details>
<summary>1. 한국어 교육 특화 RAG 파이프라인 구축 (Hallucination 방지)</summary>
<br>

**[Problem]**
범용 LLM(GPT-3.5)은 초등학생 수준에 맞지 않는 어려운 어휘를 사용하거나, 한국어 맞춤법 규정에 대해 잘못된 정보를 생성(Hallucination)하는 문제가 있었습니다.

**[Solution]**
신뢰할 수 있는 답변을 위해 **RAG(Retrieval-Augmented Generation)** 아키텍처를 도입했습니다.
* **Data Source:** '문화체육관광부 한글 맞춤법 공식 PDF'와 자체 제작한 '어휘 학습 데이터(JSON)'를 벡터 DB에 인덱싱하여 답변의 근거로 사용했습니다.
* **Embedding:** 한국어 문장 처리에 특화된 **`jhgan/ko-sroberta-multitask`** 모델을 사용하여 한국어의 의미적 뉘앙스를 정확하게 벡터화했습니다.
* **Vector Store:** 오픈소스인 **ChromaDB**를 활용하여 온프레미스 환경에서 벡터 검색 성능을 최적화했습니다.

> **[Impact]** 공신력 있는 데이터를 기반으로 답변을 생성함으로써 교육용 챗봇의 필수 요건인 '정보의 정확성'을 확보했습니다.
</details>

<details>
<summary>2. 검색 품질 향상을 위한 유사도 임계값(Threshold) 튜닝</summary>
<br>

**[Issue]**
단순 Top-k 검색 시, 사용자의 질문과 관련성이 낮은 문서까지 Context에 포함되어 LLM이 엉뚱한 답변을 하는 경우가 발생했습니다.

**[Optimization]**
**코사인 유사도(Cosine Similarity) 기반의 필터링 로직**을 추가했습니다.
* 유사도 점수가 **0.6 이상**인 문서만 필터링하여 Context에 주입하도록 `Retrieval` 로직을 개선했습니다.
* 관련 문서가 없을 경우 LLM이 거짓 정보를 지어내는 대신 "관련된 내용을 찾을 수 없습니다"라고 답변하도록 유도하여 시스템의 신뢰도를 높였습니다.

> **[Code]** [ChatService.py - search_relevant_documents() 보러가기](./app/api/chat/service/chat_service.py)
</details>
