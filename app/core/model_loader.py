import tensorflow as tf
import joblib
import os

# 相対パスに修正
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saved_models", "model.keras")
SCALER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saved_models", "scaler.pkl")

_model = None
_scaler = None

def get_model():
    global _model
    if _model is None:
        try:
            # TensorFlow 2.18.0用の読み込み方法
            _model = tf.keras.models.load_model(
                MODEL_PATH,
                compile=False  # コンパイルをスキップ
            )
            # モデルを再コンパイル
            _model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
                loss='mean_squared_error',
                metrics=['mae']
            )
        except Exception as e:
            print(f"モデルの読み込みに失敗しました: {e}")
            raise
    return _model

def get_scaler():
    global _scaler
    if _scaler is None:
        try:
            _scaler = joblib.load(SCALER_PATH)
        except Exception as e:
            print(f"スケーラーの読み込みに失敗しました: {e}")
            raise
    return _scaler