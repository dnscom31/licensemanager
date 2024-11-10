import requests

url = "https://licesne-generator.fly.dev"
headers = {
    "Admin-Token": "FlyV1 fm2_lJPECAAAAAAAB9FKxBDkwRzyJoQRs1OTxzw1ADfAwrVodHRwczovL2FwaS5mbHkuaW8vdjGWAJLOAA06wR8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDy+/9VMRP7QLOgk7nZjt0HVO10BNRtIhkUhW4kFFgoR2rr9iu/QR/O4mKo7GRfYlg5qhZ1v95SDCIIoe37EToWavkX+GkQPBflTf6pvaG9mbpQnFDvmarGIUxeSaBgXUX0q3P6Lga0dz0wGBv5zrNPin9yMWfs/wrHdt8Ab+/U7z5rPy0cJrtM6RDKJ9Q2SlAORgc4AT5EiHwWRgqdidWlsZGVyH6J3Zx8BxCAsCRBKJ8FMfNGRLg+fymYAmJ1Glac8UUAO0yfUI3qjsw==,fm2_lJPEToWavkX+GkQPBflTf6pvaG9mbpQnFDvmarGIUxeSaBgXUX0q3P6Lga0dz0wGBv5zrNPin9yMWfs/wrHdt8Ab+/U7z5rPy0cJrtM6RDKJ9cQQT8L2k6yl4lAMNVRGVD4v3MO5aHR0cHM6Ly9hcGkuZmx5LmlvL2FhYS92MZgEks5nMKPwzwAAAAEjKMIOF84ADNFACpHOAAzRQAzEEGuck3bSi3qCWdozFx2sR+nEIDl6mH3r0tl7AorjW08jV1/rcZ0g8t4g+xKS/h4XbEiR"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(response.json())  # JSON 응답을 받을 경우
    # print(response.text)  # 텍스트 응답을 받을 경우
except requests.exceptions.RequestException as e:
    print(f"요청 중 오류가 발생했습니다: {e}")
