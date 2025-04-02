import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///news.db')

SCRAPING_INTERVAL = int(os.getenv('SCRAPING_INTERVAL', '300'))
MAX_ARTICLES_PER_SOURCE = int(os.getenv('MAX_ARTICLES_PER_SOURCE', '10'))
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

SUMMARIZATION_MODEL = os.getenv('SUMMARIZATION_MODEL', 'facebook/bart-large-cnn')
CLASSIFICATION_MODEL = os.getenv('CLASSIFICATION_MODEL', 'facebook/bart-large-mnli')
MAX_SUMMARY_LENGTH = int(os.getenv('MAX_SUMMARY_LENGTH', '150'))

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'news_agent.log')

DEFAULT_PUBLISHING_INTERVAL = int(os.getenv('DEFAULT_PUBLISHING_INTERVAL', '300'))  # 5 minutes
BATCH_PUBLISH_SIZE = int(os.getenv('BATCH_PUBLISH_SIZE', '5'))  # Publish 5 articles at once
MAX_QUEUE_SIZE = int(os.getenv('MAX_QUEUE_SIZE', '100'))

CATEGORIES = [
    'politics',
    'technology',
    'business',
    'sports',
    'entertainment',
    'science',
    'health',
    'world',
    'local'
]

DEFAULT_SOURCES = [
    {
        'name': 'Reuters',
        'url': 'https://www.reuters.com/rssFeed/worldNews',
        'type': 'rss',
        'category': 'world'
    },
    {
        'name': 'TechCrunch',
        'url': 'https://techcrunch.com/feed/',
        'type': 'rss',
        'category': 'technology'
    }
]

def validate_config():
    """Validate the configuration settings."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    if not TELEGRAM_CHANNEL_ID:
        raise ValueError("TELEGRAM_CHANNEL_ID is required")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is required") 