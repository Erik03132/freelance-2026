"""
ContentCombine Normalizer: Convert Habr, Medium, Twitter, Telegram into unified format.

Handles:
- Habr: RSS, HTML, API
- Medium: RSS, API
- Twitter: API v2
- Telegram: Channel messages via API/Bot

Output: NormalizedContent (dict with standard fields)
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import feedparser
import requests
from bs4 import BeautifulSoup


class ContentSource(Enum):
    """Content source type"""
    HABR = "habr"
    MEDIUM = "medium"
    TWITTER = "twitter"
    TELEGRAM = "telegram"


class ContentType(Enum):
    """Content type classification"""
    ARTICLE = "article"
    TUTORIAL = "tutorial"
    NEWS = "news"
    DISCUSSION = "discussion"
    ANNOUNCEMENT = "announcement"
    THREAD = "thread"
    MESSAGE = "message"


@dataclass
class NormalizedContent:
    """Unified content representation"""
    id: str  # Unique hash
    source: str  # habr, medium, twitter, telegram
    source_id: str  # Original ID from source
    title: str
    content: str  # Full text or excerpt
    url: str
    author: str
    author_id: Optional[str]
    published_at: str  # ISO 8601
    fetched_at: str  # ISO 8601
    content_type: str  # article, tutorial, news, discussion, announcement, thread, message
    tags: List[str]
    metadata: Dict[str, Any]  # Source-specific fields
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class Normalizer:
    """Main normalizer for all sources"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ContentCombine/1.0 (+https://github.com/anomalyco/opencode)'
        })
    
    @staticmethod
    def _generate_id(source: str, source_id: str) -> str:
        """Generate unique content ID"""
        combined = f"{source}:{source_id}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    @staticmethod
    def _clean_html(html: str) -> str:
        """Strip HTML tags and normalize whitespace"""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def _extract_tags(text: str, source: str) -> List[str]:
        """Extract tags/keywords from content"""
        tags = []
        
        # Habr-style tags: [tag], #tag
        habr_tags = re.findall(r'\[([^\]]+)\]', text)
        tags.extend(habr_tags)
        
        # Hashtags
        hashtags = re.findall(r'#(\w+)', text)
        tags.extend(hashtags)
        
        # Return unique, lowercase
        return list(set(tag.lower() for tag in tags))[:10]
    
    # ==================== HABR ====================
    
    def normalize_habr_html(self, page_url: str = "https://habr.com/ru/articles/") -> List[NormalizedContent]:
        """Parse Habr articles from HTML (since RSS is not available)"""
        results = []
        try:
            resp = self.session.get(page_url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Find article cards
            articles = soup.find_all('article', class_='tm-articles-list__item')
            
            for article in articles[:50]:
                content = self._parse_habr_html_article(article)
                if content:
                    results.append(content)
        except Exception as e:
            print(f"Error parsing Habr HTML: {e}")
        return results
    
    def _parse_habr_html_article(self, article_elem) -> Optional[NormalizedContent]:
        """Parse Habr article from HTML element"""
        try:
            # Extract ID from article element
            source_id = article_elem.get('id', '')
            if not source_id:
                return None
            
            # Extract title and URL
            title_elem = article_elem.find('h2', class_='tm-title')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a')
            if not title_link:
                return None
            
            # Get title from span inside link
            title_span = title_link.find('span')
            title = title_span.get_text(strip=True) if title_span else title_link.get_text(strip=True)
            
            url_path = title_link.get('href', '')
            url = f"https://habr.com{url_path}" if url_path.startswith('/') else url_path
            
            # Extract author
            author_elem = article_elem.find('a', class_='tm-user-info__username')
            author = author_elem.get_text(strip=True) if author_elem else 'Anonymous'
            
            # Extract publish date
            time_elem = article_elem.find('time')
            published_at = time_elem.get('datetime', datetime.now(timezone.utc).isoformat()) if time_elem else datetime.now(timezone.utc).isoformat()
            
            # Extract tags
            tag_elems = article_elem.find_all('a', class_='tm-tag-link')
            tags = [tag.get_text(strip=True) for tag in tag_elems][:10]
            
            # Get summary - fetch full article content
            summary = self.fetch_habr_article_content(url)
            
            # Fallback to title if content fetch fails
            if not summary or len(summary) < 100:
                summary = title
            
            content_type = self._classify_habr_content(title, summary)
            
            return NormalizedContent(
                id=self._generate_id('habr', source_id),
                source='habr',
                source_id=source_id,
                title=title,
                content=summary[:500] if summary else title,
                url=url,
                author=author,
                author_id=None,
                published_at=published_at,
                fetched_at=datetime.now(timezone.utc).isoformat(),
                content_type=content_type,
                tags=tags,
                metadata={
                    'feed': 'habr_html',
                }
            )
        except Exception as e:
            print(f"Error parsing Habr HTML article: {e}")
            return None
    
    def fetch_habr_article_content(self, url: str) -> str:
        """Fetch and convert Habr article to clean Markdown"""
        try:
            from html_to_markdown import HtmlToMarkdown
            
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            
            converter = HtmlToMarkdown()
            result = converter.convert(resp.text, url)
            
            return result.markdown
        except Exception as e:
            print(f"Error fetching Habr article content: {e}")
            return ""
    
    def normalize_habr_rss(self, feed_url: str = "https://habr.com/ru/feed/") -> List[NormalizedContent]:
        """Parse Habr RSS feed (fallback - may not work)"""
        results = []
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:50]:  # Limit to 50 items
                content = self._parse_habr_entry(entry)
                if content:
                    results.append(content)
        except Exception as e:
            print(f"Error parsing Habr RSS: {e}")
        
        # If RSS fails, fall back to HTML parsing
        if not results:
            print("[normalizer] RSS failed, falling back to HTML parsing...")
            results = self.normalize_habr_html()
        
        return results
    
    def _parse_habr_entry(self, entry: Dict) -> Optional[NormalizedContent]:
        """Parse single Habr RSS entry"""
        try:
            source_id = entry.get('id', '').split('/')[-1]
            title = entry.get('title', 'No title')
            url = entry.get('link', '')
            author = entry.get('author', 'Anonymous')
            published_at = entry.get('published', datetime.now(timezone.utc).isoformat())
            summary = entry.get('summary', '')
            
            # Extract tags from content
            tags = self._extract_tags(summary, 'habr')
            
            # Determine content type
            content_type = self._classify_habr_content(title, summary)
            
            return NormalizedContent(
                id=self._generate_id('habr', source_id),
                source='habr',
                source_id=source_id,
                title=title,
                content=self._clean_html(summary)[:500],
                url=url,
                author=author,
                author_id=None,
                published_at=published_at,
                fetched_at=datetime.now(timezone.utc).isoformat(),
                content_type=content_type,
                tags=tags,
                metadata={
                    'feed': 'habr_rss',
                    'raw_summary': summary[:200],
                }
            )
        except Exception as e:
            print(f"Error parsing Habr entry: {e}")
            return None
    
    def normalize_habr_api(self, article_ids: Optional[List[str]] = None) -> List[NormalizedContent]:
        """Fetch from Habr API v2"""
        results = []
        url = "https://habr.com/api/v2/articles/"
        params = {
            'limit': 50,
            'offset': 0,
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            for article in data.get('results', [])[:50]:
                content = self._parse_habr_api_article(article)
                if content:
                    results.append(content)
        except Exception as e:
            print(f"Error fetching Habr API: {e}")
        
        return results
    
    def _parse_habr_api_article(self, article: Dict) -> Optional[NormalizedContent]:
        """Parse Habr API article"""
        try:
            source_id = str(article.get('id', ''))
            title = article.get('title', 'No title')
            url = article.get('url', '')
            author = article.get('author', {}).get('login', 'Anonymous')
            author_id = str(article.get('author', {}).get('id', ''))
            published_at = article.get('published_at', datetime.now(timezone.utc).isoformat())
            text_html = article.get('text_html', '')
            
            # Extract tags
            tags_data = article.get('hubs', [])
            tags = [hub.get('title', '') for hub in tags_data][:10]
            
            content_type = self._classify_habr_content(title, text_html)
            
            return NormalizedContent(
                id=self._generate_id('habr', source_id),
                source='habr',
                source_id=source_id,
                title=title,
                content=self._clean_html(text_html)[:500],
                url=url,
                author=author,
                author_id=author_id,
                published_at=published_at,
                fetched_at=datetime.now(timezone.utc).isoformat(),
                content_type=content_type,
                tags=tags,
                metadata={
                    'feed': 'habr_api',
                    'rating': article.get('rating', 0),
                    'comments_count': article.get('comments_count', 0),
                }
            )
        except Exception as e:
            print(f"Error parsing Habr API article: {e}")
            return None
    
    @staticmethod
    def _classify_habr_content(title: str, content: str) -> str:
        """Classify Habr content type"""
        combined = (title + ' ' + content).lower()
        
        if any(word in combined for word in ['туториал', 'tutorial', 'гайд', 'guide', 'как']):
            return ContentType.TUTORIAL.value
        elif any(word in combined for word in ['новость', 'news', 'объявление', 'announcement']):
            return ContentType.NEWS.value
        elif any(word in combined for word in ['обсуждение', 'discussion', 'вопрос', 'question']):
            return ContentType.DISCUSSION.value
        else:
            return ContentType.ARTICLE.value
    
    # ==================== MEDIUM ====================
    
    def normalize_medium_rss(self, username: str) -> List[NormalizedContent]:
        """Parse Medium RSS feed for user"""
        feed_url = f"https://medium.com/feed/@{username}"
        results = []
        
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:50]:
                content = self._parse_medium_entry(entry)
                if content:
                    results.append(content)
        except Exception as e:
            print(f"Error parsing Medium RSS: {e}")
        
        return results
    
    def _parse_medium_entry(self, entry: Dict) -> Optional[NormalizedContent]:
        """Parse Medium RSS entry"""
        try:
            source_id = entry.get('id', '').split('/')[-1]
            title = entry.get('title', 'No title')
            url = entry.get('link', '')
            author = entry.get('author', 'Anonymous')
            published_at = entry.get('published', datetime.now(timezone.utc).isoformat())
            summary = entry.get('summary', '')
            
            tags = self._extract_tags(summary, 'medium')
            
            return NormalizedContent(
                id=self._generate_id('medium', source_id),
                source='medium',
                source_id=source_id,
                title=title,
                content=self._clean_html(summary)[:500],
                url=url,
                author=author,
                author_id=None,
                published_at=published_at,
                fetched_at=datetime.now(timezone.utc).isoformat(),
                content_type=ContentType.ARTICLE.value,
                tags=tags,
                metadata={
                    'feed': 'medium_rss',
                }
            )
        except Exception as e:
            print(f"Error parsing Medium entry: {e}")
            return None
    
    # ==================== TWITTER ====================
    
    def normalize_twitter_api(self, query: str, bearer_token: str) -> List[NormalizedContent]:
        """Fetch tweets via Twitter API v2"""
        results = []
        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {
            "Authorization": f"Bearer {bearer_token}"
        }
        params = {
            "query": query,
            "max_results": 100,
            "tweet.fields": "created_at,author_id,public_metrics",
            "expansions": "author_id",
            "user.fields": "username,name"
        }
        
        try:
            resp = self.session.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            users_map = {user['id']: user for user in data.get('includes', {}).get('users', [])}
            
            for tweet in data.get('data', [])[:50]:
                content = self._parse_twitter_tweet(tweet, users_map)
                if content:
                    results.append(content)
        except Exception as e:
            print(f"Error fetching Twitter API: {e}")
        
        return results
    
    def _parse_twitter_tweet(self, tweet: Dict, users_map: Dict) -> Optional[NormalizedContent]:
        """Parse Twitter tweet"""
        try:
            source_id = tweet.get('id', '')
            author_id = tweet.get('author_id', '')
            user = users_map.get(author_id, {})
            
            title = f"Tweet by @{user.get('username', 'unknown')}"
            content = tweet.get('text', '')
            url = f"https://twitter.com/{user.get('username', '')}/status/{source_id}"
            author = user.get('name', 'Unknown')
            published_at = tweet.get('created_at', datetime.now(timezone.utc).isoformat())
            
            tags = self._extract_tags(content, 'twitter')
            
            return NormalizedContent(
                id=self._generate_id('twitter', source_id),
                source='twitter',
                source_id=source_id,
                title=title,
                content=content[:500],
                url=url,
                author=author,
                author_id=author_id,
                published_at=published_at,
                fetched_at=datetime.now(timezone.utc).isoformat(),
                content_type=ContentType.THREAD.value,
                tags=tags,
                metadata={
                    'feed': 'twitter_api',
                    'likes': tweet.get('public_metrics', {}).get('like_count', 0),
                    'retweets': tweet.get('public_metrics', {}).get('retweet_count', 0),
                }
            )
        except Exception as e:
            print(f"Error parsing Twitter tweet: {e}")
            return None
    
    # ==================== TELEGRAM ====================
    
    def normalize_telegram_channel(self, channel_id: str, bot_token: str, limit: int = 50) -> List[NormalizedContent]:
        """Fetch messages from Telegram channel"""
        results = []
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        
        # Note: This is a simplified version. In production, use telegram.py or aiogram
        # For now, we'll show the structure
        try:
            params = {'limit': limit}
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            for update in data.get('result', [])[-limit:]:
                message = update.get('message', {})
                if message:
                    content = self._parse_telegram_message(message, channel_id)
                    if content:
                        results.append(content)
        except Exception as e:
            print(f"Error fetching Telegram: {e}")
        
        return results
    
    def _parse_telegram_message(self, message: Dict, channel_id: str) -> Optional[NormalizedContent]:
        """Parse Telegram message"""
        try:
            source_id = f"{channel_id}_{message.get('message_id', '')}"
            title = f"Telegram message from {channel_id}"
            content = message.get('text', message.get('caption', ''))
            url = f"https://t.me/{channel_id}/{message.get('message_id', '')}"
            author = channel_id
            author_id = str(message.get('from', {}).get('id', ''))
            published_at = datetime.fromtimestamp(
                message.get('date', 0), 
                tz=timezone.utc
            ).isoformat()
            
            tags = self._extract_tags(content, 'telegram')
            
            return NormalizedContent(
                id=self._generate_id('telegram', source_id),
                source='telegram',
                source_id=source_id,
                title=title,
                content=content[:500],
                url=url,
                author=author,
                author_id=author_id,
                published_at=published_at,
                fetched_at=datetime.now(timezone.utc).isoformat(),
                content_type=ContentType.MESSAGE.value,
                tags=tags,
                metadata={
                    'feed': 'telegram_channel',
                    'message_id': message.get('message_id', ''),
                    'chat_id': message.get('chat', {}).get('id', ''),
                }
            )
        except Exception as e:
            print(f"Error parsing Telegram message: {e}")
            return None
    
    # ==================== BATCH OPERATIONS ====================
    
    def normalize_all_sources(self, config: Dict) -> List[NormalizedContent]:
        """Normalize content from all configured sources"""
        all_content = []
        
        # Habr
        if config.get('habr', {}).get('enabled'):
            print("[normalizer] Fetching Habr articles...")
            habr_content = self.normalize_habr_html()
            all_content.extend(habr_content)
            print(f"[normalizer] Fetched {len(habr_content)} items from Habr")
        
        # Medium
        if config.get('medium', {}).get('enabled'):
            for username in config.get('medium', {}).get('usernames', []):
                print(f"[normalizer] Fetching Medium for @{username}...")
                all_content.extend(self.normalize_medium_rss(username))
        
        # Twitter
        if config.get('twitter', {}).get('enabled'):
            bearer_token = config.get('twitter', {}).get('bearer_token')
            query = config.get('twitter', {}).get('query', 'AI')
            if bearer_token:
                print(f"[normalizer] Fetching Twitter for query: {query}...")
                all_content.extend(self.normalize_twitter_api(query, bearer_token))
        
        # Telegram
        if config.get('telegram', {}).get('enabled'):
            bot_token = config.get('telegram', {}).get('bot_token')
            channel_id = config.get('telegram', {}).get('channel_id')
            if bot_token and channel_id:
                print(f"[normalizer] Fetching Telegram channel: {channel_id}...")
                all_content.extend(self.normalize_telegram_channel(channel_id, bot_token))
        
        return all_content
    
    def deduplicate(self, content_list: List[NormalizedContent]) -> List[NormalizedContent]:
        """Remove duplicates by ID"""
        seen = set()
        unique = []
        for item in content_list:
            if item.id not in seen:
                seen.add(item.id)
                unique.append(item)
        return unique


if __name__ == '__main__':
    # Example usage
    normalizer = Normalizer()
    
    # Test Habr RSS
    print("Testing Habr RSS normalization...")
    habr_content = normalizer.normalize_habr_rss()
    print(f"Fetched {len(habr_content)} items from Habr")
    
    if habr_content:
        print("\nExample normalized content:")
        print(habr_content[0].to_json())
    
    # Test batch normalization
    config = {
        'habr': {'enabled': True},
        'medium': {'enabled': False, 'usernames': []},
        'twitter': {'enabled': False, 'bearer_token': None, 'query': 'AI'},
        'telegram': {'enabled': False, 'bot_token': None, 'channel_id': None},
    }
    
    print("\n\nTesting batch normalization...")
    all_content = normalizer.normalize_all_sources(config)
    print(f"Total normalized content: {len(all_content)}")
