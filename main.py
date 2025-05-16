from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import sys

# DEBUG
print("[DEBUG] 현재 실행 중인 파이썬:", sys.executable)

CSV_PATH = "Nutnutrition_DB.xlsx"

# CSV 로드
try:
    df = pd.read_excel(CSV_PATH, dtype={"barcode": str})
    df.fillna("", inplace=True)
    df["barcode"] = df["barcode"].astype(str).str.strip()
    df["protein"] = df["protein"].astype(float)
    df["sugar"] = df["sugar"].astype(float)
    df["sodium"] = df["sodium"].astype(float)
    df["calories"] = df["calories"].astype(float)
    print(f"[INFO] CSV 로드 완료: {len(df)}개 항목")
except Exception as e:
    print(f"[ERROR] CSV 로드 실패: {e}")
    df = pd.DataFrame()

# FastAPI 초기화
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 요청 스키마
class BarcodeRequest(BaseModel):
    barcode: str
    disease_name: str
    protein: float
    sugar: float
    sodium: float

# ✅ API 엔드포인트
@app.post("/barcode")
def get_food_info(req: BarcodeRequest):
    print(f"[API 요청됨] barcode={req.barcode}, limits=({req.protein}, {req.sugar}, {req.sodium})")

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

    # 비교
    violation = (
        protein > req.protein
        or sugar > req.sugar
        or sodium > req.sodium
    )

    notes = (
        "Safe to consume."
        if not violation else
        f"Not recommended due to limit excess for: {req.disease_name or 'your condition'}"
    )

    return {
        "barcode": barcode,
        "itemName": item_name,
        "protein": protein,
        "sugar": sugar,
        "sodium": sodium,
        "calories": calories,
        "notes": notes,
    }

# ✅ 로컬 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
