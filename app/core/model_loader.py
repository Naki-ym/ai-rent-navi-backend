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

  def determine_model_type(self, request: RentPredictionRequest) -> str:
    """
    入力データに基づいて適切なモデルタイプを決定
    
    Args:
      request: 予測リクエスト
    
    Returns:
      str: モデルタイプ
    """
    has_kanrihi = request.kanrihi is not None
    has_soukosuu = request.soukosuu is not None
    has_structure = request.structure is not None
    has_station_distance = request.station_distance is not None
    if has_kanrihi and has_soukosuu and has_structure and has_station_distance:
      return "full"
    elif has_kanrihi:
      return "kanrihi"
    elif has_soukosuu:
      return "soukosuu"
    else:
      return "base"

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
