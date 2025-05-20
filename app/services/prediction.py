from app.models.schemas import RentPredictionRequest, RentPredictionResponse

def predict_rent(request: RentPredictionRequest) -> RentPredictionResponse:
  """
  モックの家賃予測ロジック
  実際のモデルが実装されるまでの仮実装
  """
  # モックの予測ロジック
  # 面積、築年数、駅からの距離から簡易的に予測家賃を計算
  base_price = 50000  # 基本家賃
  area_factor = request.area * 1000  # 1㎡あたり1000円
  age_factor = max(0, 20 - request.age) * 1000  # 築年数による減額（20年を基準）
  distance_factor = max(0, 10 - request.distance) * 2000  # 駅からの距離による減額（10分を基準）

  predicted_rent = base_price + area_factor - age_factor - distance_factor
  difference = request.rent - predicted_rent
  is_reasonable = abs(difference) <= 10000  # 1万円以内の差額を許容

  # メッセージの生成
  if difference > 10000:
    message = f"現在の家賃は相場より{difference:,.0f}円高いです。"
  elif difference < -10000:
    message = f"現在の家賃は相場より{abs(difference):,.0f}円安いです。"
  else:
    message = "現在の家賃は相場とほぼ同等です。"

  return RentPredictionResponse(
    predicted_rent=predicted_rent,
    difference=difference,
    is_reasonable=is_reasonable,
    message=message
  )
