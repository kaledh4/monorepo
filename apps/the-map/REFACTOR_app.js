// Economic Compass - Client-Side Data Loader
// This replaces the Python/Jinja2 server-side rendering

async function loadEconomicData() {
    console.log('📊 Loading Economic Compass data...');

    // Multi-path data fetching (unified pattern)
    const dataPaths = [
        './data/latest.json',
        './latest.json',
        '../data/the-map/latest.json',
        '../../data/the-map/latest.json'
    ];

    let lastError = null;
    for (const dataPath of dataPaths) {
        try {
            const response = await fetch(`${dataPath}?t=${Date.now()}`);
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Data loaded from: ${dataPath}`);
                renderDashboard(data);
                return;
            }
        } catch (error) {
            lastError = error;
            console.debug(`Path ${dataPath} failed, trying next...`);
        }
    }

    console.error('❌ Error fetching data from all paths:', lastError);
    showError('Failed to load market data. Please try again later.');
}

function renderDashboard(data) {
    try {
        // Update generated date
        const generatedDate = new Date(data.timestamp || Date.now());
        document.getElementById('date-display').textContent =
            generatedDate.toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });

        // Fear & Greed Index
        if (data.fng) {
            document.getElementById('fng-value').textContent = data.fng.value;
            document.getElementById('fng-classification').textContent = data.fng.value_classification;

            const fngColor = data.fng.value > 60 ? '#10b981' :
                data.fng.value < 40 ? '#ef4444' : '#f59e0b';
            document.getElementById('fng-value').style.color = fngColor;
        }

        // BTC Trend
        if (data.btc) {
            document.getElementById('btc-price').textContent = `$${data.btc.price.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
            document.getElementById('btc-rsi').textContent = data.btc.rsi.toFixed(1);
            document.getElementById('btc-trend').textContent = data.btc.trend_weekly;

            const trendClass = data.btc.trend_weekly === 'Bullish' ? 'text-green' : 'text-red';
            document.getElementById('btc-trend').className = `value ${trendClass}`;
        }

        // Macro Indicators
        if (data.macro) {
            // 10Y Treasury Yield
            if (data.macro.treasury_10y) {
                const yieldValue = data.macro.treasury_10y.price.toFixed(2);
                const yieldChange = data.macro.treasury_10y.change_7d;
                const yieldSymbol = yieldChange >= 0 ? '▲' : '▼';
                const yieldColor = yieldChange >= 0 ? 'text-green' : 'text-red';

                document.getElementById('yield-value').innerHTML = `
                    ${yieldValue}%
                    <span class="${yieldColor}" style="font-size: 0.8em;">${yieldSymbol} ${Math.abs(yieldChange).toFixed(1)}%</span>
                `;
            }

            // Gold
            if (data.macro.gold) {
                const goldValue = data.macro.gold.price.toLocaleString('en-US', { maximumFractionDigits: 0 });
                const goldChange = data.macro.gold.change_7d;
                const goldSymbol = goldChange >= 0 ? '▲' : '▼';
                const goldColor = goldChange >= 0 ? 'text-green' : 'text-red';

                document.getElementById('gold-value').innerHTML = `
                    $${goldValue}
                    <span class="${goldColor}" style="font-size: 0.8em;">${goldSymbol} ${Math.abs(goldChange).toFixed(1)}%</span>
                `;
            }

            // S&P 500
            if (data.macro.sp500) {
                const sp500Value = data.macro.sp500.price.toLocaleString('en-US', { maximumFractionDigits: 0 });
                const sp500Change = data.macro.sp500.change_7d;
                const sp500Symbol = sp500Change >= 0 ? '▲' : '▼';
                const sp500Color = sp500Change >= 0 ? 'text-green' : 'text-red';

                document.getElementById('sp500-value').innerHTML = `
                    ${sp500Value}
                    <span class="${sp500Color}" style="font-size: 0.8em;">${sp500Symbol} ${Math.abs(sp500Change).toFixed(1)}%</span>
                `;
            }

            // TASI
            if (data.macro.tasi) {
                const tasiValue = data.macro.tasi.price.toLocaleString('en-US', { maximumFractionDigits: 0 });
                const tasiChange = data.macro.tasi.change_7d;
                const tasiSymbol = tasiChange >= 0 ? '▲' : '▼';
                const tasiColor = tasiChange >= 0 ? 'text-green' : 'text-red';

                document.getElementById('tasi-value').innerHTML = `
                    ${tasiValue}
                    <span class="${tasiColor}" style="font-size: 0.8em;">${tasiSymbol} ${Math.abs(tasiChange).toFixed(1)}%</span>
                `;
            }
        }

        // AI Insight Commentary
        if (data.insight_html) {
            document.getElementById('insight-content').innerHTML = data.insight_html;
        }

        // Update timestamp
        if (data.timestamp) {
            document.getElementById('timestamp').textContent = new Date(data.timestamp).toLocaleString();
        }

        console.log('✅ Dashboard rendered successfully');
    } catch (error) {
        console.error('❌ Error rendering dashboard:', error);
        showError('Error rendering market data');
    }
}

function showError(message) {
    const container = document.querySelector('.content-area') || document.querySelector('.container');
    if (container) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = 'background: rgba(239, 68, 68, 0.1); color: #ef4444; padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid rgba(239, 68, 68, 0.3);';
        errorDiv.textContent = `⚠️ ${message}`;
        container.insertBefore(errorDiv, container.firstChild);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function () {
    loadEconomicData();

    // Refresh data every 5 minutes
    setInterval(loadEconomicData, 5 * 60 * 1000);
});
