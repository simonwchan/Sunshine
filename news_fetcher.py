import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class NewsAggregator:
    def __init__(self):
        self.sources = {
            'BBC': 'http://feeds.bbc.co.uk/news/rss.xml',
            'CNN': 'http://rss.cnn.com/rss/cnn_topstories.rss',
            'Reuters': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&output=rss',
            'The Guardian': 'https://www.theguardian.com/world/rss',
            'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
            'DW': 'https://www.dw.com/en/xml/feed/rss/en',
            'France24': 'https://www.france24.com/en/rss',
            'BBC World': 'https://feeds.bbc.co.uk/news/world/rss.xml'
        }
    
    def get_top_stories(self, limit=10):
        """Fetch top stories from multiple sources with max 2 per source"""
        all_stories = []
        
        for source_name, rss_url in self.sources.items():
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:2]:  # Get max 2 per source
                    story = {
                        'title': entry.get('title', 'No title'),
                        'link': entry.get('link', '#'),
                        'source': source_name,
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', '')[:200]  # First 200 chars
                    }
                    all_stories.append(story)
            except Exception as e:
                print(f"Error fetching from {source_name}: {str(e)}")
        
        # Sort by publication date and get top N
        try:
            all_stories = sorted(
                all_stories, 
                key=lambda x: datetime.strptime(x['published'], '%a, %d %b %Y %H:%M:%S %z') if x['published'] else datetime.min,
                reverse=True
            )
        except:
            pass  # If sorting fails, keep original order
        
        return all_stories[:limit]
