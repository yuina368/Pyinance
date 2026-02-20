#!/usr/bin/env python3
"""
Database: SQLite database operations with connection pooling
"""

import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional
from contextlib import contextmanager
from threading import local

# Use DATABASE_URL from environment or default to newspy.db
DB_PATH = os.getenv("DATABASE_URL", "newspy.db")

# Thread-local storage for connections
_thread_local = local()

# Connection pool settings
MAX_CONNECTIONS = 5

# Register date adapters for Python 3.12+
def adapt_date(val):
    return val.isoformat()

def adapt_datetime(val):
    return val.isoformat()

sqlite3.register_adapter(date, adapt_date)
sqlite3.register_adapter(datetime, adapt_datetime)


@contextmanager
def get_db_connection():
    """
    Get a database connection from the pool (thread-local)
    Context manager for automatic connection handling
    """
    if not hasattr(_thread_local, 'connection'):
        _thread_local.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    
    conn = _thread_local.connection
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        # Don't close the connection, it will be reused
        pass


def close_db_connection():
    """Close the current thread's database connection"""
    if hasattr(_thread_local, 'connection'):
        _thread_local.connection.close()
        del _thread_local.connection

def init_database():
    """Initialize database tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        
        # Companies table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            keywords TEXT,
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
        
        # News Sentiments table (for detailed design prompt requirements)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_sentiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            published_at TIMESTAMP NOT NULL,
            sentiment_score REAL NOT NULL,
            label TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            url_hash TEXT UNIQUE
        )
        """)
        
        # Create index on ticker for news_sentiments
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_news_sentiments_ticker 
        ON news_sentiments(ticker)
        """)
        
        # Create index on published_at for news_sentiments
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_news_sentiments_published_at 
        ON news_sentiments(published_at)
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

def add_company(ticker: str, name: str) -> Optional[int]:
    """Add a company to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO companies (ticker, name) VALUES (?, ?)",
                (ticker, name)
            )
            conn.commit()
            company_id = cursor.lastrowid
            return company_id
        except sqlite3.IntegrityError:
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
    import time
    max_retries = 3
    retry_delay = 0.1  # 100ms
    
    for attempt in range(max_retries):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
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
                return True
        except sqlite3.IntegrityError as e:
            print(f"[DEBUG] IntegrityError for article: {title[:50]}... - {e}")
            return False
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            print(f"[DEBUG] Error adding article: {title[:50]}... - {type(e).__name__}: {e}")
            return False
        except Exception as e:
            print(f"[DEBUG] Error adding article: {title[:50]}... - {type(e).__name__}: {e}")
            return False
    
    return False

def get_company_by_ticker(ticker: str) -> Optional[int]:
    """Get company ID by ticker"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM companies WHERE ticker = ?", (ticker,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_articles_for_date(target_date: date) -> List[Dict]:
    """Get all articles for a specific date"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.id, a.company_id, a.sentiment_score, c.ticker
            FROM articles a
            JOIN companies c ON a.company_id = c.id
            WHERE DATE(a.published_at) = ?
        """, (target_date,))
        
        results = cursor.fetchall()
        
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
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO scores 
                (company_id, date, score, article_count, avg_sentiment, rank)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, date, score, article_count, avg_sentiment, rank))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving score: {e}")
            return False

def save_news_sentiment(
    ticker: str,
    published_at: str,
    sentiment_score: float,
    label: str,
    url_hash: Optional[str] = None
) -> bool:
    """Save news sentiment record"""
    import hashlib
    
    # Generate URL hash if not provided
    if url_hash is None:
        url_hash = hashlib.md5(f"{ticker}_{published_at}".encode()).hexdigest()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO news_sentiments 
                (ticker, published_at, sentiment_score, label, url_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (ticker, published_at, sentiment_score, label, url_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Duplicate entry (same url_hash)
            return False
        except Exception as e:
            print(f"Error saving news sentiment: {e}")
            return False

def get_daily_sentiments(target_date: date) -> List[Dict]:
    """Get daily sentiment scores for all companies"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                ticker,
                AVG(sentiment_score) as avg_score,
                COUNT(*) as article_count
            FROM news_sentiments
            WHERE DATE(published_at) = ?
            GROUP BY ticker
            ORDER BY avg_score DESC
        """, (target_date,))
        
        results = cursor.fetchall()
        
        return [
            {
                "ticker": row[0],
                "avg_score": row[1],
                "article_count": row[2]
            }
            for row in results
        ]

def get_ticker_sentiment_history(ticker: str, days: int = 30) -> List[Dict]:
    """Get sentiment history for a specific ticker"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(published_at) as date,
                AVG(sentiment_score) as avg_score,
                COUNT(*) as article_count,
                AVG(CASE WHEN label = 'positive' THEN 1 ELSE 0 END) * 100 as positive_pct,
                AVG(CASE WHEN label = 'negative' THEN 1 ELSE 0 END) * 100 as negative_pct,
                AVG(CASE WHEN label = 'neutral' THEN 1 ELSE 0 END) * 100 as neutral_pct
            FROM news_sentiments
            WHERE ticker = ?
            AND DATE(published_at) >= DATE('now', '-' || ? || ' days')
            GROUP BY DATE(published_at)
            ORDER BY date DESC
            LIMIT ?
        """, (ticker, days, days))
        
        results = cursor.fetchall()
        
        return [
            {
                "date": row[0],
                "avg_score": row[1],
                "article_count": row[2],
                "positive_pct": row[3],
                "negative_pct": row[4],
                "neutral_pct": row[5]
            }
            for row in results
        ]

# Initialize database on import
if not os.path.exists(DB_PATH):
    init_database()
