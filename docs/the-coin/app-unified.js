// THE COIN - Crypto Momentum Scanner

async function updateDashboard() {
    const coinData = await loadDashboardData('the-coin');
    if (!coinData) return;

    const timestampEl = document.querySelector('.timestamp');
    if (timestampEl) timestampEl.textContent = formatTimestamp(coinData.generated_at || coinData.timestamp);

    const contentEl = document.getElementById('content');

    contentEl.innerHTML = `
        <div class="content-card">
            <h2>🪙 Crypto Momentum Overview</h2>
            
            <div class="data-grid">
                <div class="data-section">
                    <h3>Bitcoin Price</h3>
                    <div class="data-value" style="color: #f7931a;">$${(coinData.btc_price || 0).toLocaleString()}</div>
                </div>
                
                <div class="data-section">
                    <h3>Ethereum Price</h3>
                    <div class="data-value" style="color: #627eea;">$${(coinData.eth_price || 0).toLocaleString()}</div>
                </div>
                
                <div class="data-section">
                    <h3>Momentum</h3>
                    <div class="data-value stance">${coinData.momentum || 'N/A'}</div>
                </div>
                
                <div class="data-section">
                    <h3>RSI</h3>
                    <div class="data-value">${coinData.rsi ? coinData.rsi.toFixed(1) : 'N/A'}</div>
                </div>
                
                <div class="data-section">
                    <h3>Trend</h3>
                    <div class="data-value">${coinData.trend || 'N/A'}</div>
                </div>
                
                <div class="data-section">
                    <h3>Fear & Greed</h3>
                    <div class="data-value">${coinData.fear_and_greed?.value || 'N/A'}</div>
                    <p class="data-text" style="text-align: center; margin-top: 10px;">
                        ${coinData.fear_and_greed?.classification || ''}
                    </p>
                </div>
            </div>
            
            <div class="data-section" style="margin-top: 20px;">
                <h3>🤖 AI Analysis</h3>
                <div class="data-text">${coinData.ai_analysis || 'Analysis temporarily unavailable'}</div>
            </div>
            
            <div class="summary-box">
                <strong>View Strategy:</strong><br>
                <em>See ${getSourceBadge('the-commander')} for how crypto momentum fits into today's action stance</em>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nav').innerHTML = renderNavigation('the-coin');
    updateDashboard();
    setInterval(updateDashboard, 5 * 60 * 1000);
});
