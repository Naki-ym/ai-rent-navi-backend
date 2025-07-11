import tensorflow as tf
import joblib
import os
import json
from typing import Tuple, Dict, Any, Optional
from app.models.schemas import RentPredictionRequest
from app.models.config import ModelInfo, AppConfig
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# モデルキャッシュ
_model_cache: Dict[str, tf.keras.Model] = {}
_scaler_cache: Dict[str, Any] = {}
_config_cache: Optional[AppConfig] = None

class ModelLoader:
  """モデルとスケーラーの読み込み・管理を行うクラス"""

  def __init__(self):
    self.base_path = os.path.join(
      os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
      "saved_models"
    )

  def get_model_path(self, region: str, model_type: str) -> str:
    """
    指定された地域とモデルタイプに基づいてモデルパスを生成
    
    Args:
      region: 地域名
      model_type: モデルタイプ
    
    Returns:
      str: モデルファイルのパス
    """
    return os.path.join(self.base_path, region, model_type, "model.keras")

  def get_scaler_path(self, region: str, model_type: str) -> str:
    """
    指定された地域とモデルタイプに基づいてスケーラーパスを生成
    
    Args:
      region: 地域名
      model_type: モデルタイプ
    
    Returns:
      str: スケーラーファイルのパス
    """
    return os.path.join(self.base_path, region, model_type, "scaler.pkl")

  def load_config(self) -> AppConfig:
    """
    設定ファイルを読み込み
    
    Returns:
      AppConfig: アプリケーション設定
    
    Raises:
      FileNotFoundError: 設定ファイルが見つからない場合
      json.JSONDecodeError: 設定ファイルの形式が正しくない場合
    """
    global _config_cache
    if _config_cache is None:
      config_path = os.path.join(self.base_path, "config.json")
      if not os.path.exists(config_path):
        logger.error(f"設定ファイルが見つかりません: {config_path}")
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")
      try:
        with open(config_path, 'r', encoding='utf-8') as f:
          config_data = json.load(f)
        _config_cache = AppConfig(**config_data)
        logger.info("設定ファイルを正常に読み込みました")
      except json.JSONDecodeError as e:
        logger.error(f"設定ファイルの形式が正しくありません: {e}")
        raise
      except Exception as e:
        logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
        raise
    return _config_cache

  def determine_model_type(self, request: RentPredictionRequest, config: AppConfig) -> str:
    """
    入力データとconfig.jsonの情報に基づいて適切なモデルタイプを決定
    
    Args:
      request: 予測リクエスト
      config: アプリケーション設定
    
    Returns:
      str: モデルタイプ
    """
    # 利用可能な特徴量を確認
    available_features = set()
    
    # 基本特徴量は常に利用可能
    available_features.update(["area", "age", "layout", "station_person"])
    
    # 任意特徴量の確認
    if request.management_fee is not None:
      available_features.add("management_fee")
    if request.total_units is not None:
      available_features.add("total_units")
    
    # 地域のモデル情報を取得
    region_models = config.regions[request.region].models
    
    # 最適なモデルを選択（より多くの特徴量を使用するモデルを優先）
    best_model = None
    best_score = 0
    
    for model_name, model_info in region_models.items():
      # このモデルが使用する特徴量のうち、利用可能な特徴量の数を計算
      model_features = set(model_info.features)
      available_model_features = model_features.intersection(available_features)
      
      # 必須特徴量がすべて利用可能か確認
      required_features = set(model_info.required_features)
      if not required_features.issubset(available_features):
        continue
      
      # スコアを計算（利用可能な特徴量の数）
      score = len(available_model_features)
      
      if score > best_score:
        best_score = score
        best_model = model_name
    
    # デフォルトはbaseモデル
    if best_model is None:
      best_model = "base"
    
    logger.info(f"選択されたモデル: {best_model} (利用可能特徴量: {list(available_features)})")
    return best_model

  def get_model(self, region: str, model_type: str) -> tf.keras.Model:
    """
    指定された地域とモデルタイプのモデルを取得（キャッシュ付き）

    Args:
      region: 地域名
      model_type: モデルタイプ
    
    Returns:
      tf.keras.Model: 読み込まれたモデル
    
    Raises:
      FileNotFoundError: モデルファイルが見つからない場合
    """
    cache_key = f"{region}_{model_type}"
    if cache_key not in _model_cache:
      model_path = self.get_model_path(region, model_type)
      if not os.path.exists(model_path):
        logger.error(f"モデルファイルが見つかりません: {model_path}")
        raise FileNotFoundError(f"モデルファイルが見つかりません: {model_path}")
      try:
        logger.info(f"モデルを読み込み中: {model_path}")
        model = tf.keras.models.load_model(
          model_path,
          compile=False
        )
        model.compile(
          optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
          loss='mean_squared_error',
          metrics=['mae']
        )
        _model_cache[cache_key] = model
        logger.info(f"モデルの読み込みが完了しました: {cache_key}")
      except Exception as e:
        logger.error(f"モデルの読み込みに失敗しました: {e}")
        raise
    return _model_cache[cache_key]

  def get_scaler(self, region: str, model_type: str) -> Any:
    """
    指定された地域とモデルタイプのスケーラーを取得（キャッシュ付き）
    
    Args:
      region: 地域名
      model_type: モデルタイプ
    
    Returns:
      Any: 読み込まれたスケーラー
    
    Raises:
      FileNotFoundError: スケーラーファイルが見つからない場合
    """
    cache_key = f"{region}_{model_type}"
    if cache_key not in _scaler_cache:
      scaler_path = self.get_scaler_path(region, model_type)
      if not os.path.exists(scaler_path):
        logger.error(f"スケーラーファイルが見つかりません: {scaler_path}")
        raise FileNotFoundError(f"スケーラーファイルが見つかりません: {scaler_path}")
      try:
        logger.info(f"スケーラーを読み込み中: {scaler_path}")
        _scaler_cache[cache_key] = joblib.load(scaler_path)
        logger.info(f"スケーラーの読み込みが完了しました: {cache_key}")
      except Exception as e:
        logger.error(f"スケーラーの読み込みに失敗しました: {e}")
        raise
    return _scaler_cache[cache_key]

  def get_model_and_scaler(self, request: RentPredictionRequest) -> Tuple[tf.keras.Model, Any, ModelInfo]:
    """
    入力データに基づいて適切なモデルとスケーラーを取得
    
    Args:
      request: 予測リクエスト
    
    Returns:
      Tuple[tf.keras.Model, Any, ModelInfo]: 
        - 選択されたモデル
        - 対応するスケーラー
        - モデル情報
    
    Raises:
      ValueError: 指定された地域またはモデルタイプが見つからない場合
    """
    config = self.load_config()
    
    # 地域の存在確認
    if request.region not in config.regions:
      available_regions = list(config.regions.keys())
      logger.error(f"指定された地域が見つかりません: {request.region}")
      raise ValueError(f"指定された地域が見つかりません: {request.region}. 利用可能な地域: {available_regions}")
    
    # モデルタイプの決定
    model_type = self.determine_model_type(request, config)
    logger.info(f"モデルタイプを決定しました: {model_type}")
    
    # モデルタイプの存在確認
    if model_type not in config.regions[request.region].models:
      available_models = list(config.regions[request.region].models.keys())
      logger.error(f"指定されたモデルタイプが見つかりません: {model_type}")
      raise ValueError(f"指定されたモデルタイプが見つかりません: {model_type}. 利用可能なモデル: {available_models}")
    
    # モデルとスケーラーの取得
    model = self.get_model(request.region, model_type)
    scaler = self.get_scaler(request.region, model_type)
    model_info = config.regions[request.region].models[model_type]
    
    logger.info(f"モデルとスケーラーの取得が完了しました: {request.region}_{model_type}")
    
    return model, scaler, model_info


# グローバル関数（後方互換性のため）
_model_loader = ModelLoader()

def get_model_and_scaler(request: RentPredictionRequest) -> Tuple[tf.keras.Model, Any, ModelInfo]:
  """
  後方互換性のためのグローバル関数
  
  Args:
    request: 予測リクエスト
  
  Returns:
    Tuple[tf.keras.Model, Any, ModelInfo]: モデル、スケーラー、モデル情報
  """
  return _model_loader.get_model_and_scaler(request)
