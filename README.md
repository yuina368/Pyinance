# NewsSpY - US Stock Sentiment Analysis Dashboard

米国株（S&P 500相当）のニュースを自動取得し、FinBERT AIモデルを用いて感情解析を行い、そのスコアを可視化するWebアプリケーションです。

## 🚀 特徴

- **自動ニュース収集**: NewsAPIおよびyfinanceから毎日自動的にニュースを収集
- **AI感情解析**: 金融特化型AIモデル「FinBERT」を用いて感情解析（ポジティブ/ネガティブ/ニュートラル）を実行
- **感情ヒートマップ**: S&P 500の各銘柄の感情スコアをタイル状に可視化
- **銘柄詳細**: 特定銘柄の感情スコアの時系列推移を折れ線グラフで表示
- **検索機能**: 500社のリストから銘柄を検索
- **リアルタイム更新**: 最新のニュースと感情スコアをリアルタイムで反映

## 🛠 技術スタック

### Backend
- **FastAPI**: 高性能なPython Webフレームワーク
- **Python 3.10+**: メインプログラミング言語
- **FinBERT**: 金融特化型AI感情解析モデル（Hugging Face Transformers）
- **SQLite**: データベース（初期フェーズ）
- **NewsAPI**: ニュースデータソース
- **yfinance**: Yahoo Financeからのニュース取得

### Frontend
- **Streamlit**: PythonベースのWebアプリケーションフレームワーク
- **Plotly**: インタラクティブなデータ可視化
- **Pandas**: データ操作と分析

### Infrastructure
- **Docker**: コンテナ化
- **Docker Compose**: マルチコンテナ管理
- **Nginx**: リバースプロキシ

## 📁 プロジェクト構造

```
newspy/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPIアプリケーションエントリーポイント
│   │   ├── config.py               # 設定ファイル
│   │   ├── database.py             # データベース操作
│   │   ├── routes/
│   │   │   ├── auth.py            # 認証API
│   │   │   ├── sentiments.py      # 感情スコアAPI
│   │   │   ├── scores.py         # スコアAPI
│   │   │   └── articles.py       # 記事API
│   │   └── services/
│   │       ├── auth.py            # 認証サービス
│   │       ├── sentiment_analyzer.py  # FinBERT感情分析
│   │       └── score_calculator.py    # スコア計算
│   ├── batch/
│   │   ├── main.py                 # バッチ処理メイン
│   │   └── news_fetcher.py         # NewsAPI連携
│   ├── companies.json              # 企業マスタ
│   ├── requirements.txt            # Python依存関係
│   └── Dockerfile                # Dockerイメージ
├── dashboard.py                   # Streamlitダッシュボード
├── nginx/
│   └── nginx.conf                # Nginxリバースプロキシ設定
├── docker-compose.yml             # Docker Compose設定
├── .env.example                 # 環境変数テンプレート
└── README.md                    # プロジェクトドキュメント
```

## 🚀 クイックスタート

### 前提条件

- Docker 20.10+ （[インストールガイド](DOCKER_INSTALL.md)を参照）
- Docker Compose 2.0+ （またはローカル開発環境）
- Git

> **💡 Dockerがインストールされていない場合**: [Dockerインストールガイド](DOCKER_INSTALL.md)を参照してください。

### インストール

#### 方法1: Docker Composeを使用（推奨）

1. リポジトリをクローン
```bash
git clone <repository-url>
cd newspy
```

2. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集してNewsAPIキーを設定
```

3. Docker Composeで起動
```bash
docker-compose up -d
```

4. アプリケーションにアクセス
- Dashboard: http://localhost:8501
- Backend API: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health/

#### 方法2: ローカル開発（Dockerなし）

Docker Composeがインストールされていない場合、ローカルで開発できます。

##### Backendの起動

```bash
cd backend

# 仮想環境を作成
python -m venv venv

# 仮想環境をアクティベート
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# データベースを初期化
python -c "from app.database import init_database; init_database()"

# サーバーを起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

##### Frontendの起動（Streamlitダッシュボード）

```bash
# 依存関係をインストール
pip install -r requirements.txt

# ダッシュボードを起動
streamlit run dashboard.py
```

##### アプリケーションにアクセス
- Dashboard: http://localhost:8501
- Backend API: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health/

#### Docker Composeのインストール

Docker Composeをインストールするには、以下のコマンドを実行してください：

**Linux:**
```bash
# 最新バージョンをダウンロード
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 実行権限を付与
sudo chmod +x /usr/local/bin/docker-compose

# バージョンを確認
docker-compose --version
```

**Mac (Homebrewを使用):**
```bash
brew install docker-compose
```

**Windows:**
Docker Desktopをインストールすると、Docker Composeも含まれています。
https://www.docker.com/products/docker-desktop/

## 📊 APIエンドポイント

### 認証API

#### ログイン（トークン取得）
```
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

#### 現在のユーザー情報取得
```
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### トークン更新
```
POST /api/auth/refresh
Authorization: Bearer <access_token>
```

### 感情スコアAPI

#### 日次感情スコア取得（ヒートマップ用）
```
GET /api/sentiments/daily?target_date=YYYY-MM-DD
```

#### 銘柄別感情履歴取得（チャート用）
```
GET /api/sentiments/{ticker}?days=30
```

#### 感情サマリー取得
```
GET /api/sentiments/summary
```

### その他API

#### ヘルスチェック
```
GET /api/health/
```

#### モデルステータス
```
GET /api/model/status
```

詳細なAPIドキュメントは、[http://localhost/api/docs](http://localhost/api/docs) で確認できます。

## 🔄 バッチ処理

バッチ処理は以下の手順で実行されます：

1. **データベース初期化**: テーブルを作成
2. **企業登録**: companies.jsonから企業を登録
3. **ニュース取得**: NewsAPIから過去24時間のニュースを取得
4. **キーワードフィルタリング**: 企業名とキーワードでニュースをフィルタリング
5. **感情解析**: FinBERTで感情解析を実行
6. **データ保存**: 解析結果をデータベースに保存

### 手動実行

#### Docker環境の場合

```bash
# Dockerコンテナ内で実行
docker-compose exec backend python batch/main.py
```

#### ローカル環境の場合

```bash
# バッチ処理スクリプトを使用（推奨）
cd backend
bash run_batch.sh

# または直接実行
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python batch/main.py
```

### 自動実行（cron）

cronを使用して定期的にバッチ処理を実行できます：

```bash
# 毎日午前9時に実行（Docker環境）
0 9 * * * cd /app && python batch/main.py

# 毎日午前9時に実行（ローカル環境）
0 9 * * * cd /path/to/backend && bash run_batch.sh
```

## 🎨 データ構造

### 企業マスタ (companies.json)

```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "keywords": ["Apple", "iPhone", "iPad", "Mac", "iOS", "Tim Cook"]
  }
]
```

### データベーステーブル

#### news_sentimentsテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| ticker | TEXT | 銘柄コード（Indexed） |
| published_at | TIMESTAMP | ニュース公開日時 |
| sentiment_score | REAL | FinBERTのスコア（-1.0 to 1.0） |
| label | TEXT | positive / negative / neutral |
| created_at | TIMESTAMP | レコード作成日 |
| url_hash | TEXT | ニュースURLのハッシュ（ユニーク制約） |

## 🔧 設定

### 環境変数

| 変数名 | 説明 | デフォルト値 |
|----------|------|------------|
| NEWSAPI_KEY | NewsAPIのAPIキー | demo |
| DATABASE_URL | データベースのパス | newspy.db |
| JWT_SECRET_KEY | JWTトークンの署名キー | your-secret-key-change-this-in-production |
| ACCESS_TOKEN_EXPIRE_MINUTES | アクセストークンの有効期限（分） | 60 |
| ALLOWED_ORIGINS | 許可するオリジン（カンマ区切り） | http://localhost:3000,http://localhost:8501 |

### NewsAPIキーの取得

1. [NewsAPI](https://newsapi.org/) にアカウント登録
2. APIキーを取得
3. `.env`ファイルに設定

## 📝 開発

### Backend開発

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend開発

```bash
cd frontend
npm install
npm start
```

### テスト

```bash
# Backendテスト
cd backend
pytest

# Frontendテスト
cd frontend
npm test
```

## 🐛 トラブルシューティング

### FinBERTモデルが読み込めない

```bash
# モデルキャッシュをクリア
rm -rf ~/.cache/huggingface

# 再インストール
pip install --upgrade transformers torch
```

### NewsAPIの制限に達した

無料枠の制限を考慮し、以下の対策を実装しています：
- 1リクエストで可能な限り多くの情報を取得
- yfinanceをフォールバックとして使用
- デモデータを提供

### Dockerコンテナが起動しない

```bash
# コンテナログを確認
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx

# 再ビルド
docker-compose build --no-cache
docker-compose up -d
```

## 📄 ライセンス

MIT License

## 🤝 貢献

プルリクエストを歓迎します！

## 📧 お問い合わせ

問題やご質問がある場合は、Issueを開いてください。

## 🙏 謝辞

- [FinBERT](https://huggingface.co/ProsusAI/finbert) - 感情解析モデル
- [NewsAPI](https://newsapi.org/) - ニュースデータ
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Financeデータ
- [FastAPI](https://fastapi.tiangolo.com/) - Webフレームワーク
- [React](https://reactjs.org/) - UIフレームワーク

---

**NewsSpY © 2026 | US Stock Sentiment Analysis Dashboard**
