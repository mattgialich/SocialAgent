# Social Agent

An intelligent web scraper that finds the latest articles for a given keyword, analyzes them for defense-related content, and generates appropriate social media posts based on the AstroForge story.

## Features

- **Article Scraping**: Searches Google News for the latest articles on any keyword
- **Content Analysis**: Uses Anthropic's Claude to determine if articles are defense-related
- **Google Docs Integration**: Fetches the AstroForge story from Google Docs
- **Smart Post Generation**:
  - **Defense articles** → Twitter posts
  - **Non-defense articles** → LinkedIn posts
- **Author Attribution**: Automatically credits article authors
- **Professional Output**: Generates engaging, platform-appropriate content

## Workflow

```
1. Search for articles by keyword
2. Extract full article content
3. Analyze: Defense-related?
   ├─ YES → Generate Twitter post (with AstroForge context)
   └─ NO  → Generate LinkedIn post (with AstroForge context)
4. Credit authors and include source links
```

## Installation

### Prerequisites

- Python 3.8+
- Anthropic API key
- Google Cloud Project with Docs API enabled (for Google Docs integration)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SocialAgent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GOOGLE_DOC_ID=your_google_doc_id_here
   DEFAULT_KEYWORD=space technology
   MAX_ARTICLES=10
   ```

4. **Set up Google Docs API** (Required for AstroForge story)

   a. Go to [Google Cloud Console](https://console.cloud.google.com/)

   b. Create a new project or select an existing one

   c. Enable the Google Docs API

   d. Create OAuth 2.0 credentials:
      - Go to "APIs & Services" → "Credentials"
      - Click "Create Credentials" → "OAuth client ID"
      - Choose "Desktop application"
      - Download the credentials

   e. Save the downloaded file as `credentials.json` in the project directory

   f. On first run, you'll be prompted to authenticate in your browser

## Usage

### Basic Usage

```bash
python main.py "space technology"
```

### Advanced Options

```bash
# Specify maximum number of articles
python main.py "asteroid mining" --max-articles 5

# Clean output - just posts and links (recommended!)
python main.py "satellite technology" --simple --quiet

# Specify output file
python main.py "satellite technology" --output my_results.json

# Override Google Doc ID
python main.py "defense tech" --google-doc-id "your-doc-id-here"

# Quiet mode - reduce logging
python main.py "space mining" --quiet
```

### Output Modes

**Simple Mode** (Recommended for clean output):
```bash
python main.py "asteroid mining" --simple --quiet
```
Shows only:
- Generated social media posts
- Source article links
- Minimal logging

**Full Mode** (Default):
```bash
python main.py "asteroid mining"
```
Shows:
- Article titles, URLs, authors
- Analysis confidence scores
- Reasoning for classification
- Generated posts
- Saves to JSON file

### Using Default Keyword

If you set `DEFAULT_KEYWORD` in `.env`, you can run without arguments:

```bash
python main.py
```

## Output

The script generates:

1. **Console output**: Real-time progress and results
2. **JSON file** (`results.json`): Complete results with all posts

### Example Output

```json
{
  "keyword": "space technology",
  "timestamp": "2024-01-06T10:30:00",
  "articles_processed": 10,
  "defense_articles": [
    {
      "title": "New Satellite Defense System Unveiled",
      "url": "https://example.com/article",
      "authors": ["John Doe"],
      "is_defense": true,
      "confidence": 0.95,
      "post_type": "twitter",
      "post": "Breaking: New satellite defense tech... 🛡️ Read more: [URL] via @JohnDoe #Defense #Space"
    }
  ],
  "non_defense_articles": [
    {
      "title": "Commercial Space Tourism Advances",
      "url": "https://example.com/article2",
      "authors": ["Jane Smith"],
      "is_defense": false,
      "confidence": 0.85,
      "post_type": "linkedin",
      "post": "Exciting developments in space tourism... [Full LinkedIn post]"
    }
  ]
}
```

## Module Documentation

### `article_scraper.py`
Scrapes articles from Google News RSS and extracts full content using newspaper3k.

**Key methods**:
- `search_google_news()`: Finds articles via RSS feed
- `extract_article_content()`: Extracts full article text
- `scrape_articles()`: Main method to get articles with content

### `content_analyzer.py`
Analyzes article content using Anthropic's Claude to determine if it's defense-related.

**Key methods**:
- `is_defense_related()`: Analyzes a single article
- `analyze_articles()`: Batch analysis of multiple articles

### `google_docs_client.py`
Fetches content from Google Docs using the Google Docs API.

**Key methods**:
- `get_document_content()`: Retrieves any Google Doc
- `get_astroforge_story()`: Specifically fetches the AstroForge story

### `post_generator.py`
Generates platform-appropriate social media posts using Anthropic's Claude.

**Key methods**:
- `generate_twitter_post()`: Creates Twitter posts for defense articles
- `generate_linkedin_post()`: Creates LinkedIn posts for non-defense articles

### `main.py`
Orchestrates the entire workflow.

**Key class**: `SocialAgent`
- `fetch_astroforge_story()`: Loads the AstroForge story
- `process_articles()`: Main workflow execution
- `save_results()`: Saves to JSON
- `print_results()`: Displays results

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `GOOGLE_DOC_ID` | Google Doc ID for AstroForge story | Required |
| `GOOGLE_CREDENTIALS_FILE` | Path to Google OAuth credentials | `credentials.json` |
| `DEFAULT_KEYWORD` | Default search keyword | `space technology` |
| `MAX_ARTICLES` | Maximum articles to process | `10` |
| `TWITTER_MAX_LENGTH` | Max Twitter post length | `280` |
| `LINKEDIN_MAX_LENGTH` | Max LinkedIn post length | `3000` |

## Testing Individual Modules

Each module can be tested independently:

```bash
# Test article scraper
python article_scraper.py

# Test content analyzer
python content_analyzer.py

# Test Google Docs client
python google_docs_client.py

# Test post generator
python post_generator.py
```

## Troubleshooting

### "Anthropic API key is required"
- Ensure `ANTHROPIC_API_KEY` is set in your `.env` file
- Get an API key from [Anthropic Console](https://console.anthropic.com/)

### "Credentials file not found"
- Download OAuth 2.0 credentials from Google Cloud Console
- Save as `credentials.json` in the project directory
- See setup instructions above

### "No articles found"
- Try a different keyword
- Check your internet connection
- Google News may have rate limits

### Articles failing to extract
- Some websites block scrapers
- The tool will skip failed articles and continue with others

## Best Practices

1. **API Costs**: Anthropic API calls cost money. Start with small `--max-articles` values for testing
2. **Rate Limiting**: Don't scrape too many articles at once to avoid rate limits
3. **Google Docs**: Keep your AstroForge story doc updated
4. **Keywords**: Use specific keywords for better results (e.g., "asteroid mining" vs "space")

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing and article extraction
- `google-api-python-client`: Google Docs API
- `anthropic`: Anthropic API client for Claude
- `python-dotenv`: Environment variable management
- `feedparser`: RSS feed parsing
- `lxml`: XML/HTML parsing

## License

MIT License - feel free to modify and use as needed.

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions, please open a GitHub issue.
