# NewsSpY プロジェクト構造

## プロジェクト概要

NewsSpYは、米国株（S&P 500相当の約500社）のニュースを毎日自動取得し、金融特化型AIモデル「FinBERT」を用いて感情解析（ポジティブ/ネガティブ/ニュートラル）を行い、その「スコア」を可視化するWebアプリケーションです。

## プロジェクト構造

```
newspy/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPIアプリケーションエントリーポイント
│   │   ├── config.py               # 設定ファイル（companies.jsonから企業データを読み込み）
│   │   ├── database.py             # データベース操作（news_sentimentsテーブルを含む）
│   │   ├── schemas.py              # データスキーマ定義
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── sentiments.py      # 感情スコアAPI（/api/sentiments/daily, /api/sentiments/{ticker}）
│   │   │   ├── scores.py         # スコアAPI
│   │   │   └── articles.py       # 記事API
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── sentiment_analyzer.py  # FinBERT感情分析
│   │       └── score_calculator.py    # スコア計算
│   ├── batch/
│   │   ├── main.py                 # バッチ処理メイン（news_sentimentsテーブルに保存）
│   │   └── news_fetcher.py         # NewsAPI連携（キーワードフィルタリング）
│   ├── companies.json              # 企業マスタ（ティッカー、企業名、キーワード）
│   ├── requirements.txt            # Python依存関係
│   ├── batch_process.sh           # バッチ処理シェルスクリプト
│   └── Dockerfile                # Dockerイメージ
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx      # ダッシュボードメイン
│   │   │   ├── StockDetail.tsx    # 銘柄詳細（感情スコアの時系列推移を折れ線グラフで表示）
│   │   │   ├── Heatmap.tsx        # 感情ヒートマップ（S&P 500の各セクター・銘柄をタイル状に表示）
│   │   │   └── Search.tsx         # 検索機能（500社のリストから銘柄を検索）
│   │   ├── services/
│   │   │   └── api.ts            # API通信（/api/sentiments/daily, /api/sentiments/{ticker}）
│   │   ├── types/
│   │   │   └── index.ts          # TypeScript型定義
│   │   ├── App.tsx                # Reactアプリケーション
│   │   ├── main.tsx              # エントリーポイント
│   │   └── index.css              # Tailwind CSSスタイル
│   ├── public/
│   │   └── index.html
│   ├── package.json               # Node.js依存関係（React, TypeScript, Tailwind CSS, Lucide-react, Recharts）
│   ├── tsconfig.json              # TypeScript設定
│   ├── tailwind.config.js         # Tailwind CSS設定
│   ├── postcss.config.js          # PostCSS設定
│   ├── nginx.conf                # フロントエンドNginx設定
│   ├── .env.example             # 環境変数テンプレート
│   └── Dockerfile                # Dockerイメージ
├── nginx/
│   └── nginx.conf                # Nginxリバースプロキシ設定
├── docker-compose.yml             # Docker Compose設定（Backend, Frontend, Nginx）
├── .env.example                 # 環境変数テンプレート
├── .gitignore                  # Git除外ファイル
└── README.md                   # プロジェクトドキュメント
```

## 主な変更点

### 1. フロントエンドの書き換え
- StreamlitからReact + TypeScriptに変更
- UIライブラリ: Tailwind CSS, Lucide-react, Recharts

### 2. データ構造の追加
- `companies.json`: 企業マスタ（ティッカー、企業名、キーワード）

### 3. データベース構造の再設計
- `news_sentiments`テーブルの追加
  - id: PK
  - ticker: 銘柄コード (Indexed)
  - published_at: ニュース公開日時 (DateTime)
  - sentiment_score: FinBERTのスコア (-1.0 to 1.0)
  - label: positive / negative / neutral
  - created_at: レコード作成日
  - url_hash: ニュースURLのハッシュ（ユニーク制約）

### 4. 機能の追加
- 感情ヒートマップ（S&P 500の各セクター・銘柄をタイル状に表示）
- 銘柄詳細（感情スコアの時系列推移を折れ線グラフで表示）
- 検索機能（500社のリストから銘柄を検索）

### 5. APIエンドポイントの追加
- `GET /api/sentiments/daily`: 本日の全銘柄の平均スコアを取得（ヒートマップ用）
- `GET /api/sentiments/{ticker}`: 特定銘柄の過去30日間のスコア推移を取得（チャート用）

### 6. インフラの改善
- Docker化
- Nginxリバースプロキシ
- API制限対策
- 非同期処理の実装

### 7. FinBERTモデルの最適化
- Lifespanイベントを使用して、サーバー起動時にFinBERTモデルを一度だけロード
- グローバルに使い回すことで、メモリ効率を向上

## 技術スタック

### Backend
- FastAPI (Python 3.10+)
- FinBERT (Hugging Face Transformers)
- SQLite (初期フェーズ) または PostgreSQL
- NewsAPI (Everything Endpoint)

### Frontend
- React (TypeScript)
- Tailwind CSS
- Lucide-react
- Recharts

### Infrastructure
- Nginx (Reverse Proxy)
- Docker (推奨)

## 実装上の注意点

### API制限対策
- NewsAPIの無料枠を考慮し、1リクエストで可能な限り多くの情報を取得
- yfinanceをフォールバックとして使用
- デモデータを提供

### 非同期処理
- FastAPIのエンドポイントは async def で実装
- モデル推論はCPU/GPU負荷が高いため、必要に応じて run_in_executor 等を検討

### 著作権配慮
- データベースにはニュースの全文を保存せず、解析結果の数値データのみを保持
