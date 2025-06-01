from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta
from .database import get_db
from .models import Article, Topic, Source, ScrapingLog
from .services.scraping_service import ScrapingService
import asyncio

app = FastAPI(title="Nigerian Financial News Scraper")

@app.on_event("startup")
async def startup_event():
    """Start the scraping scheduler on startup"""
    asyncio.create_task(start_scraping_scheduler())

async def start_scraping_scheduler():
    """Start the scraping scheduler"""
    from .services.scraping_service import schedule_scraping
    schedule_scraping()

@app.get("/")
async def root():
    return {"message": "Nigerian Financial News Scraper API"}

@app.get("/articles/latest")
async def get_latest_articles(
    limit: int = 10,
    skip: int = 0,
    category: str = None,
    source: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get latest articles with optional filtering"""
    query = select(Article).order_by(Article.published_at.desc())
    
    if category:
        query = query.filter(Article.category == category)
    if source:
        query = query.filter(Article.source == source)
        
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return articles

@app.get("/articles/trending")
async def get_trending_articles(
    hours: int = 24,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get trending articles based on recent activity"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(Article).filter(
        Article.published_at >= since
    ).order_by(Article.published_at.desc()).limit(limit)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return articles

@app.get("/topics/trending")
async def get_trending_topics(
    hours: int = 24,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get trending topics based on recent articles"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(Topic).join(
        Topic.articles
    ).filter(
        Article.published_at >= since
    ).group_by(Topic.id).order_by(
        Topic.articles.count().desc()
    ).limit(limit)
    
    result = await db.execute(query)
    topics = result.scalars().all()
    
    return topics

@app.get("/sources/status")
async def get_sources_status(db: AsyncSession = Depends(get_db)):
    """Get status of all news sources"""
    query = select(Source)
    result = await db.execute(query)
    sources = result.scalars().all()
    
    return sources

@app.get("/scraping/logs")
async def get_scraping_logs(
    limit: int = 10,
    source: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get recent scraping logs"""
    query = select(ScrapingLog).order_by(ScrapingLog.started_at.desc())
    
    if source:
        query = query.join(Source).filter(Source.name == source)
        
    query = query.limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs

@app.post("/scraping/run")
async def trigger_scraping():
    """Manually trigger a scraping run"""
    try:
        service = ScrapingService()
        await service.run_scraping()
        return {"message": "Scraping completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 