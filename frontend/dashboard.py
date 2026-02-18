#!/usr/bin/env python3
"""
NewsSpY Dashboard - Streamlit based interactive dashboard
"""

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json

# Configure Streamlit
st.set_page_config(
    page_title="NewsSpY Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .metric-card {
        border-radius: 10px;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

API_BASE_URL = "http://127.0.0.1:8000/api"

@st.cache_data(ttl=60)
def get_companies():
    """Get all companies"""
    try:
        response = requests.get(f"{API_BASE_URL}/companies/", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching companies: {e}")
        return []

@st.cache_data(ttl=60)
def get_ranking(date_str, sentiment_filter=None):
    """Get company ranking for a date"""
    try:
        params = {"limit": 100}
        if sentiment_filter:
            params["sentiment_filter"] = sentiment_filter
        
        response = requests.get(
            f"{API_BASE_URL}/scores/ranking/{date_str}",
            params=params,
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching ranking: {e}")
        return []

@st.cache_data(ttl=60)
def get_articles(company_id=None, ticker=None, sentiment_filter=None, limit=50):
    """Get articles with optional filter"""
    try:
        params = {"limit": limit}
        if company_id:
            params["company_id"] = company_id
        if ticker:
            params["ticker"] = ticker
        if sentiment_filter:
            params["sentiment_filter"] = sentiment_filter
        
        response = requests.get(
            f"{API_BASE_URL}/articles/",
            params=params,
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching articles: {e}")
        return []

@st.cache_data(ttl=300)
def get_company_scores(ticker, days=30):
    """Get score history for a company"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/scores/company/{ticker}?days={days}",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching company scores: {e}")
        return []

def render_health_check():
    """Render health check status"""
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/api/health/", timeout=5)
        data = response.json()
        return data.get("status") == "healthy"
    except:
        return False

# Header
st.title("📊 NewsSpY - NYSE News Sentiment Dashboard")
st.markdown("Real-time sentiment analysis and company scoring for NYSE listed companies")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Health check
    if render_health_check():
        st.success("✓ API Connected")
    else:
        st.error("✗ API Disconnected")
    
    # Date selector
    selected_date = st.date_input(
        "Select Date",
        value=datetime.now().date(),
        max_value=datetime.now().date()
    )
    
    # Sentiment filter
    sentiment_filter = st.selectbox(
        "Sentiment Filter",
        ["All", "Positive", "Negative"],
        index=0
    )
    
    # Companies list
    companies = get_companies()
    st.markdown("### Companies")
    for company in sorted(companies, key=lambda x: x['ticker']):
        st.caption(f"**{company['ticker']}** - {company['name']}")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📈 Ranking", "📰 Articles", "📊 Company Scores", "📋 Company Details"])

# Tab 1: Ranking
with tab1:
    st.subheader(f"Company Ranking - {selected_date.strftime('%B %d, %Y')}")
    
    # Map sentiment filter
    sentiment_map = {"All": None, "Positive": "positive", "Negative": "negative"}
    ranking_data = get_ranking(
        selected_date.isoformat(),
        sentiment_filter=sentiment_map.get(sentiment_filter)
    )
    
    if ranking_data:
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        positive_count = len([r for r in ranking_data if r['score'] > 0])
        negative_count = len([r for r in ranking_data if r['score'] < 0])
        neutral_count = len([r for r in ranking_data if r['score'] == 0])
        
        with col1:
            st.metric("Positive", positive_count, "📈")
        with col2:
            st.metric("Negative", negative_count, "📉")
        with col3:
            st.metric("Neutral", neutral_count, "➡️")
        
        st.markdown("---")
        
        # Ranking table
        ranking_df = pd.DataFrame([
            {
                "Rank": r['rank'],
                "Ticker": r['company']['ticker'],
                "Company": r['company']['name'],
                "Score": f"{r['score']:.2f}",
                "Articles": r['article_count'],
                "Avg Sentiment": f"{r['avg_sentiment']:.3f}" if r['avg_sentiment'] else "N/A"
            }
            for r in ranking_data
        ])
        
        st.dataframe(ranking_df, use_container_width=True, hide_index=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution
            scores = [float(r['score']) for r in ranking_data]
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.barh(
                [r['company']['ticker'] for r in ranking_data],
                scores,
                color=['#10b981' if s > 0 else '#ef4444' for s in scores]
            )
            ax.set_xlabel("Score")
            ax.set_title("Score Distribution")
            ax.grid(axis='x', alpha=0.3)
            st.pyplot(fig)
        
        with col2:
            # Article count
            article_counts = [r['article_count'] for r in ranking_data]
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.pie(
                article_counts,
                labels=[r['company']['ticker'] for r in ranking_data],
                autopct='%1.1f%%',
                colors=['#667eea', '#764ba2', '#fd57b1', '#ffa101', '#123456']
            )
            ax.set_title("Article Distribution")
            st.pyplot(fig)
    else:
        st.info("No ranking data available for this date")

# Tab 2: Articles
with tab2:
    st.subheader("📰 News Articles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_ticker = st.selectbox(
            "Filter by Company",
            options=[c['ticker'] for c in companies] if companies else [],
            index=0 if companies else None
        )
    
    with col2:
        articles_per_page = st.selectbox("Articles per page", [10, 20, 50], index=1)
    
    # Fetch articles
    articles = get_articles(
        ticker=selected_ticker if selected_ticker else None,
        sentiment_filter=sentiment_map.get(sentiment_filter),
        limit=articles_per_page
    )
    
    if articles:
        for article in articles:
            # Color based on sentiment
            sentiment_score = article.get('sentiment_score')
            if sentiment_score:
                if sentiment_score > 0:
                    sentiment_color = "🟢"
                    sentiment_text = "Positive"
                elif sentiment_score < 0:
                    sentiment_color = "🔴"
                    sentiment_text = "Negative"
                else:
                    sentiment_color = "🟡"
                    sentiment_text = "Neutral"
            else:
                sentiment_color = "⚪"
                sentiment_text = "Unknown"
            
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### {article['title']}")
                    st.caption(f"**{article['source']}** • {article['published_at']}")
                    st.write(article['content'][:200] + "..." if len(article['content']) > 200 else article['content'])
                
                with col2:
                    st.markdown(f"### {sentiment_color}")
                    st.caption(f"{sentiment_text}")
                    if sentiment_score is not None:
                        st.caption(f"Score: {sentiment_score:.3f}")
                        if article.get('sentiment_confidence'):
                            st.caption(f"Confidence: {article['sentiment_confidence']:.1%}")
                
                if article.get('source_url'):
                    st.markdown(f"[Read Original]({article['source_url']})", unsafe_allow_html=True)
                
                st.divider()
    else:
        st.info("No articles found")

# Tab 3: Company Scores
with tab3:
    st.subheader("📊 Company Score Trends")
    
    selected_company = st.selectbox(
        "Select Company",
        options=[c['ticker'] for c in companies] if companies else [],
        key="company_scores"
    )
    
    if selected_company:
        scores = get_company_scores(selected_company, days=30)
        
        if scores:
            scores_df = pd.DataFrame([
                {
                    "Date": s['date'],
                    "Score": float(s['score']),
                    "Articles": s['article_count'],
                    "Avg Sentiment": s.get('avg_sentiment', 0)
                }
                for s in scores
            ])
            
            # Chart
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(
                pd.to_datetime(scores_df['Date']),
                scores_df['Score'],
                marker='o',
                linewidth=2,
                markersize=8,
                color='#667eea'
            )
            ax.fill_between(
                pd.to_datetime(scores_df['Date']),
                scores_df['Score'],
                alpha=0.3,
                color='#667eea'
            )
            ax.set_xlabel("Date")
            ax.set_ylabel("Score")
            ax.set_title(f"{selected_company} Score Trend (Last 30 Days)")
            ax.grid(alpha=0.3)
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            
            st.dataframe(scores_df.sort_values('Date', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No score data available")

# Tab 4: Company Details
with tab4:
    st.subheader("📋 Company Information")
    
    selected_company_detail = st.selectbox(
        "Select Company",
        options=[c['ticker'] for c in companies] if companies else [],
        key="company_details"
    )
    
    if selected_company_detail:
        # Find company info
        company_info = next((c for c in companies if c['ticker'] == selected_company_detail), None)
        
        if company_info:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Ticker", company_info['ticker'])
            with col2:
                st.metric("Company", company_info['name'])
            with col3:
                st.metric("Created", company_info['created_at'][:10])
            
            st.markdown("---")
            
            # Get latest articles for this company
            company_articles = get_articles(ticker=selected_company_detail, limit=5)
            
            st.subheader(f"Recent Articles - {selected_company_detail}")
            if company_articles:
                for article in company_articles:
                    st.markdown(f"**{article['title']}**")
                    st.caption(f"{article['source']} • {article['published_at']}")
                    if article.get('sentiment_score') is not None:
                        st.caption(f"Sentiment: {article['sentiment_score']:.3f}")
                    st.divider()
            else:
                st.info("No recent articles")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
    NewsSpY © 2026 | NYSE News Analysis & Sentiment Scoring Dashboard
    </div>
    """, unsafe_allow_html=True)
