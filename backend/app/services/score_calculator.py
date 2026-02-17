#!/usr/bin/env python3
"""
Score calculator: Calculate company scores based on articles and sentiment
"""

from datetime import date, datetime
from typing import List, Dict, Tuple
from app.database import get_articles_for_date
from app.config import SENTIMENT_THRESHOLD_POSITIVE, SENTIMENT_THRESHOLD_NEGATIVE

class ScoreCalculator:
    """Calculate company scores"""
    
    @staticmethod
    def calculate_for_date(target_date: date) -> Dict[str, any]:
        """Calculate scores for all companies on a date"""
        
        articles = get_articles_for_date(target_date)
        
        if not articles:
            return {"companies_scored": 0, "total_articles": 0}
        
        # Group by company
        company_stats = {}
        
        for article in articles:
            ticker = article["ticker"]
            if ticker not in company_stats:
                company_stats[ticker] = {
                    "article_count": 0,
                    "sentiment_scores": []
                }
            
            company_stats[ticker]["article_count"] += 1
            if article["sentiment_score"] is not None:
                company_stats[ticker]["sentiment_scores"].append(
                    article["sentiment_score"]
                )
        
        # Calculate scores
        scores = ScoreCalculator._calculate_scores(company_stats)
        
        return {
            "companies_scored": len(scores),
            "total_articles": len(articles),
            "scores": scores
        }
    
    @staticmethod
    def _calculate_scores(company_stats: Dict) -> List[Dict]:
        """Calculate score for each company"""
        scores = []
        
        for ticker, stats in company_stats.items():
            article_count = stats["article_count"]
            sentiment_scores = stats["sentiment_scores"]
            
            if not sentiment_scores:
                avg_sentiment = 0.0
            else:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # Calculate composite score
            # Score = (positive_articles - negative_articles) / total_articles
            positive_count = sum(
                1 for s in sentiment_scores 
                if s > SENTIMENT_THRESHOLD_POSITIVE
            )
            negative_count = sum(
                1 for s in sentiment_scores 
                if s < SENTIMENT_THRESHOLD_NEGATIVE
            )
            
            if article_count > 0:
                sentiment_ratio = (positive_count - negative_count) / article_count
            else:
                sentiment_ratio = 0.0
            
            # Composite score
            score = sentiment_ratio * 100 + avg_sentiment * 50
            
            scores.append({
                "ticker": ticker,
                "score": score,
                "article_count": article_count,
                "avg_sentiment": avg_sentiment,
                "positive_count": positive_count,
                "negative_count": negative_count
            })
        
        # Rank scores
        scores.sort(key=lambda x: x["score"], reverse=True)
        for rank, score_item in enumerate(scores, 1):
            score_item["rank"] = rank
        
        return scores
