#!/usr/bin/env python3
"""
NewsSpY Dashboard - Streamlit Web App
NYSE Market Sentiment Analysis Dashboard
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Page config
st.set_page_config(
    page_title="NewsSpY - NYSE Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main { padding: 2rem; }
        .metric-card { background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; }
        .positive { color: #10b981; font-weight: bold; }
        .negative { color: #ef4444; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# API Base URL
API_URL = "http://127.0.0.1:8000/api"

# ============================================================================
# Helper Functions
# ============================================================================

@st.cache_data(ttl=60)
def fetch_companies():
    """Fetch all companies"""
    try:
        response = requests.get(f"{API_URL}/companies/", timeout=5)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Failed to fetch companies: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_ranking(date_str: str, sentiment_filter: Optional[str] = None):
    """Fetch ranking for a date"""
    try:
        params = {"limit": 100}
        if sentiment_filter:
            params["sentiment_filter"] = sentiment_filter
        response = requests.get(
            f"{API_URL}/scores/ranking/{date_str}",
            params=params,
            timeout=5
        )
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Failed to fetch ranking: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_articles(company_id: Optional[int] = None, sentiment_filter: Optional[str] = None, limit: int = 20):
    """Fetch articles"""
    try:
        params = {"limit": limit}
        if company_id:
            params["company_id"] = company_id
        if sentiment_filter:
            params["sentiment_filter"] = sentiment_filter
        response = requests.get(f"{API_URL}/articles/", params=params, timeout=5)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Failed to fetch articles: {e}")
        return []

def calculate_scores(date_str: str):
    """Calculate scores for a date"""
    try:
        response = requests.post(f"{API_URL}/scores/calculate/{date_str}", timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Failed to calculate scores: {e}")
        return None

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.header("⚙️ Settings")
    
    selected_date = st.date_input(
        "Select Date",
        value=datetime(2026, 2, 16),
        min_value=datetime(2026, 2, 1),
        max_value=datetime.now()
    )
    
    sentiment_filter = st.selectbox(
        "Sentiment Filter",
        options=["All", "Positive", "Negative"],
        index=0
    )
    
    sentiment_param = {
        "All": None,
        "Positive": "positive",
        "Negative": "negative"
    }[sentiment_filter]
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("📊 Calculate", use_container_width=True):
            with st.spinner("Calculating..."):
                result = calculate_scores(selected_date.isoformat())
                if result:
                    st.success(f"✓ {result['companies_scored']} companies")
                    st.cache_data.clear()
                    st.rerun()
    
    st.divider()
    
    try:
        health = requests.get(f"{API_URL}/health/", timeout=2).json()
        st.markdown(f"**Status**: {health['status'].upper()} ✅")
    except:
        st.warning("API unavailable")

# ============================================================================
# Main Dashboard
# ============================================================================

st.title("📊 NewsSpY - NYSE Market Sentiment")
st.markdown("Real-time news sentiment scoring for NYSE companies")

companies = fetch_companies()
ranking = fetch_ranking(selected_date.isoformat(), sentiment_param)

if not ranking:
    st.warning("No scores available. Click 'Calculate' to generate scores.")
else:
    # ========================================================================
    # Key Metrics
    # ========================================================================
    
    st.header("📈 Market Overview")
    
    positive_count = sum(1 for r in ranking if r["score"] > 0)
    negative_count = sum(1 for r in ranking if r["score"] < 0)
    neutral_count = sum(1 for r in ranking if r["score"] == 0)
    avg_score = sum(r["score"] for r in ranking) / len(ranking) if ranking else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Positive", positive_count)
    with col2:
        st.metric("📉 Negative", negative_count)
    with col3:
        st.metric("➖ Neutral", neutral_count)
    with col4:
        st.metric("📌 Avg Score", f"{avg_score:.2f}")
    
    # ========================================================================
    # Ranking Table
    # ========================================================================
    
    st.header("🏆 Company Ranking")
    
    ranking_data = []
    for item in ranking:
        ranking_data.append({
            "Rank": item["rank"],
            "Ticker": item["company"]["ticker"],
            "Company": item["company"]["name"],
            "Score": f"{item['score']:.2f}",
            "Articles": item["article_count"],
            "Avg Sentiment": f"{item['avg_sentiment']:.3f}" if item["avg_sentiment"] else "-"
        })
    
    df_ranking = pd.DataFrame(ranking_data)
    st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # Charts
    # ========================================================================
    
    st.header("📊 Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scores = [r["score"] for r in ranking[:10]]
        tickers = [r["company"]["ticker"] for r in ranking[:10]]
        
        fig = go.Figure(data=[
            go.Bar(
                x=tickers,
                y=scores,
                marker=dict(
                    color=scores,
                    colorscale="RdYlGn",
                    cmid=0,
                )
            )
        ])
        fig.update_layout(
            title="Top 10 Companies by Score",
            xaxis_title="Company",
            yaxis_title="Score",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(data=[
            go.Pie(
                labels=["Positive", "Negative", "Neutral"],
                values=[positive_count, negative_count, neutral_count],
                marker=dict(colors=["#10b981", "#ef4444", "#6b7280"])
            )
        ])
        fig.update_layout(
            title="Sentiment Distribution",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # Articles
    # ========================================================================
    
    st.header("📰 Recent News")
    
    articles = fetch_articles(sentiment_filter=sentiment_param, limit=15)
    
    if articles:
        for article in articles[:10]:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{article['title']}**")
                    st.caption(f"{article['source']} • {article['published_at'][:10]}")
                    st.markdown(article['content'][:200] + "...")
                
                with col2:
                    if article["sentiment_score"] is not None:
                        color = "🟢" if article["sentiment_score"] > 0 else "🔴"
                        st.markdown(f"{color} {article['sentiment_score']:.3f}")

st.divider()
st.markdown("NewsSpY v1.0 • API: http://localhost:8000/api", unsafe_allow_html=True)
