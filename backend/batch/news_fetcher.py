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
        """Fetch articles for a company - prioritize yfinance, then NewsAPI"""

        articles = []

        # Try yfinance first (more reliable for stock news)
        yf_articles = self._get_yfinance_articles(ticker, company_name)
        articles.extend(yf_articles)

        # Try NewsAPI to supplement
        if self.api_key != "demo":
            newsapi_articles = self._get_newsapi_articles(ticker, company_name, days, page_size)
            articles.extend(newsapi_articles)

        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in articles:
            title_lower = article.get("title", "").lower()
            if title_lower and title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)

        # Fallback to demo only if absolutely nothing found
        if not unique_articles:
            print(f"  Warning: No real articles found for {ticker}, using demo data", end="")
            unique_articles = self._get_demo_articles(ticker, company_name)

        return unique_articles[:page_size]  # Limit to page_size
    
    def _get_newsapi_articles(self, ticker: str, company_name: str, days: int, page_size: int) -> List[Dict]:
        """Fetch articles from NewsAPI with keyword filtering and rate limiting"""

        endpoint = f"{self.base_url}/everything"

        # Get keywords for this company
        company_data = next((c for c in NYSE_COMPANIES if c["ticker"] == ticker), None)
        keywords = company_data.get("keywords", [company_name]) if company_data else [company_name]

        # Build search query with keywords
        # Use OR to match any keyword, and include ticker
        keyword_query = " OR ".join([f'"{kw}"' for kw in keywords])
        query = f'"{ticker}" OR {keyword_query}'

        # Date range
        to_date = datetime.now().date()
        from_date = (datetime.now() - timedelta(days=days)).date()

        params = {
            "q": query,
            "from": str(from_date),
            "to": str(to_date),
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": self.api_key,
            "language": "en"  # Focus on English articles
        }

        try:
            # Add delay to avoid rate limiting
            import time
            time.sleep(0.5)

            response = requests.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Check for API errors
            if data.get("status") == "error":
                error_msg = data.get("message", "Unknown error")
                print(f"  (NewsAPI error for {ticker}: {error_msg})", end="")
                return []

            articles = []
            for article in data.get("articles", []):
                # Filter by keywords in title or description
                title = article.get("title", "")
                description = article.get("description", "")
                text = f"{title} {description}".lower()

                # Check if any keyword matches
                keyword_match = any(kw.lower() in text for kw in keywords)

                if keyword_match and title and title != "[Removed]":
                    articles.append({
                        "ticker": ticker,
                        "title": title,
                        "content": description or title,
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "source_url": article.get("url", ""),
                        "published_at": article.get("publishedAt", "")
                    })

            return articles

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"  (NewsAPI rate limit exceeded for {ticker})", end="")
            else:
                print(f"  (NewsAPI HTTP error for {ticker}: {e})", end="")
            return []
        except Exception as e:
            print(f"  (NewsAPI unavailable for {ticker}: {str(e)})", end="")
            return []
    
    def _get_yfinance_articles(self, ticker: str, company_name: str) -> List[Dict]:
        """Fetch articles from yfinance with improved error handling"""

        try:
            ticker_obj = yf.Ticker(ticker)

            # Try to get news with multiple attempts
            news = None
            for attempt in range(3):
                try:
                    news = ticker_obj.news
                    if news:
                        break
                except Exception as e:
                    if attempt < 2:
                        import time
                        time.sleep(1)
                    else:
                        raise

            if not news:
                return []

            articles = []
            for item in news:  # Get all available articles from yfinance
                try:
                    # Extract provider/publisher name
                    provider = item.get("providerPublishTime", "")
                    source_name = item.get("publisher", "") or "Financial News"

                    # Format the published date
                    # providerPublishTime should be a timestamp (integer)
                    # If it's not a valid timestamp, use current time
                    if provider and isinstance(provider, (int, float)):
                        try:
                            pub_date = datetime.fromtimestamp(provider)
                        except (ValueError, TypeError, OSError):
                            print(f"  [DEBUG] Invalid timestamp for {ticker}: {provider}", end="")
                            pub_date = datetime.now()
                    else:
                        pub_date = datetime.now()

                    # Validate required fields
                    title = item.get("title", "")
                    if not title or title == "[Removed]":
                        continue

                    articles.append({
                        "ticker": ticker,
                        "title": title,
                        "content": item.get("summary", "") or title,
                        "source": source_name,
                        "source_url": item.get("link", ""),
                        "published_at": pub_date.isoformat()
                    })
                except Exception as e:
                    # Skip individual article errors but continue processing
                    continue

            return articles

        except Exception as e:
            error_msg = str(e)
            if "Expecting value" in error_msg:
                # yfinance API error - likely no news available
                return []
            print(f"  (yfinance unavailable for {ticker}: {error_msg[:50]}...)", end="")
            return []
    
    def _get_demo_articles(self, ticker: str, name: str) -> List[Dict]:
        """Return demo articles for testing - Optimized for positive sentiment detection"""
        
        # ポジティブ判定に最適化されたニュースデータ
        demo_articles = {
            "AAPL": [
                {"title": f"{name} Announces Revolutionary New Product Launch", "content": f"{name} has announced a groundbreaking new product that is expected to revolutionize the industry and drive significant revenue growth.", "sentiment": "positive"},
                {"title": f"{name} Reports Record Quarterly Earnings, Beats Expectations", "content": f"{name}'s latest quarterly earnings exceeded analyst expectations by 15%, demonstrating strong operational efficiency and market leadership.", "sentiment": "positive"},
                {"title": f"{name} Expands AI Capabilities with Major Investment", "content": f"{name} invests heavily in artificial intelligence research and development, positioning itself as a leader in AI innovation.", "sentiment": "positive"},
                {"title": f"{name} Stock Reaches New All-Time High on Strong Performance", "content": f"{name} shares surge to record levels as investors respond positively to exceptional growth and profitability.", "sentiment": "positive"},
            ],
            "MSFT": [
                {"title": f"{name} Cloud Services Show Strong Growth Momentum", "content": f"{name} Azure cloud services show exceptional growth in corporate sector, expanding market share significantly.", "sentiment": "positive"},
                {"title": f"{name} Launches New Gaming Console with Overwhelming Demand", "content": f"{name} Xbox Series X2 receives overwhelming pre-orders, signaling strong consumer enthusiasm and revenue potential.", "sentiment": "positive"},
                {"title": f"{name} Partners with OpenAI for Enterprise Solutions", "content": f"{name} deepens integration of ChatGPT into enterprise solutions, creating new revenue streams and competitive advantages.", "sentiment": "positive"},
                {"title": f"{name} Reports Strong Q4 Results, Raises Guidance", "content": f"{name} delivers strong quarterly results and raises full-year guidance, reflecting confidence in continued growth.", "sentiment": "positive"},
            ],
            "GOOGL": [
                {"title": f"{name} Launches Advanced AI Model with Superior Performance", "content": f"{name} Gemini AI shows superior performance in benchmark tests, establishing leadership in AI technology.", "sentiment": "positive"},
                {"title": f"{name} Invests in Renewable Energy for Sustainable Growth", "content": f"{name} commits to 100% renewable energy by 2030, demonstrating commitment to sustainability and long-term value creation.", "sentiment": "positive"},
                {"title": f"{name} Quantum Computing Breakthrough Opens New Opportunities", "content": f"{name} quantum chips demonstrate new computational capabilities, opening doors to revolutionary applications.", "sentiment": "positive"},
                {"title": f"{name} Cloud Platform Shows Strong Adoption", "content": f"{name} Google Cloud continues to gain market share with strong enterprise adoption and revenue growth.", "sentiment": "positive"},
            ],
            "AMZN": [
                {"title": f"{name} AWS Dominates Cloud Market with Strong Growth", "content": f"{name} Web Services maintains 32% market share in cloud computing with accelerating revenue growth.", "sentiment": "positive"},
                {"title": f"{name} Expands Same-Day Delivery to 2,000 Cities", "content": f"{name} announces same-day delivery available in 2,000 cities, enhancing customer experience and competitive position.", "sentiment": "positive"},
                {"title": f"{name} Acquires Healthcare Tech Startup for $1 Billion", "content": f"{name} invests in healthcare AI company for $1 billion, expanding into high-growth healthcare technology sector.", "sentiment": "positive"},
                {"title": f"{name} E-commerce Platform Shows Strong Growth", "content": f"{name} online shopping volume grows 25% year-over-year, demonstrating strong market position and consumer demand.", "sentiment": "positive"},
            ],
            "TSLA": [
                {"title": f"{name} Breaks Sales Records with Strong Demand", "content": f"{name} delivers record 1.8 million vehicles in record-breaking year, showing exceptional market demand.", "sentiment": "positive"},
                {"title": f"{name} Stock Reaches All-Time High on Strong Performance", "content": f"{name} shares surge 45% on strong earnings report, reflecting investor confidence in growth prospects.", "sentiment": "positive"},
                {"title": f"{name} Expands to India Market with New Facility", "content": f"{name} announces new manufacturing facility in India, positioning for significant growth in emerging markets.", "sentiment": "positive"},
                {"title": f"{name} Battery Technology Breakthrough Improves Efficiency", "content": f"{name} announces major battery technology advancement, reducing costs and improving vehicle performance.", "sentiment": "positive"},
            ],
            "META": [
                {"title": f"{name} Ad Revenue Shows Strong Recovery in Q4", "content": f"{name} advertising business shows strong recovery in Q4, demonstrating resilience and growth potential.", "sentiment": "positive"},
                {"title": f"{name} AI Research Breakthrough Competes with GPT", "content": f"{name} releases advanced language model competing with GPT, establishing position in AI market.", "sentiment": "positive"},
                {"title": f"{name} User Engagement Increases Across Platforms", "content": f"{name} reports strong user engagement growth across all platforms, driving advertising revenue growth.", "sentiment": "positive"},
                {"title": f"{name} Expands E-commerce Integration", "content": f"{name} launches new e-commerce features across platforms, creating new revenue opportunities.", "sentiment": "positive"},
            ],
            "NVDA": [
                {"title": f"{name} Dominates AI Chip Market with 300% Growth", "content": f"{name} GPU sales surge 300% due to AI demand, establishing market leadership and strong revenue growth.", "sentiment": "positive"},
                {"title": f"{name} Stock Reaches $1 Trillion Valuation", "content": f"{name} becomes most valuable chipmaker in history, reflecting strong market position and growth prospects.", "sentiment": "positive"},
                {"title": f"{name} Expands Data Center Business with New Solutions", "content": f"{name} announces new data center solutions for enterprise, expanding market opportunities.", "sentiment": "positive"},
                {"title": f"{name} AI Software Platform Shows Strong Adoption", "content": f"{name} AI software platform gains strong enterprise adoption, creating recurring revenue streams.", "sentiment": "positive"},
            ],
            "JPM": [
                {"title": f"{name} Posts Record Profits in Investment Banking", "content": f"{name} investment banking division reaches record revenue, demonstrating strong market position and execution.", "sentiment": "positive"},
                {"title": f"{name} Launches New Wealth Management Platform", "content": f"{name} introduces AI-powered investment advisory for clients, expanding wealth management capabilities.", "sentiment": "positive"},
                {"title": f"{name} Expands Cryptocurrency Trading Services", "content": f"{name} expands cryptocurrency trading services, positioning for growth in digital asset markets.", "sentiment": "positive"},
                {"title": f"{name} Digital Banking Platform Shows Strong Growth", "content": f"{name} digital banking platform gains significant market share, driving customer acquisition and revenue growth.", "sentiment": "positive"},
            ],
            "V": [
                {"title": f"{name} Payment Volume Increases to New High", "content": f"{name} credit card transaction volume reaches new high, showing strong consumer spending and market position.", "sentiment": "positive"},
                {"title": f"{name} Expands B2B Solutions for Business Growth", "content": f"{name} launches new platform for business-to-business payments, expanding market opportunities.", "sentiment": "positive"},
                {"title": f"{name} Reports Strong Q4 Earnings, Beats Expectations", "content": f"{name} earnings beat analyst expectations by 8%, demonstrating strong operational performance.", "sentiment": "positive"},
                {"title": f"{name} Digital Wallet Adoption Accelerates", "content": f"{name} digital wallet platform shows strong adoption, driving transaction volume growth.", "sentiment": "positive"},
            ],
            "WMT": [
                {"title": f"{name} Q4 Sales Surge with 6.5% Growth", "content": f"{name} holiday sales exceed expectations with 6.5% growth, showing strong consumer demand.", "sentiment": "positive"},
                {"title": f"{name} E-commerce Platform Thrives with 25% Growth", "content": f"{name} online shopping volume grows 25% year-over-year, demonstrating successful digital transformation.", "sentiment": "positive"},
                {"title": f"{name} Announces Sustainability Goals for Long-term Value", "content": f"{name} commits to carbon neutrality by 2040, positioning for sustainable growth and cost savings.", "sentiment": "positive"},
                {"title": f"{name} Expands Market Share in Grocery Sector", "content": f"{name} gains market share in competitive grocery sector, showing strong operational execution.", "sentiment": "positive"},
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
