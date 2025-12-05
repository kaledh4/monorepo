// SHARED NAVIGATION COMPONENT - Used by all dashboards

const DASHBOARDS = [
    { id: 'the-commander', name: 'The Commander', mission: 'Morning Brief', icon: '../static/icons/icons8-commander-of-the-canadian-navy-48.png' },
    { id: 'the-shield', name: 'The Shield', mission: 'Risk Monitor', icon: '../static/icons/icons8-shield-48.png' },
    { id: 'the-coin', name: 'The Coin', mission: 'Crypto Scanner', icon: '../static/icons/icons8-coin-64.png' },
    { id: 'the-map', name: 'The Map', mission: 'Macro Trends', icon: '../static/icons/icons8-map-48.png' },
    { id: 'the-frontier', name: 'The Frontier', mission: 'AI Breakthroughs', icon: '../static/icons/icons8-ai-48.png' },
    { id: 'the-strategy', name: 'The Strategy', mission: 'Opportunity Radar', icon: '../static/icons/icons8-strategy-48.png' },
    { id: 'the-library', name: 'The Library', mission: 'Knowledge Archive', icon: '../static/icons/icons8-library-48.png' }
];

function renderNavigation(currentDashboard) {
    const navHTML = DASHBOARDS.map(dash => {
        const isActive = dash.id === currentDashboard;
        const url = dash.id === 'the-commander' ? '../the-commander/' : `../${dash.id}/`;

        return `
      <a href="${url}" class="nav-card ${isActive ? 'active' : ''}">
        <img src="${dash.icon}" alt="${dash.name}" class="nav-icon" style="width: 32px; height: 32px; margin-bottom: 8px;">
        <h3>${dash.name}</h3>
        <p>${dash.mission}</p>
      </a>
    `;
    }).join('');

    return `<div class="dashboard-nav">${navHTML}</div>`;
}

function getSourceBadge(dashboardId) {
    const dash = DASHBOARDS.find(d => d.id === dashboardId);
    if (!dash) return '';

    const url = dashboardId === 'the-commander' ? '../the-commander/' : `../${dashboardId}/`;

    return `<a href="${url}" class="source-badge" title="View ${dash.name}">
        <img src="${dash.icon}" alt="${dash.name}" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 4px;">
        ${dash.name}
    </a>`;
}

function formatTimestamp(timestamp) {
    if (!timestamp) return 'Loading...';
    const date = new Date(timestamp);
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'UTC'
    };
    return date.toLocaleDateString('en-US', options) + ' UTC';
}

async function loadDashboardData(dashboardId) {
    const paths = [
        // 1. GitHub Pages absolute path (Most reliable for production)
        `/daily-alpha-loop/data/${dashboardId}/latest.json`,
        // 2. Standard relative path (Works for local server and some deployments)
        `../data/${dashboardId}/latest.json`,
        // 3. Full URL fallback (If relative paths fail)
        `https://kaledh4.github.io/daily-alpha-loop/data/${dashboardId}/latest.json`,
        // 4. Deep relative path (Fallback for nested structures)
        `../../data/${dashboardId}/latest.json`,
        // 5. Local data path (Fallback for dev)
        `./data/latest.json`
    ];

    console.log(`[Navigation] Loading data for ${dashboardId}...`);

    for (const path of paths) {
        try {
            console.log(`[Navigation] Trying path: ${path}`);
            const response = await fetch(`${path}?t=${Date.now()}`);
            if (response.ok) {
                const data = await response.json();
                console.log(`[Navigation] Successfully loaded data from ${path}`);
                return data;
            } else {
                console.warn(`[Navigation] Failed to load from ${path}: ${response.status} ${response.statusText}`);
            }
        } catch (e) {
            console.warn(`[Navigation] Error loading from ${path}:`, e);
        }
    }

    console.error(`[Navigation] All data paths failed for ${dashboardId}`);
    return null;
}
