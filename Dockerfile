# 로컬과 동일한 파이썬 버전 사용(예: Python 3.12)
FROM python:3.12-slim

LABEL authors="gimgawon"

WORKDIR /app

# requirements.txt가 있을 경우, 복사 & 설치
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 소스코드 전체 복사
COPY . .

# (필요하다면 포트 오픈, FastAPI의 기본 포트 8000)
EXPOSE 8000

# FastAPI 앱 실행 예시
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
