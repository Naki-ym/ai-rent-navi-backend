from pydantic import BaseModel, Field
from typing import List, Dict, Optional

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
  model_format: str = Field(..., description="モデルの形式")
  scaler_format: str = Field(..., description="スケーラーの形式")
  last_updated: str = Field(..., description="最終更新日時") 
