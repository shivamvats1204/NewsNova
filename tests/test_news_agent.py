import unittest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from src.scraper.rss_parser import RSSParser
from src.scraper.web_scraper import WebScraper
from src.nlp.summarizer import Summarizer
from src.nlp.classifier import TopicClassifier
from src.publisher.telegram_publisher import TelegramPublisher
from src.publisher.scheduler import PublishingScheduler

class TestNewsAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.rss_parser = RSSParser()
        self.web_scraper = WebScraper()
        self.summarizer = Summarizer()
        self.classifier = TopicClassifier()
        self.telegram_publisher = TelegramPublisher()
        self.scheduler = PublishingScheduler()
    
    def test_rss_parser(self):
        """Test RSS parser functionality."""
        # Test with a known RSS feed
        test_url = "https://techcrunch.com/feed/"
        articles = self.rss_parser.parse_feed(test_url)
        
        self.assertIsInstance(articles, list)
        if articles:  # If feed is accessible
            article = articles[0]
            self.assertIn('title', article)
            self.assertIn('url', article)
            self.assertIn('content', article)
    
    def test_web_scraper(self):
        """Test web scraper functionality."""
        # Test with a known article URL
        test_url = "https://techcrunch.com/2024/01/01/test-article"
        article = self.web_scraper.scrape_article(test_url)
        
        if article:  # If URL is accessible
            self.assertIn('title', article)
            self.assertIn('url', article)
            self.assertIn('content', article)
    
    def test_summarizer(self):
        """Test summarizer functionality."""
        test_text = """
        This is a test article with multiple paragraphs.
        It contains some sample content that should be summarized.
        The summarizer should extract the key points and create a concise summary.
        This is the end of the test article.
        """
        
        summary = self.summarizer.summarize(test_text)
        self.assertIsInstance(summary, str)
        self.assertLess(len(summary), len(test_text))
    
    def test_classifier(self):
        """Test classifier functionality."""
        test_text = """
        The stock market reached new heights today as technology companies
        reported strong earnings. Investors are optimistic about the future
        of the tech sector.
        """
        
        categories = self.classifier.classify(test_text)
        self.assertIsInstance(categories, list)
        if categories:
            self.assertIn('category', categories[0])
            self.assertIn('confidence', categories[0])
    
    @patch('telegram.Bot')
    async def test_telegram_publisher(self, mock_bot):
        """Test Telegram publisher functionality."""
        test_article = {
            'title': 'Test Article',
            'url': 'https://example.com/test',
            'summary': 'This is a test summary.',
            'category': 'technology',
            'source_name': 'Test Source',
            'author': 'Test Author'
        }
        
        success = await self.telegram_publisher.publish_article(test_article)
        self.assertIsInstance(success, bool)
    
    def test_scheduler(self):
        """Test scheduler functionality."""
        test_article = {
            'title': 'Test Article',
            'url': 'https://example.com/test',
            'summary': 'This is a test summary.'
        }
        
        # Test adding to queue
        success = self.scheduler.add_to_queue(test_article)
        self.assertTrue(success)
        
        # Test queue size
        self.assertEqual(self.scheduler.get_queue_size(), 1)
        
        # Test getting next article
        article = self.scheduler.get_next_article()
        self.assertIsNotNone(article)
        self.assertEqual(article['title'], test_article['title'])
        
        # Test clearing queue
        self.scheduler.clear_queue()
        self.assertEqual(self.scheduler.get_queue_size(), 0)

if __name__ == '__main__':
    unittest.main() 