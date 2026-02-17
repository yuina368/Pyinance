# NewsSpY - NYSEニュース感情分析ダッシュボード

NYSE（ニューヨーク証券取引所）上場企業のニュース記事を収集し、感情分析を行って企業ごとのスコアを算出・可視化するWebアプリケーションです。

## 📋 概要

NewsSpYは、以下の機能を提供するニュース分析プラットフォームです：

- **ニュース収集**: NewsAPIを通じてNYSE上場企業のニュース記事を自動収集
- **感情分析**: 記事タイトルと本文からポジティブ/ネガティブな感情を分析
- **スコア計算**: 感情分析結果に基づいて企業ごとのスコアを算出（時間減衰を考慮）
- **可視化ダッシュボード**: Streamlitベースのインタラクティブなダッシュボードで結果を表示

## 🏗️ アーキテクチャ

```
newspy/
├── backend/                 # FastAPIバックエンド
│   ├── app/
│   │   ├── main.py         # APIエントリーポイント
│   │   ├── config.py       # 設定ファイル
│   │   ├── database.py     # SQLiteデータベース操作
│   │   ├── routes/         # APIルート
│   │   │   ├── articles.py # 記事関連API
│   │   │   └── scores.py   # スコア関連API
│   │   └── services/       # ビジネスロジック
│   │       ├── sentiment_analyzer.py  # 感情分析
│   │       └── score_calculator.py    # スコア計算
│   └── batch/
│       ├── main.py         # バッチ処理メイン
│       └── news_fetcher.py # NewsAPI連携
├── frontend/
│   └── dashboard.py        # Streamlitダッシュボード
├── start_dashboard.sh      # 起動スクリプト
└── requirements.txt        # フロントエンド依存関係
```

## 🚀 インストール

### 前提条件

- Python 3.8以上
- pip

### 手順

1. リポジトリをクローンまたはダウンロード

2. バックエンドの依存関係をインストール
```bash
cd backend
pip install -r requirements.txt
```

3. フロントエンドの依存関係をインストール
```bash
cd ..
pip install -r requirements.txt
```

4. 環境変数を設定

`.env`ファイルを作成し、NewsAPIのAPIキーを設定：

```env
NEWSAPI_KEY=your_newsapi_key_here
DATABASE_URL=newspy.db
```

> **注意**: NewsAPIのAPIキーは [https://newsapi.org/](https://newsapi.org/) から無料で取得できます。

## 📖 使用方法

### クイックスタート

起動スクリプトを使用して、バックエンドとフロントエンドを同時に起動：

```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

または、以下の手順で個別に起動：

#### 1. バックエンドAPIの起動

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. ダッシュボードの起動

別のターミナルで：

```bash
streamlit run frontend/dashboard.py
```

#### 3. バッチ処理の実行

ニュース収集と感情分析を実行：

```bash
cd backend
python -m batch.main
```

または：

```bash
bash backend/batch_process.sh
```

### アクセス

- ダッシュボード: http://localhost:8501
- APIドキュメント: http://localhost:8000/docs
- APIヘルスチェック: http://localhost:8000/api/health/

## 📊 ダッシュボード機能

### タブ1: 📈 ランキング
- 指定日付の企業スコアランキングを表示
- ポジティブ/ネガティブ/ニュートラルの企業数を集計
- スコア分布グラフと記事数分布を表示

### タブ2: 📰 記事
- 企業ごとのニュース記事一覧を表示
- 感情スコアと信頼度を表示
- 感情フィルタ（ポジティブ/ネガティブ/すべて）

### タブ3: 📊 企業スコア
- 選択した企業の過去30日間のスコア推移をグラフ表示
- 日次スコアデータのテーブル表示

### タブ4: 📋 企業詳細
- 企業情報の表示
- 最新のニュース記事一覧

## 🔌 APIエンドポイント

### ヘルスチェック
```
GET /api/health/
```

### 企業一覧
```
GET /api/companies/
```

### 記事取得
```
GET /api/articles/?limit=50&company_id=1&sentiment_filter=positive
```

### ランキング取得
```
GET /api/scores/ranking/{date}?limit=100&sentiment_filter=positive
```

### 企業スコア履歴
```
GET /api/scores/company/{ticker}?days=30
```

## 🧠 感情分析アルゴリズム

NewsSpYはシンプルなキーワードベースの感情分析を使用しています：

- **ポジティブワード**: excellent, great, good, positive, gain, surge, etc.
- **ネガティブワード**: poor, bad, negative, loss, decline, crash, etc.

スコアは -1.0（最もネガティブ）から 1.0（最もポジティブ）の範囲で計算されます。

信頼度は、感情ワードの数に対するテキスト全体の単語数の比率で計算されます。

## 📈 スコア計算方法

企業スコアは以下の要素を考慮して計算されます：

1. **感情比率**: (ポジティブ記事数 - ネガティブ記事数) / 総記事数
2. **平均感情スコア**: すべての記事の感情スコアの平均
3. **時間減衰**: 最新の記事ほど高い重みを付与（1時間ごとに10%減衰）

最終スコア = `感情比率 × 100 + 平均感情スコア × 50`

## 🗄️ データベース構造

### companies テーブル
- `id`: 企業ID
- `ticker`: ティッカーシンボル（例: AAPL）
- `name`: 企業名
- `created_at`: 作成日時

### articles テーブル
- `id`: 記事ID
- `company_id`: 企業ID
- `title`: 記事タイトル
- `content`: 記事本文
- `source`: ニュースソース
- `source_url`: 記事URL
- `published_at`: 公開日時
- `sentiment_score`: 感情スコア
- `sentiment_confidence`: 信頼度
- `fetched_at`: 取得日時

### scores テーブル
- `id`: スコアID
- `company_id`: 企業ID
- `date`: 対象日付
- `score`: スコア
- `article_count`: 記事数
- `avg_sentiment`: 平均感情スコア
- `rank`: ランク
- `created_at`: 作成日時

## 🏢 対象企業

以下のNYSE/NASDAQ上場企業を追跡しています：

### テクノロジー
- AAPL (Apple), MSFT (Microsoft), GOOGL (Alphabet), AMZN (Amazon), TSLA (Tesla), META (Meta), NVDA (NVIDIA), NFLX (Netflix), CRM (Salesforce), ADOBE (Adobe)

### 金融
- JPM (JPMorgan Chase), BAC (Bank of America), WFC (Wells Fargo), GS (Goldman Sachs), MS (Morgan Stanley), BLK (BlackRock), ICE (Intercontinental Exchange), CME (CME Group)

### ヘルスケア
- JNJ (Johnson & Johnson), UNH (UnitedHealth Group), PFE (Pfizer), ABBV (AbbVie), MRK (Merck), TMO (Thermo Fisher Scientific), LLY (Eli Lilly)

### 消費財/小売
- WMT (Walmart), KO (Coca-Cola), PEP (PepsiCo), COST (Costco), MCD (McDonald's), NKE (Nike), LOW (Lowe's)

### 決済/カード
- V (Visa), MA (Mastercard), AXP (American Express)

### エネルギー/産業
- XOM (Exxon Mobil), CVX (Chevron), BA (Boeing), HON (Honeywell), GE (General Electric)

### コミュニケーション
- VZ (Verizon), T (AT&T), CMCSA (Comcast), DIS (Disney)

## 🔧 設定

### 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|--------------|
| `NEWSAPI_KEY` | NewsAPIのAPIキー | `demo` |
| `DATABASE_URL` | データベースファイルパス | `newspy.db` |

### 感情分析閾値

- `SENTIMENT_THRESHOLD_POSITIVE`: 0.05
- `SENTIMENT_THRESHOLD_NEGATIVE`: -0.05

## 📝 依存関係

### バックエンド
- fastapi==0.129.0
- uvicorn==0.40.0
- newsapi==0.1.1
- requests==2.32.5
- python-dateutil==2.9.0.post0
- python-dotenv==1.0.0
- yfinance==0.2.28

### フロントエンド
- streamlit
- requests
- pandas
- matplotlib
- seaborn
- plotly

## 🤝 貢献

バグ報告や機能リクエストはIssueにてお願いします。

## 📄 ライセンス

このプロジェクトのライセンスについては、別途お問い合わせください。

## ⚠️ 注意事項

- NewsAPIの無料プランにはリクエスト数の制限があります
- 感情分析は簡易的なキーワードベースの実装です
- デモ版ではデータはローカルのSQLiteに保存されます
- 本番環境での使用には追加の設定が必要です

---

**NewsSpY** © 2026 | NYSE News Analysis & Sentiment Scoring Dashboard
