from typing import Callable, Dict, Any
from app.models.schemas import RentPredictionRequest
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class FeatureMapper:
  """特徴量マッピングを管理するクラス"""

  # 特徴量のデフォルト値
  DEFAULT_VALUES = {
    "structure": 1,        # RC
    "station_distance": 5.0,  # 5分
    "kanrihi": 0.0,        # 0万円
    "soukosuu": 0          # 0戸
  }

  # 特徴量の抽出関数マッピング
  FEATURE_EXTRACTORS: Dict[str, Callable[[RentPredictionRequest], Any]] = {
    "area": lambda req: req.area,
    "age": lambda req: req.age,
    "layout": lambda req: req.layout,
    "station_person": lambda req: req.station_person,
    "structure": lambda req: req.structure or FeatureMapper.DEFAULT_VALUES["structure"],
    "station_distance": lambda req: req.station_distance or FeatureMapper.DEFAULT_VALUES["station_distance"],
    "kanrihi": lambda req: req.kanrihi or FeatureMapper.DEFAULT_VALUES["kanrihi"],
    "soukosuu": lambda req: req.soukosuu or FeatureMapper.DEFAULT_VALUES["soukosuu"]
  }

  @classmethod
  def extract_features(cls, request: RentPredictionRequest, feature_list: list) -> list:
    """
    リクエストから指定された特徴量を抽出
    
    Args:
      request: 予測リクエスト
      feature_list: 抽出する特徴量のリスト
    
    Returns:
      list: 特徴量値のリスト
    
    Raises:
      ValueError: 不明な特徴量が指定された場合
    """
    feature_values = []
    for feature in feature_list:
      if feature not in cls.FEATURE_EXTRACTORS:
        raise ValueError(f"不明な特徴量: {feature}")
      try:
        value = cls.FEATURE_EXTRACTORS[feature](request)
        feature_values.append(value)
        logger.debug(f"特徴量 '{feature}' の値を抽出: {value}")
      except Exception as e:
        logger.error(f"特徴量 '{feature}' の抽出に失敗: {e}")
        raise
    return feature_values

  @classmethod
  def get_available_features(cls) -> list:
    """利用可能な特徴量のリストを取得"""
    return list(cls.FEATURE_EXTRACTORS.keys())

  @classmethod
  def validate_feature_list(cls, feature_list: list) -> bool:
    """特徴量リストの妥当性を検証"""
    available_features = cls.get_available_features()
    invalid_features = [f for f in feature_list if f not in available_features]
    if invalid_features:
      logger.error(f"無効な特徴量: {invalid_features}")
      return False
    return True 
