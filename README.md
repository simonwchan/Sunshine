# Sunshine - Daily Overview Web App

A Python web application that aggregates top news stories from CNN and BBC.

## Features

- ✨ Fetches top 5 news stories from BBC and CNN
- 🔗 Direct links to full articles
- 🎨 Modern, responsive web interface
- ⚡ Fast and lightweight

## Requirements

- Python 3.7+
- Flask
- feedparser
- requests
- beautifulsoup4

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

Then open your browser and navigate to `http://localhost:5000`

## Project Structure

```
Sunshine/
├── app.py              # Flask application entry point
├── news_fetcher.py     # News aggregation logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Web UI
└── static/
    ├── style.css       # Styling
    └── script.js       # Frontend JavaScript
```

## Future Features

- Mobile app version
- Additional news sources
- Weather section
- Stock market updates
- Calendar integration
