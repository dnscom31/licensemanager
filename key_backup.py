#generate_license_key.py
import hashlib
import base64
from cryptography.fernet import Fernet

LICENSE_KEY_PREFIX = "MYAPP"
LICENSE_KEY_SECRET = "your_secret_here"

# Generate a key for encryption
def generate_encryption_key():
    return base64.urlsafe_b64encode(hashlib.sha256(LICENSE_KEY_SECRET.encode()).digest())

def encrypt_user_number(user_number, key):
    f = Fernet(key)
    return f.encrypt(str(user_number).encode()).decode()

def generate_license_key(user_id, user_number):
    combined_string = f"{LICENSE_KEY_PREFIX}{user_id}{LICENSE_KEY_SECRET}"
    license_key = hashlib.sha256(combined_string.encode()).hexdigest()
    key = generate_encryption_key()
    encrypted_user_number = encrypt_user_number(user_number, key)
    return f"{license_key}#{encrypted_user_number}"

def main():
    while True:
        user_id = input("Enter the user ID to generate a license key (or 'q' to quit): ")
        if user_id.lower() == 'q':
            break
        user_number = int(input("Enter a number: "))
        license_key = generate_license_key(user_id, user_number)
        print(f"Generated license key for user {user_id}: {license_key}")

if __name__ == "__main__":
    main()
