"""
Google Docs Client Module
Fetches content from Google Docs, specifically the AstroForge story.
Can fetch from public docs without authentication.
"""

import os
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleDocsClient:
    """Client for fetching content from Google Docs."""

    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Initialize the Google Docs client.

        Args:
            credentials_file: Path to Google OAuth2 credentials JSON file (optional for public docs)
        """
        self.credentials_file = credentials_file
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_document_content(self, document_id: str) -> dict:
        """
        Retrieve content from a Google Doc (works with public docs).

        Args:
            document_id: The ID of the Google Doc

        Returns:
            Dictionary containing document title, content, and metadata
        """
        try:
            # Try to fetch as plain text export (works for public docs)
            export_url = f"https://docs.google.com/document/d/{document_id}/export?format=txt"

            logger.info(f"Fetching document {document_id} from public URL...")
            response = requests.get(export_url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                content = response.text.strip()

                # Also try to get the title from the HTML version
                html_url = f"https://docs.google.com/document/d/{document_id}/export?format=html"
                html_response = requests.get(html_url, headers=self.headers, timeout=10)

                title = "Google Doc"
                if html_response.status_code == 200:
                    soup = BeautifulSoup(html_response.content, 'html.parser')
                    title_tag = soup.find('title')
                    if title_tag:
                        title = title_tag.get_text().strip()

                logger.info(f"Successfully retrieved document: {title} ({len(content)} chars)")

                return {
                    'title': title,
                    'content': content,
                    'document_id': document_id
                }
            else:
                logger.error(f"Could not fetch document. Status: {response.status_code}")
                logger.error("Make sure the document is publicly accessible (Share > Anyone with link can view)")
                return {
                    'title': 'Error',
                    'content': 'Could not fetch document. Please ensure it is shared publicly.',
                    'document_id': document_id
                }

        except Exception as error:
            logger.error(f"Error retrieving document {document_id}: {error}")
            return {
                'title': 'Error',
                'content': f'Error fetching document: {str(error)}',
                'document_id': document_id
            }

    def get_astroforge_story(self, document_id: str = None) -> dict:
        """
        Fetch the AstroForge story from Google Docs.

        Args:
            document_id: Google Doc ID. If not provided, uses GOOGLE_DOC_ID env variable.

        Returns:
            Dictionary with story content and metadata
        """
        if not document_id:
            document_id = os.getenv('GOOGLE_DOC_ID')

        if not document_id:
            raise ValueError("Document ID is required. Set GOOGLE_DOC_ID environment variable or pass document_id parameter.")

        logger.info(f"Fetching AstroForge story from document: {document_id}")
        return self.get_document_content(document_id)


if __name__ == "__main__":
    # Test the client
    from dotenv import load_dotenv
    load_dotenv()

    client = GoogleDocsClient()
    doc_id = os.getenv('GOOGLE_DOC_ID')

    if doc_id:
        story = client.get_astroforge_story(doc_id)
        print(f"\nDocument Title: {story['title']}")
        print(f"Content length: {len(story['content'])} characters")
        print(f"\nContent preview:")
        print("-" * 80)
        print(f"{story['content'][:500]}...")
        print("-" * 80)
    else:
        print("Please set GOOGLE_DOC_ID in your .env file")
        print("\nExample:")
        print("GOOGLE_DOC_ID=1CB3rXg8Wk3fGc3mdXBI8H0rFGv7V_qthiomozUzxmV0")
