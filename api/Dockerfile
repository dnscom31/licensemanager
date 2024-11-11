# 베이스 이미지 설정
FROM python:3.9-slim

# 작업 디렉토리 설정 (api 디렉토리로 이동)
WORKDIR /app

# 현재 디렉토리의 내용 복사
COPY . /app

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 포트 노출 (필요한 경우)
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
