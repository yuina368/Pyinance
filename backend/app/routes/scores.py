from fastapi import APIRouter, HTTPException
import sqlite3
from typing import Optional
from datetime import datetime, date

router = APIRouter(tags=["scores"])

@router.get("/scores/ranking/{date_str}")
async def get_ranking(date_str: str, limit: int = 100, sentiment_filter: Optional[str] = None):
    """Get company ranking for a specific date"""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    conn = sqlite3.connect("newspy.db")
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
    
    conn.close()
    return results

@router.get("/scores/company/{ticker}")
async def get_company_scores(ticker: str, days: int = 30):
    """Get score history for a specific company"""
    conn = sqlite3.connect("newspy.db")
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
