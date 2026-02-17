#!/usr/bin/env python3
"""
News fetcher: Fetch news from NewsAPI and yfinance
"""

import requests
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.config import NEWSAPI_KEY, NEWSAPI_BASE_URL, NYSE_COMPANIES

class NewsAPIFetcher:
    """Fetch news from NewsAPI"""
    
    def __init__(self, api_key: str = NEWSAPI_KEY):
        self.api_key = api_key
        self.base_url = NEWSAPI_BASE_URL
    
    def get_articles(
        self,
        ticker: str,
        company_name: str,
        days: int = 30,
        page_size: int = 100
    ) -> List[Dict]:
        """Fetch articles for a company - try NewsAPI first, fallback to yfinance"""
        
        articles = []
        
        # Try NewsAPI first
        if self.api_key != "demo":
            articles.extend(self._get_newsapi_articles(ticker, company_name, days, page_size))
        
        # Supplement with yfinance articles
        articles.extend(self._get_yfinance_articles(ticker, company_name))
        
        # Fallback to demo if nothing found
        if not articles:
            articles = self._get_demo_articles(ticker, company_name)
        
        return articles[:page_size]  # Limit to page_size
    
    def _get_newsapi_articles(self, ticker: str, company_name: str, days: int, page_size: int) -> List[Dict]:
        """Fetch articles from NewsAPI"""
        
        endpoint = f"{self.base_url}/everything"
        
        # Search query
        query = f'"{ticker}" OR "{company_name}"'
        
        # Date range
        to_date = datetime.now().date()
        from_date = (datetime.now() - timedelta(days=days)).date()
        
        params = {
            "q": query,
            "fromDate": str(from_date),
            "toDate": str(to_date),
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "ticker": ticker,
                    "title": article.get("title", ""),
                    "content": article.get("description", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "source_url": article.get("url", ""),
                    "published_at": article.get("publishedAt", "")
                })
            
            return articles
        
        except Exception as e:
            print(f"  (NewsAPI unavailable for {ticker})", end="")
            return []
    
    def _get_yfinance_articles(self, ticker: str, company_name: str) -> List[Dict]:
        """Fetch articles from yfinance"""
        
        try:
            ticker_obj = yf.Ticker(ticker)
            news = ticker_obj.news
            
            if not news:
                return []
            
            articles = []
            for item in news[:10]:  # Limit to 10 articles from yfinance
                articles.append({
                    "ticker": ticker,
                    "title": item.get("title", ""),
                    "content": item.get("summary", "") or item.get("title", ""),
                    "source": item.get("source", "Financial News"),
                    "source_url": item.get("link", ""),
                    "published_at": datetime.now().isoformat()
                })
            
            return articles
        
        except Exception as e:
            print(f"  (yfinance unavailable for {ticker})", end="")
            return []
    
    def _get_demo_articles(self, ticker: str, name: str) -> List[Dict]:
        """Return demo articles for testing - Expanded demo data"""
        
        # より多くのバリエーション豊かなニュースデータ
        demo_articles = {
            "AAPL": [
                {"title": f"{name} Announces New Product Launch", "content": f"{name} has announced a groundbreaking new product that is expected to revolutionize the industry.", "sentiment": "positive"},
                {"title": f"{name} Reports Record Quarterly Earnings", "content": f"{name}'s latest quarterly earnings exceeded analyst expectations by 15%.", "sentiment": "positive"},
                {"title": f"{name} Faces Supply Chain Challenges", "content": f"Industry analysts warn {name} may face supply chain disruptions in Q1.", "sentiment": "negative"},
                {"title": f"{name} Expands AI Capabilities", "content": f"{name} invests heavily in artificial intelligence research and development.", "sentiment": "positive"},
            ],
            "MSFT": [
                {"title": f"{name} Cloud Services Surge", "content": f"{name} Azure cloud services show strong growth in corporate sector.", "sentiment": "positive"},
                {"title": f"{name} Announces Major Layoffs", "content": f"{name} to reduce workforce by 10,000 employees as part of restructuring.", "sentiment": "negative"},
                {"title": f"{name} Launches New Gaming Console", "content": f"{name} Xbox Series X2 receives overwhelming pre-orders.", "sentiment": "positive"},
                {"title": f"{name} Partners with OpenAI", "content": f"{name} deepens integration of ChatGPT into enterprise solutions.", "sentiment": "positive"},
            ],
            "GOOGL": [
                {"title": f"{name} Launches Advanced AI Model", "content": f"{name} Gemini AI shows superior performance in benchmark tests.", "sentiment": "positive"},
                {"title": f"{name} Faces Antitrust Challenges", "content": f"Government officials consider breaking up {name}'s advertising business.", "sentiment": "negative"},
                {"title": f"{name} Invests in Renewable Energy", "content": f"{name} commits to 100% renewable energy by 2030.", "sentiment": "positive"},
                {"title": f"{name} Quantum Computing Breakthrough", "content": f"{name} quantum chips demonstrate new computational capabilities.", "sentiment": "positive"},
            ],
            "AMZN": [
                {"title": f"{name} AWS Dominates Cloud Market", "content": f"{name} Web Services maintains 32% market share in cloud computing.", "sentiment": "positive"},
                {"title": f"{name} Expands Same-Day Delivery", "content": f"{name} announces same-day delivery available in 2,000 cities.", "sentiment": "positive"},
                {"title": f"{name} Warns on Holiday Sales", "content": f"{name} issues conservative guidance for holiday shopping season.", "sentiment": "negative"},
                {"title": f"{name} Acquires Healthcare Tech Startup", "content": f"{name} invests in healthcare AI company for $1 billion.", "sentiment": "positive"},
            ],
            "TSLA": [
                {"title": f"{name} Breaks Sales Records", "content": f"{name} delivers record 1.8 million vehicles in record-breaking year.", "sentiment": "positive"},
                {"title": f"{name} Faces Production Delays", "content": f"{name} Cybertruck production faces unexpected setbacks.", "sentiment": "negative"},
                {"title": f"{name} Stock Reaches All-Time High", "content": f"{name} shares surge 45% on strong earnings report.", "sentiment": "positive"},
                {"title": f"{name} Expands to India Market", "content": f"{name} announces new manufacturing facility in India.", "sentiment": "positive"},
            ],
            "META": [
                {"title": f"{name} Metaverse Investment Questioned", "content": f"Analysts question viability of {name}'s $100B metaverse investment.", "sentiment": "negative"},
                {"title": f"{name} Ad Revenue Rebounds", "content": f"{name} advertising business shows strong recovery in Q4.", "sentiment": "positive"},
                {"title": f"{name} Cuts 10,000 More Jobs", "content": f"{name} continues workforce reduction amid economic slowdown.", "sentiment": "negative"},
                {"title": f"{name} AI Research Breakthrough", "content": f"{name} releases advanced language model competing with GPT.", "sentiment": "positive"},
            ],
            "NVDA": [
                {"title": f"{name} Dominates AI Chip Market", "content": f"{name} GPU sales surge 300% due to AI demand.", "sentiment": "positive"},
                {"title": f"{name} Stock Reaches $1 Trillion Valuation", "content": f"{name} becomes most valuable chipmaker in history.", "sentiment": "positive"},
                {"title": f"{name} Faces Competition from AMD", "content": f"AMD's new AI chips threaten {name}'s market dominance.", "sentiment": "negative"},
                {"title": f"{name} Expands Data Center Business", "content": f"{name} announces new data center solutions for enterprise.", "sentiment": "positive"},
            ],
            "JPM": [
                {"title": f"{name} Posts Record Profits", "content": f"{name} investment banking division reaches record revenue.", "sentiment": "positive"},
                {"title": f"{name} CEO Warns on Economy", "content": f"{name} leadership cautions about potential recession ahead.", "sentiment": "negative"},
                {"title": f"{name} Launches New Wealth Management Platform", "content": f"{name} introduces AI-powered investment advisory for clients.", "sentiment": "positive"},
                {"title": f"{name} Crypto Strategy Shift", "content": f"{name} expands cryptocurrency trading services.", "sentiment": "positive"},
            ],
            "V": [
                {"title": f"{name} Payment Volume Increases", "content": f"{name} credit card transaction volume reaches new high.", "sentiment": "positive"},
                {"title": f"{name} Faces Competition from Digital Wallets", "content": f"Digital payment alternatives pose challenge to {name}'s dominance.", "sentiment": "negative"},
                {"title": f"{name} Expands B2B Solutions", "content": f"{name} launches new platform for business-to-business payments.", "sentiment": "positive"},
                {"title": f"{name} Reports Strong Q4 Earnings", "content": f"{name} earnings beat analyst expectations by 8%.", "sentiment": "positive"},
            ],
            "WMT": [
                {"title": f"{name} Q4 Sales Surge", "content": f"{name} holiday sales exceed expectations with 6.5% growth.", "sentiment": "positive"},
                {"title": f"{name} E-commerce Platform Thrives", "content": f"{name} online shopping volume grows 25% year-over-year.", "sentiment": "positive"},
                {"title": f"{name} Faces Labor Negotiations", "content": f"{name} workers demand higher wages and better benefits.", "sentiment": "negative"},
                {"title": f"{name} Announces Sustainability Goals", "content": f"{name} commits to carbon neutrality by 2040.", "sentiment": "positive"},
            ],
        }
        
        articles_data = demo_articles.get(ticker, [])
        articles = []
        
        for i, article_data in enumerate(articles_data):
            articles.append({
                "ticker": ticker,
                "title": article_data["title"],
                "content": article_data["content"],
                "source": "NewsSpY Demo Feed",
                "source_url": f"https://example.com/{ticker.lower()}-news-{i}",
                "published_at": (datetime.now() - timedelta(hours=i*2)).isoformat()
            })
        
        return articles
    
    def fetch_all_companies(self) -> List[Dict]:
        """Fetch articles for all tracked companies"""
        all_articles = []
        for company in NYSE_COMPANIES:
            articles = self.get_articles(
                company["ticker"],
                company["name"]
            )
            all_articles.extend(articles)
        
        return all_articles
