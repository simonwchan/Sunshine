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
            
            if (data.length === 0) {
                container.innerHTML = '<p class="loading">No news stories found</p>';
                return;
            }
            
            data.forEach((story, index) => {
                const card = createNewsCard(story, index + 1);
                container.appendChild(card);
            });
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
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
            <span class="news-card-source">${story.source}</span>
        </div>
        <h3 class="news-card-title"><a href="${story.link}" target="_blank">${story.title}</a></h3>
        <p class="news-card-summary">${story.summary}</p>
    `;
    
    return card;
}

function updateTimestamp() {
    const timestamp = document.getElementById('timestamp');
    const now = new Date();
    timestamp.textContent = now.toLocaleString();
}
