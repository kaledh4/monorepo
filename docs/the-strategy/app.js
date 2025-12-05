// THE STRATEGY - Unified Opportunity Radar

async function updateDashboard() {
    const strategyData = await loadDashboardData('the-strategy');
    if (!strategyData) return;

    const timestampEl = document.querySelector('.timestamp');
    if (timestampEl) timestampEl.textContent = formatTimestamp(strategyData.timestamp);

    const contentEl = document.getElementById('content');

    contentEl.innerHTML = `
        <div class="content-card">
            <h2>🎯 Strategic Stance</h2>
            
            <div class="data-section">
                <h3>Today's Stance</h3>
                <div class="data-value stance" style="font-size: 2.5rem;">
                    ${strategyData.stance || 'N/A'}
                </div>
            </div>
            
            <div class="data-section">
                <h3>Recommended Mindset</h3>
                <div class="data-text" style="font-size: 1.2rem; text-align: center; font-weight: 600; color: #f7fafc;">
                    "${strategyData.mindset || 'N/A'}"
                </div>
            </div>
            
            <h2 style="margin-top: 30px;">📊 Input Signals</h2>
            <div class="data-grid">
                <div class="data-section">
                    <h3>Risk Level ${getSourceBadge('the-shield')}</h3>
                    <div class="data-value">${strategyData.inputs?.risk || 'N/A'}</div>
                </div>
                
                <div class="data-section">
                    <h3>Crypto ${getSourceBadge('the-coin')}</h3>
                    <div class="data-value">${strategyData.inputs?.crypto || 'N/A'}</div>
                </div>
                
                <div class="data-section">
                    <h3>Macro ${getSourceBadge('the-map')}</h3>
                    <div class="data-value">${strategyData.inputs?.macro || 'N/A'}</div>
                </div>
                
                <div class="data-section">
                    <h3>Frontier ${getSourceBadge('the-frontier')}</h3>
                    <div class="data-value">${strategyData.inputs?.frontier || 'N/A'}</div>
                </div>
            </div>
            
            <div class="data-section" style="margin-top: 20px;">
                <h3>🤖 AI Synthesis</h3>
                <div class="data-text">${strategyData.ai_analysis || 'Analysis temporarily unavailable'}</div>
            </div>
            
            <div class="summary-box">
                <strong>Complete Picture:</strong><br>
                <em>View ${getSourceBadge('the-commander')} for the full Morning Brief with action stance context</em>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nav').innerHTML = renderNavigation('the-strategy');
    updateDashboard();
    setInterval(updateDashboard, 5 * 60 * 1000);
});
