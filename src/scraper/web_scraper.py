from newspaper import Article as NewsArticle
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import time
import random

from config.settings import USER_AGENT
from config.logging_config import logger

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def scrape_article(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            time.sleep(random.uniform(1, 3))
            
            article = NewsArticle(url)
            article.download()
            article.parse()
            article.nlp()
            
            title = article.title
            text = article.text
            summary = article.summary
            authors = article.authors
            publish_date = article.publish_date
            top_image = article.top_image
            
            if not title or not text:
                logger.warning(f"Missing required content for article: {url}")
                return None
            
            return {
                'title': title,
                'url': url,
                'content': text,
                'summary': summary,
                'author': ', '.join(authors) if authors else '',
                'published_at': publish_date,
                'image_url': top_image,
                'source_name': article.source_url
            }
        except Exception as e:
            logger.error(f"Error scraping article {url}: {str(e)}")
            return None
    
    def extract_links(self, url: str, max_links: int = 10) -> list:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href and self._is_article_link(href):
                    links.append(href)
                    if len(links) >= max_links:
                        break
            
            return links
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {str(e)}")
            return []
    
    def _is_article_link(self, url: str) -> bool:
        skip_patterns = [
            '/category/', '/tag/', '/author/', '/about/', '/contact/',
            '/privacy/', '/terms/', '/subscribe/', '/login/', '/register/'
        ]
        
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
        
        article_patterns = [
            '/article/', '/news/', '/story/', '/post/', '/blog/',
            '/202', '/2023/', '/2024/'
        ]
        
        return any(pattern in url.lower() for pattern in article_patterns)
    
    def validate_url(self, url: str) -> bool:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text()
            
            has_title = bool(soup.find('h1'))
            has_paragraphs = len(soup.find_all('p')) > 3
            has_sufficient_text = len(text_content.split()) > 100
            
            return has_title and has_paragraphs and has_sufficient_text
        except Exception:
            return False 