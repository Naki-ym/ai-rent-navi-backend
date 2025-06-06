# 家賃相場予測アプリケーション - バックエンド

このプロジェクトは、家賃相場予測アプリケーションのバックエンド部分です。FastAPIを使用して、物件情報と家賃を入力すると、その家賃が相場と比較してどうなのかを予測するAPIを提供します。予測には事前に学習済みのTensorFlowモデルを使用します。

## プロジェクト構成

```
backend/                 # バックエンド（FastAPI）
├── app/
│   ├── api/            # APIエンドポイント
│   │   ├── __init__.py
│   │   └── routes.py   # ルーティング定義
│   ├── core/           # コア機能
│   │   ├── __init__.py
│   │   └── model_loader.py   # モデル読み込み
│   ├── models/         # データモデル
│   │   ├── __init__.py
│   │   └── schemas.py  # Pydanticモデル（リクエスト/レスポンスの型定義）
│   ├── services/       # ビジネスロジック
│   │   ├── __init__.py
│   │   └── prediction.py # 予測ロジック
│   └── main.py         # アプリケーションのエントリーポイント
├── saved_models/       # 学習済みモデル
│   ├── model.keras     # TensorFlowモデル
│   └── scaler.pkl      # スケーラー
├── Dockerfile          # バックエンド用Dockerfile
├── docker-compose.yml  # Docker Compose設定
├── requirements.txt    # Python依存関係
└── .gitignore
```

## 技術スタック

- FastAPI: 高速なAPIフレームワーク
- Pydantic: データバリデーション
- TensorFlow: 学習済みモデルの読み込みと推論
- scikit-learn: データの前処理（StandardScaler）
- Docker: コンテナ化

## データモデル（app/models）

`app/models` ディレクトリでは、APIのリクエストとレスポンスの型定義を行います。主な役割は：

1. リクエストデータのバリデーション
2. レスポンスデータの型保証
3. OpenAPI（Swagger）ドキュメントの自動生成

### 使用例（schemas.py）

```python
from pydantic import BaseModel, Field

class RentPredictionRequest(BaseModel):
    area: float = Field(..., description="面積（㎡）", gt=0)
    age: int = Field(..., description="築年数", ge=0)
    layout: int = Field(..., description="間取り（1:1K, 2:1DK, 3:1LDK, 4:2K, 5:2DK, 6:2LDK, 7:3K, 8:3DK, 9:3LDK, 10:4K, 11:4DK, 12:4LDK）", ge=1, le=12)
    station_person: int = Field(..., description="駅の利用者数（千人/日）", ge=0)
    rent: float = Field(..., description="現在の家賃（万円）", gt=0)

class RentPredictionResponse(BaseModel):
    input_conditions: RentPredictionRequest
    predicted_rent: float
    reasonable_range: dict
    price_evaluation: int
```

## 開発環境のセットアップ

1. リポジトリのクローン
```bash
git clone [repository-url]
cd rent_prediction/backend
```

2. 学習済みモデルの配置
```bash
# saved_models/ ディレクトリに以下を配置
# - model.keras（TensorFlowモデル）
# - scaler.pkl（スケーラー）
```

3. Dockerコンテナの起動
```bash
docker-compose up --build
```

## API仕様

### 家賃相場予測API

- エンドポイント: `/api/v1/predict`
- メソッド: POST
- リクエストボディ:
```json
{
  "area": float,          // 面積（㎡）
  "age": int,            // 築年数
  "layout": int,         // 間取り（1-12）
  "station_person": int, // 駅の利用者数（千人/日）
  "rent": float         // 現在の家賃（万円）
}
```
- レスポンス:
```json
{
  "input_conditions": {
    "area": float,
    "age": int,
    "layout": int,
    "station_person": int,
    "rent": float
  },
  "predicted_rent": float,  // 予測家賃（万円）
  "reasonable_range": {
    "min": float,  // 適正価格の下限（万円）
    "max": float   // 適正価格の上限（万円）
  },
  "price_evaluation": int  // 価格評価（1:割安, 2:適正だが安い, 3:相場通り, 4:適正だが高い, 5:割高）
}
```

## APIのテスト方法

### Postmanを使用したテスト

1. **新しいリクエストの作成**
   - メソッド: `POST`
   - URL: `http://localhost:8000/api/v1/predict`
   - Headers: `Content-Type: application/json`

2. **テストケース例**

基本ケース:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 8.0
}
```

高めの家賃:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 10.0
}
```

安めの家賃:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 6.0
}
```

古い物件:
```json
{
    "area": 30.0,
    "age": 30,
    "layout": 3,
    "station_person": 100,
    "rent": 8.0
}
```

駅の利用者数が多い物件:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 500,
    "rent": 8.0
}
```

3. **バリデーションテスト**

負の値:
```json
{
    "area": -30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 8.0
}
```

不正な間取り:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 13,
    "station_person": 100,
    "rent": 8.0
}
```

## 開発ガイドライン

### コード規約
- PEP 8に準拠
- 型ヒントの使用を推奨
- ドキュメンテーション文字列（docstring）の記述を必須

### テスト
- 各APIエンドポイントに対するユニットテスト
- 統合テストの実装
- テストカバレッジの維持

### エラーハンドリング
- 適切なHTTPステータスコードの使用
- エラーメッセージの統一
- ログ出力の実装

## デプロイメント

### 本番環境
- Dockerコンテナの使用
- 環境変数による設定管理
- ヘルスチェックエンドポイントの実装

### モニタリング
- ログ収集
- パフォーマンスモニタリング
- エラー通知
