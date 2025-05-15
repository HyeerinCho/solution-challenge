from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
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

    # 🔥 바코드 문자열 변환 + 공백 제거
    df["barcode"] = df["barcode"].astype(str).str.strip()

    # float 변환
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

# ✅ FastAPI 앱 초기화
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
    disease_ids: List[int]

# ✅ API 엔드포인트
@app.post("/barcode")
def get_food_info(req: BarcodeRequest):
    print(f"[API 요청됨] barcode={req.barcode}, diseases={req.disease_ids}")
    print(f"[DEBUG] 바코드 비교 대상들: {df['barcode'].tolist()[:5]}")

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

    # ✅ 질환 제한 비교
    violations = []
    for d in disease_limits:
        if d["diseaseId"] in req.disease_ids:
            if (
                protein > d["proteinLimit"]
                or sugar > d["sugarLimit"]
                or sodium > d["sodiumLimit"]
            ):
                violations.append(f'{d["diseaseName"]}: {d["notes"]}')

    notes = "Safe to consume." if not violations else "Not recommended: " + "; ".join(violations)

    return {
        "barcode": barcode,
        "itemName": item_name,
        "protein": protein,
        "sugar": sugar,
        "sodium": sodium,
        "calories": calories,
        "notes": notes,
    }

# ✅ 직접 실행 시
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
