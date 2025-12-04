// ==========================================
// ECONOMIC COMPASS - INTERACTIVE FEATURES
// ==========================================

// ==========================================
// 1. TOOLTIP SYSTEM FOR EDUCATION
// ==========================================

const tooltipData = {
    'rsi': {
        title: 'RSI (Relative Strength Index)',
        content: 'Measures momentum on a scale of 0-100. Below 30 = Oversold (potential buy), Above 70 = Overbought (potential sell).',
        historicalNote: 'Buying during oversold periods historically yields positive returns 68% of the time.'
    },
    'fng': {
        title: 'Fear & Greed Index',
        content: 'Aggregates sentiment from volatility, market momentum, social media, and surveys. 0 = Extreme Fear, 100 = Extreme Greed.',
        historicalNote: 'Extreme Fear (0-25) has preceded an average 15% gain over the next 3 months historically.'
    },
    'yield': {
        title: '10-Year Treasury Yield',
        content: 'The interest rate on US government 10-year bonds. Rising yields often pressure risk assets like crypto.',
        historicalNote: 'When yields spike >4.5%, BTC typically consolidates for 2-4 weeks before resuming trend.'
    },
    'gold': {
        title: 'Gold (Safe Haven Asset)',
        content: 'Traditional store of value. When gold rises significantly, it often signals "risk-off" sentiment in markets.',
        historicalNote: 'BTC correlation with gold typically ranges from -0.2 to +0.5'
    },
    'sp500': {
        title: 'S&P 500 Index',
        content: 'Benchmark US stock index. Crypto often correlates with tech stocks and broader risk appetite.',
        historicalNote: 'BTC correlation with S&P 500 has averaged +0.65 in 2023-2024'
    },
    'tasi': {
        title: 'TASI (Tadawul All Share Index)',
        content: 'Saudi Arabia\'s main stock index. Represents Middle East market sentiment and oil-related flows.',
        historicalNote: 'Regional indicator for petrostate capital flows into crypto markets'
    },
    'gex': {
        title: 'CBOE Gamma Exposure (GEX)',
        content: 'Measures how much market makers must buy/sell to hedge options. High GEX dampens volatility, Low GEX amplifies it.',
        historicalNote: 'Negative GEX environments have led to 2-3x larger price swings historically'
    },
    'bullmarketband': {
        title: 'Bull Market Support Band',
        content: 'Combination of 20-week and 21-week exponential moving averages. Holding above = bullish structure intact.',
        historicalNote: 'Losing this level in previous cycles signaled -30% corrections'
    }
};

class TooltipManager {
    constructor() {
        this.activeTooltip = null;
        this.init();
    }

    init() {
        // Create tooltip container
        const tooltipEl = document.createElement('div');
        tooltipEl.id = 'custom-tooltip';
        tooltipEl.className = 'tooltip-popup hidden';
        document.body.appendChild(tooltipEl);

        // Add click listeners to all tooltip triggers
        this.attachTooltips();
    }

    attachTooltips() {
        // Add tooltip icons next to technical terms
        const termsToEnhance = {
            'RSI (14)': 'rsi',
            'Fear & Greed': 'fng',
            '10Y Yield': 'yield',
            'Gold': 'gold',
            'S&P 500': 'sp500',
            'TASI': 'tasi'
        };

        Object.entries(termsToEnhance).forEach(([term, key]) => {
            const elements = Array.from(document.querySelectorAll('span, h3')).filter(el =>
                el.textContent.trim() === term
            );

            elements.forEach(el => {
                if (!el.querySelector('.tooltip-icon')) {
                    const icon = document.createElement('span');
                    icon.className = 'tooltip-icon';
                    icon.innerHTML = ' ⓘ';
                    icon.dataset.tooltip = key;
                    icon.addEventListener('click', (e) => this.showTooltip(e, key));
                    el.appendChild(icon);
                }
            });
        });
    }

    showTooltip(event, key) {
        event.stopPropagation();
        const tooltip = document.getElementById('custom-tooltip');
        const data = tooltipData[key];

        if (!data) return;

        tooltip.innerHTML = `
            <div class="tooltip-header">
                <strong>${data.title}</strong>
                <button class="tooltip-close" onclick="tooltipManager.hideTooltip()">×</button>
            </div>
            <p class="tooltip-content">${data.content}</p>
            ${data.historicalNote ? `<p class="tooltip-historical">📊 ${data.historicalNote}</p>` : ''}
        `;

        // Position tooltip
        const rect = event.target.getBoundingClientRect();
        tooltip.style.top = `${rect.bottom + 10}px`;
        tooltip.style.left = `${Math.min(rect.left, window.innerWidth - 320)}px`;

        tooltip.classList.remove('hidden');
        this.activeTooltip = tooltip;

        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', this.closeOnOutsideClick.bind(this), { once: true });
        }, 100);
    }

    hideTooltip() {
        const tooltip = document.getElementById('custom-tooltip');
        tooltip.classList.add('hidden');
    }

    closeOnOutsideClick(event) {
        const tooltip = document.getElementById('custom-tooltip');
        if (!tooltip.contains(event.target)) {
            this.hideTooltip();
        }
    }
}

// ==========================================
// 2. SPARKLINE CHARTS (30-DAY MINI TRENDS)
// ==========================================

class SparklineManager {
    constructor() {
        this.canvas = null;
    }

    // Generate simple sparkline using canvas
    createSparkline(container, data, color = '#3b82f6') {
        const canvas = document.createElement('canvas');
        canvas.width = 60;
        canvas.height = 20;
        canvas.className = 'sparkline-chart';

        const ctx = canvas.getContext('2d');

        // Normalize data
        const max = Math.max(...data);
        const min = Math.min(...data);
        const range = max - min || 1;

        // Draw line
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();

        data.forEach((value, index) => {
            const x = (index / (data.length - 1)) * canvas.width;
            const y = canvas.height - ((value - min) / range) * canvas.height;

            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();

        // Add to container
        container.appendChild(canvas);
    }

    // Generate mock 30-day data (in production, fetch from API)
    generateMockData(currentValue, volatility = 0.05) {
        const data = [];
        let value = currentValue * 0.95; // Start slightly lower

        for (let i = 0; i < 30; i++) {
            value += (Math.random() - 0.48) * currentValue * volatility;
            data.push(value);
        }

        data[data.length - 1] = currentValue; // Ensure last value matches current
        return data;
    }

    addSparklines() {
        // Add sparklines to BTC price
        const btcPriceElement = document.querySelector('.trend-row:has(#price-label) .value');
        if (btcPriceElement && !btcPriceElement.querySelector('.sparkline-chart')) {
            const priceText = btcPriceElement.textContent.replace(/[$,]/g, '');
            const price = parseFloat(priceText);
            if (!isNaN(price)) {
                const sparklineContainer = document.createElement('span');
                sparklineContainer.className = 'sparkline-container';
                this.createSparkline(sparklineContainer, this.generateMockData(price, 0.03), '#3b82f6');
                btcPriceElement.appendChild(sparklineContainer);
            }
        }

        // Add sparklines to RSI
        const rsiElement = document.querySelector('.trend-row:has(#rsi-label) .value');
        if (rsiElement && !rsiElement.querySelector('.sparkline-chart')) {
            const rsiText = rsiElement.textContent;
            const rsi = parseFloat(rsiText);
            if (!isNaN(rsi)) {
                const sparklineContainer = document.createElement('span');
                sparklineContainer.className = 'sparkline-container';
                const color = rsi < 30 ? '#10b981' : rsi > 70 ? '#ef4444' : '#f59e0b';
                this.createSparkline(sparklineContainer, this.generateMockData(rsi, 0.1, 0, 100), color);
                rsiElement.appendChild(sparklineContainer);
            }
        }
    }
}

// ==========================================
// 3. INTERACTIVE GAUGE FOR FEAR & GREED
// ==========================================

class GaugeVisualizer {
    createGauge(value, container) {
        const gaugeHTML = `
            <svg class="gauge-svg" viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">
                <!-- Background arc -->
                <path d="M 20 100 A 80 80 0 0 1 180 100" 
                      fill="none" 
                      stroke="rgba(255,255,255,0.1)" 
                      stroke-width="20" 
                      stroke-linecap="round"/>
                
                <!-- Gradient definitions -->
                <defs>
                    <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#ef4444;stop-opacity:1" />
                        <stop offset="50%" style="stop-color:#f59e0b;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#10b981;stop-opacity:1" />
                    </linearGradient>
                </defs>
                
                <!-- Colored arc based on value -->
                <path d="M 20 100 A 80 80 0 0 1 180 100" 
                      fill="none" 
                      stroke="url(#gaugeGradient)" 
                      stroke-width="20" 
                      stroke-linecap="round"
                      stroke-dasharray="${(value / 100) * 251} 251"
                      class="gauge-fill"/>
                
                <!-- Needle -->
                <g transform="rotate(${-90 + (value / 100) * 180} 100 100)">
                    <line x1="100" y1="100" x2="100" y2="30" 
                          stroke="#ffffff" 
                          stroke-width="3" 
                          stroke-linecap="round"/>
                    <circle cx="100" cy="100" r="6" fill="#ffffff"/>
                </g>
                
                <!-- Value text -->
                <text x="100" y="95" text-anchor="middle" fill="#ffffff" font-size="32" font-weight="bold">
                    ${value}
                </text>
            </svg>
        `;

        container.innerHTML = gaugeHTML;
    }

    init() {
        const gaugeContainer = document.querySelector('.gauge-container');
        if (gaugeContainer) {
            const valueElement = gaugeContainer.querySelector('.gauge-value');
            if (valueElement) {
                const value = parseInt(valueElement.textContent);
                if (!isNaN(value)) {
                    // Keep the label but replace gauge-value with SVG
                    const label = gaugeContainer.querySelector('.gauge-label');
                    gaugeContainer.innerHTML = '';
                    this.createGauge(value, gaugeContainer);
                    if (label) {
                        gaugeContainer.appendChild(label);
                    }
                }
            }
        }
    }
}

// ==========================================
// 4. USER SENTIMENT POLL
// ==========================================

class SentimentPoll {
    constructor() {
        this.storageKey = 'economicCompass_userVote';
        this.votesKey = 'economicCompass_voteStats';
    }

    init() {
        const insightPanel = document.querySelector('.insight-panel');
        if (!insightPanel) return;

        const pollHTML = `
            <div class="sentiment-poll glass-panel-inner" id="sentiment-poll">
                <h3 class="poll-title">📊 Community Sentiment</h3>
                <p class="poll-question">The system says market is cautious. What do you think?</p>
                <div class="poll-buttons">
                    <button class="poll-btn poll-bullish" data-vote="bullish">
                        <span class="poll-icon">📈</span> Bullish
                    </button>
                    <button class="poll-btn poll-bearish" data-vote="bearish">
                        <span class="poll-icon">📉</span> Bearish
                    </button>
                </div>
                <div class="poll-results hidden" id="poll-results">
                    <div class="result-bar">
                        <div class="result-bullish" id="result-bullish-bar"></div>
                        <div class="result-bearish" id="result-bearish-bar"></div>
                    </div>
                    <div class="result-labels">
                        <span class="result-label">Bullish: <strong id="bullish-percent">0</strong>%</span>
                        <span class="result-label">Bearish: <strong id="bearish-percent">0</strong>%</span>
                    </div>
                    <p class="poll-note">Based on <span id="total-votes">0</span> votes</p>
                </div>
            </div>
        `;

        // Insert before the main content
        const insightContent = insightPanel.querySelector('.markdown-body');
        if (insightContent) {
            insightContent.insertAdjacentHTML('beforebegin', pollHTML);
            this.attachListeners();
            this.checkExistingVote();
        }
    }

    attachListeners() {
        const buttons = document.querySelectorAll('.poll-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const vote = e.currentTarget.dataset.vote;
                this.submitVote(vote);
            });
        });
    }

    submitVote(vote) {
        // Save user's vote
        localStorage.setItem(this.storageKey, vote);

        // Update vote statistics
        const stats = this.getVoteStats();
        stats[vote]++;
        stats.total++;
        localStorage.setItem(this.votesKey, JSON.stringify(stats));

        // Show results
        this.displayResults(stats);
    }

    getVoteStats() {
        const stored = localStorage.getItem(this.votesKey);
        return stored ? JSON.parse(stored) : { bullish: 0, bearish: 0, total: 0 };
    }

    displayResults(stats) {
        const resultsDiv = document.getElementById('poll-results');
        const buttonsDiv = document.querySelector('.poll-buttons');

        if (!resultsDiv || !buttonsDiv) return;

        // Hide buttons, show results
        buttonsDiv.classList.add('hidden');
        resultsDiv.classList.remove('hidden');

        const bullishPercent = stats.total > 0 ? Math.round((stats.bullish / stats.total) * 100) : 50;
        const bearishPercent = 100 - bullishPercent;

        document.getElementById('bullish-percent').textContent = bullishPercent;
        document.getElementById('bearish-percent').textContent = bearishPercent;
        document.getElementById('total-votes').textContent = stats.total;

        const bullishBar = document.getElementById('result-bullish-bar');
        const bearishBar = document.getElementById('result-bearish-bar');

        if (bullishBar && bearishBar) {
            bullishBar.style.width = bullishPercent + '%';
            bearishBar.style.width = bearishPercent + '%';
        }
    }

    checkExistingVote() {
        const existingVote = localStorage.getItem(this.storageKey);
        if (existingVote) {
            const stats = this.getVoteStats();
            this.displayResults(stats);
        }
    }
}

// ==========================================
// 5. PERSONA TOGGLE (Trader vs Investor)
// ==========================================

class PersonaToggle {
    constructor() {
        this.currentPersona = localStorage.getItem('economicCompass_persona') || 'trader';
    }

    init() {
        const header = document.querySelector('header');
        if (!header) return;

        const toggleHTML = `
            <div class="persona-toggle">
                <button class="persona-btn ${this.currentPersona === 'trader' ? 'active' : ''}" data-persona="trader">
                    📊 Trader
                </button>
                <button class="persona-btn ${this.currentPersona === 'investor' ? 'active' : ''}" data-persona="investor">
                    💼 Investor
                </button>
            </div>
        `;

        header.querySelector('.header-controls')?.insertAdjacentHTML('beforeend', toggleHTML);

        this.attachListeners();
        this.applyPersona(this.currentPersona);
    }

    attachListeners() {
        const buttons = document.querySelectorAll('.persona-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const persona = e.currentTarget.dataset.persona;
                this.switchPersona(persona);
            });
        });
    }

    switchPersona(persona) {
        this.currentPersona = persona;
        localStorage.setItem('economicCompass_persona', persona);

        // Update button states
        document.querySelectorAll('.persona-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.persona === persona);
        });

        this.applyPersona(persona);
    }

    applyPersona(persona) {
        const insightContent = document.querySelector('.markdown-body');
        if (!insightContent) return;

        if (persona === 'trader') {
            // Highlight short-term elements
            document.querySelectorAll('.trend-row:has(#rsi-label)').forEach(el => {
                el.classList.add('highlight-trader');
            });

            // Add trader-specific note
            const existingNote = document.getElementById('persona-note');
            if (existingNote) existingNote.remove();

            const note = document.createElement('div');
            note.id = 'persona-note';
            note.className = 'persona-note trader-note';
            note.innerHTML = '📊 <strong>Trader Mode:</strong> Focus on RSI, short-term support levels, and intraday volatility.';
            insightContent.insertBefore(note, insightContent.firstChild);

        } else {
            // Highlight long-term elements
            document.querySelectorAll('.trend-row:has(#rsi-label)').forEach(el => {
                el.classList.remove('highlight-trader');
            });

            const existingNote = document.getElementById('persona-note');
            if (existingNote) existingNote.remove();

            const note = document.createElement('div');
            note.id = 'persona-note';
            note.className = 'persona-note investor-note';
            note.innerHTML = '💼 <strong>Investor Mode:</strong> Focus on macro trends, 200-day MA, and fundamental developments.';
            insightContent.insertBefore(note, insightContent.firstChild);
        }
    }
}

// ==========================================
// 6. SHAREABLE SNAPSHOT
// ==========================================

class ShareableSnapshot {
    init() {
        const insightHeader = document.querySelector('.insight-header');
        if (!insightHeader) return;

        const shareBtn = document.createElement('button');
        shareBtn.className = 'share-btn';
        shareBtn.innerHTML = '📤 Share';
        shareBtn.addEventListener('click', () => this.generateSnapshot());

        insightHeader.appendChild(shareBtn);
    }

    async generateSnapshot() {
        const fngValue = document.querySelector('.gauge-value, .gauge-svg text')?.textContent || 'N/A';
        const btcPrice = document.querySelector('.trend-row:has(#price-label) .value')?.textContent || 'N/A';
        const rsiValue = document.querySelector('.trend-row:has(#rsi-label) .value')?.textContent || 'N/A';
        const trend = document.getElementById('trend-value')?.textContent || 'N/A';

        const text = `📊 Economic Compass - ${new Date().toLocaleDateString()}

🎭 Fear & Greed: ${fngValue}/100
₿ BTC: ${btcPrice}
📈 RSI: ${rsiValue}
🎯 Trend: ${trend}

Check the full analysis at: ${window.location.href}

#Bitcoin #CryptoAnalysis #EconomicCompass`;

        // Use Web Share API if available
        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'Economic Compass Update',
                    text: text
                });
            } catch (err) {
                console.log('Share cancelled or failed:', err);
                this.fallbackCopy(text);
            }
        } else {
            this.fallbackCopy(text);
        }
    }

    fallbackCopy(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('📋 Snapshot copied to clipboard!');
        }).catch(() => {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            this.showNotification('📋 Snapshot copied!');
        });
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'share-notification';
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// ==========================================
// 7. EVENT COUNTDOWN TIMERS
// ==========================================

class EventCountdown {
    init() {
        // This would parse the watchlist section and add countdown timers
        // For now, we'll add a placeholder that can be enhanced with real event data

        const watchlistItems = document.querySelectorAll('.markdown-body li');
        watchlistItems.forEach(item => {
            const text = item.textContent;

            // Look for date patterns (you'll need to customize based on your format)
            const dateMatch = text.match(/(\w+ \d{1,2})/); // e.g., "Jan 15"

            if (dateMatch) {
                const countdownBadge = document.createElement('span');
                countdownBadge.className = 'countdown-badge';
                countdownBadge.innerHTML = ' ⏰ Soon';
                item.appendChild(countdownBadge);
            }
        });
    }
}

// ==========================================
// INITIALIZATION
// ==========================================

let tooltipManager, sparklineManager, gaugeVisualizer, sentimentPoll, personaToggle, shareableSnapshot, eventCountdown;

function initializeInteractiveFeatures() {
    console.log('🚀 Initializing Economic Compass Interactive Features...');

    // Initialize all modules
    tooltipManager = new TooltipManager();
    sparklineManager = new SparklineManager();
    gaugeVisualizer = new GaugeVisualizer();
    sentimentPoll = new SentimentPoll();
    personaToggle = new PersonaToggle();
    shareableSnapshot = new ShareableSnapshot();
    eventCountdown = new EventCountdown();

    // Add sparklines
    sparklineManager.addSparklines();

    // Initialize gauge
    gaugeVisualizer.init();

    // Initialize sentiment poll
    sentimentPoll.init();

    // Initialize persona toggle
    personaToggle.init();

    // Initialize share button
    shareableSnapshot.init();

    // Initialize countdown badges
    eventCountdown.init();

    console.log('✅ All interactive features loaded');
}

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeInteractiveFeatures);
} else {
    initializeInteractiveFeatures();
}
