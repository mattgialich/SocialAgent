#!/usr/bin/env python3
"""
Social Agent - Main Orchestration Script

This script:
1. Scrapes articles for a given keyword
2. Analyzes if they're defense-related
3. Fetches the AstroForge story from Google Docs
4. Generates appropriate social media posts:
   - Twitter posts for defense articles
   - LinkedIn posts for non-defense articles
"""

import os
import sys
import argparse
import json
from datetime import datetime
from dotenv import load_dotenv
import logging

from article_scraper import ArticleScraper
from content_analyzer import ContentAnalyzer
from google_docs_client import GoogleDocsClient
from post_generator import PostGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SocialAgent:
    """Main orchestrator for the social media content generation workflow."""

    def __init__(self, google_doc_id: str = None):
        """
        Initialize the SocialAgent.

        Args:
            google_doc_id: Google Doc ID for the AstroForge story
        """
        logger.info("Initializing SocialAgent...")

        # Initialize components
        self.scraper = ArticleScraper()
        self.analyzer = ContentAnalyzer()
        self.post_generator = PostGenerator()

        # Initialize Google Docs client (may require authentication)
        try:
            self.docs_client = GoogleDocsClient()
            self.google_doc_id = google_doc_id or os.getenv('GOOGLE_DOC_ID')
        except FileNotFoundError:
            logger.warning("Google Docs client not initialized - credentials missing")
            self.docs_client = None
            self.google_doc_id = None

        self.astroforge_story = None

    def fetch_astroforge_story(self):
        """Fetch the AstroForge story from Google Docs."""
        if not self.docs_client:
            logger.error("Google Docs client not initialized")
            return None

        if not self.google_doc_id:
            logger.error("Google Doc ID not provided")
            return None

        try:
            logger.info("Fetching AstroForge story from Google Docs...")
            self.astroforge_story = self.docs_client.get_astroforge_story(self.google_doc_id)
            logger.info(f"Successfully fetched: {self.astroforge_story['title']}")
            return self.astroforge_story
        except Exception as e:
            logger.error(f"Error fetching AstroForge story: {e}")
            return None

    def process_articles(self, keyword: str, max_articles: int = 10):
        """
        Main processing workflow.

        Args:
            keyword: Search keyword for articles
            max_articles: Maximum number of articles to process

        Returns:
            Dictionary with results including generated posts
        """
        logger.info(f"Starting article processing for keyword: '{keyword}'")

        # Step 1: Scrape articles
        logger.info("Step 1: Scraping articles...")
        articles = self.scraper.scrape_articles(keyword, max_articles)

        if not articles:
            logger.warning("No articles found")
            return {'error': 'No articles found'}

        logger.info(f"Found {len(articles)} articles")

        # Step 2: Fetch AstroForge story (if not already fetched)
        if not self.astroforge_story:
            logger.info("Step 2: Fetching AstroForge story...")
            astroforge = self.fetch_astroforge_story()
            if not astroforge:
                logger.warning("Could not fetch AstroForge story - using placeholder")
                self.astroforge_story = {
                    'title': 'AstroForge Story',
                    'content': 'AstroForge is pioneering asteroid mining technology...'
                }

        # Step 3: Analyze and generate posts
        logger.info("Step 3: Analyzing articles and generating posts...")
        results = {
            'keyword': keyword,
            'timestamp': datetime.now().isoformat(),
            'articles_processed': len(articles),
            'defense_articles': [],
            'non_defense_articles': []
        }

        for i, article in enumerate(articles, 1):
            logger.info(f"\nProcessing article {i}/{len(articles)}: {article['title'][:50]}...")

            # Analyze if defense-related
            analysis = self.analyzer.is_defense_related(article)

            article_data = {
                'title': article['title'],
                'url': article['url'],
                'authors': article.get('authors', []),
                'is_defense': analysis['is_defense'],
                'confidence': analysis['confidence'],
                'reasoning': analysis['reasoning']
            }

            # Generate appropriate post
            if analysis['is_defense']:
                logger.info("→ Defense-related - Generating Twitter post")
                post = self.post_generator.generate_twitter_post(
                    article,
                    self.astroforge_story,
                    article['url'],
                    article.get('authors', [])
                )
                article_data['post_type'] = 'twitter'
                article_data['post'] = post
                results['defense_articles'].append(article_data)

            else:
                logger.info("→ Non-defense - Generating LinkedIn post")
                post = self.post_generator.generate_linkedin_post(
                    article,
                    self.astroforge_story,
                    article['url'],
                    article.get('authors', [])
                )
                article_data['post_type'] = 'linkedin'
                article_data['post'] = post
                results['non_defense_articles'].append(article_data)

            logger.info(f"✓ Generated {article_data['post_type']} post")

        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("PROCESSING COMPLETE")
        logger.info(f"Total articles: {len(articles)}")
        logger.info(f"Defense articles (Twitter): {len(results['defense_articles'])}")
        logger.info(f"Non-defense articles (LinkedIn): {len(results['non_defense_articles'])}")
        logger.info(f"{'='*80}\n")

        return results

    def save_results(self, results: dict, output_file: str = 'results.json'):
        """
        Save results to a JSON file.

        Args:
            results: Results dictionary
            output_file: Output filename
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def print_results(self, results: dict):
        """
        Print results in a readable format.

        Args:
            results: Results dictionary
        """
        print(f"\n{'='*80}")
        print(f"SOCIAL AGENT RESULTS")
        print(f"{'='*80}")
        print(f"Keyword: {results['keyword']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Articles processed: {results['articles_processed']}")
        print(f"{'='*80}\n")

        # Defense articles (Twitter)
        if results['defense_articles']:
            print(f"\n🛡️  DEFENSE ARTICLES (Twitter Posts) - {len(results['defense_articles'])}")
            print("="*80)
            for i, article in enumerate(results['defense_articles'], 1):
                print(f"\n[{i}] {article['title']}")
                print(f"URL: {article['url']}")
                print(f"Authors: {', '.join(article['authors']) if article['authors'] else 'Unknown'}")
                print(f"Confidence: {article['confidence']:.2f}")
                print(f"\nTwitter Post:")
                print("-" * 80)
                print(article['post'])
                print("-" * 80)

        # Non-defense articles (LinkedIn)
        if results['non_defense_articles']:
            print(f"\n🌐 NON-DEFENSE ARTICLES (LinkedIn Posts) - {len(results['non_defense_articles'])}")
            print("="*80)
            for i, article in enumerate(results['non_defense_articles'], 1):
                print(f"\n[{i}] {article['title']}")
                print(f"URL: {article['url']}")
                print(f"Authors: {', '.join(article['authors']) if article['authors'] else 'Unknown'}")
                print(f"Confidence: {article['confidence']:.2f}")
                print(f"\nLinkedIn Post:")
                print("-" * 80)
                print(article['post'])
                print("-" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Social Agent - Automated article scraping and social media post generation'
    )
    parser.add_argument(
        'keyword',
        type=str,
        nargs='?',
        default=None,
        help='Search keyword for articles'
    )
    parser.add_argument(
        '--max-articles',
        type=int,
        default=10,
        help='Maximum number of articles to process (default: 10)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='results.json',
        help='Output file for results (default: results.json)'
    )
    parser.add_argument(
        '--google-doc-id',
        type=str,
        default=None,
        help='Google Doc ID for AstroForge story (overrides env variable)'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Get keyword from args or env
    keyword = args.keyword or os.getenv('DEFAULT_KEYWORD', 'space technology')

    logger.info("="*80)
    logger.info("SOCIAL AGENT - Starting")
    logger.info("="*80)

    try:
        # Initialize agent
        agent = SocialAgent(google_doc_id=args.google_doc_id)

        # Process articles
        results = agent.process_articles(keyword, args.max_articles)

        # Save and print results
        agent.save_results(results, args.output)
        agent.print_results(results)

        logger.info("\n✓ Social Agent completed successfully")
        return 0

    except KeyboardInterrupt:
        logger.info("\n\nProcess interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
