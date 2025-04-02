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
        if not self.is_running:
            self.is_running = True
            self.schedule_thread = threading.Thread(target=self._run_scheduler)
            self.schedule_thread.daemon = True
            self.schedule_thread.start()
            logger.info("Publishing scheduler started")
    
    def stop(self):
        self.is_running = False
        if self.schedule_thread:
            self.schedule_thread.join()
        logger.info("Publishing scheduler stopped")
    
    def _run_scheduler(self):
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def add_to_queue(self, article: Dict[str, Any], priority: int = 0,
                     scheduled_time: Optional[datetime] = None) -> bool:
        try:
            if scheduled_time is None:
                scheduled_time = datetime.utcnow() + timedelta(seconds=self.publishing_interval)
            
            queue_item = (
                -priority,
                scheduled_time.timestamp(),
                article
            )
            
            self.queue.put(queue_item)
            logger.info(f"Added article to queue: {article.get('title', '')}")
            return True
        except Exception as e:
            logger.error(f"Error adding article to queue: {str(e)}")
            return False
    
    def get_next_article(self) -> Optional[Dict[str, Any]]:
        try:
            if self.queue.empty():
                return None
            
            current_time = datetime.utcnow()
            articles = []
            
            for _ in range(BATCH_PUBLISH_SIZE):
                if self.queue.empty():
                    break
                    
                priority, timestamp, article = self.queue.get()
                scheduled_time = datetime.fromtimestamp(timestamp)
                
                if scheduled_time > current_time:
                    self.queue.put((priority, timestamp, article))
                    break
                
                articles.append(article)
            
            if articles:
                return {'batch': articles}
            return None
            
        except Exception as e:
            logger.error(f"Error getting next articles from queue: {str(e)}")
            return None
    
    def schedule_article(self, article: Dict[str, Any], time_str: str) -> bool:
        try:
            hour, minute = map(int, time_str.split(':'))
            
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
        try:
            hour, minute = map(int, time_str.split(':'))
            
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
        pass
    
    def clear_queue(self):
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                pass
        logger.info("Publishing queue cleared")
    
    def get_queue_size(self) -> int:
        return self.queue.qsize()
    
    def set_publishing_interval(self, interval: int):
        self.publishing_interval = interval
        logger.info(f"Publishing interval set to {interval} seconds") 