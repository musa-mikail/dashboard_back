import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import AsyncSessionLocal
from ..scrapers.nairametrics import NairametricsScraper
from ..models import Source

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self):
        self.scrapers = [
            NairametricsScraper(),
            # Add more scrapers here
        ]

    async def run_scraping(self):
        """Run scraping for all sources"""
        async with AsyncSessionLocal() as session:
            for scraper in self.scrapers:
                try:
                    await self._scrape_source(scraper, session)
                except Exception as e:
                    logger.error(f"Error scraping {scraper.source_name}: {str(e)}")
                    await scraper.log_scraping(
                        status="error",
                        articles_found=0,
                        articles_scraped=0,
                        error_message=str(e),
                        session=session
                    )

    async def _scrape_source(self, scraper, session: AsyncSession):
        """Scrape a single source"""
        total_articles_found = 0
        total_articles_scraped = 0
        error_message = None

        try:
            async with scraper as scraper_instance:
                for category in scraper.categories:
                    try:
                        # Get article URLs
                        urls = await scraper_instance.get_article_urls(category)
                        total_articles_found += len(urls)

                        # Scrape articles
                        articles = await scraper_instance.scrape_category(category)
                        total_articles_scraped += len(articles)

                        # Save articles
                        if articles:
                            await scraper_instance.save_articles(articles, session)

                    except Exception as e:
                        logger.error(f"Error scraping category {category}: {str(e)}")
                        error_message = str(e)
                        continue

                # Update source last scraped time
                await self._update_source_last_scraped(scraper.source_name, session)

                # Log scraping results
                status = "success" if not error_message else "partial"
                await scraper_instance.log_scraping(
                    status=status,
                    articles_found=total_articles_found,
                    articles_scraped=total_articles_scraped,
                    error_message=error_message,
                    session=session
                )

        except Exception as e:
            logger.error(f"Error in scraping process for {scraper.source_name}: {str(e)}")
            raise

    async def _update_source_last_scraped(self, source_name: str, session: AsyncSession):
        """Update the last scraped timestamp for a source"""
        try:
            await session.execute(
                "UPDATE sources SET last_scraped_at = :now WHERE name = :name",
                {"now": datetime.utcnow(), "name": source_name}
            )
            await session.commit()
        except Exception as e:
            logger.error(f"Error updating last scraped time for {source_name}: {str(e)}")

async def run_scraping_job():
    """Run the scraping job"""
    service = ScrapingService()
    await service.run_scraping()

def schedule_scraping():
    """Schedule regular scraping jobs"""
    import schedule
    import time
    import asyncio

    def run_job():
        asyncio.run(run_scraping_job())

    # Schedule scraping every 30 minutes
    schedule.every(30).minutes.do(run_job)

    # Run immediately on startup
    run_job()

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_scraping() 