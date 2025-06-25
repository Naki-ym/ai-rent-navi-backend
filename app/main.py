import os
from fastapi import FastAPI
from app.models.schemas import RentPredictionRequest, RentPredictionResponse
from app.services.prediction import predict_rent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
  title="家賃相場予測API",
  description="物件情報から家賃相場を予測するAPI",
  version="1.0.0"
)

cors_origins_env = os.environ.get("CORS_ORIGINS")
if cors_origins_env:
    cors_origins = cors_origins_env.split(",")
else:
    cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
  """
  ヘルスチェックエンドポイント
  """
  return {"status": "healthy"}

@app.post("/api/v1/predict", response_model=RentPredictionResponse)
async def predict_rent_endpoint(request: RentPredictionRequest):
  """
  家賃相場予測エンドポイント
  
  - **area**: 面積（㎡）
  - **age**: 築年数
  - **distance**: 最寄駅までの距離（分）
  - **rent**: 現在の家賃（円）
  """
  return predict_rent(request)
