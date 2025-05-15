from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import sys

print("[DEBUG] 현재 실행 중인 파이썬:", sys.executable)
print("[DEBUG] sys.path:", sys.path)
print("[DEBUG] fastapi 로드 성공 ✅")

# ✅ 파일 경로
CSV_PATH = "Nutnutrition_DB.xlsx"
JSON_PATH = "disease_limits.json"

# ✅ CSV 로드
try:
    df = pd.read_excel(CSV_PATH, dtype={"barcode": str})
    df.fillna("", inplace=True)

    df["barcode"] = df["barcode"].astype(str).str.strip()
    df["protein"] = df["protein"].astype(float)
    df["sugar"] = df["sugar"].astype(float)
    df["sodium"] = df["sodium"].astype(float)
    df["calories"] = df["calories"].astype(float)

    print(df["barcode"].head(10))
    print(f"[INFO] CSV 로드 완료: {len(df)}개 항목")
except Exception as e:
    print(f"[ERROR] CSV 로드 실패: {e}")
    df = pd.DataFrame()

# ✅ JSON 로드
try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        disease_limits = json.load(f)
    print(f"[INFO] 질환 제한 로드 완료: {len(disease_limits)}개")
except Exception as e:
    print(f"[ERROR] JSON 로드 실패: {e}")
    disease_limits = []

# ✅ FastAPI 초기화
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 요청 스키마 (문자열)
class BarcodeRequest(BaseModel):
    barcode: str
    disease_name: str  # ✔️ 하나만 받음

# ✅ API 엔드포인트
@app.post("/barcode")
def get_food_info(req: BarcodeRequest):
    print(f"[API 요청됨] barcode={req.barcode}, disease={req.disease_name}")

    barcode = req.barcode.strip()
    result = df[df["barcode"] == barcode]

    if result.empty:
        raise HTTPException(status_code=404, detail="해당 바코드 정보 없음")

    row = result.iloc[0]
    protein = row["protein"]
    sugar = row["sugar"]
    sodium = row["sodium"]
    item_name = row["itemName"]
    calories = row["calories"]

    # ✅ 해당 질환 기준 찾기
    disease = next((d for d in disease_limits if d["diseaseName"] == req.disease_name), None)

    if not disease:
        raise HTTPException(status_code=400, detail="해당 질환 이름이 존재하지 않음")

    violation = (
        protein > disease["proteinLimit"]
        or sugar > disease["sugarLimit"]
        or sodium > disease["sodiumLimit"]
    )

    notes = "Safe to consume." if not violation else f'Not recommended: {disease["diseaseName"]}: {disease["notes"]}'

    return {
        "barcode": barcode,
        "itemName": item_name,
        "protein": protein,
        "sugar": sugar,
        "sodium": sodium,
        "calories": calories,
        "notes": notes,
    }

# ✅ 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
