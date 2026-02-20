from fastapi import APIRouter, HTTPException
import sqlite3
from typing import Optional
from datetime import datetime, date

from app.database import DB_PATH, get_company_by_ticker, save_score
from app.services.score_calculator import ScoreCalculator

router = APIRouter(tags=["scores"])

@router.get("/scores/ranking/{date_str}")
async def get_ranking(date_str: str, limit: int = 100, sentiment_filter: Optional[str] = None):
    """Get company ranking for a specific date"""
    print(f"[DEBUG] get_ranking called with date_str: {date_str}, limit: {limit}, sentiment_filter: {sentiment_filter}")
    
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    print(f"[DEBUG] target_date: {target_date}, DB_PATH: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        c.id as company_id,
        c.ticker,
        c.name,
        s.score,
        s.article_count,
        s.avg_sentiment,
        s.rank
    FROM scores s
    JOIN companies c ON s.company_id = c.id
    WHERE s.date = ?
    """
    
    params = [target_date]
    
    if sentiment_filter:
        if sentiment_filter == "positive":
            query += " AND s.score > 0"
        elif sentiment_filter == "negative":
            query += " AND s.score < 0"
    
    query += " ORDER BY s.rank LIMIT ?"
    params.append(limit)
    
    print(f"[DEBUG] query: {query}")
    print(f"[DEBUG] params: {params}")
    
    cursor.execute(query, params)
    results = []
    for row in cursor.fetchall():
        results.append({
            "company": {
                "id": row[0],
                "ticker": row[1],
                "name": row[2]
            },
            "score": row[3],
            "article_count": row[4],
            "avg_sentiment": row[5],
            "rank": row[6]
        })
    
    print(f"[DEBUG] results count: {len(results)}")
    conn.close()
    return results

@router.post("/scores/calculate/{date_str}")
async def calculate_scores(date_str: str):
    """Calculate scores for all companies on a specific date"""
    print(f"[DEBUG] calculate_scores called with date_str: {date_str}")
    
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    print(f"[DEBUG] target_date: {target_date}")
    
    # Calculate scores using ScoreCalculator
    result = ScoreCalculator.calculate_for_date(target_date)
    print(f"[DEBUG] ScoreCalculator result: {result}")
    
    if result["companies_scored"] == 0:
        return {
            "companies_scored": 0,
            "message": "No articles found for this date. Please fetch news first."
        }
    
    # Save scores to database
    scores_saved = 0
    for score_item in result["scores"]:
        ticker = score_item["ticker"]
        company_id = get_company_by_ticker(ticker)
        
        if company_id is None:
            print(f"[DEBUG] Company not found for ticker: {ticker}")
            continue
        
        success = save_score(
            company_id=company_id,
            date=target_date,
            score=score_item["score"],
            article_count=score_item["article_count"],
            avg_sentiment=score_item["avg_sentiment"],
            rank=score_item["rank"]
        )
        
        if success:
            scores_saved += 1
    
    print(f"[DEBUG] Saved {scores_saved} scores to database")
    
    return {
        "companies_scored": result["companies_scored"],
        "total_articles": result["total_articles"],
        "scores_saved": scores_saved
    }

@router.get("/scores/company/{ticker}")
async def get_company_scores(ticker: str, days: int = 30):
    """Get score history for a specific company"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM companies WHERE ticker = ?", (ticker,))
    company = cursor.fetchone()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company_id = company[0]
    
    query = """
    SELECT 
        s.date,
        s.score,
        s.article_count,
        s.avg_sentiment
    FROM scores s
    WHERE s.company_id = ?
    ORDER BY s.date DESC
    LIMIT ?
    """
    
    cursor.execute(query, (company_id, days))
    results = []
    for row in cursor.fetchall():
        results.append({
            "date": row[0],
            "score": row[1],
            "article_count": row[2],
            "avg_sentiment": row[3]
        })
    
    conn.close()
    return results
