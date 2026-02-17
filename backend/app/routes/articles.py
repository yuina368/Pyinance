from fastapi import APIRouter, HTTPException
import sqlite3
from typing import Optional

router = APIRouter(tags=["articles"])

@router.get("/articles/")
async def get_articles(
    company_id: Optional[int] = None,
    ticker: Optional[str] = None,
    sentiment_filter: Optional[str] = None,
    limit: int = 50
):
    """Get articles with optional filters"""
    conn = sqlite3.connect("newspy.db")
    cursor = conn.cursor()
    
    query = """
    SELECT 
        a.id,
        a.title,
        a.content,
        a.source,
        a.source_url,
        a.published_at,
        a.sentiment_score,
        a.sentiment_confidence,
        a.company_id,
        c.ticker
    FROM articles a
    JOIN companies c ON a.company_id = c.id
    """
    
    params = []
    
    conditions = []
    if company_id:
        conditions.append("a.company_id = ?")
        params.append(company_id)
    if ticker:
        conditions.append("c.ticker = ?")
        params.append(ticker)
    if sentiment_filter:
        if sentiment_filter == "positive":
            conditions.append("a.sentiment_score > 0")
        elif sentiment_filter == "negative":
            conditions.append("a.sentiment_score < 0")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY a.published_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "source": row[3],
            "source_url": row[4],
            "published_at": row[5],
            "sentiment_score": row[6],
            "sentiment_confidence": row[7],
            "company_id": row[8],
            "ticker": row[9]
        })
    
    conn.close()
    return results
