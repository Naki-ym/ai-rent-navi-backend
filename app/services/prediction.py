from app.models.schemas import RentPredictionRequest, RentPredictionResponse
from app.models.config import ModelInfo
from app.core.model_loader import get_model_and_scaler
from app.core.feature_mapper import FeatureMapper
from app.core.logging_config import get_logger
import numpy as np
from typing import Dict, Any

logger = get_logger(__name__)

class RentPredictionService:
  """家賃予測サービス"""
  def __init__(self):
    self.feature_mapper = FeatureMapper()
  def predict_rent(self, request: RentPredictionRequest) -> RentPredictionResponse:
    """
    家賃相場を予測する
    Args:
      request: 予測リクエスト
    Returns:
      RentPredictionResponse: 予測結果
    Raises:
      ValueError: 特徴量の抽出に失敗した場合
      Exception: 予測処理中にエラーが発生した場合
    """
    try:
      logger.info(f"予測開始: region={request.region}, area={request.area}, age={request.age}")
      model, scaler, model_info = get_model_and_scaler(request)
      input_data = self._prepare_input_data(request, model_info.features, scaler)
      logger.info(f"予測実行中: 特徴量数={len(model_info.features)}")
      input_data_scaled = scaler.transform(input_data)
      predicted_rent = float(model.predict(input_data_scaled)[0][0])
      reasonable_range = self._calculate_reasonable_range(predicted_rent)
      price_evaluation = self._evaluate_price(request.rent, predicted_rent, reasonable_range)
      logger.info(f"予測完了: 予測家賃={predicted_rent:.2f}, 評価={price_evaluation}")
      return RentPredictionResponse(
        input_conditions=request,
        model_info=model_info.dict(),
        predicted_rent=predicted_rent,
        reasonable_range=reasonable_range,
        price_evaluation=price_evaluation
      )
    except Exception as e:
      logger.error(f"予測処理中にエラーが発生しました: {e}", exc_info=True)
      raise
  def _prepare_input_data(self, request: RentPredictionRequest, features: list, scaler) -> np.ndarray:
    """
    特徴量リストに基づいて入力データを準備
    Args:
      request: 予測リクエスト
      features: 使用する特徴量のリスト
      scaler: スケーラー
    Returns:
      np.ndarray: 特徴量データ
    Raises:
      ValueError: 特徴量の抽出に失敗した場合
    """
    try:
      if not self.feature_mapper.validate_feature_list(features):
        raise ValueError("無効な特徴量リストが指定されました")
      expected_feature_count = scaler.n_features_in_
      logger.debug(f"スケーラーが期待する特徴量数: {expected_feature_count}")
      feature_values = self.feature_mapper.extract_features(request, features)
      if len(feature_values) < expected_feature_count:
        padding_needed = expected_feature_count - len(feature_values)
        feature_values.extend([0.0] * padding_needed)
        logger.warning(f"特徴量数が不足しているため、{padding_needed}個の0を追加しました")
      elif len(feature_values) > expected_feature_count:
        feature_values = feature_values[:expected_feature_count]
        logger.warning(f"特徴量数が多すぎるため、{len(feature_values) - expected_feature_count}個を切り捨てました")
      return np.array([feature_values], dtype=np.float32)
    except Exception as e:
      logger.error(f"入力データの準備に失敗しました: {e}")
      raise ValueError(f"入力データの準備に失敗しました: {e}")
  def _calculate_reasonable_range(self, predicted_rent: float) -> Dict[str, float]:
    """
    適正価格範囲を計算
    Args:
      predicted_rent: 予測家賃
    Returns:
      Dict[str, float]: 適正価格範囲
    """
    return {
      "min": predicted_rent * 0.9,
      "max": predicted_rent * 1.1
    }
  def _evaluate_price(self, current_rent: float, predicted_rent: float, reasonable_range: Dict[str, float]) -> int:
    """
    価格評価を判定（5段階）
    Args:
      current_rent: 現在の家賃
      predicted_rent: 予測家賃
      reasonable_range: 適正価格範囲
    Returns:
      int: 価格評価（1:割安, 2:適正だが安い, 3:相場通り, 4:適正だが高い, 5:割高）
    """
    if current_rent < reasonable_range["min"]:
      return 1
    elif current_rent < predicted_rent:
      return 2
    elif current_rent == predicted_rent:
      return 3
    elif current_rent <= reasonable_range["max"]:
      return 4
    else:
      return 5

prediction_service = RentPredictionService()

def predict_rent(request: RentPredictionRequest) -> RentPredictionResponse:
  """後方互換性のための関数"""
  return prediction_service.predict_rent(request)

def prepare_input_data(request: RentPredictionRequest, features: list, scaler) -> np.ndarray:
  """後方互換性のための関数"""
  return prediction_service._prepare_input_data(request, features, scaler)
