"""
HTML to Markdown Converter for ContentCombine
Based on: https://github.com/Ademking/MD-This-Page

Uses BeautifulSoup for clean content extraction.
Converts web pages to LLM-ready Markdown.
"""

import re
from typing import Optional
from dataclasses import dataclass

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("⚠️ BeautifulSoup not installed. Using fallback HTML parser.")


@dataclass
class PageContent:
    """Extracted page content"""
    markdown: str
    title: str
    author: str
    date: str
    url: str
    word_count: int = 0
    
    def __post_init__(self):
        self.word_count = len(self.markdown.split())


class HtmlToMarkdown:
    """Convert HTML to clean Markdown using BeautifulSoup"""
    
    def __init__(self):
        self.has_bs4 = HAS_BS4
    
    def convert(self, html: str, url: str = "") -> PageContent:
        """Convert HTML to Markdown"""
        if self.has_bs4:
            return self._convert_with_bs4(html, url)
        else:
            return self._convert_fallback(html, url)
    
    def _convert_with_bs4(self, html: str, url: str) -> PageContent:
        """Convert using BeautifulSoup (preferred)"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract metadata
            title = soup.title.string if soup.title else ""
            
            # Remove script and style tags
            for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # Get main content
            main_content = soup.find('article') or soup.find('main') or soup.body or soup
            
            # Convert to markdown
            markdown = self._element_to_markdown(main_content)
            
            # Clean up
            markdown = self._clean_markdown(markdown)
            
            return PageContent(
                markdown=markdown,
                title=title,
                author="",
                date="",
                url=url,
            )
        except Exception as e:
            print(f"⚠️ BeautifulSoup error: {e}")
            return self._convert_fallback(html, url)
    
    def _element_to_markdown(self, element) -> str:
        """Convert BeautifulSoup element to Markdown"""
        if element.name is None:  # NavigableString
            text = str(element)
            return text if text.strip() else ""
        
        # Headers
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            return f"\n{'#' * level} {element.get_text(strip=True)}\n"
        
        # Paragraphs
        if element.name == 'p':
            # Use recursive conversion to preserve inline formatting
            parts = []
            for child in element.children:
                parts.append(self._element_to_markdown(child))
            return f"\n{''.join(parts)}\n"
        
        # Lists
        if element.name in ['ul', 'ol']:
            items = []
            for i, li in enumerate(element.find_all('li', recursive=False)):
                prefix = f"{i+1}." if element.name == 'ol' else "-"
                items.append(f"{prefix} {li.get_text(strip=True)}")
            return "\n" + "\n".join(items) + "\n"
        
        # Links
        if element.name == 'a':
            href = element.get('href', '')
            text = element.get_text(strip=True)
            return f"[{text}]({href})" if href else text
        
        # Images
        if element.name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', '')
            return f"![{alt}]({src})" if src else ""
        
        # Code
        if element.name == 'code':
            return f"`{element.get_text()}`"
        
        if element.name == 'pre':
            return f"\n```\n{element.get_text()}\n```\n"
        
        # Bold
        if element.name in ['strong', 'b']:
            return f"**{element.get_text(strip=True)}**"
        
        # Italic
        if element.name in ['em', 'i']:
            return f"*{element.get_text(strip=True)}*"
        
        # Blockquote
        if element.name == 'blockquote':
            text = element.get_text(strip=True)
            return "\n> " + "\n> ".join(text.split('\n')) + "\n"
        
        # Default: recurse into children with spaces
        parts = []
        for child in element.children:
            parts.append(self._element_to_markdown(child))
        return "".join(parts)
    
    def _convert_fallback(self, html: str, url: str) -> PageContent:
        """Fallback HTML parser (no dependencies)"""
        # Simple regex-based extraction
        title = self._extract_tag(html, "title")
        
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        
        # Remove HTML tags but keep text
        text = re.sub(r'<[^>]+>', '\n', html)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        # Convert to basic markdown
        markdown = self._html_to_markdown(html)
        
        return PageContent(
            markdown=markdown,
            title=title,
            author="",
            date="",
            url=url,
        )
    
    def _extract_tag(self, html: str, tag: str) -> str:
        """Extract content from HTML tag"""
        match = re.search(f'<{tag}[^>]*>(.*?)</{tag}>', html, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to basic Markdown"""
        # Headers
        for i in range(6, 0, -1):
            html = re.sub(f'<h{i}[^>]*>(.*?)</h{i}>', f'\n{"#" * i} \\1\n', html, flags=re.DOTALL)
        
        # Bold and italic
        html = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html, flags=re.DOTALL)
        html = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html, flags=re.DOTALL)
        html = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', html, flags=re.DOTALL)
        html = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', html, flags=re.DOTALL)
        
        # Links
        html = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', html, flags=re.DOTALL)
        
        # Images
        html = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>', r'![\2](\1)', html)
        html = re.sub(r'<img[^>]*src="([^"]*)"[^>]*/?>', r'![](\1)', html)
        
        # Lists
        html = re.sub(r'<li[^>]*>(.*?)</li>', r'\n- \1', html, flags=re.DOTALL)
        html = re.sub(r'<ul[^>]*>(.*?)</ul>', r'\1', html, flags=re.DOTALL)
        html = re.sub(r'<ol[^>]*>(.*?)</ol>', r'\1', html, flags=re.DOTALL)
        
        # Code
        html = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html, flags=re.DOTALL)
        html = re.sub(r'<pre[^>]*>(.*?)</pre>', r'\n```\n\1\n```\n', html, flags=re.DOTALL)
        
        # Blockquotes
        html = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'\n> \1\n', html, flags=re.DOTALL)
        
        # Remove remaining HTML tags
        html = re.sub(r'<[^>]+>', '\n', html)
        
        # Clean up whitespace
        html = re.sub(r'\n\s*\n', '\n\n', html)
        
        return html.strip()
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean up extracted Markdown"""
        # Remove excessive blank lines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Remove navigation/header cruft (Habr-specific)
        # Remove lines that are just links or empty markers
        lines = markdown.split('\n')
        cleaned_lines = []
        skip_patterns = [
            r'^\s*\[.*?\]\(/ru/users/.*?\)\s*$',  # User links
            r'^\s*\[.*?\]\(/ru/companies/.*?\)\s*$',  # Company links
            r'^\s*\[.*?\]\(/ru/hubs/.*?\)\s*$',  # Hub links
            r'^\s*\d+\s+.*?в\s+\d+:\d+\s*$',  # Date stamps
            r'^\s*Уровень сложности.*$',  # Difficulty level
            r'^\s*Время на прочтение.*$',  # Read time
            r'^\s*Охват и читатели.*$',  # Coverage
            r'^\s*Читать далее\s*$',  # Read more
            r'^\s*Комментировать\s*$',  # Comment
            r'^\s*Поделиться\s*$',  # Share
            r'^\s*Понравилась статья\s*$',  # Liked
            r'^\s*\[\]\[.*?\]\s*$',  # Empty markdown links
            r'^\s*\[.*?\]\(/.*?\)\s*\[.*?\]\(/.*?\)\s*$',  # Double links
            r'^\s*\*\*Кейс.*?\*\*\s*$',  # Case badges
        ]
        
        # More generic: remove lines that are mostly markdown links
        link_pattern = re.compile(r'^\s*(\[.*?\]\(/.*?\)\s*)+$')
        # Also remove lines that start with empty markdown links or just `[`
        empty_link_start = re.compile(r'^\s*\[.*?\]\s*\[')
        
        for line in lines:
            skip = False
            # Check specific patterns
            for pattern in skip_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    skip = True
                    break
            # Check generic link-only pattern
            if not skip and link_pattern.match(line):
                skip = True
            # Check empty link start pattern
            if not skip and empty_link_start.match(line):
                skip = True
            if not skip:
                cleaned_lines.append(line)
        
        markdown = '\n'.join(cleaned_lines)
        
        # Remove trailing whitespace
        lines = [line.rstrip() for line in markdown.split('\n')]
        markdown = '\n'.join(lines)
        
        # Final cleanup of excessive newlines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        return markdown.strip()
    
    def convert_url(self, url: str) -> PageContent:
        """Fetch and convert URL to Markdown"""
        import requests
        
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            return self.convert(resp.text, url)
        except Exception as e:
            print(f"⚠️ Failed to fetch URL: {e}")
            return PageContent(
                markdown="",
                title="",
                author="",
                date="",
                url=url,
            )


# Convenience function
def html_to_markdown(html: str, url: str = "") -> str:
    """Convert HTML to Markdown (simple interface)"""
    converter = HtmlToMarkdown()
    result = converter.convert(html, url)
    return result.markdown


def url_to_markdown(url: str) -> str:
    """Fetch URL and convert to Markdown"""
    converter = HtmlToMarkdown()
    result = converter.convert_url(url)
    return result.markdown


# Example usage
if __name__ == "__main__":
    # Test with sample HTML
    sample_html = """
    <html>
    <head><title>Test Article</title></head>
    <body>
        <h1>Hello World</h1>
        <p>This is a <strong>test</strong> article with <em>emphasis</em>.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <a href="https://example.com">Link</a>
    </body>
    </html>
    """
    
    converter = HtmlToMarkdown()
    result = converter.convert(sample_html, "https://example.com")
    
    print(f"Title: {result.title}")
    print(f"Words: {result.word_count}")
    print(f"\nMarkdown:\n{result.markdown}")
