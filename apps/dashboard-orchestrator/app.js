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

    // Update overview metrics if available
    if (data.overview) {
        // We could update header info here if needed
        console.log('Dashboard Overview:', data.overview);
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
