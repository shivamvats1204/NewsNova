import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio
from queue import PriorityQueue
import threading

from config.settings import DEFAULT_PUBLISHING_INTERVAL, MAX_QUEUE_SIZE, BATCH_PUBLISH_SIZE
from config.logging_config import logger

class PublishingScheduler:
    def __init__(self):
        self.queue = PriorityQueue(maxsize=MAX_QUEUE_SIZE)
        self.schedule_thread = None
        self.is_running = False
        self.publishing_interval = DEFAULT_PUBLISHING_INTERVAL
    
    def start(self):
        """Start the scheduler."""
        if not self.is_running:
            self.is_running = True
            self.schedule_thread = threading.Thread(target=self._run_scheduler)
            self.schedule_thread.daemon = True
            self.schedule_thread.start()
            logger.info("Publishing scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.is_running = False
        if self.schedule_thread:
            self.schedule_thread.join()
        logger.info("Publishing scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def add_to_queue(self, article: Dict[str, Any], priority: int = 0,
                     scheduled_time: Optional[datetime] = None) -> bool:
        """Add an article to the publishing queue."""
        try:
            if scheduled_time is None:
                scheduled_time = datetime.utcnow() + timedelta(seconds=self.publishing_interval)
            
            # Create queue item with tuple for proper ordering
            queue_item = (
                -priority,  # Negative for correct priority queue ordering
                scheduled_time.timestamp(),  # Convert to timestamp for comparison
                article
            )
            
            # Add to queue
            self.queue.put(queue_item)
            logger.info(f"Added article to queue: {article.get('title', '')}")
            return True
        except Exception as e:
            logger.error(f"Error adding article to queue: {str(e)}")
            return False
    
    def get_next_article(self) -> Optional[Dict[str, Any]]:
        """Get the next batch of articles from the queue."""
        try:
            if self.queue.empty():
                return None
            
            current_time = datetime.utcnow()
            articles = []
            
            # Try to get up to BATCH_PUBLISH_SIZE articles that are ready
            for _ in range(BATCH_PUBLISH_SIZE):
                if self.queue.empty():
                    break
                    
                priority, timestamp, article = self.queue.get()
                scheduled_time = datetime.fromtimestamp(timestamp)
                
                if scheduled_time > current_time:
                    # Put back in queue if not ready
                    self.queue.put((priority, timestamp, article))
                    break
                
                articles.append(article)
            
            # If we got any articles, return them as a batch
            if articles:
                return {'batch': articles}
            return None
            
        except Exception as e:
            logger.error(f"Error getting next articles from queue: {str(e)}")
            return None
    
    def schedule_article(self, article: Dict[str, Any], time_str: str) -> bool:
        """Schedule an article to be published at a specific time."""
        try:
            # Parse time string (format: "HH:MM")
            hour, minute = map(int, time_str.split(':'))
            
            # Create schedule job
            schedule.every().day.at(time_str).do(
                self.add_to_queue,
                article=article,
                priority=1
            )
            
            logger.info(f"Scheduled article for {time_str}: {article.get('title', '')}")
            return True
        except Exception as e:
            logger.error(f"Error scheduling article: {str(e)}")
            return False
    
    def schedule_category(self, category: str, time_str: str) -> bool:
        """Schedule all articles of a specific category to be published at a time."""
        try:
            # Parse time string (format: "HH:MM")
            hour, minute = map(int, time_str.split(':'))
            
            # Create schedule job
            schedule.every().day.at(time_str).do(
                self._schedule_category_articles,
                category=category
            )
            
            logger.info(f"Scheduled category {category} for {time_str}")
            return True
        except Exception as e:
            logger.error(f"Error scheduling category: {str(e)}")
            return False
    
    def _schedule_category_articles(self, category: str):
        """Helper method to schedule articles of a specific category."""
        # This method should be implemented to work with your database
        # to find and schedule articles of the specified category
        pass
    
    def clear_queue(self):
        """Clear the publishing queue."""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                pass
        logger.info("Publishing queue cleared")
    
    def get_queue_size(self) -> int:
        """Get the current size of the publishing queue."""
        return self.queue.qsize()
    
    def set_publishing_interval(self, interval: int):
        """Set the publishing interval in seconds."""
        self.publishing_interval = interval
        logger.info(f"Publishing interval set to {interval} seconds") 