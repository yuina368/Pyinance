#!/usr/bin/env python3
"""
Sentiment analyzer: Analyze sentiment of text
"""

from typing import Tuple, Optional

class SentimentAnalyzer:
    """Simple sentiment analyzer using TextBlob-like approach"""
    
    def __init__(self):
        self.positive_words = {
            "excellent", "great", "good", "positive", "gain", "surge",
            "rocket", "breakthrough", "record", "beat", "outperform",
            "strong", "impressive", "bullish", "growth", "rise"
        }
        
        self.negative_words = {
            "poor", "bad", "negative", "loss", "decline", "crash",
            "drop", "fail", "miss", "underperform", "weak", "bearish",
            "down", "slump", "concern", "risk", "warning", "trouble"
        }
    
    def analyze(self, text: str) -> Tuple[float, float]:
        """
        Analyze sentiment of text
        Returns: (sentiment_score, confidence)
        sentiment_score: -1.0 to 1.0 (negative to positive)
        confidence: 0.0 to 1.0 (0 = no confidence, 1 = high confidence)
        """
        
        if not text:
            return 0.0, 0.0
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return 0.0, 0.0
        
        # Calculate sentiment score
        score = (positive_count - negative_count) / max(total_sentiment_words, 1)
        
        # Normalize to -1 to 1 range
        score = max(-1.0, min(1.0, score))
        
        # Calculate confidence
        confidence = min(total_sentiment_words / len(words), 1.0)
        
        return score, confidence
    
    def analyze_batch(self, texts: list) -> list:
        """Analyze multiple texts"""
        results = []
        for text in texts:
            score, confidence = self.analyze(text)
            results.append({
                "sentiment_score": score,
                "sentiment_confidence": confidence
            })
        return results
