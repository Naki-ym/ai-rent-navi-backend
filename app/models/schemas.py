from pydantic import BaseModel, Field

class RentPredictionRequest(BaseModel):
  area: float = Field(..., description="面積（㎡）", gt=0)
  age: int = Field(..., description="築年数", ge=0)
  distance: float = Field(..., description="最寄駅までの距離（分）", ge=0)
  rent: float = Field(..., description="現在の家賃（円）", gt=0)

class RentPredictionResponse(BaseModel):
  # 入力された条件
  input_conditions: RentPredictionRequest = Field(..., description="入力された条件")
  
  # 予測結果
  predicted_rent: float = Field(..., description="予測家賃")
  
  # 相場分析
  reasonable_range: dict = Field(..., description="適正な価格帯の範囲")
  price_evaluation: int = Field(..., description="価格評価（1:割安, 2:適正だが安い, 3:相場通り, 4:適正だが高い, 5:割高）", ge=1, le=5)