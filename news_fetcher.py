import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai
import os

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
    
    def get_summary_from_gemini(self, title, content):
        """Generate a summary using Gemini API"""
        if not GEMINI_API_KEY:
            # Fallback if API key not set
            return content[:300] + "..." if len(content) > 300 else content
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""Summarize the following news article in 2-3 paragraphs. Be concise and informative.

Title: {title}

Content: {content}

Summary:"""
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating summary with Gemini: {str(e)}")
            # Fallback to using the original content
            return content[:300] + "..." if len(content) > 300 else content
    
    def get_top_stories(self, limit=10):
        """Fetch top stories from multiple sources with max 2 per source"""
        all_stories = []
        
        for source_name, rss_url in self.sources.items():
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:2]:  # Get max 2 per source
                    # Get title and summary/description
                    title = entry.get('title', 'No title')
                    summary = entry.get('summary', '')
                    
                    # If summary is empty, try to get description
                    if not summary:
                        summary = entry.get('description', '')
                    
                    # Clean up HTML tags from summary if present
                    if summary:
                        summary = BeautifulSoup(summary, 'html.parser').get_text()
                    
                    # Generate summary using Gemini
                    if summary:
                        full_summary = self.get_summary_from_gemini(title, summary)
                    else:
                        full_summary = f"No content available for this story. Please visit the source for more information."
                    
                    story = {
                        'title': title,
                        'link': entry.get('link', '#'),
                        'source': source_name,
                        'published': entry.get('published', ''),
                        'summary': full_summary
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
