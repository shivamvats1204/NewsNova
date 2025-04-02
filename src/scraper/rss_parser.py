import feedparser
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from config.settings import USER_AGENT
from config.logging_config import logger

class RSSParser:
    def __init__(self):
        self.feedparser = feedparser
        self.feedparser.USER_AGENT = USER_AGENT
    
    def parse_feed(self, url: str) -> List[Dict[str, Any]]:
        """Parse an RSS feed and return a list of articles."""
        try:
            feed = self.feedparser.parse(url)
            if feed.bozo:  # Feed parsing error
                logger.error(f"Error parsing feed {url}: {feed.bozo_exception}")
                return []
            
            articles = []
            for entry in feed.entries:
                article = self._extract_article_data(entry, feed.feed.get('title', ''))
                if article:
                    articles.append(article)
            
            return articles
        except Exception as e:
            logger.error(f"Error fetching feed {url}: {str(e)}")
            return []
    
    def _extract_article_data(self, entry: Any, source_name: str) -> Optional[Dict[str, Any]]:
        """Extract article data from a feed entry."""
        try:
            # Get the link
            link = entry.get('link', '')
            if not link:
                return None
            
            # Get the title
            title = entry.get('title', '')
            if not title:
                return None
            
            # Get the content
            content = ''
            if 'content' in entry:
                content = entry.content[0].value
            elif 'summary_detail' in entry:
                content = entry.summary_detail.value
            elif 'summary' in entry:
                content = entry.summary
            
            # Get the publication date
            published = entry.get('published_parsed', None)
            if published:
                published = datetime(*published[:6])
            else:
                published = datetime.utcnow()
            
            # Get the author
            author = entry.get('author', '')
            
            # Get categories
            categories = []
            if 'tags' in entry:
                categories = [tag.term for tag in entry.tags]
            elif 'category' in entry:
                categories = [entry.category]
            
            return {
                'title': title,
                'url': link,
                'content': content,
                'author': author,
                'published_at': published,
                'categories': categories
            }
        except Exception as e:
            logger.error(f"Error extracting article data: {str(e)}")
            return None
    
    def validate_feed(self, url: str) -> bool:
        """Validate if a URL is a valid RSS feed."""
        try:
            feed = self.feedparser.parse(url)
            return not feed.bozo and len(feed.entries) > 0
        except Exception:
            return False 