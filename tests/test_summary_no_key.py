import os
# Ensure GEMINI_API_KEY is not set for this test
os.environ.pop('GEMINI_API_KEY', None)
from news_fetcher import NewsAggregator

agg = NewsAggregator()
text = "This is a small test article. " * 200
print('Running local fallback summary (no key)')
print(agg.get_summary_from_gemini('Test Title', text)[:1000])
