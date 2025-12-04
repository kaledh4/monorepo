/**
 * PWA Manifest Template Generator
 * 
 * Generates PWA manifest files for each dashboard application with unique configurations.
 */

/**
 * Generate a PWA manifest for a specific app
 * @param {Object} config - Configuration object
 * @param {string} config.name - Full name of the application
 * @param {string} config.shortName - Short name for the application
 * @param {string} config.description - Description of the application
 * @param {string} config.startUrl - Start URL for the application
 * @param {string} config.themeColor - Theme color (hex)
 * @param {string} config.backgroundColor - Background color (hex)
 * @param {Array} config.icons - Array of icon objects
 * @returns {Object} The manifest object
 */
export function generateManifest(config) {
    const {
        name,
        shortName,
        description = '',
        startUrl = './',
        themeColor = '#1a1a1a',
        backgroundColor = '#ffffff',
        icons = [],
        display = 'standalone',
        orientation = 'any',
        id = startUrl,
        scope = './',
        lang = 'en-US',
        dir = 'ltr',
        categories = [],
        shortcuts = [],
        screenshots = [],
        display_override = ['window-controls-overlay', 'standalone', 'minimal-ui', 'browser'],
        launch_handler = { client_mode: 'auto' },
        prefer_related_applications = false,
        related_applications = []
    } = config;

    return {
        id,
        name,
        short_name: shortName,
        description,
        start_url: startUrl,
        display,
        display_override,
        background_color: backgroundColor,
        theme_color: themeColor,
        orientation,
        scope,
        lang,
        dir,
        categories,
        shortcuts,
        screenshots,
        launch_handler,
        prefer_related_applications,
        related_applications,
        icons: icons.length > 0 ? icons : [
            {
                src: 'icons/icon-192.png',
                sizes: '192x192',
                type: 'image/png',
                purpose: 'any maskable'
            },
            {
                src: 'icons/icon-512.png',
                sizes: '512x512',
                type: 'image/png',
                purpose: 'any maskable'
            }
        ]
    };
}

/**
 * Default manifest configurations for each dashboard
 */
export const DASHBOARD_MANIFESTS = {
    'the-frontier': {
        name: 'The Frontier - Silicon Frontier Watch',
        shortName: 'The Frontier',
        description: 'Track the global AI development race and scientific breakthroughs across multiple domains.',
        startUrl: '/daily-alpha-loop/the-frontier/',
        id: '/daily-alpha-loop/the-frontier/',
        scope: '/daily-alpha-loop/the-frontier/',
        themeColor: '#6366f1',
        backgroundColor: '#0f172a',
        categories: ['productivity', 'education', 'news'],
        display: 'standalone',
        orientation: 'portrait'
    },
    'the-shield': {
        name: 'The Shield - Market Fragility Monitor',
        shortName: 'The Shield',
        description: 'Real-time market crash detection and analysis system. Monitors global financial stress indicators, crypto markets, and macroeconomic data to predict market downturns.',
        startUrl: '/daily-alpha-loop/the-shield/',
        id: '/daily-alpha-loop/the-shield/',
        scope: '/daily-alpha-loop/the-shield/',
        themeColor: '#ef4444',
        backgroundColor: '#1a1a1a',
        categories: ['finance', 'productivity', 'utilities'],
        display: 'standalone',
        orientation: 'portrait'
    },
    'the-commander': {
        name: 'The Commander - Master Orchestrator',
        shortName: 'The Commander',
        description: 'Unified dashboard orchestration platform for managing multiple intelligence streams, including AI development, financial markets, and economic indicators.',
        startUrl: '/daily-alpha-loop/the-commander/',
        id: '/daily-alpha-loop/the-commander/',
        scope: '/daily-alpha-loop/the-commander/',
        themeColor: '#8b5cf6',
        backgroundColor: '#1e1b4b',
        categories: ['productivity', 'finance', 'utilities'],
        display: 'standalone',
        orientation: 'portrait'
    },
    'the-map': {
        name: 'The Map - Macro & TASI Trendsetter',
        shortName: 'The Map',
        description: 'Navigate global economic indicators, TASI markets, and crypto trends with AI-powered daily insights.',
        startUrl: '/daily-alpha-loop/the-map/',
        id: '/daily-alpha-loop/the-map/',
        scope: '/daily-alpha-loop/the-map/',
        themeColor: '#10b981',
        backgroundColor: '#064e3b',
        categories: ['finance', 'productivity', 'news'],
        display: 'standalone',
        orientation: 'portrait'
    },
    'the-strategy': {
        name: 'The Strategy - Unified Opportunity Radar',
        shortName: 'The Strategy',
        description: 'Market intelligence and analysis platform powered by AI. Get daily strategic insights and market analysis.',
        startUrl: '/daily-alpha-loop/the-strategy/',
        id: '/daily-alpha-loop/the-strategy/',
        scope: '/daily-alpha-loop/the-strategy/',
        themeColor: '#f59e0b',
        backgroundColor: '#78350f',
        categories: ['finance', 'productivity', 'news'],
        display: 'standalone',
        orientation: 'portrait'
    },
    'the-coin': {
        name: 'The Coin - Crypto Momentum Scanner',
        shortName: 'The Coin',
        description: 'Advanced market analytics and risk metrics. Data-driven crypto market intelligence with quantitative analysis.',
        startUrl: '/daily-alpha-loop/the-coin/',
        id: '/daily-alpha-loop/the-coin/',
        scope: '/daily-alpha-loop/the-coin/',
        themeColor: '#06b6d4',
        backgroundColor: '#164e63',
        categories: ['finance', 'productivity', 'utilities'],
        display: 'standalone',
        orientation: 'portrait'
    },
    'the-library': {
        name: 'The Library - Alpha-Clarity Archive',
        shortName: 'The Library',
        description: 'Archive of daily briefs, market insights, and strategic reports.',
        startUrl: '/daily-alpha-loop/the-library/',
        id: '/daily-alpha-loop/the-library/',
        scope: '/daily-alpha-loop/the-library/',
        themeColor: '#8b5cf6',
        backgroundColor: '#1e1b4b',
        categories: ['productivity', 'education', 'news'],
        display: 'standalone',
        orientation: 'portrait'
    }
};

/**
 * Get manifest configuration for a specific dashboard
 * @param {string} dashboardName - Name of the dashboard
 * @returns {Object} Manifest configuration
 */
export function getManifestForDashboard(dashboardName) {
    const config = DASHBOARD_MANIFESTS[dashboardName];
    if (!config) {
        throw new Error(`No manifest configuration found for dashboard: ${dashboardName}`);
    }
    return generateManifest(config);
}

export default {
    generateManifest,
    getManifestForDashboard,
    DASHBOARD_MANIFESTS
};
