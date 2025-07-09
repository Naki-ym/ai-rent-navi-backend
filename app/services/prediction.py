from app.models.schemas import RentPredictionRequest, RentPredictionResponse
from app.core.model_loader import get_model_and_scaler
import numpy as np

def predict_rent(request: RentPredictionRequest) -> RentPredictionResponse:
    # 入力データに基づいて適切なモデルとスケーラーを取得
    model, scaler, model_info = get_model_and_scaler(request)
    
    # 特徴量を正しい順序で準備
    input_data = prepare_input_data(request, model_info["features"], scaler)
    
    # 予測実行
    input_data_scaled = scaler.transform(input_data)
    predicted_rent = float(model.predict(input_data_scaled)[0][0])
    
    # 適正価格範囲の計算
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
        model_info=model_info,
        predicted_rent=predicted_rent,
        reasonable_range=reasonable_range,
        price_evaluation=price_evaluation
    )

def prepare_input_data(request: RentPredictionRequest, features: list, scaler) -> np.ndarray:
    """特徴量リストに基づいて入力データを準備"""
    # スケーラーが期待する特徴量数を取得
    expected_feature_count = scaler.n_features_in_
    
    # 特徴量の順序を定義（スケーラーの学習時の順序に合わせる）
    all_features = ["area", "age", "layout", "station_person", "structure", "station_distance", "kanrihi", "soukosuu"]
    
    # スケーラーの特徴量数に基づいて特徴量を準備
    feature_values = []
    
    # スケーラーが期待する特徴量数分だけ値を準備
    for i in range(expected_feature_count):
        if i < len(all_features):
            feature = all_features[i]
            if feature == "area":
                feature_values.append(request.area)
            elif feature == "age":
                feature_values.append(request.age)
            elif feature == "layout":
                feature_values.append(request.layout)
            elif feature == "station_person":
                feature_values.append(request.station_person)
            elif feature == "structure":
                feature_values.append(request.structure if request.structure is not None else 1)  # デフォルト: RC
            elif feature == "station_distance":
                feature_values.append(request.station_distance if request.station_distance is not None else 5.0)  # デフォルト: 5分
            elif feature == "kanrihi":
                feature_values.append(request.kanrihi if request.kanrihi is not None else 0.0)
            elif feature == "soukosuu":
                feature_values.append(request.soukosuu if request.soukosuu is not None else 0)
        else:
            # 予期しない特徴量がある場合は0で埋める
            feature_values.append(0.0)
    
    return np.array([feature_values], dtype=np.float32)
