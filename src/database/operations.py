from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import Source, Article, PublishingQueue
from config.logging_config import logger

class DatabaseOperations:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)
    
    def add_source(self, source_data: Dict[str, Any]) -> Optional[Source]:
        """Add a new news source."""
        session = self.Session()
        try:
            source = Source(**source_data)
            session.add(source)
            session.commit()
            return source
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Error adding source: {e}")
            return None
        finally:
            session.close()
    
    def get_sources(self, active_only: bool = True) -> List[Source]:
        """Get all news sources."""
        session = self.Session()
        try:
            query = session.query(Source)
            if active_only:
                query = query.filter(Source.is_active == True)
            return query.all()
        finally:
            session.close()
    
    def add_article(self, article_data: Dict[str, Any]) -> Optional[Article]:
        """Add a new article."""
        session = self.Session()
        try:
            article = Article(**article_data)
            session.add(article)
            session.commit()
            return article
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Error adding article: {e}")
            return None
        finally:
            session.close()
    
    def get_article_by_url(self, url: str) -> Optional[Article]:
        """Get an article by its URL."""
        session = self.Session()
        try:
            return session.query(Article).filter(Article.url == url).first()
        finally:
            session.close()
    
    def get_unpublished_articles(self, limit: int = 10) -> List[Article]:
        """Get articles that haven't been published yet."""
        session = self.Session()
        try:
            return session.query(Article)\
                .filter(Article.is_published == False)\
                .order_by(Article.published_at.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    def mark_article_as_published(self, article_id: int) -> bool:
        """Mark an article as published."""
        session = self.Session()
        try:
            article = session.query(Article).filter(Article.id == article_id).first()
            if article:
                article.is_published = True
                article.published_at = datetime.utcnow()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error marking article as published: {e}")
            return False
        finally:
            session.close()
    
    def add_to_publishing_queue(self, article_id: int, priority: int = 0, 
                              scheduled_time: Optional[datetime] = None) -> Optional[PublishingQueue]:
        """Add an article to the publishing queue."""
        session = self.Session()
        try:
            queue_item = PublishingQueue(
                article_id=article_id,
                priority=priority,
                scheduled_time=scheduled_time or datetime.utcnow()
            )
            session.add(queue_item)
            session.commit()
            return queue_item
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding to publishing queue: {e}")
            return None
        finally:
            session.close()
    
    def get_next_queued_article(self) -> Optional[PublishingQueue]:
        """Get the next article from the publishing queue."""
        session = self.Session()
        try:
            return session.query(PublishingQueue)\
                .filter(PublishingQueue.status == 'pending')\
                .order_by(PublishingQueue.priority.desc(), PublishingQueue.scheduled_time.asc())\
                .first()
        finally:
            session.close()
    
    def update_queue_item_status(self, queue_id: int, status: str) -> bool:
        """Update the status of a queue item."""
        session = self.Session()
        try:
            queue_item = session.query(PublishingQueue).filter(PublishingQueue.id == queue_id).first()
            if queue_item:
                queue_item.status = status
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating queue item status: {e}")
            return False
        finally:
            session.close() 