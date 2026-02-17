#!/usr/bin/env python3
"""
Config: Application configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# NewsAPI
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "demo")
NEWSAPI_BASE_URL = "https://newsapi.org/v2"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "newspy.db")

# Companies to track (NYSE/NASDAQ top companies - Expanded list)
NYSE_COMPANIES = [
    # Technology
    {"ticker": "AAPL", "name": "Apple Inc."},
    {"ticker": "MSFT", "name": "Microsoft Corporation"},
    {"ticker": "GOOGL", "name": "Alphabet Inc."},
    {"ticker": "AMZN", "name": "Amazon.com Inc."},
    {"ticker": "TSLA", "name": "Tesla Inc."},
    {"ticker": "META", "name": "Meta Platforms Inc."},
    {"ticker": "NVDA", "name": "NVIDIA Corporation"},
    {"ticker": "NFLX", "name": "Netflix Inc."},
    {"ticker": "CRM", "name": "Salesforce Inc."},
    {"ticker": "ADOBE", "name": "Adobe Inc."},
    
    # Finance
    {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
    {"ticker": "BAC", "name": "Bank of America Corporation"},
    {"ticker": "WFC", "name": "Wells Fargo & Company"},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc."},
    {"ticker": "MS", "name": "Morgan Stanley"},
    {"ticker": "BLK", "name": "BlackRock Inc."},
    {"ticker": "ICE", "name": "Intercontinental Exchange Inc."},
    {"ticker": "CME", "name": "CME Group Inc."},
    
    # Healthcare
    {"ticker": "JNJ", "name": "Johnson & Johnson"},
    {"ticker": "UNH", "name": "UnitedHealth Group Inc."},
    {"ticker": "PFE", "name": "Pfizer Inc."},
    {"ticker": "ABBV", "name": "AbbVie Inc."},
    {"ticker": "MRK", "name": "Merck & Co. Inc."},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific"},
    {"ticker": "LLY", "name": "Eli Lilly and Company"},
    
    # Consumer/Retail
    {"ticker": "WMT", "name": "Walmart Inc."},
    {"ticker": "KO", "name": "The Coca-Cola Company"},
    {"ticker": "PEP", "name": "PepsiCo Inc."},
    {"ticker": "COST", "name": "Costco Wholesale Corporation"},
    {"ticker": "MCD", "name": "McDonald's Corporation"},
    {"ticker": "NKE", "name": "Nike Inc."},
    {"ticker": "LOW", "name": "Lowe's Companies Inc."},
    
    # Finance (Payment/Card)
    {"ticker": "V", "name": "Visa Inc."},
    {"ticker": "MA", "name": "Mastercard Incorporated"},
    {"ticker": "AXP", "name": "American Express Company"},
    
    # Energy/Industrials
    {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "BA", "name": "Boeing Company"},
    {"ticker": "HON", "name": "Honeywell International Inc."},
    {"ticker": "GE", "name": "General Electric Company"},
    
    # Communications
    {"ticker": "VZ", "name": "Verizon Communications Inc."},
    {"ticker": "T", "name": "AT&T Inc."},
    {"ticker": "CMCSA", "name": "Comcast Corporation"},
    {"ticker": "DIS", "name": "The Walt Disney Company"},
]

# Sentiment Analysis
SENTIMENT_THRESHOLD_POSITIVE = 0.05
SENTIMENT_THRESHOLD_NEGATIVE = -0.05
