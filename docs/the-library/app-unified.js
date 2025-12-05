// THE LIBRARY - Alpha-Clarity Archive

async function updateDashboard() {
    const libraryData = await loadDashboardData('the-library');
    if (!libraryData) return;

    const timestampEl = document.querySelector('.timestamp');
    if (timestampEl) timestampEl.textContent = formatTimestamp(libraryData.timestamp);

    const contentEl = document.getElementById('content');

    contentEl.innerHTML = `
        <div class="content-card">
            <h2>📚 Simplified Knowledge</h2>
            <p class="data-text" style="margin-bottom: 20px;">
                Complex market concepts explained simply
            </p>
            
            ${(libraryData.summaries || []).map((s, i) => `
                <div class="data-section">
                    <h3>${i + 1}. ${s.title}</h3>
                    <div class="data-text" style="margin-bottom: 15px;">
                        <strong>🧒 Explain Like I'm 5:</strong><br>
                        ${s.eli5}
                    </div>
                    <div class="data-text" style="background: rgba(66, 153, 225, 0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #4299e1;">
                        <strong>📈 Long-term Impact:</strong><br>
                        ${s.long_term}
                    </div>
                </div>
            `).join('') || '<p class="data-text">No summaries available yet. Check back after data update.</p>'}
            
            <div class="summary-box" style="margin-top: 20px;">
                <strong>Daily Context:</strong><br>
                <em>See ${getSourceBadge('the-commander')} to understand how these topics fit today's market picture</em>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nav').innerHTML = renderNavigation('the-library');
    updateDashboard();
    setInterval(updateDashboard, 5 * 60 * 1000);
});
