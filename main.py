from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# ✅ CSV 로드
CSV_PATH = "Nutnutrition_DB.csv"
try:
    df = pd.read_csv(CSV_PATH, dtype=str)
    df.fillna("", inplace=True)
    print(f"[INFO] DB 로드 완료: {len(df)}개 항목")
except Exception as e:
    print(f"[ERROR] CSV 로드 실패: {e}")
    df = pd.DataFrame()

# ✅ FastAPI 초기화
app = FastAPI()

# ✅ CORS 허용 (모든 origin 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중엔 모든 요청 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 요청 스키마
class BarcodeRequest(BaseModel):
    barcode: str

# ✅ API 엔드포인트
@app.post("/barcode")
def get_food_info(req: BarcodeRequest):
    barcode = req.barcode
    result = df[df["barcode"] == barcode]

    if result.empty:
        raise HTTPException(status_code=404, detail="해당 바코드 정보 없음")

    row = result.iloc[0]
    return {
        "barcode": row["barcode"],
        "식품명": row.get("식품명", ""),
        "열량(kcal)": row.get("열량(kcal)", ""),
        "단백질(g)": row.get("단백질(g)", ""),
        "당류(g)": row.get("당류(g)", ""),
        "나트륨(mg)": row.get("나트륨(mg)", ""),
        "등록여부": "개인DB 등록됨"
    }
