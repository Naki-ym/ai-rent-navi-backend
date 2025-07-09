import os
import json
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

@app.get("/api/v1/models")
async def get_available_models():
    """
    利用可能なモデル情報を取得するエンドポイント
    """
    config_path = os.path.join(os.path.dirname(__file__), "..", "saved_models", "config.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        return {"error": "設定ファイルが見つかりません"}
    except json.JSONDecodeError:
        return {"error": "設定ファイルの形式が正しくありません"}

@app.post("/api/v1/predict", response_model=RentPredictionResponse)
async def predict_rent_endpoint(request: RentPredictionRequest):
    """
    家賃相場予測エンドポイント
    
    必須パラメータ:
    - **area**: 面積（㎡）
    - **age**: 築年数
    - **layout**: 間取り（1-12）
    - **station_person**: 駅の利用者数（千人/日）
    - **rent**: 現在の家賃（万円）
    - **region**: 地域名（例: suginami）
    
    任意パラメータ:
    - **kanrihi**: 管理費（万円）
    - **soukosuu**: 総戸数
    - **structure**: 建物構造（1:RC, 2:S, 3:SRC, 4:木造）
    - **station_distance**: 最寄り駅までの距離（分）
    
    入力されたパラメータに基づいて適切なモデルが自動選択されます。
    """
    return predict_rent(request)
