# 기존 Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# 캐시 정리 및 최적화된 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip cache purge

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]