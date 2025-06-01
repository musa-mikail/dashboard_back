from abc import ABC, abstractmethod
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Article, Source, ScrapingLog, Topic
from ..database import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.session = None
        self.rate_limit = asyncio.Semaphore(5)  # Max 5 concurrent requests

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def get_article_urls(self, category: str) -> List[str]:
        """Get list of article URLs for a given category"""
        pass

    @abstractmethod
    async def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a single article page"""
        pass

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with rate limiting"""
        async with self.rate_limit:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    logger.error(f"Failed to fetch {url}: Status {response.status}")
                    return None
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                return None

    async def scrape_category(self, category: str) -> List[Dict]:
        """Scrape all articles in a category"""
        articles = []
        urls = await self.get_article_urls(category)
        
        for url in urls:
            try:
                article_data = await self.parse_article(url)
                if article_data:
                    articles.append(article_data)
            except Exception as e:
                logger.error(f"Error scraping article {url}: {str(e)}")
                continue
                
        return articles

    async def save_articles(self, articles: List[Dict], session: AsyncSession):
        """Save scraped articles to database"""
        for article_data in articles:
            try:
                # Check if article already exists
                existing = await session.execute(
                    "SELECT id FROM articles WHERE url = :url",
                    {"url": article_data['url']}
                )
                if existing.scalar_one_or_none():
                    continue

                # Create new article
                article = Article(**article_data)
                session.add(article)
                
                # Handle topics
                if 'topics' in article_data:
                    for topic_name in article_data['topics']:
                        topic = await session.execute(
                            "SELECT id FROM topics WHERE name = :name",
                            {"name": topic_name}
                        )
                        topic_id = topic.scalar_one_or_none()
                        
                        if not topic_id:
                            new_topic = Topic(name=topic_name)
                            session.add(new_topic)
                            await session.flush()
                            topic_id = new_topic.id
                            
                        await session.execute(
                            "INSERT INTO article_topics (article_id, topic_id) VALUES (:article_id, :topic_id)",
                            {"article_id": article.id, "topic_id": topic_id}
                        )

            except Exception as e:
                logger.error(f"Error saving article {article_data.get('url')}: {str(e)}")
                continue

        await session.commit()

    async def log_scraping(self, status: str, articles_found: int, articles_scraped: int, 
                          error_message: Optional[str] = None, session: AsyncSession = None):
        """Log scraping activity"""
        try:
            if not session:
                async with AsyncSessionLocal() as session:
                    await self._create_log(session, status, articles_found, articles_scraped, error_message)
            else:
                await self._create_log(session, status, articles_found, articles_scraped, error_message)
        except Exception as e:
            logger.error(f"Error logging scraping activity: {str(e)}")

    async def _create_log(self, session: AsyncSession, status: str, articles_found: int, 
                         articles_scraped: int, error_message: Optional[str]):
        """Create scraping log entry"""
        source = await session.execute(
            "SELECT id FROM sources WHERE name = :name",
            {"name": self.source_name}
        )
        source_id = source.scalar_one_or_none()
        
        if not source_id:
            source = Source(name=self.source_name, base_url=self.base_url)
            session.add(source)
            await session.flush()
            source_id = source.id

        log = ScrapingLog(
            source_id=source_id,
            status=status,
            articles_found=articles_found,
            articles_scraped=articles_scraped,
            error_message=error_message,
            started_at=datetime.utcnow()
        )
        session.add(log)
        await session.commit() 