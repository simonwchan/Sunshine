// Fetch and display news on page load
document.addEventListener('DOMContentLoaded', function() {
    fetchNews();
    updateTimestamp();
});

function fetchNews() {
    const container = document.getElementById('news-container');
    fetch('/api/news')
        .then(response => response.json())
        .then(data => {
            container.innerHTML = '';

            // Support both old format (array) and new format ({stories, summary})
            const stories = data.stories || data;
            const combinedSummary = data.summary || '';

            if (!stories || stories.length === 0) {
                container.innerHTML = '<p class="loading">No news stories found</p>';
                // still update summary box
                const sumElEmpty = document.getElementById('combined-summary');
                if (sumElEmpty) sumElEmpty.textContent = combinedSummary || 'No summary available.';
                return;
            }

            stories.forEach((story, index) => {
                const card = createNewsCard(story, index + 1);
                container.appendChild(card);
            });

            // Render combined summary at the bottom
            const summaryEl = document.getElementById('combined-summary');
            if (summaryEl) summaryEl.textContent = combinedSummary || 'No summary available.';
        })
        .catch(error => {
            console.error('Error fetching news:', error);
            container.innerHTML = '<p class="loading">Error loading news. Please try again later.</p>';
        });
}

function createNewsCard(story, index) {
    const card = document.createElement('div');
    card.className = 'news-card';
    
    card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px;">
            <span class="news-card-source">${story.source}</span>
        </div>
        <h3 class="news-card-title"><a href="${story.link}" target="_blank">${story.title}</a></h3>
    `;
    
    return card;
}

function updateTimestamp() {
    const timestamp = document.getElementById('timestamp');
    const now = new Date();
    timestamp.textContent = now.toLocaleString();
}
