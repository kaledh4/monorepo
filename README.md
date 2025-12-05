# Daily Alpha Loop
### AI-Powered Market Intelligence System

A unified dashboard orchestrator providing daily market insights through 7 specialized intelligence dashboards.

## 🎯 The Seven Dashboards

| Dashboard | Mission | Focus | Link |
|-----------|---------|-------|------|
| **The Shield** | Market Fragility Monitor | Detect systemic stress before crashes | [🔗 Launch](the-shield/) |
| **The Coin** | Crypto Momentum Scanner | Track BTC/ETH momentum shifts | [🔗 Launch](the-coin/) |
| **The Map** | Macro & TASI Trendsetter | Align global macro with Saudi markets | [🔗 Launch](the-map/) |
| **The Frontier** | Silicon Frontier Watch | Identify AI/tech breakthroughs | [🔗 Launch](the-frontier/) |
| **The Strategy** | Unified Opportunity Radar | Synthesize cross-dashboard insights | [🔗 Launch](the-strategy/) |
| **The Library** | Alpha-Clarity Archive | Simplify complex market knowledge | [🔗 Launch](the-library/) |
| **The Commander** | Master Orchestrator | Generate daily “Morning Brief” | [🔗 Launch](the-commander/) |

## 🚀 Quick Start

### Install dependencies
```bash
cd tools
pip install -r requirements.txt
```

### Run data fetcher
```bash
# Run for all dashboards
python fetchers/unified_fetcher.py --all

# Or run for specific dashboard
python fetchers/unified_fetcher.py --app the-shield
```

## 📦 Architecture

```
daily-alpha-loop/
├── apps/               # 7 dashboard applications
│   ├── the-shield/
│   ├── the-coin/
│   ├── the-map/
│   ├── the-frontier/
│   ├── the-strategy/
│   ├── the-library/
│   └── the-commander/
├── data/              # Generated JSON data
├── tools/             # Unified fetcher script
│   └── fetchers/
│       └── unified_fetcher.py
├── static/            # Shared icons and assets
└── .github/workflows/ # Daily automation
```

## 🔧 Configuration

Set environment variables:

```bash
export OPENROUTER_API_KEY="your_key"
export NEWS_API_KEY="your_key"
export FRED_API_KEY="your_key"
export ALPHA_VANTAGE_KEY="your_key"
```

## ⏰ Automation

The system runs automatically daily at 4 AM UTC via GitHub Actions (`daily_alpha_loop.yml`).

## 📊 Data Flow

1. **Unified Fetcher runs daily**
2. Fetches data from multiple sources (FRED, Alpha Vantage, NewsAPI, arXiv)
3. AI models analyze data (via OpenRouter)
4. Generates JSON outputs for each dashboard
5. **The Commander** synthesizes all data into Morning Brief
6. Dashboards update automatically

## 🤖 AI Models

Each dashboard uses specialized AI models with fallback:

*   **The Shield**: llama-70b → olmo-32b
*   **The Coin**: mistral-24b → dolphin-24b
*   **The Map**: qwen-235b → glm-4
*   **The Frontier**: tongyi-30b → nemotron-12b
*   **The Strategy**: chimera → kimi
*   **The Library**: longcat → gemma-2b
*   **The Commander**: llama-70b → olmo-32b-alt

## 📱 PWA Support

All dashboards are Progressive Web Apps with:
*   Offline support
*   Install to home screen
*   Custom icons per dashboard
*   Service worker caching

## 🛠️ Tools

*   `generate-icons.py` - Generate PWA icons from static assets
*   `rename-dashboards.ps1` - Batch rename dashboard folders
*   `tools/fetchers/unified_fetcher.py` - Central data fetching

## 📄 License

MIT License - See individual dashboard folders for specific licensing.

## 🌟 Features

*   **Morning Brief**: 30-second daily intelligence summary
*   **Cross-Dashboard Synthesis**: Unified insights across all data sources
*   **Free-Tier Optimization**: Efficient API usage with model fallbacks
*   **Real-Time Updates**: 5-minute refresh intervals
*   **Mobile-First**: Responsive PWA design

Built for clarity, focus, and smarter decision-making.
