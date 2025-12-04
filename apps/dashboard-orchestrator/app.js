// Dashboard Orchestrator Dynamic Data Loading
// Unified fetcher pattern for loading dashboard metrics

async function fetchDashboardData() {
    const dataPaths = [
        './data/latest.json',
        './latest.json',
        '../data/dashboard-orchestrator/latest.json',
        '../../data/dashboard-orchestrator/latest.json'
    ];

    let lastError = null;

    for (const dataPath of dataPaths) {
        try {
            const response = await fetch(`${dataPath}?t=${Date.now()}`);
            if (response.ok) {
                const data = await response.json();
                console.log(`Dashboard data loaded from: ${dataPath}`);
                return data;
            }
        } catch (error) {
            lastError = error;
            console.debug(`Path ${dataPath} failed, trying next...`);
        }
    }

    console.error('Error fetching dashboard data from all paths:', lastError);
    return null;
}

async function updateDashboard() {
    const data = await fetchDashboardData();

    if (!data) {
        console.error('Failed to load dashboard data');
        return;
    }

    // Update timestamp
    const timestampEl = document.querySelector('.timestamp');
    if (timestampEl && data.timestamp) {
        const date = new Date(data.timestamp);
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'UTC'
        };
        timestampEl.textContent = date.toLocaleDateString('en-US', options) + ' UTC';
    }

    // Update market overview
    if (data.overview) {
        const overviewEl = document.getElementById('market-overview');
        if (overviewEl) {
            const metrics = [
                { label: 'Bitcoin', value: data.overview.BTC, format: '$', decimals: 0 },
                { label: 'Ethereum', value: data.overview.ETH, format: '$', decimals: 0 },
                { label: 'S&P 500', value: data.overview.SP500, format: '', decimals: 2 },
                { label: 'DXY', value: data.overview.DXY, format: '', decimals: 2 },
                { label: 'Gold', value: data.overview.Gold, format: '$', decimals: 2 }
            ];

            overviewEl.innerHTML = metrics.map(m => `
                <div class="metric-card">
                    <div class="metric-label">${m.label}</div>
                    <div class="metric-value">${m.format}${Number(m.value).toLocaleString('en-US', { minimumFractionDigits: m.decimals, maximumFractionDigits: m.decimals })}</div>
                </div>
            `).join('');
        }
    }

    // Update dashboard status
    if (data.apps_status) {
        const statusEl = document.getElementById('dashboard-status');
        if (statusEl) {
            const statusGrid = statusEl.querySelector('.status-grid');
            if (statusGrid) {
                const statusItems = Object.entries(data.apps_status).map(([app, status]) => `
                    <div class="status-item">
                        <span class="status-indicator ${status}"></span>
                        <span class="status-name">${app}</span>
                        <span class="status-label">${status}</span>
                    </div>
                `).join('');
                statusGrid.innerHTML = statusItems;
            }
        }
    }
}

// Load data when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateDashboard);
} else {
    updateDashboard();
}

// Refresh data every 5 minutes
setInterval(updateDashboard, 5 * 60 * 1000);
