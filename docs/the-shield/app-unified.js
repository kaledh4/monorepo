// THE SHIELD - Risk Monitor

async function updateDashboard() {
    const shieldData = await loadDashboardData('the-shield');
    if (!shieldData) return;

    const timestampEl = document.querySelector('.timestamp');
    if (timestampEl) {
        timestampEl.textContent = formatTimestamp(shieldData.last_update);
    }

    const contentEl = document.getElementById('content');
    const risk = shieldData.risk_assessment;

    contentEl.innerHTML = `
        <div class="content-card">
            <h2>🛡️ Risk Assessment</h2>
            
            <div class="data-section">
                <h3>Overall Risk Level</h3>
                <div class="data-value" style="color: ${risk.color}; font-size: 2.5rem;">
                    ${risk.level}
                </div>
                <div class="data-text" style="text-align: center;">
                    Risk Score: ${risk.score}/100
                </div>
            </div>
            
            <h2 style="margin-top: 30px;">📊 Stress Indicators</h2>
            <div class="data-grid">
                ${shieldData.metrics.map(m => `
                    <div class="data-section">
                        <h3>${m.name}</h3>
                        <div class="data-value" style="font-size: 1.4rem;">${m.value}</div>
                        <div class="data-text" style="text-align: center; margin-top: 10px;">
                            Signal: <strong style="color: ${m.signal === 'CRITICAL SHOCK' ? '#fc8181' :
            m.signal === 'HIGH STRESS' ? '#f6ad55' :
                m.signal === 'RISING STRESS' ? '#fbd38d' : '#68d391'
        }">${m.signal}</strong>
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <div class="data-section" style="margin-top: 20px;">
                <h3>🤖 AI Analysis</h3>
                <div class="data-text">${shieldData.ai_analysis || 'Analysis temporarily unavailable'}</div>
            </div>
            
            <div class="summary-box">
                <strong>View Detailed Analysis:</strong><br>
                <em>Check ${getSourceBadge('the-commander')} for how this risk level affects overall strategy</em>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nav').innerHTML = renderNavigation('the-shield');
    updateDashboard();
    setInterval(updateDashboard, 5 * 60 * 1000);
});
