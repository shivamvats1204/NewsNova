from telegram import Bot
from telegram.error import TelegramError
from typing import Optional, Dict, Any
import asyncio
import aiohttp
from datetime import datetime

from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from config.logging_config import logger

class TelegramPublisher:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.channel_id = TELEGRAM_CHANNEL_ID
    
    async def publish_article(self, article: Dict[str, Any]) -> bool:
        try:
            message = self._format_message(article)
            
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            
            return True
        except TelegramError as e:
            logger.error(f"Telegram error while publishing article: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error publishing article: {str(e)}")
            return False
    
    def _format_message(self, article: Dict[str, Any]) -> str:
        title = article.get('title', '')
        summary = article.get('summary', '')
        url = article.get('url', '')
        category = article.get('category', 'general')
        source = article.get('source_name', '')
        author = article.get('author', '')
        
        message = f"<b>{title}</b>\n\n"
        
        if summary:
            message += f"{summary}\n\n"
        
        if category:
            message += f"Category: #{category}\n"
        
        if source:
            message += f"Source: {source}\n"
        
        if author:
            message += f"Author: {author}\n"
        
        if url:
            message += f"\nRead more: {url}"
        
        return message
    
    async def publish_media_article(self, article: Dict[str, Any]) -> bool:
        try:
            media_url = article.get('image_url')
            if not media_url:
                return await self.publish_article(article)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url) as response:
                    if response.status == 200:
                        media_data = await response.read()
                        
                        caption = self._format_message(article)
                        await self.bot.send_photo(
                            chat_id=self.channel_id,
                            photo=media_data,
                            caption=caption,
                            parse_mode='HTML'
                        )
                        return True
            
            return await self.publish_article(article)
            
        except Exception as e:
            logger.error(f"Error publishing media article: {str(e)}")
            return await self.publish_article(article)
    
    async def edit_message(self, message_id: int, article: Dict[str, Any]) -> bool:
        try:
            message = self._format_message(article)
            await self.bot.edit_message_text(
                chat_id=self.channel_id,
                message_id=message_id,
                text=message,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logger.error(f"Error editing message: {str(e)}")
            return False
    
    async def delete_message(self, message_id: int) -> bool:
        try:
            await self.bot.delete_message(
                chat_id=self.channel_id,
                message_id=message_id
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
            return False 