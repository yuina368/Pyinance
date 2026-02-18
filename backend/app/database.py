#!/usr/bin/env python3
"""
Database: SQLite database operations
"""

import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional

# Use DATABASE_URL from environment or default to newspy.db
DB_PATH = os.getenv("DATABASE_URL", "newspy.db")

# Register date adapters for Python 3.12+
def adapt_date(val):
    return val.isoformat()

def adapt_datetime(val):
    return val.isoformat()

sqlite3.register_adapter(date, adapt_date)
sqlite3.register_adapter(datetime, adapt_datetime)

def init_database():
    """Initialize database tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Companies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Articles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        source TEXT,
        source_url TEXT UNIQUE,
        published_at TIMESTAMP,
        sentiment_score REAL,
        sentiment_confidence REAL,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (id)
    )
    """)
    
    # Scores table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        date DATE NOT NULL,
        score REAL,
        article_count INTEGER,
        avg_sentiment REAL,
        rank INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (id),
        UNIQUE (company_id, date)
    )
    """)
    
    conn.commit()
    conn.close()

def add_company(ticker: str, name: str) -> Optional[int]:
    """Add a company to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO companies (ticker, name) VALUES (?, ?)",
            (ticker, name)
        )
        conn.commit()
        company_id = cursor.lastrowid
        conn.close()
        return company_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def add_article(
    company_id: int,
    title: str,
    content: str,
    source: str,
    source_url: str,
    published_at: str,
    sentiment_score: Optional[float] = None,
    sentiment_confidence: Optional[float] = None
) -> bool:
    """Add an article to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO articles (
                company_id, title, content, source, source_url,
                published_at, sentiment_score, sentiment_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company_id, title, content, source, source_url,
            published_at, sentiment_score, sentiment_confidence
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_company_by_ticker(ticker: str) -> Optional[int]:
    """Get company ID by ticker"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM companies WHERE ticker = ?", (ticker,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_articles_for_date(target_date: date) -> List[Dict]:
    """Get all articles for a specific date"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            a.id, a.company_id, a.sentiment_score, c.ticker
        FROM articles a
        JOIN companies c ON a.company_id = c.id
        WHERE DATE(a.published_at) = ?
    """, (target_date,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "company_id": row[1],
            "sentiment_score": row[2],
            "ticker": row[3]
        }
        for row in results
    ]

def save_score(
    company_id: int,
    date: date,
    score: float,
    article_count: int,
    avg_sentiment: float,
    rank: int
) -> bool:
    """Save score for a company on a date"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO scores 
            (company_id, date, score, article_count, avg_sentiment, rank)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_id, date, score, article_count, avg_sentiment, rank))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving score: {e}")
        conn.close()
        return False

# Initialize database on import
if not os.path.exists(DB_PATH):
    init_database()
