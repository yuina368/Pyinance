#!/usr/bin/env python3
"""
Config: Application configuration
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# NewsAPI
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "demo")
NEWSAPI_BASE_URL = "https://newsapi.org/v2"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "newspy.db")

# Load companies from JSON file
def load_companies():
    """Load companies from companies.json file"""
    companies_file = Path(__file__).parent.parent / "companies.json"
    
    if companies_file.exists():
        with open(companies_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Fallback to hardcoded list if file doesn't exist
        return [
            {"ticker": "AAPL", "name": "Apple Inc.", "keywords": ["Apple", "iPhone"]},
            {"ticker": "MSFT", "name": "Microsoft Corporation", "keywords": ["Microsoft", "Windows"]},
            {"ticker": "GOOGL", "name": "Alphabet Inc.", "keywords": ["Google", "Alphabet"]},
            {"ticker": "AMZN", "name": "Amazon.com Inc.", "keywords": ["Amazon", "AWS"]},
            {"ticker": "TSLA", "name": "Tesla Inc.", "keywords": ["Tesla", "Elon Musk"]},
        ]

NYSE_COMPANIES = load_companies()

# Sentiment Analysis
SENTIMENT_THRESHOLD_POSITIVE = 0.05
SENTIMENT_THRESHOLD_NEGATIVE = -0.05
