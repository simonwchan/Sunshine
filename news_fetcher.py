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

# Mock summary mode (set MOCK_SUMMARY=1 or true to enable)
MOCK_SUMMARY = os.getenv('MOCK_SUMMARY', '').lower() in ('1', 'true', 'yes')

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
        # If mock mode enabled, generate a local mock summary and avoid external calls
        if MOCK_SUMMARY:
            return self.generate_mock_summary(title, content, target_words=1000)
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

    def generate_mock_summary(self, title, content, target_words=1000):
        """Create a mock, human-readable summary approximately target_words long.

        This avoids calling external APIs when MOCK_SUMMARY is enabled. The function
        expands and restructures the provided content to produce a longer summary.
        """
        # Base pieces: title and content words
        words = []
        if title:
            words.extend(title.split())
        content_words = content.split()
        # Use content as primary material; if short, repeat with transitions
        if not content_words:
            filler = (title or "News summary")
            content_words = (filler + ' ') * 200

        # Build paragraphs with gentle transitions until target reached
        summary_words = []
        para_count = 0
        i = 0
        while len(summary_words) < target_words:
            para_count += 1
            # Take a slice of content words
            slice_len = min( max(80, target_words // 6), len(content_words) )
            start = (i * slice_len) % len(content_words)
            chunk = content_words[start:start+slice_len]
            if not chunk:
                chunk = content_words[:slice_len]

            # Add a leading sentence for the paragraph
            lead = []
            if para_count == 1:
                lead = [f"Overview: {title}."]
            else:
                lead = ["Further context:"]

            para = ' '.join(lead + chunk)
            # Ensure paragraph ends in a period
            if not para.endswith('.'):
                para = para.rstrip() + '.'

            # Append paragraph words
            summary_words.extend(para.split())
            # Add a transition sentence occasionally
            if len(summary_words) < target_words:
                transition = "This development is significant because it highlights broader trends and implications in current affairs."
                summary_words.extend(transition.split())

            i += 1

            # Safety: if we've looped too many times, break
            if para_count > 20:
                break

        # Trim to target and join into paragraphs of ~120 words
        summary_words = summary_words[:target_words]
        # Build paragraphs
        paras = []
        w = summary_words
        psize = 120
        for j in range(0, len(w), psize):
            paras.append(' '.join(w[j:j+psize]).strip())

        return '\n\n'.join(paras)
    
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
