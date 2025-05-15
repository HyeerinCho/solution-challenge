import requests

res = requests.post(
    "https://solution-challenge-9bby.onrender.com/barcode",
    json={
        "barcode": "8809423780375",
        "disease_ids": [1, 3]
    }
)

print(res.status_code)
print(res.json())
