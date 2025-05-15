import requests

response = requests.post(
    "http://127.0.0.1:8000/barcode",
    json={
        "barcode": "8809423780375",  # 확인된 바코드
        "disease_ids": [1, 3]         # 아무 질환 ID 테스트용
    }
)

print(response.status_code)
print(response.json())
