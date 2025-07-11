from pydantic import BaseModel, Field
from typing import Optional

class RentPredictionRequest(BaseModel):
  # 必須パラメータ
  area: float = Field(..., description="面積（㎡）", gt=0)
  age: int = Field(..., description="築年数", ge=0)
  layout: int = Field(..., description="間取り（1:1K, 2:1DK, 3:1LDK, 4:2K, 5:2DK, 6:2LDK, 7:3K, 8:3DK, 9:3LDK, 10:4K, 11:4DK, 12:4LDK）", ge=1, le=12)
  station_person: int = Field(..., description="駅の利用者数（千人/日）", ge=0)
  rent: float = Field(..., description="現在の家賃（万円）", gt=0)

  # 任意パラメータ（config.jsonの特徴量名に統一）
  management_fee: Optional[float] = Field(None, description="管理費（万円）", ge=0)
  total_units: Optional[int] = Field(None, description="総戸数", gt=0)

  # 地域情報
  region: str = Field(..., description="地域名（suginami, musashino, kitaku, nakanoku, nerimaku）")

class RentPredictionResponse(BaseModel):
  # 入力された条件
  input_conditions: RentPredictionRequest = Field(..., description="入力された条件")

  # 使用されたモデル情報
  model_info: dict = Field(..., description="使用されたモデルの情報")

  # 予測結果
  predicted_rent: float = Field(..., description="予測家賃")

  # 相場分析
  reasonable_range: dict = Field(..., description="適正な価格帯の範囲")
  price_evaluation: int = Field(..., description="価格評価（1:割安, 2:適正だが安い, 3:相場通り, 4:適正だが高い, 5:割高）", ge=1, le=5)
