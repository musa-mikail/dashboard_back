from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import Dict, List, Optional
from .base import BaseScraper
import logging

logger = logging.getLogger(__name__)

class NairametricsScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_name="Nairametrics",
            base_url="https://nairametrics.com"
        )
        self.categories = [
            'banking',
            'economy',
            'markets',
            'technology',
            'business'
        ]
        self.selectors = {
            'article_list': 'div.post-listing article.post',
            'title': 'h2.entry-title a',
            'content': 'div.entry-content p',
            'date': 'time.entry-date',
            'author': 'span.author-name',
            'category': 'span.category-name'
        }

    async def get_article_urls(self, category: str) -> List[str]:
        """Get list of article URLs for a given category"""
        urls = []
        category_url = f"{self.base_url}/category/{category}/"
        
        try:
            html = await self.fetch_page(category_url)
            if not html:
                return urls

            soup = BeautifulSoup(html, 'lxml')
            articles = soup.select(self.selectors['article_list'])
            
            for article in articles:
                link = article.select_one(self.selectors['title'])
                if link and 'href' in link.attrs:
                    urls.append(link['href'])

        except Exception as e:
            logger.error(f"Error getting article URLs for {category}: {str(e)}")

        return urls

    async def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a single article page"""
        try:
            html = await self.fetch_page(url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'lxml')
            
            # Extract title
            title_elem = soup.select_one(self.selectors['title'])
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Extract content
            content_elems = soup.select(self.selectors['content'])
            content = ' '.join([p.get_text(strip=True) for p in content_elems])
            
            # Extract date
            date_elem = soup.select_one(self.selectors['date'])
            published_at = datetime.utcnow()
            if date_elem and 'datetime' in date_elem.attrs:
                try:
                    published_at = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Could not parse date for {url}")

            # Extract author
            author_elem = soup.select_one(self.selectors['author'])
            author = author_elem.get_text(strip=True) if author_elem else None

            # Extract category
            category_elem = soup.select_one(self.selectors['category'])
            category = category_elem.get_text(strip=True) if category_elem else None

            # Calculate word count and reading time
            word_count = len(content.split())
            reading_time = max(1, word_count // 200)  # Assuming 200 words per minute

            # Extract topics (using category and content analysis)
            topics = self._extract_topics(content, category)

            return {
                'title': title,
                'content': content,
                'url': url,
                'source': self.source_name,
                'published_at': published_at,
                'author': author,
                'category': category,
                'word_count': word_count,
                'reading_time': reading_time,
                'topics': topics
            }

        except Exception as e:
            logger.error(f"Error parsing article {url}: {str(e)}")
            return None

    def _extract_topics(self, content: str, category: Optional[str]) -> List[str]:
        """Extract topics from content and category"""
        topics = set()
        
        # Add category as a topic
        if category:
            topics.add(category.lower())

        # Common financial topics to look for
        financial_topics = {
            'banking': ['bank', 'banking', 'cbn', 'central bank'],
            'economy': ['economy', 'economic', 'gdp', 'inflation'],
            'markets': ['market', 'stock', 'nse', 'trading'],
            'technology': ['tech', 'digital', 'fintech', 'blockchain'],
            'business': ['business', 'company', 'corporate', 'enterprise']
        }

        # Check content for topic keywords
        content_lower = content.lower()
        for topic, keywords in financial_topics.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.add(topic)

        return list(topics) 