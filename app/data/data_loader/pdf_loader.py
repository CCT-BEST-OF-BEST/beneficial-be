import os
import logging
from typing import List, Dict, Any
import pdfplumber
import re

logger = logging.getLogger(__name__)

class SimpleTextSplitter:
    """간단한 텍스트 분할기 (LangChain 대체)"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = [
            "\n\n제", "\n\n",  # 제N항 우선
            "\n제", "제",      # 제 키워드
            "\n\n", "\n",     # 일반 줄바꿈
            ".", "!", "?",    # 문장 단위
            " ", ""           # 최후 수단
        ]
    
    def split_text(self, text: str) -> List[str]:
        """텍스트를 청크로 분할"""
        chunks = []
        current_chunk = ""
        
        # 줄 단위로 처리
        lines = text.split('\n')
        
        for line in lines:
            # 현재 청크에 라인을 추가했을 때 크기 확인
            test_chunk = current_chunk + "\n" + line if current_chunk else line
            
            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                # 현재 청크 저장
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # 새 청크 시작 (overlap 고려)
                if len(chunks) > 0 and self.chunk_overlap > 0:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + "\n" + line
                else:
                    current_chunk = line
        
        # 마지막 청크 추가
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

class PDFDataLoader:
    """PDF 문서 로더 및 전처리기 - 초등학생 돌봄반용"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = SimpleTextSplitter(chunk_size, chunk_overlap)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF에서 텍스트 추출"""
        try:
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        # 페이지 구분자 추가
                        full_text += f"\n\n[페이지 {page_num}]\n{text}"
            
            logger.info(f"[OK] PDF 텍스트 추출 완료: {len(full_text)}자")
            return full_text
            
        except Exception as e:
            logger.error(f"[ERROR] PDF 텍스트 추출 실패: {e}")
            return ""
    
    def chunk_pdf_text(self, text: str, pdf_filename: str) -> List[Dict[str, Any]]:
        """다단계 Fallback을 적용한 유연한 청킹"""
        try:
            processed_chunks = []
            
            # 1단계: 규칙 번호 기반 분할 시도
            try:
                rule_chunks = self._try_rule_based_chunking(text)
                if len(rule_chunks) > 0:
                    logger.info("[OK] 규칙 기반 청킹 성공")
                    return rule_chunks
            except Exception as e:
                logger.warning(f"[WARN] 규칙 기반 청킹 실패: {e}")
            
            # 2단계: 의미 단위 분할 (Fallback #1)
            try:
                semantic_chunks = self._try_semantic_chunking(text)
                if len(semantic_chunks) > 0:
                    logger.info("[OK] 의미 기반 청킹 성공")
                    return semantic_chunks
            except Exception as e:
                logger.warning(f"[WARN] 의미 기반 청킹 실패: {e}")
            
            # 3단계: 기본 분할 (Final Fallback)
            logger.warning("[REVIEW] 기본 청킹으로 폴백")
            return self._basic_chunking(text, pdf_filename)
            
        except Exception as e:
            logger.error(f"[ERROR] 모든 청킹 방식 실패: {e}")
            return []

    def _try_rule_based_chunking(self, text: str) -> List[Dict[str, Any]]:
        """규칙 번호 기준 분할 (제N항 패턴)"""

        pattern = r'제(\d+)항\s*(.*?)(?=제\d+항|부록|\Z)'
        matches = re.findall(pattern, text, re.DOTALL)

        if len(matches) > 5:
            chunks = self._build_rule_chunks(matches, pattern)

            # 부록(문장 부호) 별도 추출 - 부호 종류별로 분할
            appendix_match = re.search(r'부록.*?문장 부호(.*?)(?=\Z)', text, re.DOTALL)
            if appendix_match:
                appendix_content = appendix_match.group(1).strip()
                # 마침표, 물음표 등 각 부호별 섹션으로 분할
                sections = re.split(r'\n(?=\d+\.\s)', appendix_content)
                for j, section in enumerate(sections):
                    section = section.strip()
                    if len(section) < 20:
                        continue
                    chunks.append({
                        "id": f"korean_grammar_appendix_{j}",
                        "text": f"[부록 문장 부호] {section}",
                        "metadata": {
                            "source": "korean_grammar_official.pdf",
                            "document_type": "official_grammar_rule",
                            "rule_number": 0,
                            "sub_index": len(chunks) + j,
                            "authority": "문화체육관광부",
                            "year": "2017",
                            "topics": "문장 부호",
                            "examples": "",
                            "difficulty_level": "elementary",
                            "chunk_method": "rule_based"
                        }
                    })

            return chunks

        raise ValueError("규칙 패턴을 찾을 수 없음")
    
    def _build_rule_chunks(self, matches: List, pattern: str) -> List[Dict[str, Any]]:
        """규칙 매칭 결과를 청크로 변환 (중복 rule_number는 긴 것 우선)"""
        seen: dict = {}  # rule_number → (index, content)

        for i, match in enumerate(matches):
            rule_number, content = match
            clean_content = content.strip()
            if len(clean_content) < 10:
                continue
            # 중복 시 더 긴 내용(더 완전한 추출)을 유지
            if rule_number not in seen or len(clean_content) > len(seen[rule_number][1]):
                seen[rule_number] = (i, clean_content)

        chunks = []
        for rule_number, (i, clean_content) in sorted(seen.items(), key=lambda x: int(x[0])):
            topics = self._extract_elementary_topics(clean_content)
            examples = self._extract_examples(clean_content)

            chunks.append({
                "id": f"korean_grammar_rule_{rule_number}",
                "text": f"제{rule_number}항: {clean_content}",
                "metadata": {
                    "source": "korean_grammar_official.pdf",
                    "document_type": "official_grammar_rule",
                    "rule_number": int(rule_number),
                    "sub_index": i,
                    "authority": "문화체육관광부",
                    "year": "2017",
                    "topics": ", ".join(topics) if topics else "",
                    "examples": ", ".join(examples) if examples else "",
                    "difficulty_level": "elementary",
                    "chunk_method": "rule_based"
                }
            })

        logger.info(f"[OK] 규칙 기반 청킹 완료: {len(chunks)}개")
        return chunks

    def _try_semantic_chunking(self, text: str) -> List[Dict[str, Any]]:
        """의미 단위 분할 (초등학생이 자주 헷갈리는 주제별)"""
        
        # 초등학생이 자주 헷갈리는 문법 키워드
        elementary_keywords = [
            "된소리", "자음", "모음", "외래어", "띄어쓰기", 
            "발음", "표기", "한자음", "받침", "어간",
            "되다", "돼다", "하다", "해다"
        ]
        
        chunks = []
        current_chunk = ""
        current_topic = "일반"
        
        lines = text.split('\n')
        for line in lines:
            # 새로운 주제 발견
            detected_topic = self._detect_topic(line, elementary_keywords)
            
            if detected_topic != current_topic and current_chunk.strip():
                # 이전 청크 저장
                chunks.append(self._create_semantic_chunk(
                    current_chunk, current_topic, len(chunks)
                ))
                current_chunk = line
                current_topic = detected_topic
            else:
                current_chunk += "\n" + line
        
        # 마지막 청크
        if current_chunk.strip():
            chunks.append(self._create_semantic_chunk(
                current_chunk, current_topic, len(chunks)
            ))
        
        if len(chunks) < 3:
            raise ValueError("의미적 분할 실패")
        
        return chunks

    def _basic_chunking(self, text: str, pdf_filename: str) -> List[Dict[str, Any]]:
        """기본 분할 (RecursiveCharacterTextSplitter)"""
        
        chunks = self.text_splitter.split_text(text)
        
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            # 최소한의 메타데이터라도 추출
            topics = self._extract_elementary_topics(chunk)
            examples = self._extract_examples(chunk)
            
            processed_chunks.append({
                "id": f"korean_grammar_basic_{i}",
                "text": chunk.strip(),
                "metadata": {
                    "source": "korean_grammar_official.pdf",
                    "document_type": "official_grammar_rule",
                    "chunking_method": "basic_fallback",
                    "chunk_index": i,
                    "topics": ", ".join(topics) if topics else "",  # 리스트 → 문자열
                    "examples": ", ".join(examples) if examples else "",  # 리스트 → 문자열
                    "authority": "문화체육관광부",
                    "year": "2017",
                    "difficulty_level": "elementary"
                }
            })
        
        logger.info(f"[OK] 기본 청킹 완료: {len(processed_chunks)}개")
        return processed_chunks

    def _detect_topic(self, text: str, keywords: List[str]) -> str:
        """텍스트에서 문법 주제 감지"""
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                return keyword
        
        return "일반"

    def _extract_elementary_topics(self, content: str) -> List[str]:
        """초등학생용 문법 주제 추출"""
        topics = []
        
        # 초등학생이 이해하기 쉬운 주제 분류
        topic_keywords = {
            "띄어쓰기": ["띄어쓰기", "띄어 쓰기", "띄우기"],
            "받침": ["받침", "자음", "ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ"],
            "모음": ["모음", "ㅏ", "ㅑ", "ㅓ", "ㅕ", "ㅗ", "ㅛ"],
            "발음": ["발음", "소리", "읽기"],
            "외래어": ["외래어", "외국어", "영어"],
            "어려운_구분": ["되다", "돼다", "하다", "해다"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content for keyword in keywords):
                topics.append(topic)
        
        return topics[:3]  # 최대 3개만

    def _extract_examples(self, content: str) -> List[str]:
        """예시 추출 (초등학생이 이해하기 쉬운 것들)"""
        examples = []
        
        # 예시 패턴들
        example_patterns = [
            r'[가-힣]+/[가-힣]+',      # 단어1/단어2 형태
            r'○\s*[가-힣\s]+',         # ○ 올바른 예시
            r'×\s*[가-힣\s]+',         # × 틀린 예시
            r'예:\s*[가-힣\s,]+',      # 예: 단어들
        ]
        
        for pattern in example_patterns:
            matches = re.findall(pattern, content)
            examples.extend(matches)
        
        # 너무 긴 예시는 제외 (초등학생용)
        clean_examples = [ex.strip() for ex in examples if len(ex.strip()) < 20]
        
        return clean_examples[:5]  # 최대 5개만

    def _create_semantic_chunk(self, content: str, topic: str, index: int) -> Dict[str, Any]:
        """의미 기반 청크 생성"""
        return {
            "id": f"korean_grammar_semantic_{topic}_{index}",
            "text": content.strip(),
            "metadata": {
                "source": "korean_grammar_official.pdf",
                "document_type": "official_grammar_rule", 
                "chunking_method": "semantic",
                "topic": topic,
                "chunk_index": index,
                "authority": "문화체육관광부",
                "year": "2017",
                "difficulty_level": "elementary"
            }
        }


# 전역 PDF 로더
pdf_loader = None

def get_pdf_loader() -> PDFDataLoader:
    """전역 PDF 로더 인스턴스 반환"""
    global pdf_loader
    if pdf_loader is None:
        pdf_loader = PDFDataLoader()
    return pdf_loader

def load_pdf_documents(pdf_directory: str = "app/data/pdfs/") -> List[Dict[str, Any]]:
    """PDF 디렉토리에서 모든 PDF 문서 로드"""
    loader = get_pdf_loader()
    all_documents = []
    
    if not os.path.exists(pdf_directory):
        logger.warning(f"PDF 디렉토리가 없습니다: {pdf_directory}")
        return []
    
    # 특정 파일만 처리 (korea_grammar_official.pdf)
    target_file = "korea_grammar_official.pdf"
    pdf_path = os.path.join(pdf_directory, target_file)
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return []
    
    logger.info(f"📄 PDF 처리 중: {target_file}")
    
    # 텍스트 추출
    full_text = loader.extract_text_from_pdf(pdf_path)
    if full_text:
        # 청킹
        chunks = loader.chunk_pdf_text(full_text, target_file)
        all_documents.extend(chunks)
        
        logger.info(f"[OK] {target_file} 처리 완료: {len(chunks)}개 청크")
    else:
        logger.error(f"[ERROR] {target_file} 텍스트 추출 실패")
    
    logger.info(f"[OK] 총 {len(all_documents)}개 PDF 문서 청크 로드 완료")
    return all_documents