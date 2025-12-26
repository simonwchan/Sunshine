from flask import Flask, render_template, jsonify
from news_fetcher import NewsAggregator
from collections import Counter
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/news')
def get_news():
    aggregator = NewsAggregator()
    news = aggregator.get_top_stories(limit=20)
    return jsonify(news)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
