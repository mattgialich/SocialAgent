"""
Multi-Source Article Finder
Searches multiple sources and ranks articles to find the best, most relevant content.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
import re
from xml.etree import ElementTree as ET
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiSourceArticleFinder:
    """Finds articles from multiple sources and ranks them by relevance."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.newsapi_key = os.getenv('NEWSAPI_KEY')

    def search_newsapi(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        Search using NewsAPI (provides article descriptions).
        Free tier: 100 requests/day, articles from last 30 days.
        Sign up at: https://newsapi.org/
        """
        if not self.newsapi_key:
            logger.warning("NewsAPI key not found - skipping NewsAPI source")
            return []

        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': keyword,
                'apiKey': self.newsapi_key,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': max_results
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = []

            for item in data.get('articles', []):
                # NewsAPI provides description and some content
                article_data = {
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'published': item.get('publishedAt', ''),
                    'source': item.get('source', {}).get('name', 'Unknown'),
                    'description': item.get('description', ''),
                    'content': item.get('content', ''),  # Often truncated
                    'author': item.get('author', ''),
                    'image': item.get('urlToImage', ''),
                    'score': 10  # NewsAPI results are highly relevant
                }
                articles.append(article_data)

            logger.info(f"NewsAPI: Found {len(articles)} articles")
            return articles

        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []

    def search_bing_news(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        Search using Bing News Search (free tier available).
        Better for recent, high-quality news sources.
        """
        bing_key = os.getenv('BING_SEARCH_KEY')
        if not bing_key:
            logger.warning("Bing Search key not found - skipping Bing News")
            return []

        try:
            url = "https://api.bing.microsoft.com/v7.0/news/search"
            headers = {'Ocp-Apim-Subscription-Key': bing_key}
            params = {
                'q': keyword,
                'count': max_results,
                'mkt': 'en-US',
                'freshness': 'Month'
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = []

            for item in data.get('value', []):
                article_data = {
                    'title': item.get('name', ''),
                    'url': item.get('url', ''),
                    'published': item.get('datePublished', ''),
                    'source': item.get('provider', [{}])[0].get('name', 'Unknown'),
                    'description': item.get('description', ''),
                    'content': item.get('description', ''),
                    'author': '',
                    'image': item.get('image', {}).get('thumbnail', {}).get('contentUrl', ''),
                    'score': 8  # Bing results are good quality
                }
                articles.append(article_data)

            logger.info(f"Bing News: Found {len(articles)} articles")
            return articles

        except Exception as e:
            logger.error(f"Bing News error: {e}")
            return []

    def search_google_news_rss(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """Search Google News RSS (free, no API key needed)."""
        try:
            encoded_keyword = keyword.replace(' ', '+')
            rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"

            logger.info(f"Google News RSS: Fetching...")
            response = requests.get(rss_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            articles = []
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
                    'source': source_elem.text if source_elem is not None else 'Unknown',
                    'description': '',
                    'content': '',
                    'author': '',
                    'image': '',
                    'score': 5  # Google News RSS is okay but no content
                }
                articles.append(article_data)

            logger.info(f"Google News: Found {len(articles)} articles")
            return articles

        except Exception as e:
            logger.error(f"Google News error: {e}")
            return []

    def extract_full_content(self, article: Dict) -> Dict:
        """
        Try to extract full article content from URL.
        Enhanced version with better extraction strategies.
        """
        url = article.get('url', '')
        if not url:
            return article

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove noise
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
                tag.decompose()

            # Try multiple strategies to find content
            article_body = None

            # Strategy 1: <article> tag
            article_body = soup.find('article')

            # Strategy 2: Common content classes/ids
            if not article_body:
                patterns = ['article-body', 'article-content', 'post-content',
                           'entry-content', 'content-body', 'story-body', 'article-text']
                for pattern in patterns:
                    article_body = soup.find(class_=re.compile(pattern, re.I))
                    if article_body:
                        break

            # Strategy 3: <main> tag
            if not article_body:
                article_body = soup.find('main')

            # Strategy 4: Find div with most paragraphs
            if not article_body:
                divs = soup.find_all('div')
                max_paragraphs = 0
                best_div = None
                for div in divs:
                    p_count = len(div.find_all('p'))
                    if p_count > max_paragraphs:
                        max_paragraphs = p_count
                        best_div = div
                if best_div and max_paragraphs > 3:
                    article_body = best_div

            # Extract text
            text = ''
            if article_body:
                paragraphs = article_body.find_all('p')
                text_parts = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                text = '\n\n'.join(text_parts)

            # Fallback
            if not text or len(text) < 200:
                paragraphs = soup.find_all('p')
                text_parts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50]
                text = '\n\n'.join(text_parts[:20])  # Top 20 paragraphs

            # Clean up
            text = re.sub(r'\n\s*\n+', '\n\n', text)
            text = re.sub(r'[ \t]+', ' ', text)
            text = text.strip()

            # Extract author
            authors = []
            author_meta = (soup.find('meta', {'name': 'author'}) or
                          soup.find('meta', {'property': 'article:author'}))
            if author_meta and author_meta.get('content'):
                authors = [author_meta.get('content')]
            elif article.get('author'):
                authors = [article['author']]

            # Update article with extracted content
            if text and len(text) > 200:
                article['content'] = text[:10000]
                article['text'] = text[:10000]
                article['authors'] = authors
                article['score'] += 5  # Bonus for having full content
                logger.info(f"✓ Extracted {len(text)} chars from {url[:50]}...")
            else:
                # Use description if we couldn't get full content
                article['text'] = article.get('description', '')[:2000]
                logger.warning(f"✗ Could not extract full content from {url[:50]}...")

            return article

        except Exception as e:
            logger.error(f"Extraction error for {url[:50]}: {e}")
            # Use description as fallback
            article['text'] = article.get('description', '')[:2000]
            return article

    def rank_articles(self, articles: List[Dict], keyword: str) -> List[Dict]:
        """
        Rank articles by relevance, quality, and content availability.
        """
        keyword_lower = keyword.lower()
        keywords = set(keyword_lower.split())

        for article in articles:
            score = article.get('score', 0)

            # Check keyword presence
            title = article.get('title', '').lower()
            content = article.get('text', '').lower()

            # Title match (important)
            if keyword_lower in title:
                score += 10
            else:
                # Partial keyword match
                matching_words = sum(1 for word in keywords if word in title)
                score += matching_words * 3

            # Content match
            if content:
                content_matches = sum(1 for word in keywords if word in content)
                score += content_matches * 2

            # Content length bonus
            content_length = len(article.get('text', ''))
            if content_length > 2000:
                score += 8
            elif content_length > 1000:
                score += 5
            elif content_length > 500:
                score += 3

            # Recency bonus (if available)
            published = article.get('published', '')
            if published and '2024' in published or '2025' in published or '2026' in published:
                score += 3

            article['relevance_score'] = score

        # Sort by score
        ranked = sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        return ranked

    def find_top_articles(self, keyword: str, top_n: int = 5) -> List[Dict]:
        """
        Main method: Search multiple sources and return top N most relevant articles.
        """
        logger.info(f"🔍 Deep search for: '{keyword}'")
        logger.info("="*80)

        all_articles = []

        # Search all available sources
        sources = [
            ('NewsAPI', lambda: self.search_newsapi(keyword, 15)),
            ('Bing News', lambda: self.search_bing_news(keyword, 15)),
            ('Google News', lambda: self.search_google_news_rss(keyword, 15))
        ]

        for source_name, search_func in sources:
            try:
                articles = search_func()
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error with {source_name}: {e}")

        if not all_articles:
            logger.error("No articles found from any source!")
            return []

        logger.info(f"\n📰 Found {len(all_articles)} total articles from all sources")

        # Remove duplicates (same URL)
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)

        logger.info(f"📰 {len(unique_articles)} unique articles after deduplication")

        # Rank articles
        logger.info("\n⚡ Ranking articles by relevance...")
        ranked_articles = self.rank_articles(unique_articles, keyword)

        # Get top N
        top_articles = ranked_articles[:top_n * 2]  # Get 2x to account for extraction failures

        # Try to extract full content for top articles
        logger.info(f"\n📖 Extracting full content for top {len(top_articles)} articles...")
        for i, article in enumerate(top_articles, 1):
            logger.info(f"  [{i}/{len(top_articles)}] {article['title'][:60]}...")
            self.extract_full_content(article)

        # Re-rank after extraction (content extraction adds bonus points)
        final_ranked = self.rank_articles(top_articles, keyword)

        # Return top N
        top_n_articles = final_ranked[:top_n]

        logger.info(f"\n✅ Returning top {len(top_n_articles)} articles")
        logger.info("="*80)

        return top_n_articles


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    finder = MultiSourceArticleFinder()
    articles = finder.find_top_articles("asteroid mining", top_n=5)

    for i, article in enumerate(articles, 1):
        print(f"\n[{i}] {article['title']}")
        print(f"    Source: {article['source']}")
        print(f"    URL: {article['url']}")
        print(f"    Score: {article.get('relevance_score', 0)}")
        print(f"    Content: {len(article.get('text', ''))} chars")
        if article.get('text'):
            print(f"    Preview: {article['text'][:150]}...")
