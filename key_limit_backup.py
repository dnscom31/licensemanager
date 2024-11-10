# generate_license_key.py
import hashlib
import base64
from cryptography.fernet import Fernet
import os
import uuid

LICENSE_KEY_PREFIX = "MYAPP"
LICENSE_KEY_SECRET = "your_secret_here"
LICENSE_DATA_FILE = "license_data.dat"
MAX_LICENSE_COUNT = 100

# 암호화 키 생성
def generate_encryption_key():
    return base64.urlsafe_b64encode(hashlib.sha256(LICENSE_KEY_SECRET.encode()).digest())

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(data, key):
    f = Fernet(key)
    return f.decrypt(data.encode()).decode()

def get_mac_address():
    return hex(uuid.getnode())

def initialize_license_data(key):
    mac_address = get_mac_address()
    encrypted_mac = encrypt_data(mac_address, key)
    license_count = '0'
    encrypted_count = encrypt_data(license_count, key)
    with open(LICENSE_DATA_FILE, 'w') as f:
        f.write(f"{encrypted_mac}\n{encrypted_count}")

def read_license_data(key):
    with open(LICENSE_DATA_FILE, 'r') as f:
        encrypted_mac = f.readline().strip()
        encrypted_count = f.readline().strip()
    mac_address = decrypt_data(encrypted_mac, key)
    license_count = int(decrypt_data(encrypted_count, key))
    return mac_address, license_count

def write_license_data(mac_address, license_count, key):
    encrypted_mac = encrypt_data(mac_address, key)
    encrypted_count = encrypt_data(str(license_count), key)
    with open(LICENSE_DATA_FILE, 'w') as f:
        f.write(f"{encrypted_mac}\n{encrypted_count}")

def generate_license_key(user_id, user_number):
    combined_string = f"{LICENSE_KEY_PREFIX}{user_id}{LICENSE_KEY_SECRET}"
    license_key = hashlib.sha256(combined_string.encode()).hexdigest()
    key = generate_encryption_key()
    encrypted_user_number = encrypt_data(str(user_number), key)
    return f"{license_key}#{encrypted_user_number}"

def main():
    key = generate_encryption_key()

    # 라이선스 데이터 파일 존재 여부 확인
    if not os.path.exists(LICENSE_DATA_FILE):
        # 라이선스 데이터 초기화
        initialize_license_data(key)
    else:
        # 라이선스 데이터 읽기
        stored_mac_address, license_count = read_license_data(key)
        current_mac_address = get_mac_address()
        if stored_mac_address != current_mac_address:
            print("이 프로그램은 이 컴퓨터에서만 실행할 수 있습니다.")
            return
        if license_count >= MAX_LICENSE_COUNT:
            print("최대 라이선스 생성 수에 도달했습니다. 더 이상 라이선스를 생성할 수 없습니다.")
            return

    while True:
        user_id = input("라이선스 키를 생성할 사용자 ID를 입력하세요 (종료하려면 'q' 입력): ")
        if user_id.lower() == 'q':
            break
        try:
            user_number = int(input("숫자를 입력하세요: "))
        except ValueError:
            print("유효한 숫자를 입력하세요.")
            continue
        license_key = generate_license_key(user_id, user_number)
        # 라이선스 데이터 읽기
        stored_mac_address, license_count = read_license_data(key)
        # 라이선스 카운트 증가
        license_count += 1
        # 업데이트된 라이선스 데이터 저장
        write_license_data(stored_mac_address, license_count, key)
        print(f"사용자 {user_id}에 대한 라이선스 키가 생성되었습니다: {license_key}")
        print(f"현재 생성된 라이선스 수: {license_count}/{MAX_LICENSE_COUNT}")

if __name__ == "__main__":
    main()
