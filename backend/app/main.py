#!/usr/bin/env python3
"""
NewsSpY Backend API
FastAPI based backend for news sentiment analysis and company scoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from datetime import datetime, date
from typing import List, Optional

from app.routes.articles import router as articles_router
from app.routes.scores import router as scores_router

app = FastAPI(
    title="NewsSpY API",
    description="API for NYSE news sentiment analysis and company scoring",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(articles_router, prefix="/api")
app.include_router(scores_router, prefix="/api")

@app.get("/api/health/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/companies/")
async def get_companies():
    """Get all companies"""
    conn = sqlite3.connect("newspy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies ORDER BY ticker")
    companies = []
    for row in cursor.fetchall():
        companies.append({
            "id": row[0],
            "ticker": row[1],
            "name": row[2],
            "created_at": row[3]
        })
    conn.close()
    return companies

