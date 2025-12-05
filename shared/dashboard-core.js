/**
 * SHARED DASHBOARD CORE
 * Renders the unified theme for all dashboards.
 * Relies on navigation.js for loadDashboardData and renderNavigation.
 */

function renderHeader(data) {
    const header = document.querySelector('.header');
    if (!header) return;

    // Find the dashboard config to get the icon
    // We assume DASHBOARDS is available from navigation.js
    const dashConfig = typeof DASHBOARDS !== 'undefined'
        ? DASHBOARDS.find(d => d.id === (window.DASHBOARD_NAME || data.dashboard))
        : null;

    const iconHtml = dashConfig && dashConfig.icon
        ? `<img src="${dashConfig.icon}" alt="${data.name}" style="width: 48px; height: 48px; vertical-align: middle; margin-right: 10px;">`
        : '';

    header.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            ${iconHtml}
            <h1 style="margin: 0;">${data.name}</h1>
        </div>
        <p style="font-size: 1.4rem; color: #90cdf4; font-weight: 600; margin-bottom: 10px;">${data.role}</p>
        <p style="max-width: 800px; margin: 0 auto; color: #cbd5e0;">${data.mission}</p>
        <div class="timestamp">Updated: ${data.last_update || data.timestamp || 'Just now'}</div>
    `;
}

function renderScoring(scoring) {
    if (!scoring) return '';

    const getScale = (key, value) => {
        const k = key.toLowerCase();
        if (k.includes('rate') || k.includes('percent') || k === 'risk_level') return '/ 100';
        if (k === 'confidence' || k === 'uncertainty') return ''; // Usually 0-1
        return '/ 10';
    };

    return `
        <div class="content-card">
            <h2><img src="../static/icons/icons8-strategy-48.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Core Metrics</h2>
            <div class="data-grid">
                ${Object.entries(scoring).map(([key, value]) => `
                    <div class="data-section">
                        <h3>${key.replace(/_/g, ' ').toUpperCase()}</h3>
                        <div class="data-value" style="color: #63b3ed;">
                            ${value} <span style="font-size: 0.8rem; color: #718096;">${getScale(key, value)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderDataSources(sources) {
    if (!sources || sources.length === 0) return '';

    return `
        <div class="content-card" style="margin-top: 20px;">
            <h2><img src="../static/icons/icons8-map-48.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Data Sources</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                ${sources.map(source => `
                    <span class="source-badge">${source.split('/').pop()}</span>
                `).join('')}
            </div>
        </div>
    `;
}

function renderAIAnalysis(analysis) {
    return `
        <div class="content-card" style="margin-top: 20px; border-color: #48bb78;">
            <h2 style="color: #48bb78; border-color: #48bb78;"><img src="../static/icons/icons8-ai-48.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> AI Analysis</h2>
            <div class="data-text" style="font-size: 1.2rem; white-space: pre-line;">
                ${analysis || 'Analysis temporarily unavailable. The system is gathering more data.'}
            </div>
        </div>
    `;
}

function renderMorningBrief(brief) {
    if (!brief) return '';

    const getWeatherIcon = (weather) => {
        const w = weather.toLowerCase();
        if (w.includes('storm')) return '⛈️';
        if (w.includes('cloud')) return '☁️';
        if (w.includes('sun') || w.includes('clear')) return '☀️';
        if (w.includes('fog')) return '🌫️';
        if (w.includes('volat')) return '⚡';
        if (w.includes('rain')) return '🌧️';
        return '🌡️';
    };

    return `
        <div class="content-card">
            <div class="weather-badge" style="text-align: center; font-size: 1.5rem; display: flex; align-items: center; justify-content: center; gap: 10px;">
                <span>Weather: ${brief.weather_of_the_day}</span>
                <span style="font-size: 2rem;">${getWeatherIcon(brief.weather_of_the_day)}</span>
            </div>
            
            <div class="data-grid" style="margin-top: 20px;">
                <div class="data-section">
                    <h3>TOP SIGNAL</h3>
                    <div class="data-value" style="font-size: 1.2rem; text-align: left;">${brief.top_signal}</div>
                </div>
                <div class="data-section">
                    <h3>ACTION STANCE</h3>
                    <div class="stance" style="text-align: center;">${brief.action_stance}</div>
                </div>
            </div>

            <div class="summary-box" style="margin-top: 20px; text-align: left;">
                <h3 style="color: #90cdf4; margin-bottom: 10px;">Why It Matters</h3>
                <p>${brief.why_it_matters}</p>
            </div>

            <div class="data-section" style="margin-top: 20px;">
                <h3>Cross-Dashboard Convergence</h3>
                <p class="data-text">${brief.cross_dashboard_convergence}</p>
            </div>

            <div class="data-section" style="margin-top: 20px;">
                <h3>The Commander's Summary</h3>
                <p class="data-text" style="font-style: italic;">"${brief.summary_sentence}"</p>
            </div>
        </div>
    `;
}

async function initDashboard(dashboardName) {
    const data = await loadDashboardData(dashboardName);

    // Render Navigation (assuming navigation.js is loaded)
    if (window.renderNavigation) {
        document.getElementById('nav').innerHTML = window.renderNavigation(dashboardName);
    }

    if (!data) {
        document.getElementById('content').innerHTML = `
            <div class="content-card">
                <h2>Loading Data...</h2>
                <p>Please wait while we fetch the latest intelligence.</p>
            </div>
        `;
        return;
    }

    renderHeader(data);

    const contentEl = document.getElementById('content');

    if (dashboardName === 'the-commander') {
        contentEl.innerHTML = renderMorningBrief(data.morning_brief);
    } else {
        let html = '';

        // 1. Scoring Metrics
        html += renderScoring(data.scoring);

        // 2. Specific Dashboard Data (Custom rendering can be added here if needed, 
        // but for now we stick to the unified structure requested: Scoring + AI Analysis)

        // 3. AI Analysis (The main difference)
        html += renderAIAnalysis(data.ai_analysis);

        // 4. Data Sources
        html += renderDataSources(data.data_sources);

        contentEl.innerHTML = html;
    }
}

// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// Auto-initialize if dashboard name is provided in global scope
if (window.DASHBOARD_NAME) {
    document.addEventListener('DOMContentLoaded', () => {
        initDashboard(window.DASHBOARD_NAME);
        // Refresh every 5 minutes
        setInterval(() => initDashboard(window.DASHBOARD_NAME), 5 * 60 * 1000);
    });
}

// PWA Install Logic
let deferredPrompt;
const installBtn = document.getElementById('install-app-btn');

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;
    // Update UI to notify the user they can add to home screen
    if (installBtn) {
        installBtn.style.display = 'block';

        installBtn.addEventListener('click', (e) => {
            // Hide our user interface that shows our A2HS button
            installBtn.style.display = 'none';
            // Show the prompt
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the A2HS prompt');
                } else {
                    console.log('User dismissed the A2HS prompt');
                }
                deferredPrompt = null;
            });
        });
    }
});
