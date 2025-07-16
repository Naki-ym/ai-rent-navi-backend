import logging
import sys
from typing import Dict, Any

def setup_logging() -> None:
  """アプリケーション全体のログ設定を初期化"""
  # ログフォーマットの設定
  log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format = "%Y-%m-%d %H:%M:%S"
  # ルートロガーの設定
  logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=date_format,
    handlers=[
      logging.StreamHandler(sys.stdout)
    ]
  )
  # 特定のライブラリのログレベルを調整
  logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
  logging.getLogger("tensorflow").setLevel(logging.WARNING)
  logging.getLogger("sklearn").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
  """指定された名前のロガーを取得"""
  return logging.getLogger(name)

class LoggerMixin:
  """ログ機能を提供するMixinクラス"""
  @property
  def logger(self) -> logging.Logger:
    """インスタンス固有のロガーを取得"""
    return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}") 
