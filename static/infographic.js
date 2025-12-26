// Fetch and display infographic data
document.addEventListener('DOMContentLoaded', function() {
    fetchInfographicData();
    updateTimestamp();
});

function fetchInfographicData() {
    fetch('/api/infographic-data')
        .then(response => response.json())
        .then(data => {
            displayStats(data);
            displaySourceChart(data.source_counts);
            displayKeywordChart(data.word_frequency);
            displaySourceCards(data.source_counts);
            displayModernWordCloud(data.word_frequency);
        })
        .catch(error => {
            console.error('Error fetching infographic data:', error);
        });
}

function displayStats(data) {
    document.getElementById('total-stories').textContent = data.total_stories;
    document.getElementById('total-sources').textContent = Object.keys(data.source_counts).length;
}

function displaySourceChart(sourceCounts) {
    const ctx = document.getElementById('sourceChart').getContext('2d');
    
    const labels = Object.keys(sourceCounts);
    const data = Object.values(sourceCounts);
    
    // Generate vibrant colors
    const colors = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b',
        '#fa709a', '#feca57', '#ff9ff3', '#54a0ff', '#48dbfb'
    ];
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: '#fff',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: { size: 13, weight: 'bold' },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            }
        }
    });
}

function displayKeywordChart(wordFrequency) {
    const ctx = document.getElementById('keywordChart').getContext('2d');
    
    const words = Object.keys(wordFrequency).slice(0, 8);
    const frequencies = Object.values(wordFrequency).slice(0, 8);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: words,
            datasets: [{
                label: 'Mentions',
                data: frequencies,
                backgroundColor: 'rgba(102, 126, 234, 0.7)',
                borderColor: '#667eea',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function displaySourceCards(sourceCounts) {
    const container = document.getElementById('sourceCards');
    container.innerHTML = '';
    
    const entries = Object.entries(sourceCounts).sort((a, b) => b[1] - a[1]);
    const maxCount = Math.max(...entries.map(e => e[1]));
    
    entries.forEach(([source, count]) => {
        const percentage = (count / maxCount) * 100;
        
        const card = document.createElement('div');
        card.className = 'source-card';
        card.innerHTML = `
            <p class="source-card-name">${source}</p>
            <p class="source-card-count">${count}</p>
            <div class="source-card-bar">
                <div class="source-card-bar-fill" style="width: ${percentage}%"></div>
            </div>
        `;
        container.appendChild(card);
    });
}

function displayModernWordCloud(wordFrequency) {
    const cloudContainer = document.getElementById('wordCloud');
    cloudContainer.innerHTML = '';
    
    const words = Object.entries(wordFrequency);
    const maxFreq = Math.max(...words.map(w => w[1]));
    const minFreq = Math.min(...words.map(w => w[1]));
    
    words.forEach(([word, freq]) => {
        const normalized = (freq - minFreq) / (maxFreq - minFreq);
        let sizeClass = 'word-tag-sm';
        
        if (normalized > 0.75) {
            sizeClass = 'word-tag-xl';
        } else if (normalized > 0.5) {
            sizeClass = 'word-tag-lg';
        } else if (normalized > 0.25) {
            sizeClass = 'word-tag-md';
        }
        
        const wordElement = document.createElement('span');
        wordElement.className = `word-tag ${sizeClass}`;
        wordElement.textContent = word;
        cloudContainer.appendChild(wordElement);
    });
}

function updateTimestamp() {
    const timestamp = document.getElementById('timestamp');
    const now = new Date();
    timestamp.textContent = now.toLocaleString();
}
