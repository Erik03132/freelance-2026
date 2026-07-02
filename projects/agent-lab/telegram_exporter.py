"""
Telegram Exporter for ContentCombine
Handles sending content to Telegram channels/chats with Pexels visuals
"""

import asyncio
import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import aiohttp
import json

@dataclass
class TelegramMessage:
    chat_id: str
    text: str
    parse_mode: str = 'HTML'
    disable_web_page_preview: bool = False
    photo_url: Optional[str] = None
    reply_markup: Optional[Dict] = None


class PexelsFetcher:
    """Fetch photos from Pexels API for visual content"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY", "")
        self.base_url = "https://api.pexels.com/v1/search"
    
    async def search_photo(self, query: str, per_page: int = 1) -> Optional[Dict]:
        """Search for a photo on Pexels"""
        if not self.api_key:
            print("[pexels] No API key configured")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    headers={"Authorization": self.api_key},
                    params={"query": query, "per_page": per_page, "orientation": "landscape"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        photos = data.get("photos", [])
                        if photos:
                            photo = photos[0]
                            return {
                                "url": photo["src"]["large"],
                                "photographer": photo["photographer"],
                                "page": photo["photographer_url"],
                                "alt": photo.get("alt", query)
                            }
                    return None
        except Exception as e:
            print(f"[pexels] Error: {e}")
            return None
    
    async def fetch_photos_for_articles(self, articles: List[Dict]) -> List[Dict]:
        """Fetch relevant photos for a list of articles"""
        results = []
        
        for article in articles:
            # Generate search query from title and tags
            title = article.get("title", "")
            tags = article.get("tags", [])
            
            # Create search query
            search_terms = []
            if tags:
                search_terms.extend(tags[:2])
            else:
                # Extract key words from title
                words = re.findall(r'\b[a-zA-Zа-яА-Я]{4,}\b', title)
                search_terms.extend(words[:2])
            
            query = " ".join(search_terms) if search_terms else "technology"
            
            # Fetch photo
            photo = await self.search_photo(query)
            if photo:
                article["photo"] = photo
            else:
                article["photo"] = None
            
            results.append(article)
        
        return results

class TelegramExporter:
    def __init__(self, bot_token: str, pexels_api_key: Optional[str] = None):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.pexels = PexelsFetcher(pexels_api_key)
    
    async def send_message(self, message: TelegramMessage) -> bool:
        """Send single message to Telegram (text or photo)"""
        try:
            async with aiohttp.ClientSession() as session:
                if message.photo_url:
                    # Send photo with caption
                    async with session.post(
                        f"{self.base_url}/sendPhoto",
                        json={
                            'chat_id': message.chat_id,
                            'photo': message.photo_url,
                            'caption': message.text,
                            'parse_mode': message.parse_mode,
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as resp:
                        data = await resp.json()
                        if data.get('ok'):
                            return True
                        else:
                            print(f"[telegram] Error: {data.get('description', 'Unknown error')}")
                            return False
                else:
                    # Send text message
                    async with session.post(
                        f"{self.base_url}/sendMessage",
                        json={
                            'chat_id': message.chat_id,
                            'text': message.text,
                            'parse_mode': message.parse_mode,
                            'disable_web_page_preview': message.disable_web_page_preview,
                            'reply_markup': message.reply_markup,
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as resp:
                        data = await resp.json()
                        if data.get('ok'):
                            return True
                        else:
                            print(f"[telegram] Error: {data.get('description', 'Unknown error')}")
                            return False
        except Exception as e:
            print(f"[telegram] Error sending message: {e}")
            return False
    
    async def send_messages(self, messages: List[TelegramMessage]) -> int:
        """Send multiple messages (rate-limited)"""
        sent = 0
        for message in messages:
            if await self.send_message(message):
                sent += 1
            await asyncio.sleep(0.5)  # Rate limit: 2 messages per second
        return sent
    
    def format_alerts(self, alerts: List[Dict], chat_id: str) -> TelegramMessage:
        """Format alerts for Telegram"""
        top5 = alerts[:5]
        text = "🚨 <b>ALERTS</b>\n\n"
        
        for i, item in enumerate(top5, 1):
            text += f"{i}. <b>{self.escape_html(item['title'])}</b>\n"
            text += f"   Score: {item.get('score', 0)} | Priority: {item.get('priority', 'unknown')}\n"
            text += f"   Source: {item.get('source', 'unknown')} | Author: {self.escape_html(item.get('author', 'Unknown'))}\n"
            text += f"   <a href=\"{item.get('url', '#')}\">Read more</a>\n\n"
        
        return TelegramMessage(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
        )
    
    def format_digest(self, digest: List[Dict], chat_id: str) -> TelegramMessage:
        """Format digest for Telegram with optional photos"""
        top10 = digest[:10]
        
        # Check if any item has a photo
        items_with_photos = [item for item in top10 if item.get("photo")]
        
        if items_with_photos:
            # Send first item with photo
            first_item = items_with_photos[0]
            photo_url = first_item.get("photo", {}).get("url")
            
            text = "📰 <b>DIGEST</b>\n\n"
            for i, item in enumerate(top10, 1):
                text += f"{i}. <b>{self.escape_html(item['title'])}</b>\n"
                text += f"   {self.escape_html(item.get('author', 'Unknown'))} | {item.get('source', 'unknown')}\n"
                text += f"   <a href=\"{item.get('url', '#')}\">Read</a>\n\n"
            
            return TelegramMessage(
                chat_id=chat_id,
                text=text,
                parse_mode='HTML',
                photo_url=photo_url
            )
        else:
            # Send text only
            text = "📰 <b>DIGEST</b>\n\n"
            for i, item in enumerate(top10, 1):
                text += f"{i}. <b>{self.escape_html(item['title'])}</b>\n"
                text += f"   {self.escape_html(item.get('author', 'Unknown'))} | {item.get('source', 'unknown')}\n"
                text += f"   <a href=\"{item.get('url', '#')}\">Read</a>\n\n"
            
            return TelegramMessage(
                chat_id=chat_id,
                text=text,
                parse_mode='HTML'
            )
    
    def format_trending(self, trending: List[Dict], chat_id: str) -> TelegramMessage:
        """Format trending topics for Telegram"""
        top5 = trending[:5]
        text = "🔥 <b>TRENDING</b>\n\n"
        
        for i, cluster in enumerate(top5, 1):
            items_count = len(cluster.get('items', []))
            avg_score = cluster.get('avg_score', 0)
            tags = ', '.join(cluster.get('tags', [])[:3])
            
            text += f"{i}. <b>{self.escape_html(cluster.get('topic', 'Unknown'))}</b>\n"
            text += f"   Items: {items_count} | Avg score: {avg_score:.0f}\n"
            text += f"   Tags: {self.escape_html(tags)}\n\n"
        
        return TelegramMessage(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
        )
    
    def format_summary(self, stats: Dict, chat_id: str) -> TelegramMessage:
        """Format summary statistics"""
        text = "📊 <b>SUMMARY</b>\n\n"
        text += f"Total items: {stats.get('total_items', 0)}\n"
        text += f"Alerts: {stats.get('alerts_count', 0)}\n"
        text += f"Digest items: {stats.get('digest_count', 0)}\n"
        text += f"Trending topics: {stats.get('trending_count', 0)}\n"
        text += f"Avg score: {stats.get('avg_score', 0):.0f}\n"
        text += f"Updated: {stats.get('updated_at', 'N/A')}\n"
        
        return TelegramMessage(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
        )
    
    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML special characters for Telegram"""
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
        )
    
    async def export_pipeline_results(
        self,
        chat_id: str,
        alerts: List[Dict],
        digest: List[Dict],
        trending: List[Dict],
        stats: Dict,
        fetch_photos: bool = True
    ) -> int:
        """Export full pipeline results to Telegram with optional Pexels photos"""
        messages = []
        
        # Fetch photos for digest items if enabled
        if fetch_photos and digest:
            digest = await self.pexels.fetch_photos_for_articles(digest)
        
        # Send summary first
        messages.append(self.format_summary(stats, chat_id))
        
        # Send alerts if any
        if alerts:
            messages.append(self.format_alerts(alerts, chat_id))
        
        # Send digest
        if digest:
            messages.append(self.format_digest(digest, chat_id))
        
        # Send trending
        if trending:
            messages.append(self.format_trending(trending, chat_id))
        
        return await self.send_messages(messages)


# Example usage
async def main():
    import os
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
    pexels_key = os.getenv("PEXELS_API_KEY", "")
    
    exporter = TelegramExporter(bot_token, pexels_key)
    
    # Example data
    alerts = [
        {
            'title': 'Critical security vulnerability found',
            'score': 95,
            'priority': 'critical',
            'source': 'habr',
            'author': 'security_researcher',
            'url': 'https://habr.com/ru/articles/1234567/'
        }
    ]
    
    digest = [
        {
            'title': 'Python 3.12 Features Overview',
            'source': 'medium',
            'author': 'python_dev',
            'url': 'https://medium.com/@python_dev/...',
            'tags': ['python', 'programming']
        }
    ]
    
    trending = [
        {
            'topic': 'AI/ML',
            'items': [1, 2, 3],
            'avg_score': 75,
            'tags': ['ai', 'ml', 'python']
        }
    ]
    
    stats = {
        'total_items': 150,
        'alerts_count': 5,
        'digest_count': 50,
        'trending_count': 10,
        'avg_score': 65,
        'updated_at': '2024-01-15 10:30:00'
    }
    
    sent = await exporter.export_pipeline_results(
        chat_id, alerts, digest, trending, stats, fetch_photos=True
    )
    print(f"Sent {sent} messages to Telegram")


if __name__ == '__main__':
    asyncio.run(main())
