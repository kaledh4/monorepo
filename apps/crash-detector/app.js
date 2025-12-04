// Crash Detector - Data Fetching and Rendering
// Service Worker registration is handled in index.html inline script

// PWA Install Prompt
let deferredPrompt;
const installBtn = document.getElementById('install-btn');

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) installBtn.style.display = 'block';
});

if (installBtn) {
    installBtn.addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            deferredPrompt = null;
            installBtn.style.display = 'none';
        }
    });
}

window.addEventListener('appinstalled', () => {
    console.log('PWA was installed');
    if (installBtn) installBtn.style.display = 'none';
});


// Fetch and Render Data
async function fetchData() {
    // Try multiple data paths for flexibility
    const dataPaths = [
        './data/latest.json',           // Local data folder
        './latest.json',                 // Same directory
        '../data/crash-detector/latest.json',  // GitHub Pages structure
        '../../data/crash-detector/latest.json' // Local dev structure
    ];

    let lastError = null;

    for (const dataPath of dataPaths) {
        try {
            const response = await fetch(`${dataPath}?t=${Date.now()}`);
            if (response.ok) {
                const data = await response.json();
                console.log(`Data loaded from: ${dataPath}`);
                renderDashboard(data);
                return;
            }
        } catch (error) {
            lastError = error;
            console.debug(`Path ${dataPath} failed, trying next...`);
        }
    }

    console.error('Error fetching data from all paths:', lastError);
    document.getElementById('last-updated').textContent = 'Error loading data. Please try again later.';
}


function renderDashboard(data) {
    // Update Header Info
    document.getElementById('last-updated').textContent = `Last Updated: ${data.last_update}`;
    document.getElementById('days-remaining').textContent = data.days_remaining;

    // Render Risk Assessment
    const riskEl = document.getElementById('risk-level');
    const riskScoreEl = document.getElementById('risk-score');
    const riskCard = document.getElementById('risk-card');

    if (data.risk_assessment) {
        riskEl.textContent = data.risk_assessment.level;
        riskScoreEl.textContent = data.risk_assessment.score;
        riskCard.style.borderLeft = `5px solid ${data.risk_assessment.color}`;
        riskEl.style.color = data.risk_assessment.color;
    }

    // Render Metrics
    const metricsContainer = document.getElementById('metrics-container');
    metricsContainer.innerHTML = '';

    data.metrics.forEach(metric => {
        const card = document.createElement('div');
        card.className = 'metric-card glass';

        let statusColor = '#28a745'; // Normal
        if (metric.signal.includes('CRITICAL')) statusColor = '#dc3545';
        else if (metric.signal.includes('HIGH')) statusColor = '#fd7e14';
        else if (metric.signal.includes('RISING')) statusColor = '#ffc107';

        card.innerHTML = `
            <h3>${metric.name}</h3>
            <div class="value">${metric.value}</div>
            <div class="signal" style="color: ${statusColor}">
                <span class="dot" style="background-color: ${statusColor}"></span>
                ${metric.signal}
            </div>
            ${metric.desc ? `<div class="desc" style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">${metric.desc}</div>` : ''}
            ${metric.volatility_24h ? `<div class="volatility">24h Volatility: ${metric.volatility_24h}</div>` : ''}
        `;
        metricsContainer.appendChild(card);
    });

    // Render AI Insights - Updated to use crash_analysis and news_summary
    if (data.ai_insights) {
        const crashAnalysisEl = document.getElementById('crash-analysis-content');
        const newsSummaryEl = document.getElementById('news-summary-content');

        if (crashAnalysisEl) crashAnalysisEl.innerHTML = data.ai_insights.crash_analysis || 'No data available.';
        if (newsSummaryEl) newsSummaryEl.innerHTML = data.ai_insights.news_summary || 'No data available.';
    }
}

// Initial Load
fetchData();
