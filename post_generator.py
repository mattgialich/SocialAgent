"""
Post Generator Module
Generates Twitter and LinkedIn posts based on article analysis and AstroForge story.
"""

import os
from anthropic import Anthropic
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostGenerator:
    """Generates social media posts for Twitter and LinkedIn."""

    def __init__(self, api_key: str = None):
        """
        Initialize the PostGenerator.

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")

        self.client = Anthropic(api_key=self.api_key)
        self.twitter_max_length = int(os.getenv('TWITTER_MAX_LENGTH', 280))
        self.linkedin_max_length = int(os.getenv('LINKEDIN_MAX_LENGTH', 3000))

    def generate_twitter_post(
        self,
        article: Dict,
        astroforge_story: Dict,
        article_url: str = None,
        authors: List[str] = None
    ) -> str:
        """
        Generate a Twitter post for defense-related articles.

        Args:
            article: The original article data
            astroforge_story: AstroForge story from Google Docs
            article_url: URL of the original article
            authors: List of article authors

        Returns:
            Twitter post text
        """
        try:
            article_title = article.get('title', 'Unknown')
            astroforge_content = astroforge_story.get('content', '')
            astroforge_title = astroforge_story.get('title', 'AstroForge Story')

            # Get author information
            author_credit = ""
            if authors and len(authors) > 0:
                if len(authors) == 1:
                    author_credit = f"by {authors[0]}"
                else:
                    author_credit = f"by {authors[0]} et al."

            # Prepare the prompt
            prompt = f"""Create an engaging Twitter post (max {self.twitter_max_length} characters) that:

1. References the AstroForge story below
2. Links it to this defense-related article: "{article_title}"
3. Includes the article URL: {article_url or '[URL]'}
4. Credits the author: {author_credit or 'Unknown Author'}

AstroForge Story:
{astroforge_content[:2000]}

Requirements:
- Stay under {self.twitter_max_length} characters total
- Make it engaging and newsworthy
- Include relevant hashtags (1-2 max)
- Must include the article URL
- Must credit the author
- Connect the AstroForge story context to the current article

Return ONLY the tweet text, nothing else."""

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=200,
                temperature=0.7,
                system="You are a social media expert specializing in defense and aerospace topics. Create engaging, concise Twitter posts.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            tweet = response.content[0].text.strip()

            # Ensure it's within length limits
            if len(tweet) > self.twitter_max_length:
                logger.warning(f"Tweet too long ({len(tweet)} chars), truncating...")
                tweet = tweet[:self.twitter_max_length-3] + "..."

            logger.info(f"Generated Twitter post ({len(tweet)} chars)")
            return tweet

        except Exception as e:
            logger.error(f"Error generating Twitter post: {e}")
            # Return a simple fallback post
            url_text = f" {article_url}" if article_url else ""
            author_text = f" - {authors[0]}" if authors else ""
            return f"Defense tech update{author_text}{url_text}"

    def generate_linkedin_post(
        self,
        article: Dict,
        astroforge_story: Dict,
        article_url: str = None,
        authors: List[str] = None
    ) -> str:
        """
        Generate a LinkedIn post for non-defense articles.

        Args:
            article: The original article data
            astroforge_story: AstroForge story from Google Docs
            article_url: URL of the original article
            authors: List of article authors

        Returns:
            LinkedIn post text
        """
        try:
            article_title = article.get('title', 'Unknown')
            article_text = article.get('text', '')[:1000]  # First 1000 chars for context
            astroforge_content = astroforge_story.get('content', '')
            astroforge_title = astroforge_story.get('title', 'AstroForge Story')

            # Get author information
            author_credit = ""
            if authors and len(authors) > 0:
                if len(authors) == 1:
                    author_credit = f"by {authors[0]}"
                elif len(authors) == 2:
                    author_credit = f"by {authors[0]} and {authors[1]}"
                else:
                    author_credit = f"by {authors[0]}, {authors[1]}, and others"

            # Prepare the prompt
            prompt = f"""Create a professional LinkedIn post (max {self.linkedin_max_length} characters) that:

1. Discusses insights from the AstroForge story
2. Connects it to this article: "{article_title}"
3. Provides thoughtful commentary on the broader implications
4. Includes the article URL: {article_url or '[URL]'}
5. Credits the author(s): {author_credit or 'the authors'}

Article Preview:
{article_text}

AstroForge Story Context:
{astroforge_content[:2000]}

Requirements:
- Professional tone suitable for LinkedIn
- 3-5 paragraphs
- Include relevant insights and analysis
- Must include the article URL
- Must credit the author(s)
- Use line breaks for readability
- Add 2-3 relevant hashtags at the end
- Draw meaningful connections between the AstroForge story and the current article

Return ONLY the LinkedIn post text, nothing else."""

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0.7,
                system="You are a professional content creator specializing in technology and aerospace topics for LinkedIn. Create thoughtful, engaging posts that provide value.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            post = response.content[0].text.strip()

            # Ensure it's within length limits
            if len(post) > self.linkedin_max_length:
                logger.warning(f"LinkedIn post too long ({len(post)} chars), truncating...")
                post = post[:self.linkedin_max_length-3] + "..."

            logger.info(f"Generated LinkedIn post ({len(post)} chars)")
            return post

        except Exception as e:
            logger.error(f"Error generating LinkedIn post: {e}")
            # Return a simple fallback post
            url_text = f"\n\nRead more: {article_url}" if article_url else ""
            author_text = f"\n\nCredit: {authors[0]}" if authors else ""
            return f"Interesting developments in the space industry.\n\n{article_title}{author_text}{url_text}"


if __name__ == "__main__":
    # Test the generator
    from dotenv import load_dotenv
    load_dotenv()

    generator = PostGenerator()

    # Test data
    test_article = {
        'title': 'New Satellite Launch Technology',
        'text': 'Revolutionary advances in satellite deployment systems...',
        'url': 'https://example.com/article'
    }

    test_astroforge = {
        'title': 'AstroForge Mining Mission',
        'content': 'AstroForge is pioneering asteroid mining technology with their upcoming mission to extract platinum-group metals from near-Earth asteroids...'
    }

    # Test Twitter post
    print("\n=== TWITTER POST (Defense) ===")
    twitter_post = generator.generate_twitter_post(
        test_article,
        test_astroforge,
        'https://example.com/article',
        ['John Doe']
    )
    print(twitter_post)
    print(f"Length: {len(twitter_post)}")

    # Test LinkedIn post
    print("\n=== LINKEDIN POST (Non-Defense) ===")
    linkedin_post = generator.generate_linkedin_post(
        test_article,
        test_astroforge,
        'https://example.com/article',
        ['Jane Smith', 'Bob Johnson']
    )
    print(linkedin_post)
    print(f"Length: {len(linkedin_post)}")
