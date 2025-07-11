import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import RentPredictionRequest, RentPredictionResponse
from app.models.config import AppConfig
from app.services.prediction import predict_rent
from app.core.logging_config import setup_logging, get_logger
from fastapi.middleware.cors import CORSMiddleware

# ログ設定の初期化
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
  title="家賃相場予測API",
  description="物件情報から家賃相場を予測するAPI",
  version="1.0.0"
)

# CORS設定
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

@app.on_event("startup")
async def startup_event():
  """アプリケーション起動時の処理"""
  logger.info("家賃相場予測APIを起動しました")

@app.on_event("shutdown")
async def shutdown_event():
  """アプリケーション終了時の処理"""
  logger.info("家賃相場予測APIを終了しました")

@app.get("/health")
async def health_check():
  """
  ヘルスチェックエンドポイント
  
  Returns:
    dict: アプリケーションの状態
  """
  logger.debug("ヘルスチェックが実行されました")
  return {"status": "healthy", "service": "rent-prediction-api"}

@app.get("/api/v1/models")
async def get_available_models():
  """
  利用可能なモデル情報を取得するエンドポイント
  
  Returns:
    dict: 利用可能な地域とモデルの情報
    
  Raises:
    HTTPException: 設定ファイルの読み込みに失敗した場合
  """
  try:
    logger.info("モデル情報の取得リクエストを受けました")
    
    config_path = os.path.join(os.path.dirname(__file__), "..", "saved_models", "config.json")
    
    if not os.path.exists(config_path):
      logger.error(f"設定ファイルが見つかりません: {config_path}")
      raise HTTPException(status_code=500, detail="設定ファイルが見つかりません")
    
    with open(config_path, 'r', encoding='utf-8') as f:
      config_data = json.load(f)
    
    # 設定の妥当性を検証
    config = AppConfig(**config_data)
    
    logger.info("モデル情報を正常に取得しました")
    return config.dict()
    
  except json.JSONDecodeError as e:
    logger.error(f"設定ファイルの形式が正しくありません: {e}")
    raise HTTPException(status_code=500, detail="設定ファイルの形式が正しくありません")
  except Exception as e:
    logger.error(f"モデル情報の取得に失敗しました: {e}")
    raise HTTPException(status_code=500, detail="モデル情報の取得に失敗しました")

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
  - **management_fee**: 管理費（万円）
  - **total_units**: 総戸数
  
  入力されたパラメータに基づいて適切なモデルが自動選択されます。
  利用可能なモデル：
  - **base**: 基本モデル（面積、築年数、間取り、駅利用者数）
  - **kanrihi**: 管理費モデル（基本特徴量＋管理費）
  - **soukosuu**: 総戸数モデル（基本特徴量＋総戸数）
  - **full**: 全特徴量モデル（基本特徴量＋管理費＋総戸数）
  
  Returns:
    RentPredictionResponse: 予測結果
    
  Raises:
    HTTPException: 予測処理中にエラーが発生した場合
  """
  try:
    logger.info(f"予測リクエストを受けました: region={request.region}")
    result = predict_rent(request)
    logger.info(f"予測が正常に完了しました: region={request.region}")
    return result
    
  except ValueError as e:
    logger.error(f"バリデーションエラー: {e}")
    raise HTTPException(status_code=400, detail=str(e))
  except FileNotFoundError as e:
    logger.error(f"モデルファイルが見つかりません: {e}")
    raise HTTPException(status_code=500, detail="モデルファイルが見つかりません")
  except Exception as e:
    logger.error(f"予測処理中にエラーが発生しました: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="予測処理中にエラーが発生しました")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
  """グローバル例外ハンドラー"""
  logger.error(f"未処理の例外が発生しました: {exc}", exc_info=True)
  return JSONResponse(
    status_code=500,
    content={"detail": "内部サーバーエラーが発生しました"}
  )
