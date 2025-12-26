import os
import sys

# Allow enabling mock summary mode via command-line flag before importing news_fetcher.
# Examples:
#   python app.py --mock
#   python app.py MOCK=1
for a in sys.argv[1:]:
    if a.lower() in ('--mock', '-m') or a.upper().startswith('MOCK='):
        os.environ['MOCK_SUMMARY'] = '1'
        break

from flask import Flask, render_template, jsonify
from news_fetcher import NewsAggregator
from collections import Counter
import re
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    aggregator = NewsAggregator()
    news = aggregator.get_top_stories(limit=20)
    # news may be the new structure {"stories": [...], "summary": "..."}
    stories = news.get('stories') if isinstance(news, dict) else news
    summary = news.get('summary') if isinstance(news, dict) else ''
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Title changes when running in mock mode
    app_title = 'Sunshine Mock' if os.getenv('MOCK_SUMMARY', '').lower() in ('1', 'true', 'yes') else '☀️ Sunshine'
    return render_template('index.html', stories=stories, summary=summary, timestamp=timestamp, app_title=app_title)

@app.route('/api/news')
def get_news():
    aggregator = NewsAggregator()
    news = aggregator.get_top_stories(limit=20)
    # `news` is a dict with `stories` and `summary`
    return jsonify(news)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
