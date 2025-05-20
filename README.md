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
│   │   └── config.py   # 設定ファイル
│   ├── models/         # データモデル
│   │   ├── __init__.py
│   │   └── schemas.py  # Pydanticモデル（リクエスト/レスポンスの型定義）
│   │   └── enums.py    # 列挙型の定義
│   ├── services/       # ビジネスロジック
│   │   ├── __init__.py
│   │   └── prediction.py # 予測ロジック
│   └── main.py         # アプリケーションのエントリーポイント
├── tests/              # テストコード
│   ├── __init__.py
│   └── test_api.py
├── saved_model/        # 学習済みモデル
│   └── rent_model/     # TensorFlow SavedModel
├── Dockerfile          # バックエンド用Dockerfile
├── requirements.txt    # Python依存関係
└── .gitignore
```

## 技術スタック

- FastAPI: 高速なAPIフレームワーク
- Pydantic: データバリデーション
- TensorFlow: 学習済みモデルの読み込みと推論
- Docker: コンテナ化

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
    area: float = Field(..., description="面積（㎡）", gt=0)
    age: int = Field(..., description="築年数", ge=0)
    distance: float = Field(..., description="最寄駅までの距離（分）", ge=0)
    rent: float = Field(..., description="現在の家賃（円）", gt=0)

class RentPredictionResponse(BaseModel):
    predicted_rent: float = Field(..., description="予測家賃")
    difference: float = Field(..., description="現在の家賃との差額")
    is_reasonable: bool = Field(..., description="相場に対して適正かどうか")
```

### 使用例（enums.py）

```python
from enum import Enum

class PropertyType(str, Enum):
    APARTMENT = "apartment"
    MANSION = "mansion"
    HOUSE = "house"
```

## 開発環境のセットアップ

1. リポジトリのクローン
```bash
git clone [repository-url]
cd rent_prediction/backend
```

2. 環境変数の設定
```bash
cp .env.example .env
```

3. 学習済みモデルの配置
```bash
# saved_model/rent_model/ ディレクトリに学習済みモデルを配置
```

4. Dockerコンテナの起動
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
  "distance": float,     // 最寄駅までの距離（分）
  "rent": float         // 現在の家賃（円）
}
```
- レスポンス:
```json
{
  "predicted_rent": float,  // 予測家賃
  "difference": float,      // 現在の家賃との差額
  "is_reasonable": boolean  // 相場に対して適正かどうか
  "message": string        // 相場との比較メッセージ
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
    "area": 50,
    "age": 5,
    "distance": 5,
    "rent": 80000
}
```

高めの家賃:
```json
{
    "area": 50,
    "age": 5,
    "distance": 5,
    "rent": 100000
}
```

安めの家賃:
```json
{
    "area": 50,
    "age": 5,
    "distance": 5,
    "rent": 60000
}
```

古い物件:
```json
{
    "area": 50,
    "age": 30,
    "distance": 5,
    "rent": 80000
}
```

駅から遠い物件:
```json
{
    "area": 50,
    "age": 5,
    "distance": 20,
    "rent": 80000
}
```

3. **バリデーションテスト**

負の値:
```json
{
    "area": -50,
    "age": 5,
    "distance": 5,
    "rent": 80000
}
```

不正な型:
```json
{
    "area": "50",
    "age": 5,
    "distance": 5,
    "rent": 80000
}
```

### 期待されるレスポンス

正常系のレスポンス例:
```json
{
    "predicted_rent": 85000,
    "difference": -5000,
    "is_reasonable": true,
    "message": "現在の家賃は相場とほぼ同等です。"
}
```

エラー時のレスポンス例:
```json
{
    "detail": [
        {
            "loc": ["body", "area"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt",
            "ctx": {"limit_value": 0}
        }
    ]
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
