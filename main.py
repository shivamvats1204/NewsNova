import asyncio
import argparse
from datetime import datetime
import sys

from config.settings import validate_config, DATABASE_URL, DEFAULT_SOURCES
from config.logging_config import logger
from src.database.models import init_db
from src.database.operations import DatabaseOperations
from src.scraper.rss_parser import RSSParser
from src.scraper.web_scraper import WebScraper
from src.nlp.summarizer import Summarizer
from src.nlp.classifier import TopicClassifier
from src.publisher.telegram_publisher import TelegramPublisher
from src.publisher.scheduler import PublishingScheduler

class NewsAgent:
    def __init__(self):
        self.db_engine = init_db(DATABASE_URL)
        self.db_ops = DatabaseOperations(self.db_engine)
        self.rss_parser = RSSParser()
        self.web_scraper = WebScraper()
        self.summarizer = Summarizer()
        self.classifier = TopicClassifier()
        self.telegram_publisher = TelegramPublisher()
        self.scheduler = PublishingScheduler()
        
        self._init_default_sources()
    
    def _init_default_sources(self):
        for source in DEFAULT_SOURCES:
            self.db_ops.add_source(source)
    
    async def process_article(self, article_data: dict) -> bool:
        try:
            existing_article = self.db_ops.get_article_by_url(article_data['url'])
            if existing_article:
                logger.info(f"Article already exists: {article_data['url']}")
                return False
            
            article_data['summary'] = self.summarizer.summarize(article_data['content'])
            
            categories = self.classifier.classify(article_data['content'])
            if categories:
                article_data['category'] = categories[0]['category']
            elif 'categories' in article_data and article_data['categories']:
                article_data['category'] = article_data['categories'][0]
            
            if 'categories' in article_data:
                del article_data['categories']
            
            article = self.db_ops.add_article(article_data)
            if not article:
                return False
            
            self.scheduler.add_to_queue(article_data)
            
            return True
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            return False
    
    async def scrape_sources(self):
        sources = self.db_ops.get_sources()
        for source in sources:
            try:
                if source.type == 'rss':
                    articles = self.rss_parser.parse_feed(source.url)
                else:
                    articles = []
                    links = self.web_scraper.extract_links(source.url)
                    for link in links:
                        article = self.web_scraper.scrape_article(link)
                        if article:
                            articles.append(article)
                
                for article in articles:
                    article['source_id'] = source.id
                    await self.process_article(article)
                
            except Exception as e:
                logger.error(f"Error scraping source {source.name}: {str(e)}")
    
    async def publish_queued_articles(self):
        while True:
            try:
                next_batch = self.scheduler.get_next_article()
                if next_batch and 'batch' in next_batch:
                    articles = next_batch['batch']
                    for article in articles:
                        success = await self.telegram_publisher.publish_media_article(article)
                        if success:
                            self.db_ops.mark_article_as_published(article['id'])
                        await asyncio.sleep(1)
                
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error publishing queued articles: {str(e)}")
                await asyncio.sleep(5)
    
    async def run(self):
        try:
            self.scheduler.start()
            
            publishing_task = asyncio.create_task(self.publish_queued_articles())
            
            while True:
                await self.scrape_sources()
                
                await asyncio.sleep(300)
                
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            self.scheduler.stop()
            publishing_task.cancel()
            raise

def main():
    parser = argparse.ArgumentParser(description='AI-Powered News Agent')
    parser.add_argument('--init-db', action='store_true', help='Initialize the database')
    parser.add_argument('--add-source', action='store_true', help='Add a new source')
    parser.add_argument('--url', help='URL for the new source')
    parser.add_argument('--type', choices=['rss', 'web'], help='Type of source')
    parser.add_argument('--category', help='Category for the new source')
    args = parser.parse_args()
    
    try:
        validate_config()
        
        if args.init_db:
            init_db(DATABASE_URL)
            logger.info("Database initialized")
            return
        
        if args.add_source:
            if not all([args.url, args.type, args.category]):
                print("Error: URL, type, and category are required for adding a source")
                return
            
            db_ops = DatabaseOperations(init_db(DATABASE_URL))
            source_data = {
                'name': args.url.split('/')[-1],
                'url': args.url,
                'type': args.type,
                'category': args.category
            }
            
            if db_ops.add_source(source_data):
                logger.info(f"Added new source: {args.url}")
            else:
                logger.error("Failed to add new source")
            return
        
        news_agent = NewsAgent()
        asyncio.run(news_agent.run())
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 