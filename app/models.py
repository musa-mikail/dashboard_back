from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Association table for article topics
article_topics = Table(
    'article_topics',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id')),
    Column('topic_id', Integer, ForeignKey('topics.id'))
)

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(255), unique=True, nullable=False)
    source = Column(String(50), nullable=False)
    published_at = Column(DateTime, nullable=False)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    author = Column(String(100))
    category = Column(String(50))
    word_count = Column(Integer)
    reading_time = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    topics = relationship("Topic", secondary=article_topics, back_populates="articles")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    articles = relationship("Article", secondary=article_topics, back_populates="topics")

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    base_url = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)
    last_scraped_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScrapingLog(Base):
    __tablename__ = "scraping_logs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('sources.id'))
    status = Column(String(20), nullable=False)  # success, error, partial
    articles_found = Column(Integer, default=0)
    articles_scraped = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow) 