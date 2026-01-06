"""
Google Docs Client Module
Fetches content from Google Docs, specifically the AstroForge story.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']


class GoogleDocsClient:
    """Client for fetching content from Google Docs."""

    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Initialize the Google Docs client.

        Args:
            credentials_file: Path to Google OAuth2 credentials JSON file
        """
        self.credentials_file = credentials_file
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Docs API."""
        creds = None

        # The file token.json stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    logger.info("Please download credentials from Google Cloud Console")
                    logger.info("See: https://developers.google.com/docs/api/quickstart/python")
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('docs', 'v1', credentials=creds)
            logger.info("Successfully authenticated with Google Docs API")
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise

    def get_document_content(self, document_id: str) -> dict:
        """
        Retrieve content from a Google Doc.

        Args:
            document_id: The ID of the Google Doc

        Returns:
            Dictionary containing document title, content, and metadata
        """
        try:
            # Retrieve the document
            document = self.service.documents().get(documentId=document_id).execute()

            title = document.get('title', 'Untitled')
            content = self._extract_text(document)

            logger.info(f"Successfully retrieved document: {title}")

            return {
                'title': title,
                'content': content,
                'document_id': document_id,
                'raw_document': document
            }

        except HttpError as error:
            logger.error(f"Error retrieving document {document_id}: {error}")
            raise

    def _extract_text(self, document: dict) -> str:
        """
        Extract plain text from a Google Doc.

        Args:
            document: The document resource from Google Docs API

        Returns:
            Plain text content
        """
        content = document.get('body', {}).get('content', [])
        text_parts = []

        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    text_run = elem.get('textRun', {})
                    if 'content' in text_run:
                        text_parts.append(text_run['content'])

        return ''.join(text_parts)

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

    try:
        client = GoogleDocsClient()
        doc_id = os.getenv('GOOGLE_DOC_ID')

        if doc_id:
            story = client.get_astroforge_story(doc_id)
            print(f"\nDocument Title: {story['title']}")
            print(f"Content preview: {story['content'][:300]}...")
        else:
            print("Please set GOOGLE_DOC_ID in your .env file")

    except FileNotFoundError as e:
        print(f"\nSetup required: {e}")
        print("\nTo use Google Docs API:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Google Docs API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Download credentials.json to this directory")
