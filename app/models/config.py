from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class FeatureDescription(BaseModel):
  """特徴量の説明情報"""
  name: str = Field(..., description="特徴量名")
  unit: str = Field(..., description="単位")
  description: str = Field(..., description="説明")

class ModelConfig(BaseModel):
  """モデル設定情報"""
  description: str = Field(..., description="モデルの説明")
  features: List[str] = Field(..., description="使用する特徴量のリスト")
  required_features: List[str] = Field(..., description="必須特徴量のリスト")
  optional_features: List[str] = Field(..., description="任意特徴量のリスト")

class RegionConfig(BaseModel):
  """地域設定情報"""
  name: str = Field(..., description="地域名")
  description: str = Field(..., description="地域の説明")
  models: Dict[str, ModelConfig] = Field(..., description="利用可能なモデル")

class ModelInfo(BaseModel):
  """モデル情報"""
  region: str = Field(..., description="地域名")
  model_type: str = Field(..., description="モデルタイプ")
  features: List[str] = Field(..., description="使用する特徴量のリスト")
  description: str = Field(..., description="モデルの説明")

class AppConfig(BaseModel):
  """アプリケーション全体の設定"""
  regions: Dict[str, RegionConfig] = Field(..., description="地域別設定")
  feature_descriptions: Dict[str, FeatureDescription] = Field(..., description="特徴量の説明") 
