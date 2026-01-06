"""
Article Scraper Module
Finds and retrieves the latest articles for a given keyword using Google News RSS and web scraping.
"""

import requests
from bs4 import BeautifulSoup
import feedparser
import html2text
from typing import List, Dict
import logging
import re

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
            feed = feedparser.parse(rss_url)

            articles = []
            for entry in feed.entries[:max_results]:
                article_data = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': entry.get('source', {}).get('title', 'Unknown')
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

            # Extract title
            title = soup.find('title')
            title = title.get_text().strip() if title else 'Unknown'

            # Try to find article content in common article tags
            article_body = None
            for tag in ['article', 'main', {'class': re.compile('article|content|post')}]:
                article_body = soup.find(tag)
                if article_body:
                    break

            if not article_body:
                article_body = soup.find('body')

            # Convert HTML to text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            text = h.handle(str(article_body)) if article_body else ''

            # Clean up the text
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove multiple newlines
            text = text.strip()

            # Try to extract author from meta tags
            authors = []
            author_meta = soup.find('meta', {'name': 'author'}) or soup.find('meta', {'property': 'article:author'})
            if author_meta and author_meta.get('content'):
                authors = [author_meta.get('content')]

            return {
                'url': url,
                'title': title,
                'authors': authors,
                'publish_date': None,
                'text': text[:5000],  # Limit to first 5000 chars
                'top_image': None,
                'summary': text[:200] if text else ''
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
