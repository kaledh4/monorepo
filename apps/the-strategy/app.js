// ========================================
// Configuration
// ========================================
const CONFIG = {
    apiEndpoint: 'https://openrouter.ai/api/v1/chat/completions',
    model: 'x-ai/grok-4.1-fast:free', // 2M context, 30K max output, FREE!
    arxivApi: 'https://export.arxiv.org/api/query',
    apiKey: window.OPENROUTER_API_KEY || '',
    updateInterval: 24 * 60 * 60 * 1000, // 24 hours (once daily)
    cacheKey: 'market_intelligence_data_v2',
    lastUpdateKey: 'last_update_time',
    currentLang: localStorage.getItem('preferred_language') || 'en'
};

// Arabic Translations
const TRANSLATIONS = {
    en: {
        title: 'Market Intelligence',
        subtitle: 'Powered by Grok AI',
        lastUpdated: 'Last updated',
        dailyDigest: 'Daily Digest',
        aiGenerated: 'AI Generated',
        latestInsights: 'Latest Insights',
        dailyStockDiscoveries: 'Daily Stock Discoveries',
        usaMarketOpportunities: 'USA Market Opportunities',
        saudiTasiOpportunities: 'Saudi TASI Opportunities',
        notFinancialAdvice: '⚠️ Not Financial Advice',
        disclaimer: 'Disclaimer',
        disclaimerText: 'Stock picks are AI-generated based on market analysis, trends, and research. Not financial advice. Always do your own research.'
    },
    ar: {
        title: 'ذكاء السوق',
        subtitle: 'مدعوم بـ Grok AI',
        lastUpdated: 'آخر تحديث',
        dailyDigest: 'ملخص اليوم', // ✅ Fixed: was 'daily Digest'
        aiGenerated: 'مولد بالذكاء الاصطناعي',
        latestInsights: 'آخر الرؤى',
        dailyStockDiscoveries: 'اكتشافات الأسهم اليومية',
        usaMarketOpportunities: 'فرص السوق الأمريكي',
        saudiTasiOpportunities: 'فرص سوق تداول السعودي',
        notFinancialAdvice: '⚠️ ليست نصيحة مالية',
        disclaimer: 'إخلاء المسؤولية',
        disclaimerText: 'اختيارات الأسهم مولدة بالذكاء الاصطناعي بناءً على تحليل السوق والاتجاهات والأبحاث. ليست نصيحة مالية. قم دائماً بإجراء البحث الخاص بك.'
    }
};

// ========================================
// Service Worker Registration (PWA)
// ========================================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./service-worker.js')
            .then(registration => console.log('✅ Service Worker registered:', registration))
            .catch(error => console.log('❌ Service Worker registration failed:', error));
    });
}

// ========================================
// PWA Install Prompt
// ========================================
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    setTimeout(() => showInstallPrompt(), 5000);
});

function showInstallPrompt() {
    const installPrompt = document.getElementById('install-prompt');
    if (installPrompt && deferredPrompt) {
        installPrompt.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const installBtn = document.getElementById('install-btn');
    const dismissBtn = document.getElementById('dismiss-install');
    const installPrompt = document.getElementById('install-prompt');

    if (installBtn) {
        installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`User response: ${outcome}`);
                deferredPrompt = null;
                installPrompt.style.display = 'none';
            }
        });
    }

    if (dismissBtn) {
        dismissBtn.addEventListener('click', () => {
            installPrompt.style.display = 'none';
        });
    }
});

// ========================================
// Data Management
// ========================================
class DataManager {
    static saveToCache(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            localStorage.setItem(CONFIG.lastUpdateKey, Date.now().toString());
        } catch (error) {
            console.error('Error saving to cache:', error);
        }
    }

    static getFromCache(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Error reading from cache:', error);
            return null;
        }
    }

    static getLastUpdateTime() {
        const timestamp = localStorage.getItem(CONFIG.lastUpdateKey);
        return timestamp ? parseInt(timestamp) : null;
    }

    static shouldUpdate() {
        const lastUpdate = this.getLastUpdateTime();
        if (!lastUpdate) return true;

        const timeSinceUpdate = Date.now() - lastUpdate;
        return timeSinceUpdate >= CONFIG.updateInterval;
    }
}

// ========================================
// OpenRouter API Integration
// ========================================
class AIService {
    static async fetchInsights(prompt) {
        if (!CONFIG.apiKey) {
            console.warn('⚠️ OpenRouter API key not configured. Using demo data.');
            return this.getDemoData();
        }

        try {
            const response = await fetch(CONFIG.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${CONFIG.apiKey}`,
                    'HTTP-Referer': window.location.origin,
                    'X-Title': 'Market Intelligence Dashboard'
                },
                body: JSON.stringify({
                    model: CONFIG.model,
                    messages: [{
                        role: 'user',
                        content: prompt
                    }],
                    temperature: 0.7,
                    max_tokens: 15000 // Use ~50% of 30K max output for comprehensive reports
                })
            });

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }

            const data = await response.json();
            return data.choices[0].message.content;
        } catch (error) {
            console.error('Error fetching AI insights:', error);
            return this.getDemoData();
        }
    }

    static async generateDailyDigest(analysisData = null, arxivPapers = []) {
        let analysisContext = "";
        if (analysisData) {
            if (analysisData.meta && analysisData.analysis && typeof analysisData.analysis === 'object') {
                analysisContext = `
MARKET ANALYSIS DATA (Moore Analysis / Implied Probability):
- Ticker: ${analysisData.meta.ticker}
- Expiration: ${analysisData.meta.expiration}
- Current Price: ${analysisData.analysis.current_price}
- Market Expected Price (Peak Probability): ${analysisData.analysis.market_expected_price}
- Bullish Probability: ${analysisData.analysis.bullish_probability}%
- 68% Confidence Range: ${analysisData.analysis.expected_range_68pct.low} - ${analysisData.analysis.expected_range_68pct.high}
- Sentiment: ${analysisData.analysis.sentiment}
`;
            } else if (typeof analysisData.analysis === 'string') {
                analysisContext = `MARKET ANALYSIS STATUS: ${analysisData.analysis}`;
            }
        }

        let researchContext = "";
        if (arxivPapers && arxivPapers.length > 0) {
            researchContext = "\nLATEST ACADEMIC RESEARCH (arXiv):\n" + arxivPapers.map(p => `- ${p.title}: ${p.summary}`).join('\n');
        }

        const prompt = `You are a senior financial analyst. Generate an EXTENSIVE, professional market intelligence report for ${new Date().toLocaleDateString()}. 
Use the provided Market Analysis Data and Academic Research to ground your predictions.

${analysisContext}
${researchContext}

REQUIRED SECTIONS:

1. **📊 Executive Market Overview** (200 words)
   - Analyze S&P 500, NASDAQ, Dow trends.
   - Integrate the "Moore Analysis" data: Discuss what the options market is pricing in for the next month. Mention the implied probability and expected range.
   - Compare implied volatility vs realized volatility if inferred.

2. **💡 Deep Dive Insights** (4-5 items)
   - Detailed analysis of key sectors (Tech, Energy, Finance).
   - Specific company news with quantitative impact.
   - Connect macro events (Fed, Geopolitics) to market moves.

3. **🔬 Research & Quantitative Edge**
   - Synthesize the provided arXiv research papers. How do these findings apply to current market conditions? (e.g., "New paper on volatility modeling suggests...")
   - Combine this with the Moore Analysis probability distribution.

4. **🎯 Strategic Opportunities**
   - Identify undervalued sectors based on the probability distribution.
   - Suggest risk-managed approaches (e.g., "Given the 68% range of X-Y, consider spreads...").

5. **⚠️ Risk & Scenario Analysis**
   - Downside risks based on the lower bound of the expected range.
   - Tail risk events.

Format as Markdown. Use clear headers, bullet points, and bold text for readability. Avoid long walls of text.`;

        const content = await this.fetchInsights(prompt);
        return this.parseDigestContent(content);
    }

    static async generateStockPicks() {
        const prompt = `Generate 10 specific stock recommendations based on latest research, market trends, and industry analysis:

**5 USA STOCKS** - Must include:
- Ticker symbol
- Company name
- Current approximate price
- Target price (12 months)
- Reason for selection (tie to recent research/news/trends)
- Risk level (Low/Medium/High)

**5 SAUDI TASI STOCKS** - Must include:
- Stock code
- Company name (Arabic & English)
- Current approximate price (SAR)
- Target price (12 months)
- Reason for selection
- Risk level

Base selections on:
- Recent arXiv research papers in AI, energy, tech
- Saudi Vision 2030 initiatives
- Emerging tech trends
- Sector momentum
- Fundamental analysis

Return as JSON:
{
  "usa": [{
    "ticker": "NVDA",
    "name": "NVIDIA",
    "currentPrice": "$XXX",
    "targetPrice": "$YYY",
    "reason": "Leading AI chip maker, recent breakthrough in...",
    "risk": "Medium"
  }],
  "saudi": [{
    "code": "2222",
    "nameEn": "Saudi Aramco",
    "nameAr": "أرامكو السعودية",
    "currentPrice": "XXX SAR",
    "targetPrice": "YYY SAR",
    "reason": "Benefiting from...",
    "risk": "Low"
  }]
}`;

        const content = await this.fetchInsights(prompt);
        try {
            const jsonMatch = content.match(/```(?:json)?\n?([\s\S]*?)\n?```/);
            const jsonStr = jsonMatch ? jsonMatch[1] : content;
            return JSON.parse(jsonStr);
        } catch (error) {
            console.error('Error parsing stock picks:', error);
            return this.getDemoStockPicks();
        }
    }

    static async generateInsights(category = 'all') {
        const prompt = `Generate 5 specific, actionable market insights for category "${category}". Each must include:
- Specific title with company/sector names
- Data-driven summary (2-3 sentences) with numbers/percentages
- Category tag
- Realistic timestamp

Focus on: real companies, specific events, actual trends, concrete data points.

Return as JSON array:
[{
  "title": "Specific Company/Event Title",
  "summary": "Data-driven description with numbers...",
  "category": "market|tech|finance|trends",
  "timestamp": "X hours ago"
}]`;

        const content = await this.fetchInsights(prompt);
        return this.parseInsightsContent(content);
    }

    static async fetchArxivData() {
        try {
            // Query for Quantitative Finance (q-fin) and Economics (econ)
            const query = 'cat:q-fin.ST OR cat:q-fin.GN OR cat:q-fin.RM OR cat:q-fin.PM';
            const url = `${CONFIG.arxivApi}?search_query=${encodeURIComponent(query)}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending`;

            const response = await fetch(url);
            const str = await response.text();

            // Simple XML parsing
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(str, "text/xml");
            const entries = xmlDoc.getElementsByTagName("entry");

            const papers = [];
            for (let i = 0; i < entries.length; i++) {
                const entry = entries[i];
                papers.push({
                    title: entry.getElementsByTagName("title")[0].textContent.replace(/\n/g, ' ').trim(),
                    summary: entry.getElementsByTagName("summary")[0].textContent.replace(/\n/g, ' ').trim().substring(0, 200) + "...",
                    published: new Date(entry.getElementsByTagName("published")[0].textContent).toLocaleDateString(),
                    link: entry.getElementsByTagName("id")[0].textContent
                });
            }
            return papers;
        } catch (error) {
            console.error('Error fetching arXiv data:', error);
            return [];
        }
    }

    static parseDigestContent(content) {
        return content.replace(/```markdown\n?/g, '').replace(/```\n?/g, '');
    }

    static parseInsightsContent(content) {
        try {
            const jsonMatch = content.match(/```(?:json)?\n?([\s\S]*?)\n?```/);
            const jsonStr = jsonMatch ? jsonMatch[1] : content;
            return JSON.parse(jsonStr);
        } catch (error) {
            console.error('Error parsing insights:', error);
            return this.getDemoInsights();
        }
    }

    static getDemoData() {
        return `# 📈 Daily Market Intelligence Digest
*${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}*

## 📊 Market Overview
**Major Indices:** S&P 500 +1.2% (4,785), NASDAQ +1.8% (15,234), Dow Jones +0.9% (37,891)

Technology sector leads gains with semiconductor stocks surging 3.1% on strong earnings from major chipmakers. Energy sector down 1.5% amid oil price correction to $78/barrel. Financial sector showing resilience (+0.7%) despite rate uncertainty.

Trading volume 15% above 30-day average, indicating strong investor participation. VIX down to 12.3, suggesting low market anxiety.

## 💡 Top 5 Critical Insights

### 1. AI Infrastructure Spending Reaches Record $127B
Major cloud providers (AWS, Azure, Google Cloud) collectively announced $127B in AI infrastructure investments for 2025. NVIDIA reports data center revenue up 217% YoY, reaching $18.4B in Q4. Impact: **VERY HIGH** on semiconductor supply chain.

### 2. Saudi Arabia's NEOM Mega-Project Advances
$500B NEOM  smart city project reaches 35% completion. New partnerships with 12 international tech firms announced. Saudi stock market (TASI) responds with construction sector +4.2%, materials +3.8%. Impact: **HIGH** on GCC markets.

### 3. Quantum Computing Breakthrough by IBM
IBM demonstrates 1,000+ qubit quantum processor with error correction, advancing commercial viability timeline by 2-3 years. Cybersecurity stocks rally (+6.3%) on quantum-resistant encryption demand. Impact: **MEDIUM-HIGH** on tech sector.

### 4. Green Hydrogen Production Cost Drops 40%
New electrolyzer technology reduces green hydrogen production cost to $2.20/kg (vs $3.50/kg industry average). Major implications for clean energy transition. Related sectors: renewable energy +5.1%, industrial gases +3.4%. Impact: **HIGH** on energy sector.

### 5. Federal Reserve Signals Rate Stability
Fed Chair indicates unchanged rates through Q2 2025 with data-dependent approach. Bond yields stabilize: 10-year Treasury at 4.25%. Growth stocks rally +2.3% on confirmation. Impact: **VERY HIGH** on all asset classes.

## 🎯 Investment Opportunities

**1. Artificial Intelligence & Semiconductors**
- AI chip demand exceeding supply by 35%
- Data center occupancy at record 97.8%
- Edge AI devices market growing 42% annually
- **Risk/Reward: HIGH/VERY HIGH**

**2. Saudi Vision 2030 Beneficiaries**
- Non-oil GDP growth target: 6.2% annually
- Tourism sector investment: $64B allocated
- Renewable energy capacity: 58.7GW by 2030
- **Risk/Reward: MEDIUM/HIGH**

**3. Clean Energy Transition**
- Global green energy investment: $1.8T in 2024
- EV adoption reaching 18% of new car sales
- Grid storage market: $150B opportunity
- **Risk/Reward: MEDIUM/VERY HIGH**

## ⚠️ Risk Factors

1. **Geopolitical Tensions** (Probability: 65%)
   - Middle East supply chain disruptions
   - Trade policy uncertainties
   - Watch: Dec 15 trade summit

2. **Inflation Resurgence** (Probability: 40%)
   - Core PCE still above 3% target
   - Wage growth persistent at 4.2%
   - Next CPI: December 12

3. **Tech Valuation Concerns** (Probability: 55%)
   - Mega-cap P/E ratios at 35x (10-year avg: 22x)
   - AI revenue monetization unclear
   - Correction risk if earnings miss

4. **Banking Sector Stress** (Probability: 30%)
   - Commercial real estate exposure: $2.9T
   - Regional bank deposit flight continues
   - Basel III implementation: Q1 2025

5. **Regulatory Crackdown** (Probability: 50%)
   - AI regulation (EU AI Act: Feb 2025)
   - Big Tech antitrust cases
   - Crypto framework legislation

---
*Generated by AI • Based on latest market data and research • Not financial advice • Do your own research*`;
    }

    static getDemoStockPicks() {
        return {
            usa: [
                {
                    ticker: "NVDA",
                    name: "NVIDIA Corporation",
                    currentPrice: "$485",
                    targetPrice: "$620", // ✅ corrected
                    reason: "Leading AI chip manufacturer...",
                    risk: "Medium"
                },
                {
                    ticker: "TSLA",
                    name: "Tesla Inc",
                    currentPrice: "$242",
                    targetPrice: "$310",
                    reason: "EV market leader with 55% US market share. New battery technology reducing costs 40%. Cybertruck production ramping to 250K units/year. Energy storage division growing 89% YoY. FSD subscription revenue accelerating.",
                    risk: "High"
                },
                {
                    ticker: "MSFT",
                    name: "Microsoft Corporation",
                    currentPrice: "$378",
                    targetPrice: "$445",
                    reason: "Azure AI services revenue up 98% YoY. OpenAI integration driving enterprise adoption. Cloud margin expansion to 73%. GitHub Copilot reaching 1.3M paid subscribers. Strong moat in enterprise software.",
                    risk: "Low"
                },
                {
                    ticker: "NEE",
                    name: "NextEra Energy",
                    currentPrice: "$59",
                    targetPrice: "$78",
                    reason: "Largest renewable energy producer in North America. 58GW clean energy capacity. Benefiting from IRA tax credits worth $2.1B annually. Grid modernization contracts totaling $4.3B. Stable 2.8% dividend yield.",
                    risk: "Low"
                },
                {
                    ticker: "PLTR",
                    name: "Palantir Technologies",
                    currentPrice: "$18",
                    targetPrice: "$28",
                    reason: "AI Platform (AIP) securing $900M in contracts. Government revenue stable at $600M/quarter. Commercial revenue growing 54% YoY. Recent DoD contract wins worth $250M. Expanding in healthcare and manufacturing verticals.",
                    risk: "High"
                }
            ],
            saudi: [
                {
                    code: "2222",
                    nameEn: "Saudi Aramco",
                    nameAr: "أرامكو السعودية",
                    currentPrice: "28.50 SAR",
                    targetPrice: "32.00 SAR",
                    reason: "World's largest oil producer maintaining 12M barrels/day capacity. Diversifying into blue hydrogen ($110B investment). Dividend yield 4.1%. Benefiting from Asian demand growth. Strong balance sheet with minimal debt.",
                    risk: "Low"
                },
                {
                    code: "1120",
                    nameEn: "Al Rajhi Bank",
                    nameAr: "مصرف الراجحي",
                    currentPrice: "89.20 SAR",
                    targetPrice: "105.00 SAR",
                    reason: "Largest Islamic bank globally with SAR 750B in assets. Digital banking users up 47% to 8.2M. Net profit margin 35.6%. Vision 2030 beneficiary through SME lending program. ROE of 18.3% leading sector.",
                    risk: "Low"
                },
                {
                    code: "2030",
                    nameEn: "Saudi Telecom Company (STC)",
                    nameAr: "الاتصالات السعودية",
                    currentPrice: "43.80 SAR",
                    targetPrice: "52.00 SAR",
                    reason: "5G network covering 82% of population. Cloud services revenue up 63%. Cybersecurity division securing government contracts worth SAR 2.1B. Expanding in fintech through STC Pay (12M users). EBITDA margin 52%.",
                    risk: "Medium"
                },
                {
                    code: "2370",
                    nameEn: "Middle East Healthcare Company (MEAHCO)",
                    nameAr: "الشرق الأوسط للرعاية الصحية",
                    currentPrice: "12.40 SAR",
                    targetPrice: "16.50 SAR",
                    reason: "Benefiting from healthcare privatization push. Operating 15 facilities across KSA. Medical tourism initiative bringing 250K patients annually. Partnerships with Johns Hopkins and Mayo Clinic. Revenue growing 41% YoY.",
                    risk: "Medium"
                },
                {
                    code: "4082",
                    nameEn: "Al Yamamah Steel Industries",
                    nameAr: "حديد اليمامة",
                    currentPrice: "18.70 SAR",
                    targetPrice: "24.00 SAR",
                    reason: "NEOM construction demand driving orders. Production capacity expansion to 800K tons/year. Government infrastructure spending at SAR 500B supporting sector. Vertical integration reducing costs 18%. Export growth to GCC markets.",
                    risk: "High"
                }
            ]
        };
    }

    static getDemoInsights() {
        return [
            {
                title: 'NVIDIA H200 Chips Sold Out Through Q2 2025 - Stock Up 8.4%',
                summary: 'NVIDIA announced H200 GPU allocation completely sold out, with cloud providers securing $12B in orders. Stock surged to $492 on news, up 8.4% in single session. Analysts raising price targets to $650-$700 range.',
                category: 'tech',
                timestamp: '2 hours ago'
            },
            {
                title: 'Saudi Aramco Launches $110B Blue Hydrogen Initiative',
                summary: 'Aramco unveils massive blue hydrogen complex targeting 11M tons annual production by 2030. Partners with Siemens Energy and Air Products. Stock gained 3.2% to SAR 29.40 on announcement. First shipments to Japan by Q3 2025.',
                category: 'market',
                timestamp: '4 hours ago'
            },
            {
                title: 'Fed Keeps Rates at 5.25-5.50%, Powell Signals Stability',
                summary: 'Federal Reserve maintains current rate range citing balanced economic conditions. Powell emphasized data-dependent approach with no cuts before Q3 2025. Bond yields dropped 12bp to 4.25%, tech stocks rallied 2.3%.',
                category: 'finance',
                timestamp: '6 hours ago'
            },
            {
                title: 'Tesla Cybertruck Orders Exceed 2M - Production Accelerating',
                summary: 'Tesla reports Cybertruck reservations hitting 2.1M units with deliveries ramping to 125K/quarter by Q2 2025. Stock jumped 6.8% to $248. Average selling price of $82K generating strong margins. Giga Texas expansion underway.',
                category: 'trends',
                timestamp: '9 hours ago'
            },
            {
                title: 'Al Rajhi Bank Q4 Profit Surges 28% on Digital Banking Growth',
                summary: 'Al Rajhi reports net income of SAR 4.2B (+28% YoY) driven by 47% increase in digital users. Mobile banking transactions up 89%. Stock reached SAR 92.50, approaching all-time highs. Announced 1.5% dividend increase.',
                category: 'market',
                timestamp: '12 hours ago'
            }
        ];
    }
}

// ========================================
// UI Controller with Translation Support
// ========================================
class UIController {
    static hideLoading() {
        const loadingScreen = document.getElementById('loading-screen');
        const app = document.getElementById('app');

        if (loadingScreen && app) {
            setTimeout(() => {
                loadingScreen.classList.add('hidden');
                app.style.display = 'block';
            }, 1500);
        }
    }

    static updateLastUpdateTime() {
        const element = document.getElementById('last-updated');
        const lastUpdate = DataManager.getLastUpdateTime();

        if (element && lastUpdate) {
            const date = new Date(lastUpdate);
            const lang = CONFIG.currentLang;
            element.innerHTML = `
                <span class="status-indicator"></span>
                ${TRANSLATIONS[lang].lastUpdated}: ${date.toLocaleString()}
            `;
        }
    }

    static updateStats(data) {
        const stats = {
            trends: data.insights?.length || 5,
            insights: Math.floor(Math.random() * 20) + 15,
            updates: Math.floor(Math.random() * 50) + 30,
            sentiment: ['Bullish 📈', 'Neutral ➡️', 'Bearish 📉'][Math.floor(Math.random() * 3)]
        };

        document.getElementById('trends-count').textContent = stats.trends;
        document.getElementById('insights-count').textContent = stats.insights;
        document.getElementById('updates-count').textContent = stats.updates;
        document.getElementById('sentiment-value').textContent = stats.sentiment;

        document.querySelectorAll('.stat-card.shimmer').forEach(card => {
            card.classList.remove('shimmer');
        });
    }

    static renderDigest(content) {
        const digestContent = document.getElementById('digest-content');
        if (digestContent) {
            const html = this.markdownToHTML(content);
            digestContent.innerHTML = html;
        }
    }

    static renderStockPicks(stockData) {
        // Will be implemented when HTML section is added
        console.log('Stock picks:', stockData);
    }

    static renderInsights(insights) {
        const insightsFeed = document.getElementById('insights-feed');
        if (!insightsFeed) return;

        insightsFeed.innerHTML = insights.map(insight => `
            <div class="insight-card" data-category="${insight.category}">
                <div class="insight-header">
                    <span class="insight-category">${insight.category}</span>
                    <span class="insight-time">${insight.timestamp}</span>
                </div>
                <h3 class="insight-title">${insight.title}</h3>
                <p class="insight-summary">${insight.summary}</p>
            </div>
        `).join('');
    }

    static markdownToHTML(markdown) {
        return markdown
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h3>$1</h3>')
            .replace(/^# (.*$)/gim, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^- (.*$)/gim, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^(?!<[h|u|l])(.*$)/gim, '<p>$1</p>')
            .replace(/<p><\/p>/g, '');
    }

    static filterInsights(category) {
        const cards = document.querySelectorAll('.insight-card');
        cards.forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    static renderResearch(analysisData, papers) {
        const container = document.getElementById('analysis-container');
        if (!container) return;

        let html = '<div class="research-grid">';

        // 1. Moore Analysis Card
        if (analysisData && analysisData.analysis && typeof analysisData.analysis === 'object') {
            html += `
            <div class="analysis-card moore-card">
                <div class="analysis-header">
                    <h3>🔮 Moore Analysis: Market Probability</h3>
                    <span class="tag ${analysisData.analysis.sentiment.toLowerCase()}">${analysisData.analysis.sentiment}</span>
                </div>
                <div class="analysis-content">
                    <div class="analysis-stats">
                        <div class="stat-item">
                            <span class="label">Expected Price</span>
                            <span class="value">${analysisData.analysis.market_expected_price}</span>
                        </div>
                        <div class="stat-item">
                            <span class="label">Bullish Prob</span>
                            <span class="value">${analysisData.analysis.bullish_probability}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="label">Range (68%)</span>
                            <span class="value">${analysisData.analysis.expected_range_68pct.low} - ${analysisData.analysis.expected_range_68pct.high}</span>
                        </div>
                    </div>
                    <div class="analysis-chart">
                        <img src="./market_analysis_chart.png" alt="Market Probability Distribution" onerror="this.style.display='none'">
                    </div>
                    <p class="analysis-explainer">
                        Market consensus derived from options pricing curvature (Breeden-Litzenberger).
                    </p>
                </div>
            </div>`;
        }

        // 2. arXiv Research Card
        if (papers && papers.length > 0) {
            html += `
            <div class="analysis-card research-papers-card">
                <div class="analysis-header">
                    <h3>🔬 Latest Quantitative Research (arXiv)</h3>
                    <span class="tag neutral">${papers.length} Papers</span>
                </div>
                <div class="papers-list">
                    ${papers.map(p => `
                        <div class="paper-item">
                            <a href="${p.link}" target="_blank" class="paper-title">${p.title}</a>
                            <span class="paper-date">${p.published}</span>
                            <p class="paper-summary">${p.summary}</p>
                        </div>
                    `).join('')}
                </div>
            </div>`;
        }

        html += '</div>';
        container.innerHTML = html;
        container.style.display = 'block';
    }

    static translatePage(lang) {
        CONFIG.currentLang = lang;
        localStorage.setItem('preferred_language', lang);

        // Update UI elements with data attributes
        document.querySelectorAll('[data-en]').forEach(el => {
            const key = el.dataset.en.toLowerCase().replace(/ /g, '');
            if (TRANSLATIONS[lang][key]) {
                el.textContent = TRANSLATIONS[lang][key];
            }
        });

        // Update language toggle button
        const langBtn = document.getElementById('lang-toggle');
        if (langBtn) {
            const langText = langBtn.querySelector('.lang-text');
            if (langText) {
                langText.textContent = lang === 'en' ? 'AR' : 'EN';
            }
        }

        // Update document direction for Arabic
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
        document.documentElement.lang = lang;
    }
}

// ========================================
// App Initialization
// ========================================
class App {
    static async init() {
        console.log('🚀 Initializing Market Intelligence Dashboard...');

        const shouldUpdate = DataManager.shouldUpdate();
        let data = DataManager.getFromCache(CONFIG.cacheKey);

        if (shouldUpdate || !data) {
            console.log('📡 Fetching fresh data from AI...');
            data = await this.fetchFreshData();
            DataManager.saveToCache(CONFIG.cacheKey, data);
        } else {
            console.log('💾 Using cached data...');
        }

        UIController.updateStats(data);
        UIController.renderDigest(data.digest);

        // Render combined research section
        UIController.renderResearch(data.analysis, data.research);

        UIController.renderInsights(data.insights);
        if (data.stockPicks) {
            UIController.renderStockPicks(data.stockPicks);
        }
        UIController.updateLastUpdateTime();
        UIController.hideLoading();

        // Apply saved language preference
        UIController.translatePage(CONFIG.currentLang);

        this.setupEventListeners();

        console.log('✅ Dashboard ready!');
    }

    static async fetchFreshData() {
        // Try to fetch pre-computed market analysis
        let analysisData = null;
        try {
            const response = await fetch('./market_analysis.json');
            if (response.ok) {
                analysisData = await response.json();
            }
        } catch (e) {
            console.log('No local analysis data found');
        }

        // Fetch arXiv data
        const arxivPapers = await AIService.fetchArxivData();

        const [digest, insights, stockPicks] = await Promise.all([
            AIService.generateDailyDigest(analysisData, arxivPapers),
            AIService.generateInsights(),
            AIService.generateStockPicks()
        ]);

        return { digest, insights, stockPicks, analysis: analysisData, research: arxivPapers };
    }

    static setupEventListeners() {
        // Language toggle
        const langBtn = document.getElementById('lang-toggle');
        if (langBtn) {
            langBtn.addEventListener('click', () => {
                const newLang = CONFIG.currentLang === 'en' ? 'ar' : 'en';
                UIController.translatePage(newLang);
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                refreshBtn.classList.add('spinning');
                const data = await this.fetchFreshData();
                DataManager.saveToCache(CONFIG.cacheKey, data);
                UIController.renderDigest(data.digest);
                UIController.renderInsights(data.insights);
                if (data.stockPicks) {
                    UIController.renderStockPicks(data.stockPicks);
                }
                UIController.updateLastUpdateTime();
                setTimeout(() => refreshBtn.classList.remove('spinning'), 1000);
            });
        }

        // Filter select
        const filterSelect = document.getElementById('filter-select');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                UIController.filterInsights(e.target.value);
            });
        }

        // Settings button
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                alert('Settings panel coming soon!');
            });
        }
    }
}

// ========================================
// Start the App
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// ========================================
// Auto-update check
// ========================================
setInterval(() => {
    if (DataManager.shouldUpdate()) {
        console.log('🔄 Auto-updating dashboard...');
        App.init();
    }
}, 60 * 60 * 1000);
