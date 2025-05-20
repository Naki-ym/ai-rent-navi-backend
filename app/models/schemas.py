from pydantic import BaseModel, Field

class RentPredictionRequest(BaseModel):
  area: float = Field(..., description="面積（㎡）", gt=0)
  age: int = Field(..., description="築年数", ge=0)
  distance: float = Field(..., description="最寄駅までの距離（分）", ge=0)
  rent: float = Field(..., description="現在の家賃（円）", gt=0)

class RentPredictionResponse(BaseModel):
  predicted_rent: float = Field(..., description="予測家賃")
  difference: float = Field(..., description="現在の家賃との差額")
  is_reasonable: bool = Field(..., description="相場に対して適正かどうか")
  message: str = Field(..., description="相場との比較メッセージ") 