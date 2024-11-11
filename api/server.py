# server.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import os
from pymongo import MongoClient, ASCENDING
import logging
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import secrets


# 환경 변수 로드
load_dotenv()

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost",
    "http://localhost:8000",
    # 필요 시 추가 도메인
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션 시 특정 도메인으로 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB 연결 설정
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    logger.error("MONGODB_URI 환경 변수가 설정되지 않았습니다.")
    raise EnvironmentError("MONGODB_URI 환경 변수가 설정되지 않았습니다.")

try:
    client = MongoClient(MONGODB_URI)
    db = client["license_db"]
    licenses_collection = db["licenses"]
    # license_key에 인덱스 추가
    licenses_collection.create_index([("license_key", ASCENDING)], unique=True)
    logger.info("MongoDB 연결 성공")
except Exception as e:
    logger.error(f"MongoDB 연결 실패: {e}")
    raise e  # 초기화 실패 시 에러를 던짐

# 환경 변수에서 ADMIN_TOKEN 가져오기
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
if not ADMIN_TOKEN:
    logger.error("ADMIN_TOKEN 환경 변수가 설정되지 않았습니다.")
    raise EnvironmentError("ADMIN_TOKEN 환경 변수가 설정되지 않았습니다.")

# 요청 모델 정의
class License(BaseModel):
    user_id: str
    license_key: str
    is_valid: bool = True

class RegisterRequest(BaseModel):
    user_id: str
    license_key: str

class InvalidateRequest(BaseModel):
    license_key: str
    admin_token: str

class GenerateLicenseRequest(BaseModel):
    user_id: str

# 인증 종속성
def verify_admin_token(request: InvalidateRequest):
    if request.admin_token != ADMIN_TOKEN:
        logger.warning("Invalid admin token")
        raise HTTPException(status_code=403, detail="Invalid admin token.")
    return True

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/register_license", response_model=dict)
def register_license(request: RegisterRequest):
    logger.info(f"Register license 요청: {request.user_id}")
    try:
        # 라이선스 중복 확인
        if licenses_collection.find_one({"license_key": request.license_key}):
            logger.warning("License key 이미 존재")
            raise HTTPException(status_code=400, detail="License key already exists.")

        license = License(**request.dict())
        licenses_collection.insert_one(license.dict())
        logger.info("License 등록 성공")
        return {"status": "registered"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"register_license 에러: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/invalidate_license", response_model=dict)
def invalidate_license(request: InvalidateRequest, valid: bool = Depends(verify_admin_token)):
    logger.info(f"Invalidate license 요청: {request.license_key}")
    try:
        result = licenses_collection.update_one(
            {"license_key": request.license_key},
            {"$set": {"is_valid": False}}
        )
        if result.modified_count == 1:
            logger.info("License invalidated")
            return {"status": "invalidated"}
        else:
            logger.warning("License key not found")
            raise HTTPException(status_code=404, detail="License key not found.")
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"invalidate_license 에러: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/generate_license", response_model=dict)
def generate_license(request: GenerateLicenseRequest):
    logger.info(f"Generate license 요청: {request.user_id}")
    try:
        # 유저 ID에 기반한 고유한 라이선스 키 생성
        license_key = secrets.token_hex(16)  # 32자리 16진수 키 생성

        # 라이선스 중복 확인
        if licenses_collection.find_one({"license_key": license_key}):
            logger.warning("Generated license key already exists, regenerating...")
            # 재생성 시도
            for _ in range(5):
                license_key = secrets.token_hex(16)
                if not licenses_collection.find_one({"license_key": license_key}):
                    break
            else:
                logger.error("Failed to generate a unique license key after multiple attempts.")
                raise HTTPException(status_code=500, detail="Failed to generate a unique license key.")

        # 라이선스 객체 생성 및 데이터베이스에 저장
        license = License(user_id=request.user_id, license_key=license_key)
        licenses_collection.insert_one(license.dict())
        logger.info("License 생성 및 등록 성공")
        return {"status": "generated", "license_key": license_key}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"generate_license 에러: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/get_licenses", response_model=dict)
def get_licenses():
    logger.info("Get licenses 요청")
    try:
        licenses = list(licenses_collection.find({}, {"_id": 0}))
        logger.info("Get licenses 성공")
        return {"status": "success", "licenses": licenses}
    except Exception as e:
        logger.error(f"get_licenses 에러: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


