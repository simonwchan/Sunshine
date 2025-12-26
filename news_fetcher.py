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

# (no mock mode) configure normally from environment

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
        # No mock mode: attempt to call Gemini if key present, otherwise fallback
        if not GEMINI_API_KEY:
            # Fallback if API key not set: return up to ~8000 chars (~1000 words)
            return content[:8000] + "..." if len(content) > 8000 else content
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""Summarize the following news article in approximately 1000 words (aim for a comprehensive, informative summary — roughly 3–6 paragraphs). Include key facts, relevant context, and explain the significance of the story. Use a clear, neutral tone.

Title: {title}

Content: {content}

Summary (about 1000 words):"""
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating summary with Gemini: {str(e)}")
            # Fallback to using the original content
            return content[:8000] + "..." if len(content) > 8000 else content

    
    
    def get_top_stories(self, limit=10):
        """Fetch top stories from multiple sources with max 2 per source"""
        all_stories = []
        
        for source_name, rss_url in self.sources.items():
            try:
                feed = feedparser.parse(rss_url)
                # Collect up to 2 valid entries per source, but only try up to 3 entries per source
                count_for_source = 0
                attempts = 0
                for entry in feed.entries:
                    if count_for_source >= 2 or attempts >= 3:
                        break

                    attempts += 1

                    # Get title and summary/description
                    title = entry.get('title', 'No title')
                    summary = entry.get('summary', '')

                    # If summary is empty, try to get description
                    if not summary:
                        summary = entry.get('description', '')

                    # Clean up HTML tags from summary if present
                    if summary:
                        summary = BeautifulSoup(summary, 'html.parser').get_text().strip()

                    # Skip entries with no usable content
                    if not summary:
                        continue

                    # Keep the cleaned summary/content for the story
                    story = {
                        'title': title,
                        'link': entry.get('link', '#'),
                        'source': source_name,
                        'published': entry.get('published', ''),
                        'summary': summary
                    }
                    all_stories.append(story)
                    count_for_source += 1
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
        
        top_stories = all_stories[:limit]

        # Build a combined text from the top stories to generate a single summary
        combined_parts = []
        for s in top_stories:
            part = f"Title: {s.get('title','')}\nContent: {s.get('summary','')}"
            combined_parts.append(part)

        combined_text = "\n\n".join(combined_parts)

        # Generate a single combined summary for all stories
        combined_summary = self.get_summary_from_gemini("Daily News Summary", combined_text)

        return {"stories": top_stories, "summary": combined_summary}
