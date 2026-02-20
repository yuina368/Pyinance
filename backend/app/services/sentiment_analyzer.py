#!/usr/bin/env python3
from typing import Tuple
from transformers import pipeline

class SentimentAnalyzer:
    
    def __init__(self):
        self.classifier = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert"
        )
        
        # ポジティブキーワードのリスト
        self.positive_keywords = [
            "growth", "increase", "rise", "surge", "gain", "profit", "revenue",
            "earnings", "beat", "exceed", "strong", "positive", "bullish",
            "expansion", "success", "breakthrough", "innovation", "launch",
            "record", "high", "upgrade", "outperform", "buy", "recommend",
            "recovery", "momentum", "rally", "boost", "accelerate", "expand",
            "acquire", "partnership", "collaboration", "investment", "fund",
            "dividend", "yield", "return", "margin", "outlook", "guidance",
            "forecast", "target", "potential", "opportunity", "advantage",
            "lead", "dominate", "market share", "competitive", "scale",
            "efficient", "productivity", "optimize", "streamline", "improve",
            "enhance", "upgrade", "modernize", "transform", "revolutionize"
        ]
        
        # ネガティブキーワードのリスト
        self.negative_keywords = [
            "decline", "decrease", "fall", "drop", "loss", "downgrade", "sell",
            "underperform", "miss", "weak", "negative", "bearish", "concern",
            "risk", "challenge", "issue", "problem", "crisis", "recession",
            "slowdown", "contraction", "layoff", "cut", "reduce", "downsize",
            "delay", "postpone", "cancel", "suspend", "investigation", "lawsuit",
            "regulatory", "compliance", "penalty", "fine", "sanction", "ban",
            "restriction", "limit", "shortage", "shortfall", "deficit", "debt",
            "default", "bankruptcy", "insolvency", "liquidation", "closure",
            "shutdown", "exit", "withdraw", "abandon", "fail", "failure",
            "disappoint", "disappointing", "worse", "worsening", "deteriorate"
        ]
    
    def analyze(self, text: str) -> Tuple[float, float]:
        if not text:
            return 0.0, 0.0
        
        # FinBERTはトークン上限512なので切り捨て
        result = self.classifier(text[:512])[0]
        
        label = result["label"]   # positive / negative / neutral
        confidence = result["score"]
        
        # キーワードベースの感情スコア計算
        text_lower = text.lower()
        keyword_score = self._calculate_keyword_score(text_lower)
        
        # FinBERTの結果とキーワードスコアを組み合わせる
        if label == "positive":
            # ポジティブ判定の場合、キーワードスコアを加算して強化
            score = confidence + (keyword_score * 0.3)
        elif label == "negative":
            # ネガティブ判定の場合、キーワードスコアを加算して調整
            score = -confidence + (keyword_score * 0.3)
        else:
            # ニュートラル判定の場合、キーワードスコアを主要な判定基準に
            score = keyword_score * 0.7
        
        # スコアを-1.0から1.0の範囲に正規化
        score = max(-1.0, min(1.0, score))
        
        return score, confidence
    
    def _calculate_keyword_score(self, text: str) -> float:
        """キーワードベースの感情スコアを計算"""
        positive_count = sum(1 for kw in self.positive_keywords if kw in text)
        negative_count = sum(1 for kw in self.negative_keywords if kw in text)
        
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.0
        
        # ポジティブキーワードが多いほどポジティブスコア
        score = (positive_count - negative_count) / max(1, total_count)
        return score
    
    def analyze_batch(self, texts: list) -> list:
        results = []
        for text in texts:
            score, confidence = self.analyze(text)
            results.append({
                "sentiment_score": score,
                "sentiment_confidence": confidence
            })
        return results
