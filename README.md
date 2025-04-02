# AI-Powered News Agent

An intelligent news aggregation and publishing system that scrapes articles from various sources, processes them using AI, and publishes them to a Telegram channel.

## Tech Stack

### Core Technologies
- **Python 3.8+**: Main programming language
- **SQLAlchemy**: Database ORM
- **SQLite**: Database storage
- **asyncio**: Asynchronous programming
- **schedule**: Task scheduling

### Web Scraping
- **newspaper3k**: Article extraction
- **beautifulsoup4**: HTML parsing
- **feedparser**: RSS feed parsing
- **requests**: HTTP requests
- **lxml**: HTML processing

### Natural Language Processing
- **transformers**: Hugging Face transformers for text processing
- **nltk**: Natural Language Toolkit
- **torch**: PyTorch for deep learning
- **pandas**: Data manipulation
- **numpy**: Numerical computing

### Publishing
- **python-telegram-bot**: Telegram API integration
- **aiohttp**: Asynchronous HTTP client

## Project Structure

```
newsnova/
├── src/
│   ├── database/         # Database models and operations
│   ├── nlp/             # Natural Language Processing components
│   ├── publisher/       # Publishing and scheduling
│   ├── scraper/        # Web scraping components
│   └── utils/          # Utility functions
├── config/             # Configuration files
├── logs/              # Application logs
├── tests/             # Test files
├── main.py            # Main application entry point
├── requirements.txt   # Python dependencies
└── .env              # Environment variables
```

## Components

### 1. Database Layer
- **models.py**: SQLAlchemy models for articles, sources, and publishing queue
- **operations.py**: Database operations and queries

### 2. Scraping Layer
- **rss_parser.py**: RSS feed parsing and article extraction
- **web_scraper.py**: Web page scraping and article extraction

### 3. NLP Layer
- **summarizer.py**: Article summarization using transformers
- **classifier.py**: Topic classification using zero-shot learning

### 4. Publishing Layer
- **telegram_publisher.py**: Telegram channel publishing
- **scheduler.py**: Article publishing scheduling

## Workflow

1. **Article Collection**
   - RSS feeds are parsed using `feedparser`
   - Web pages are scraped using `newspaper3k`
   - Articles are extracted and normalized

2. **Article Processing**
   - Content is cleaned and normalized
   - Articles are summarized using transformer models
   - Topics are classified using zero-shot learning
   - Duplicates are detected and filtered

3. **Queue Management**
   - Articles are added to a priority queue
   - Publishing schedule is managed
   - Batch processing is handled

4. **Publication**
   - Articles are published to Telegram channel
   - Media content is handled
   - Error handling and retries are managed

## Configuration

The application is configured through environment variables in `.env`:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id

# Database Configuration
DATABASE_URL=sqlite:///news.db

# Scraping Configuration
SCRAPING_INTERVAL=300
MAX_ARTICLES_PER_SOURCE=10
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36

# NLP Configuration
SUMMARIZATION_MODEL=facebook/bart-large-cnn
CLASSIFICATION_MODEL=facebook/bart-large-mnli
MAX_SUMMARY_LENGTH=150

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=news_agent.log

# Publishing Configuration
DEFAULT_PUBLISHING_INTERVAL=600
BATCH_PUBLISH_SIZE=5
MAX_QUEUE_SIZE=100
```

## Usage

1. **Setup**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/newsnova.git
   cd newsnova

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows

   # Install dependencies
   pip install -r requirements.txt

   # Copy environment file
   cp .env.example .env
   ```

2. **Configure**
   - Edit `.env` with your settings
   - Add your Telegram bot token and channel ID
   - Configure news sources

3. **Run**
   ```bash
   # Initialize database
   python main.py --init-db

   # Add a new source
   python main.py --add-source --url https://example.com/feed --type rss --category technology

   # Start the application
   python main.py
   ```

## Features

- **Intelligent Summarization**: Uses transformer models to generate concise summaries
- **Topic Classification**: Automatically categorizes articles using zero-shot learning
- **Batch Publishing**: Publishes articles in configurable batches
- **Scheduling**: Flexible publishing schedule with priority queue
- **Media Support**: Handles images and rich content
- **Error Handling**: Robust error handling and retry mechanisms
- **Logging**: Comprehensive logging system

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 