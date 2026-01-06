"""
Content Analyzer Module
Uses OpenAI to analyze article content and determine if it's defense-related.
"""

import os
from openai import OpenAI
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Analyzes article content to determine if it's defense-related."""

    def __init__(self, api_key: str = None):
        """
        Initialize the ContentAnalyzer.

        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)

    def is_defense_related(self, article: Dict) -> Dict:
        """
        Analyze if an article is defense-related.

        Args:
            article: Dictionary containing article data (title, text, etc.)

        Returns:
            Dictionary with:
                - is_defense: Boolean indicating if article is defense-related
                - confidence: Confidence score (0-1)
                - reasoning: Explanation of the decision
        """
        try:
            # Prepare the content for analysis
            title = article.get('title', '')
            text = article.get('text', '')

            # Truncate text if too long (to save tokens)
            max_text_length = 3000
            if len(text) > max_text_length:
                text = text[:max_text_length] + "..."

            # Create the prompt
            prompt = f"""Analyze the following article and determine if it is primarily related to defense, military, national security, or defense contractors.

Title: {title}

Content: {text}

Consider an article "defense-related" if it discusses:
- Military technology, weapons, or defense systems
- Defense contractors or aerospace/defense companies
- National security topics
- Military operations or strategy
- Defense budgets or procurement
- Military partnerships or alliances

Respond in the following format:
DECISION: [YES or NO]
CONFIDENCE: [0.0 to 1.0]
REASONING: [Brief explanation of your decision]

Be strict in your assessment - only classify as defense-related if the primary focus is on defense topics."""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert analyst specializing in identifying defense and military-related content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )

            # Parse the response
            response_text = response.choices[0].message.content
            logger.info(f"Analysis response: {response_text}")

            # Extract decision, confidence, and reasoning
            lines = response_text.strip().split('\n')
            is_defense = False
            confidence = 0.0
            reasoning = ""

            for line in lines:
                if line.startswith('DECISION:'):
                    is_defense = 'YES' in line.upper()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':')[1].strip())
                    except:
                        confidence = 0.5
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()

            result = {
                'is_defense': is_defense,
                'confidence': confidence,
                'reasoning': reasoning,
                'article_title': title
            }

            logger.info(f"Article '{title[:50]}...' - Defense: {is_defense}, Confidence: {confidence}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {
                'is_defense': False,
                'confidence': 0.0,
                'reasoning': f"Error during analysis: {str(e)}",
                'article_title': article.get('title', 'Unknown')
            }

    def analyze_articles(self, articles: list) -> list:
        """
        Analyze multiple articles.

        Args:
            articles: List of article dictionaries

        Returns:
            List of analysis results
        """
        results = []
        for article in articles:
            analysis = self.is_defense_related(article)
            analysis['article_url'] = article.get('url', '')
            analysis['article_authors'] = article.get('authors', [])
            results.append(analysis)

        return results


if __name__ == "__main__":
    # Test the analyzer
    from dotenv import load_dotenv
    load_dotenv()

    analyzer = ContentAnalyzer()

    # Test article
    test_article = {
        'title': 'New F-35 Fighter Jet Technology Breakthrough',
        'text': 'The latest developments in fighter jet technology show significant improvements in stealth capabilities and weapons systems for military applications.'
    }

    result = analyzer.is_defense_related(test_article)
    print(f"\nTest Analysis Result:")
    print(f"Is Defense: {result['is_defense']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reasoning: {result['reasoning']}")
