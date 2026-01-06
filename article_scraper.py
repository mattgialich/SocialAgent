"""
Article Scraper Module
Finds and retrieves the latest articles for a given keyword using Google News RSS and web scraping.
"""

import requests
from bs4 import BeautifulSoup
import html2text
from typing import List, Dict
import logging
import re
from xml.etree import ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleScraper:
    """Scrapes and retrieves articles based on keywords."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def search_google_news(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        Search Google News RSS feed for articles matching the keyword.

        Args:
            keyword: Search keyword
            max_results: Maximum number of articles to return

        Returns:
            List of article dictionaries with title, url, published date
        """
        try:
            # Google News RSS feed URL
            encoded_keyword = keyword.replace(' ', '+')
            rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"

            logger.info(f"Fetching articles for keyword: {keyword}")

            # Fetch the RSS feed
            response = requests.get(rss_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # Parse RSS XML
            root = ET.fromstring(response.content)

            articles = []
            # RSS items are in channel/item
            items = root.findall('.//item')[:max_results]

            for item in items:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                source_elem = item.find('source')

                article_data = {
                    'title': title_elem.text if title_elem is not None else '',
                    'url': link_elem.text if link_elem is not None else '',
                    'published': pub_date_elem.text if pub_date_elem is not None else '',
                    'source': source_elem.text if source_elem is not None else 'Unknown'
                }
                articles.append(article_data)

            logger.info(f"Found {len(articles)} articles")
            return articles

        except Exception as e:
            logger.error(f"Error searching Google News: {e}")
            return []

    def extract_article_content(self, url: str) -> Dict:
        """
        Extract full article content from URL using requests and BeautifulSoup.

        Args:
            url: Article URL

        Returns:
            Dictionary with article content, author, and metadata
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()

            # Extract title
            title = soup.find('title')
            title = title.get_text().strip() if title else 'Unknown'

            # Also try meta title tags
            if title == 'Unknown':
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    title = og_title.get('content', 'Unknown')

            # Try to find article content - multiple strategies
            article_body = None

            # Strategy 1: Look for article tag
            article_body = soup.find('article')

            # Strategy 2: Look for common content classes
            if not article_body:
                for class_pattern in ['article-body', 'article-content', 'post-content',
                                     'entry-content', 'content-body', 'story-body']:
                    article_body = soup.find(class_=re.compile(class_pattern, re.I))
                    if article_body:
                        break

            # Strategy 3: Look for main tag
            if not article_body:
                article_body = soup.find('main')

            # Strategy 4: Find all paragraphs and combine
            if not article_body:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    # Create a container for all paragraphs
                    article_body = soup.new_tag('div')
                    for p in paragraphs:
                        article_body.append(p)

            # Extract text content
            text = ''
            if article_body:
                # Get all paragraph text
                paragraphs = article_body.find_all('p')
                text_parts = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                text = '\n\n'.join(text_parts)

            # Fallback: just get all text from body
            if not text or len(text) < 100:
                body = soup.find('body')
                if body:
                    text = body.get_text(separator='\n', strip=True)

            # Clean up the text
            text = re.sub(r'\n\s*\n+', '\n\n', text)  # Remove multiple newlines
            text = re.sub(r'[ \t]+', ' ', text)  # Remove multiple spaces
            text = text.strip()

            # Try to extract author from meta tags
            authors = []
            author_meta = (soup.find('meta', {'name': 'author'}) or
                          soup.find('meta', {'property': 'article:author'}) or
                          soup.find('meta', {'name': 'dc.creator'}))
            if author_meta and author_meta.get('content'):
                authors = [author_meta.get('content')]

            # Log what we extracted
            logger.info(f"Extracted {len(text)} chars from {url[:50]}...")
            if text:
                logger.debug(f"Content preview: {text[:200]}...")

            return {
                'url': url,
                'title': title,
                'authors': authors,
                'publish_date': None,
                'text': text[:10000],  # Increased limit to 10000 chars
                'top_image': None,
                'summary': text[:300] if text else ''
            }

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def scrape_articles(self, keyword: str, max_articles: int = 10) -> List[Dict]:
        """
        Main method to scrape articles with full content.

        Args:
            keyword: Search keyword
            max_articles: Maximum number of articles to retrieve

        Returns:
            List of articles with full content
        """
        # Get article links from Google News
        article_links = self.search_google_news(keyword, max_articles)

        # Extract full content for each article
        full_articles = []
        for article_data in article_links:
            logger.info(f"Extracting content from: {article_data['title']}")
            content = self.extract_article_content(article_data['url'])

            if content:
                # Merge the metadata from RSS with extracted content
                content['rss_title'] = article_data['title']
                content['source'] = article_data.get('source', 'Unknown')
                full_articles.append(content)

        logger.info(f"Successfully extracted {len(full_articles)} articles with full content")
        return full_articles


if __name__ == "__main__":
    # Test the scraper
    scraper = ArticleScraper()
    articles = scraper.scrape_articles("space technology", max_articles=5)

    for i, article in enumerate(articles, 1):
        print(f"\n{'='*80}")
        print(f"Article {i}: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Authors: {', '.join(article.get('authors', ['Unknown']))}")
        print(f"Content preview: {article['text'][:200]}...")
