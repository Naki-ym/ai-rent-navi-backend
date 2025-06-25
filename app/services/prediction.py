from app.models.schemas import RentPredictionRequest, RentPredictionResponse
from app.core.model_loader import get_model, get_scaler
import numpy as np

def predict_rent(request: RentPredictionRequest) -> RentPredictionResponse:
  model = get_model()
  scaler = get_scaler()
  
  # 4つの特徴量を正しい順序で設定
  input_data = np.array([[
    request.area,      # 面積_数値
    request.age,       # 築年数
  ]], dtype=np.float32)
  
  input_data_scaled = scaler.transform(input_data)
  predicted_rent = float(model.predict(input_data_scaled)[0][0])
  
  reasonable_range = {
    "min": predicted_rent * 0.9,
    "max": predicted_rent * 1.1
  }
  
  # 価格評価の判定（5段階）
  if request.rent < reasonable_range["min"]:
    price_evaluation = 1  # 割安
  elif request.rent < predicted_rent:
    price_evaluation = 2  # 適正だが安い
  elif request.rent == predicted_rent:
    price_evaluation = 3  # 相場通り
  elif request.rent <= reasonable_range["max"]:
    price_evaluation = 4  # 適正だが高い
  else:
    price_evaluation = 5  # 割高

  return RentPredictionResponse(
    input_conditions=request,
    predicted_rent=predicted_rent,
    reasonable_range=reasonable_range,
    price_evaluation=price_evaluation
  )
