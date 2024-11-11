# 베이스 이미지 설정
FROM python:3.9-slim

# 시스템 패키지 업데이트 및 OpenSSL 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 패키지 설치
COPY api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 전체 애플리케이션 코드 복사
COPY . /app

# 포트 노출 (필요한 경우)
EXPOSE 8000

# 애플리케이션 실행
CMD ["sh", "-c", "uvicorn api.server:app --host 0.0.0.0 --port ${PORT}"]


