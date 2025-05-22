from app.models.schemas import RentPredictionRequest, RentPredictionResponse

def predict_rent(request: RentPredictionRequest) -> RentPredictionResponse:
  """
  モックの家賃予測ロジック
  実際のモデルが実装されるまでの仮実装
  """
  
  # 面積、築年数、駅からの距離から簡易的に予測家賃を計算
  base_price = 50000  # 基本家賃
  area_factor = request.area * 1000  # 1㎡あたり1000円
  age_factor = max(0, 20 - request.age) * 1000  # 築年数による減額（20年を基準）
  distance_factor = max(0, 10 - request.distance) * 2000  # 駅からの距離による減額（10分を基準）

  predicted_rent = base_price + area_factor - age_factor - distance_factor
  
  # 適正範囲の計算（予測家賃の±10%を適正範囲とする）
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
