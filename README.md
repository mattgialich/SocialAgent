# Social Agent

An intelligent web scraper that finds the latest articles for a given keyword, analyzes them for defense-related content, and generates appropriate social media posts based on the AstroForge story.

## Features

- **Multi-Source Article Search**: Deep search across multiple sources via web scraping
  - Google News Web (direct scraping) - high-quality, recent articles
  - Bing News Web (direct scraping) - enterprise news sources
  - Yahoo News (direct scraping) - diverse coverage
  - Google News RSS (always free) - additional source
  - **No API keys required for news search!**
  - Smart ranking by relevance and content quality
  - Returns top 5 most relevant articles with full content
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
- **Required:** Anthropic API key (for AI content analysis and post generation)
- **Required:** Public Google Doc with your AstroForge story
- **No other API keys needed!** Article search uses web scraping

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
   # Required
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GOOGLE_DOC_ID=your_google_doc_id_here

   # Configuration
   DEFAULT_KEYWORD=space technology
   MAX_ARTICLES=5
   ```

   **Get your Anthropic API key:**
   - Sign up at https://console.anthropic.com/
   - Navigate to API Keys section
   - Create a new API key

4. **Share your Google Doc publicly** (for AstroForge story)

   a. Open your Google Doc with the AstroForge story

   b. Click "Share" button (top right)

   c. Click "Change to anyone with the link"

   d. Set to "Viewer" access

   e. Copy the document ID from the URL:
      - URL format: `https://docs.google.com/document/d/{DOCUMENT_ID}/edit`
      - Example ID: `1CB3rXg8Wk3fGc3mdXBI8H0rFGv7V_qthiomozUzxmV0`

   f. Add the ID to your `.env` file:
      ```
      GOOGLE_DOC_ID=your_document_id_here
      ```

   **No API keys or OAuth needed!** Just make the doc publicly viewable.

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

### Web Viewer (New!)

**View your results in a beautiful web interface!**

After running the scraper, launch the web viewer to see your results in an easy-to-read format:

```bash
python web_viewer.py
```

Then open your browser to: **http://localhost:5000**

The web viewer displays:
- 📊 Statistics dashboard (articles processed, defense vs non-defense)
- 🛡️ Defense articles with Twitter posts
- 🌐 Non-defense articles with LinkedIn posts
- 🎯 Confidence scores with color coding
- 💭 AI reasoning for each classification
- 📰 Direct links to original articles
- 🎨 Clean, modern interface that works on mobile and desktop

**Auto-refresh:** The viewer reads from `results.json`, so just run the scraper again and refresh the page to see new results!

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

### `multi_source_finder.py` (Primary)
**New!** Intelligent multi-source article finder that searches across multiple platforms via web scraping:
- Scrapes Google News Web, Bing News Web, Yahoo News, and Google News RSS simultaneously
- **No API keys required!** All searches use direct web scraping
- Ranks articles by relevance, quality, and content availability
- Deduplicates results
- Extracts full article content with multiple strategies
- Returns top N most relevant articles with actual content

**Key methods**:
- `find_top_articles()`: Main method - returns top N ranked articles
- `search_google_news_web()`: Scrape Google News web results
- `search_bing_news_web()`: Scrape Bing News web results
- `search_yahoo_news()`: Scrape Yahoo News search results
- `search_google_news_rss()`: Parse Google News RSS feed
- `extract_full_content()`: Enhanced content extraction
- `rank_articles()`: Intelligent relevance ranking

### `article_scraper.py` (Fallback)
Scrapes articles from Google News RSS - used as fallback if multi-source fails.

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
| `ANTHROPIC_API_KEY` | Anthropic API key for AI analysis and post generation | Required |
| `GOOGLE_DOC_ID` | Google Doc ID for AstroForge story (must be publicly shared) | Required |
| `DEFAULT_KEYWORD` | Default search keyword | `space technology` |
| `MAX_ARTICLES` | Maximum articles to process (returns top N ranked) | `5` |
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

### "Could not fetch document"
- Make sure your Google Doc is shared publicly ("Anyone with the link can view")
- Check that the GOOGLE_DOC_ID in .env is correct
- Verify the document ID from the URL

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
- `anthropic`: Anthropic API client for Claude
- `python-dotenv`: Environment variable management
- `lxml`: XML/HTML parsing

## License

MIT License - feel free to modify and use as needed.

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions, please open a GitHub issue.
