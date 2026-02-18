from fastapi import APIRouter, HTTPException
import sqlite3
from typing import Optional
from datetime import datetime, date
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import (
    DB_PATH,
    get_daily_sentiments,
    get_ticker_sentiment_history,
    get_company_by_ticker
)

router = APIRouter(tags=["sentiments"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/sentiments/daily")
@limiter.limit("10/minute")
async def get_daily_sentiments_api(request, target_date: Optional[str] = None):
    """
    Get today's sentiment scores for all companies (heatmap data)
    
    Parameters:
    - target_date: Optional date string in YYYY-MM-DD format. Defaults to today.
    
    Returns:
    - List of companies with average sentiment scores and article counts
    """
    try:
        if target_date:
            parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        else:
            parsed_date = datetime.now().date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    sentiments = get_daily_sentiments(parsed_date)
    
    # Enrich with company names
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    enriched_sentiments = []
    for sentiment in sentiments:
        ticker = sentiment["ticker"]
        cursor.execute("SELECT name FROM companies WHERE ticker = ?", (ticker,))
        result = cursor.fetchone()
        company_name = result[0] if result else ticker
        
        enriched_sentiments.append({
            "ticker": ticker,
            "name": company_name,
            "avg_score": sentiment["avg_score"],
            "article_count": sentiment["article_count"],
            "date": parsed_date.isoformat()
        })
    
    conn.close()
    
    return {
        "date": parsed_date.isoformat(),
        "count": len(enriched_sentiments),
        "sentiments": enriched_sentiments
    }

@router.get("/sentiments/{ticker}")
@limiter.limit("30/minute")
async def get_ticker_sentiment_history_api(
    request,
    ticker: str,
    days: int = 30
):
    """
    Get sentiment history for a specific ticker (chart data)
    
    Parameters:
    - ticker: Stock ticker symbol (e.g., AAPL)
    - days: Number of days to look back (default: 30)
    
    Returns:
    - Historical sentiment data for the ticker
    """
    # Validate ticker exists
    company_id = get_company_by_ticker(ticker)
    if not company_id:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    
    # Validate days parameter
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
    
    history = get_ticker_sentiment_history(ticker, days)
    
    # Get company name
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM companies WHERE ticker = ?", (ticker,))
    result = cursor.fetchone()
    company_name = result[0] if result else ticker
    conn.close()
    
    return {
        "ticker": ticker,
        "name": company_name,
        "days": days,
        "count": len(history),
        "history": history
    }

@router.get("/sentiments/summary")
@limiter.limit("5/minute")
async def get_sentiment_summary(request):
    """
    Get overall sentiment summary for today
    
    Returns:
    - Summary statistics including positive/negative/neutral counts
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    target_date = datetime.now().date()
    
    # Get label distribution
    cursor.execute("""
        SELECT 
            label,
            COUNT(*) as count,
            AVG(sentiment_score) as avg_score
        FROM news_sentiments
        WHERE DATE(published_at) = ?
        GROUP BY label
    """, (target_date,))
    
    label_stats = cursor.fetchall()
    
    # Get top positive and negative tickers
    cursor.execute("""
        SELECT 
            ticker,
            AVG(sentiment_score) as avg_score,
            COUNT(*) as article_count
        FROM news_sentiments
        WHERE DATE(published_at) = ?
        GROUP BY ticker
        ORDER BY avg_score DESC
        LIMIT 5
    """, (target_date,))
    
    top_positive = [
        {"ticker": row[0], "avg_score": row[1], "article_count": row[2]}
        for row in cursor.fetchall()
    ]
    
    cursor.execute("""
        SELECT 
            ticker,
            AVG(sentiment_score) as avg_score,
            COUNT(*) as article_count
        FROM news_sentiments
        WHERE DATE(published_at) = ?
        GROUP BY ticker
        ORDER BY avg_score ASC
        LIMIT 5
    """, (target_date,))
    
    top_negative = [
        {"ticker": row[0], "avg_score": row[1], "article_count": row[2]}
        for row in cursor.fetchall()
    ]
    
    conn.close()
    
    return {
        "date": target_date.isoformat(),
        "label_distribution": [
            {"label": row[0], "count": row[1], "avg_score": row[2]}
            for row in label_stats
        ],
        "top_positive": top_positive,
        "top_negative": top_negative
    }
