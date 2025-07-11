# 家賃相場予測アプリケーション - バックエンド

このプロジェクトは、家賃相場予測アプリケーションのバックエンド部分です。FastAPIを使用して、物件情報と家賃を入力すると、その家賃が相場と比較してどうなのかを予測するAPIを提供します。予測には事前に学習済みのTensorFlowモデルを使用し、入力データに基づいて適切なモデルを自動選択します。

## プロジェクト構成

```
backend/                 # バックエンド（FastAPI）
├── app/
│   ├── api/            # APIエンドポイント
│   │   ├── __init__.py
│   │   └── routes.py   # ルーティング定義
│   ├── core/           # コア機能
│   │   ├── __init__.py
│   │   ├── feature_mapper.py  # 特徴量マッピング
│   │   ├── logging_config.py  # ログ設定
│   │   └── model_loader.py    # モデル読み込み・選択
│   ├── models/         # データモデル
│   │   ├── __init__.py
│   │   ├── config.py   # 設定モデル
│   │   └── schemas.py  # Pydanticモデル（リクエスト/レスポンスの型定義）
│   ├── services/       # ビジネスロジック
│   │   ├── __init__.py
│   │   └── prediction.py # 予測ロジック
│   └── main.py         # アプリケーションのエントリーポイント
├── saved_models/       # 学習済みモデル
│   ├── config.json     # モデル設定ファイル（全地域・モデル情報）
│   ├── suginami/       # 地域別モデル
│   │   ├── base/       # 基本モデル（必須パラメータのみ）
│   │   │   ├── model.keras
│   │   │   └── scaler.pkl
│   │   ├── kanrihi/    # 管理費を含むモデル
│   │   │   ├── model.keras
│   │   │   └── scaler.pkl
│   │   ├── soukosuu/   # 総戸数を含むモデル
│   │   │   ├── model.keras
│   │   │   └── scaler.pkl
│   │   └── full/       # 全特徴量を含むモデル
│   │       ├── model.keras
│   │       └── scaler.pkl
│   └── [他の地域]/     # 他の地域モデル（musashino, kitaku, nakanoku, nerimaku）
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

## 自動モデル選択システム

このシステムは、`config.json`の情報と入力データに基づいて最適なモデルを自動選択します：

### 基本特徴量（必須）
- 面積（㎡）
- 築年数
- 間取り（1-12）
- 駅利用者数（千人/日）

### 追加特徴量（任意）
- 管理費（万円）
- 総戸数

### 自動モデル選択ロジック
1. **基本モデル（base）**: 基本特徴量のみ使用
2. **管理費モデル（kanrihi）**: 基本特徴量 + 管理費
3. **総戸数モデル（soukosuu）**: 基本特徴量 + 総戸数
4. **全特徴量モデル（full）**: 基本特徴量 + 管理費 + 総戸数

システムは入力された特徴量を分析し、利用可能な特徴量を最大限活用できるモデルを自動選択します。

### config.jsonの構造
```json
{
  "regions": {
    "suginami": {
      "name": "杉並区",
      "models": {
        "base": {
          "features": ["area", "age", "layout", "station_person"],
          "required_features": ["area", "age", "layout", "station_person"]
        },
        "kanrihi": {
          "features": ["area", "age", "layout", "station_person", "management_fee"],
          "required_features": ["area", "age", "layout", "station_person", "management_fee"]
        }
      }
    }
  }
}
```

## データモデル（app/models）

`app/models` ディレクトリでは、APIのリクエストとレスポンスの型定義を行います。主な役割は：

1. リクエストデータのバリデーション
2. レスポンスデータの型保証
3. OpenAPI（Swagger）ドキュメントの自動生成

### 使用例（schemas.py）

```python
from pydantic import BaseModel, Field
from typing import Optional

class RentPredictionRequest(BaseModel):
    # 必須パラメータ
    area: float = Field(..., description="面積（㎡）", gt=0)
    age: int = Field(..., description="築年数", ge=0)
    layout: int = Field(..., description="間取り（1-12）", ge=1, le=12)
    station_person: int = Field(..., description="駅の利用者数（千人/日）", ge=0)
    rent: float = Field(..., description="現在の家賃（万円）", gt=0)
    region: str = Field(..., description="地域名（例: suginami）")
    
    # 任意パラメータ（config.jsonの特徴量名に統一）
    management_fee: Optional[float] = Field(None, description="管理費（万円）", ge=0)
    total_units: Optional[int] = Field(None, description="総戸数", gt=0)

class RentPredictionResponse(BaseModel):
    input_conditions: RentPredictionRequest
    model_info: dict  # 使用されたモデルの情報
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
# - suginami/base/model.keras（基本モデル）
# - suginami/base/scaler.pkl（基本スケーラー）
# - suginami/kanrihi/model.keras（管理費モデル）
# - suginami/kanrihi/scaler.pkl（管理費スケーラー）
# - suginami/soukosuu/model.keras（総戸数モデル）
# - suginami/soukosuu/scaler.pkl（総戸数スケーラー）
# - suginami/full/model.keras（全特徴量モデル）
# - suginami/full/scaler.pkl（全特徴量スケーラー）
```

3. Dockerコンテナの起動
```bash
docker-compose up --build
```

## API仕様

### 利用可能モデル情報取得API

- エンドポイント: `/api/v1/models`
- メソッド: GET
- レスポンス: 利用可能な地域とモデルの情報

### 家賃相場予測API

- エンドポイント: `/api/v1/predict`
- メソッド: POST
- リクエストボディ:
```json
{
  "area": float,                // 面積（㎡）
  "age": int,                   // 築年数
  "layout": int,                // 間取り（1-12）
  "station_person": int,        // 駅の利用者数（千人/日）
  "rent": float,                // 現在の家賃（万円）
  "region": string,             // 地域名（例: suginami）
  "management_fee": float,      // 管理費（万円）- 任意
  "total_units": int            // 総戸数 - 任意
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
    "rent": float,
    "region": string,
    "management_fee": float,
    "total_units": int
  },
  "model_info": {
    "description": string,      // モデルの説明
    "features": [string],       // 使用された特徴量
    "required_features": [string],  // 必須特徴量
    "optional_features": [string]   // 任意特徴量
  },
  "predicted_rent": float,      // 予測家賃（万円）
  "reasonable_range": {
    "min": float,               // 適正価格の下限（万円）
    "max": float                // 適正価格の上限（万円）
  },
  "price_evaluation": int       // 価格評価（1:割安, 2:適正だが安い, 3:相場通り, 4:適正だが高い, 5:割高）
}
```

## APIのテスト方法

### cURLを使用したテスト例

**基本モデル（必須パラメータのみ）**:
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 10.0,
    "region": "suginami"
  }'
```

**管理費モデル**:
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 10.0,
    "management_fee": 1.5,
    "region": "suginami"
  }'
```

**総戸数モデル**:
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 10.0,
    "total_units": 50,
    "region": "suginami"
  }'
```

**全特徴量モデル**:
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 10.0,
    "management_fee": 1.5,
    "total_units": 50,
    "region": "suginami"
  }'
```

### Postmanを使用したテスト

1. **新しいリクエストの作成**
   - メソッド: `POST`
   - URL: `http://localhost:8000/api/v1/predict`
   - Headers: `Content-Type: application/json`

2. **テストケース例**

基本モデル（必須パラメータのみ）:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 8.0,
    "region": "suginami"
}
```

管理費を含むモデル:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 8.0,
    "region": "suginami",
    "management_fee": 1.5
}
```

総戸数を含むモデル:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 8.0,
    "region": "suginami",
    "total_units": 50
}
```

全特徴量を含むモデル:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 8.0,
    "region": "suginami",
    "management_fee": 1.5,
    "total_units": 50
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
    "rent": 8.0,
    "region": "suginami"
}
```

不正な間取り:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 13,
    "station_person": 100,
    "rent": 8.0,
    "region": "suginami"
}
```

不正な地域名:
```json
{
    "area": 30.0,
    "age": 5,
    "layout": 3,
    "station_person": 100,
    "rent": 8.0,
    "region": "invalid_region"
}
```

## 対応地域

現在、以下の地域に対応しています：

- **suginami**: 杉並区
- **musashino**: 武蔵野市
- **kitaku**: 北区
- **nakanoku**: 中野区
- **nerimaku**: 練馬区

新しい地域の追加方法：
1. 該当地域のモデルファイルを`saved_models/[地域名]/`に配置
2. `config.json`に地域とモデル情報を追加

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
