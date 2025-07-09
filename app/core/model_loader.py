import tensorflow as tf
import joblib
import os
from typing import Tuple, Dict, Any
from app.models.schemas import RentPredictionRequest

# モデルキャッシュ
_model_cache: Dict[str, tf.keras.Model] = {}
_scaler_cache: Dict[str, Any] = {}

def get_model_path(region: str, model_type: str) -> str:
    """指定された地域とモデルタイプに基づいてモデルパスを生成"""
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saved_models")
    return os.path.join(base_path, region, model_type, "model.keras")

def get_scaler_path(region: str, model_type: str) -> str:
    """指定された地域とモデルタイプに基づいてスケーラーパスを生成"""
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saved_models")
    return os.path.join(base_path, region, model_type, "scaler.pkl")

def determine_model_type(request: RentPredictionRequest) -> str:
    """入力データに基づいて適切なモデルタイプを決定"""
    has_kanrihi = request.kanrihi is not None
    has_soukosuu = request.soukosuu is not None
    
    if has_kanrihi and has_soukosuu:
        return "full"
    elif has_kanrihi:
        return "kanrihi"
    elif has_soukosuu:
        return "soukosuu"
    else:
        return "base"

def get_model(region: str, model_type: str) -> tf.keras.Model:
    """指定された地域とモデルタイプのモデルを取得（キャッシュ付き）"""
    cache_key = f"{region}_{model_type}"
    
    if cache_key not in _model_cache:
        model_path = get_model_path(region, model_type)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"モデルファイルが見つかりません: {model_path}")
        
        try:
            # TensorFlow 2.18.0用の読み込み方法
            model = tf.keras.models.load_model(
                model_path,
                compile=False  # コンパイルをスキップ
            )
            # モデルを再コンパイル
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
                loss='mean_squared_error',
                metrics=['mae']
            )
            _model_cache[cache_key] = model
        except Exception as e:
            print(f"モデルの読み込みに失敗しました: {e}")
            raise
    
    return _model_cache[cache_key]

def get_scaler(region: str, model_type: str) -> Any:
    """指定された地域とモデルタイプのスケーラーを取得（キャッシュ付き）"""
    cache_key = f"{region}_{model_type}"
    
    if cache_key not in _scaler_cache:
        scaler_path = get_scaler_path(region, model_type)
        
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"スケーラーファイルが見つかりません: {scaler_path}")
        
        try:
            _scaler_cache[cache_key] = joblib.load(scaler_path)
        except Exception as e:
            print(f"スケーラーの読み込みに失敗しました: {e}")
            raise
    
    return _scaler_cache[cache_key]

def get_model_and_scaler(request: RentPredictionRequest) -> Tuple[tf.keras.Model, Any, Dict[str, Any]]:
    """入力データに基づいて適切なモデルとスケーラーを取得"""
    region = request.region.lower()
    model_type = determine_model_type(request)
    
    model = get_model(region, model_type)
    scaler = get_scaler(region, model_type)
    
    model_info = {
        "region": region,
        "model_type": model_type,
        "features": get_feature_list(model_type)
    }
    
    return model, scaler, model_info

def get_feature_list(model_type: str) -> list:
    """モデルタイプに基づいて特徴量リストを取得"""
    if model_type == "base":
        return ["area", "age", "layout", "station_person"]
    elif model_type == "kanrihi":
        return ["area", "age", "layout", "station_person", "kanrihi"]
    elif model_type == "soukosuu":
        return ["area", "age", "layout", "station_person", "soukosuu"]
    elif model_type == "full":
        # 8つの特徴量: 面積, 築年数, 間取り, 駅利用者数, 構造, 最寄り駅1, 管理費, 総戸数
        return ["area", "age", "layout", "station_person", "structure", "station_distance", "kanrihi", "soukosuu"]
    else:
        raise ValueError(f"不明なモデルタイプ: {model_type}")

# 後方互換性のための関数
def get_model_legacy():
    """後方互換性のための関数（非推奨）"""
    return get_model("suginami", "base")

def get_scaler_legacy():
    """後方互換性のための関数（非推奨）"""
    return get_scaler("suginami", "base")
