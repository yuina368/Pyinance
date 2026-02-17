#!/usr/bin/env python3
"""
NewsSpY Batch Processing - Main
手動実行: python batch_process.py
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import NYSE_COMPANIES, NEWSAPI_KEY
from app.database import (
    init_database, add_company, add_article, get_company_by_ticker,
    save_score, get_articles_for_date
)
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.services.score_calculator import ScoreCalculator
from batch.news_fetcher import NewsAPIFetcher

class NewsSpYBatchProcessor:
    """メインバッチプロセッサ"""
    
    def __init__(self):
        self.fetcher = NewsAPIFetcher(api_key=NEWSAPI_KEY)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.companies_tracked = 0
        self.articles_fetched = 0
        self.articles_added = 0
        
    def run(self):
        """メインプロセス実行"""
        print("=" * 60)
        print("  🚀 NewsSpY Batch Processing Start")
        print("=" * 60)
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Initialize Database
        print("[1/5] Initializing Database...")
        init_database()
        print("      ✓ Database initialized")
        print()
        
        # 2. Register Companies
        print("[2/5] Registering Companies...")
        self._register_companies()
        print(f"      ✓ {self.companies_tracked} companies registered")
        print()
        
        # 3. Fetch Articles
        print("[3/5] Fetching Articles from NewsAPI...")
        self._fetch_articles()
        print(f"      ✓ {self.articles_fetched} articles fetched")
        print(f"      ✓ {self.articles_added} articles added to database")
        print()
        
        # 4. Analyze Sentiment
        print("[4/5] Analyzing Sentiment...")
        self._analyze_sentiment()
        print("      ✓ Sentiment analysis completed")
        print()
        
        # 5. Calculate Scores
        print("[5/5] Calculating Scores...")
        target_date = datetime.now().date()
        self._calculate_scores(target_date)
        print(f"      ✓ Scores calculated for {target_date}")
        print()
        
        print("=" * 60)
        print("  ✓ Batch Processing Complete!")
        print("=" * 60)
        print()
    
    def _register_companies(self):
        """企業を登録"""
        for company in NYSE_COMPANIES:
            ticker = company["ticker"]
            name = company["name"]
            
            # 既に存在するかチェック
            company_id = get_company_by_ticker(ticker)
            if not company_id:
                company_id = add_company(ticker, name)
            
            if company_id:
                self.companies_tracked += 1
                print(f"      • {ticker}: {name}")
    
    def _fetch_articles(self):
        """記事を取得"""
        for company in NYSE_COMPANIES:
            ticker = company["ticker"]
            name = company["name"]
            
            print(f"      • Fetching {ticker}...", end="", flush=True)
            
            # NewsAPIから記事取得
            articles = self.fetcher.get_articles(ticker, name, days=30, page_size=100)
            self.articles_fetched += len(articles)
            
            # DBに追加
            company_id = get_company_by_ticker(ticker)
            if company_id:
                for article in articles:
                    success = add_article(
                        company_id=company_id,
                        title=article["title"],
                        content=article["content"],
                        source=article["source"],
                        source_url=article["source_url"],
                        published_at=article["published_at"]
                    )
                    if success:
                        self.articles_added += 1
            
            print(f" ({len(articles)} articles)")
    
    def _analyze_sentiment(self):
        """感情分析を実行"""
        import sqlite3
        conn = sqlite3.connect("newspy.db")
        cursor = conn.cursor()
        
        # センチメント未分析の記事を取得
        cursor.execute("""
            SELECT id, title, content 
            FROM articles 
            WHERE sentiment_score IS NULL
            LIMIT 1000
        """)
        
        articles = cursor.fetchall()
        analyzed_count = 0
        
        for article_id, title, content in articles:
            # テキスト結合
            text = f"{title} {content}"
            
            # センチメント分析
            score, confidence = self.sentiment_analyzer.analyze(text)
            
            # DB更新
            cursor.execute("""
                UPDATE articles 
                SET sentiment_score = ?, sentiment_confidence = ?
                WHERE id = ?
            """, (score, confidence, article_id))
            
            analyzed_count += 1
        
        conn.commit()
        conn.close()
        print(f"      ✓ {analyzed_count} articles analyzed")
    
    def _calculate_scores(self, target_date):
        """スコア計算（時間減衰を考慮）"""
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect("newspy.db")
        cursor = conn.cursor()
        
        # 対象日の記事を取得
        cursor.execute("""
            SELECT 
                c.id, c.ticker, c.name,
                a.id, a.published_at, a.sentiment_score
            FROM articles a
            JOIN companies c ON a.company_id = c.id
            WHERE DATE(a.published_at) = ?
            ORDER BY c.id
        """, (target_date,))
        
        articles = cursor.fetchall()
        
        if not articles:
            print("      ! No articles for this date")
            conn.close()
            return
        
        # 企業ごとにスコア計算
        company_scores = {}
        current_time = datetime.now()
        
        for company_id, ticker, name, article_id, published_at, sentiment_score in articles:
            if company_id not in company_scores:
                company_scores[company_id] = {
                    "ticker": ticker,
                    "name": name,
                    "scores": [],
                    "count": 0
                }
            
            if sentiment_score is not None:
                # 公開時刻を解析
                try:
                    pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    pub_time = datetime.now()
                
                # 時間差を計算
                time_diff = current_time - pub_time
                hours_ago = time_diff.total_seconds() / 3600
                
                # 時間減衰スコア計算
                # 最新: 1.0, 1時間後: 0.9, 2時間後: 0.8 ... 10時間以上: 0.0
                time_decay = max(0.0, 1.0 - (hours_ago * 0.1))
                
                # 最終スコア = センチメント × 時間減衰
                final_score = sentiment_score * time_decay
                
                company_scores[company_id]["scores"].append(final_score)
                company_scores[company_id]["count"] += 1
        
        # ランキング生成
        ranking = []
        for company_id, data in company_scores.items():
            if data["count"] > 0:
                avg_score = sum(data["scores"]) / len(data["scores"])
                ranking.append({
                    "company_id": company_id,
                    "score": avg_score,
                    "article_count": data["count"],
                    "avg_sentiment": sum(s / time_decay for s in data["scores"]) / len(data["scores"]) 
                                    if data["scores"] else 0
                })
        
        # ランクを付与
        ranking.sort(key=lambda x: x["score"], reverse=True)
        
        for rank, item in enumerate(ranking, 1):
            item["rank"] = rank
            
            # DBに保存
            success = save_score(
                company_id=item["company_id"],
                date=target_date,
                score=item["score"],
                article_count=item["article_count"],
                avg_sentiment=item["avg_sentiment"],
                rank=rank
            )
            
            if success:
                ticker = company_scores[item['company_id']]['ticker']
                print(f"      • Rank {rank}: {ticker} = {item['score']:.3f}")
        
        conn.close()

if __name__ == "__main__":
    processor = NewsSpYBatchProcessor()
    processor.run()
