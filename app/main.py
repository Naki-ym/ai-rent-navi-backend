from fastapi import FastAPI
from app.models.schemas import RentPredictionRequest, RentPredictionResponse
from app.services.prediction import predict_rent

app = FastAPI(
  title="家賃相場予測API",
  description="物件情報から家賃相場を予測するAPI",
  version="1.0.0"
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