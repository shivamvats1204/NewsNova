from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    type = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    articles = relationship("Article", back_populates="source")

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    content = Column(Text)
    summary = Column(Text)
    category = Column(String(50))
    author = Column(String(200))
    published_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_published = Column(Boolean, default=False)
    
    source = relationship("Source", back_populates="articles")

class PublishingQueue(Base):
    __tablename__ = 'publishing_queue'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    priority = Column(Integer, default=0)
    scheduled_time = Column(DateTime)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    article = relationship("Article")

def init_db(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine 