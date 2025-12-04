# Unified API Library

> 🚀 **Centralized data fetching, caching, and AI integration for all monorepo apps**

This library eliminates redundant code across the 7 dashboard apps by providing:

- **Unified Data Fetching**: Consistent API calls with built-in caching
- **Centralized AI/LLM Integration**: Single interface for OpenRouter API
- **Shared Caching Layer**: In-memory and persistent caching
- **App-Specific Configurations**: Pre-configured setups for each app

## Quick Start

```javascript
import { fetchCryptoPrices, fetchNews, callAI } from '@monorepo/unified-api';

// Fetch crypto prices (with caching)
const prices = await fetchCryptoPrices(['bitcoin', 'ethereum']);

// Fetch news
const news = await fetchNews({ query: 'crypto market' });

// Call AI for analysis
const analysis = await callAI(
    'Analyze the current market conditions',
    { model: 'grok', systemPrompt: 'You are a market analyst' }
);
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       UNIFIED API LIBRARY                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  fetchers.js │  │ ai-service.js│  │   cache.js   │           │
│  │              │  │              │  │              │           │
│  │ • fetchNews  │  │ • callAI     │  │ • getCached  │           │
│  │ • fetchCrypto│  │ • TEMPLATES  │  │ • setCache   │           │
│  │ • fetchFRED  │  │ • parseJSON  │  │ • memoize    │           │
│  │ • fetcharXiv │  │ • generators │  │ • clearCache │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      index.js                             │   │
│  │  • createAppFetcher() - App-specific pre-configured      │   │
│  │  • createReport() - Unified report structure             │   │
│  │  • APP_CONFIGS - Per-app settings                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  ai-race      │  │crash-detector │  │ hyper-        │
│               │  │               │  │ analytical    │
└───────────────┘  └───────────────┘  └───────────────┘
```

## Data Sources

| Source | Function | TTL |
|--------|----------|-----|
| NewsAPI | `fetchNews()` | 10 min |
| CoinGecko | `fetchCryptoPrices()` | 1 min |
| Fear & Greed | `fetchFearAndGreed()` | 15 min |
| Treasury API | `fetchTreasuryAuction()` | 5 min |
| FRED | `fetchFREDData()` | 1 hour |
| arXiv | `fetchArxivPapers()` | 1 hour |
| RSS Feeds | `fetchRSSNews()` | 10 min |

## AI Integration

### Models Available

```javascript
const AI_MODELS = {
    grok: 'x-ai/grok-4.1-fast:free',
    chimera: 'tngtech/tng-r1t-chimera:free',
    gpt: 'openai/gpt-oss-20b:free'
};
```

### Pre-Built Generators

```javascript
import { 
    generateMarketAnalysis,
    generateResearchBriefing,
    generateCrashAnalysis,
    generateCryptoOutlook 
} from '@monorepo/unified-api';

// Generate market analysis
const analysis = await generateMarketAnalysis(marketData);

// Generate crash analysis
const risk = await generateCrashAnalysis({ metrics, news });
```

## App-Specific Fetcher

```javascript
import { createAppFetcher } from '@monorepo/unified-api';

// Create app-specific fetcher with pre-configured settings
const fetcher = createAppFetcher('crash-detector');

// Fetch all data the app needs
const data = await fetcher.fetchAll();

// Get AI analysis
const analysis = await fetcher.getAnalysis(data, 'crash');

// Clear cache for this app
fetcher.clearCache();
```

## Caching

### In-Memory Cache

```javascript
import { getCached, setCache, memoize } from '@monorepo/unified-api';

// Manual caching
setCache('my-key', data, 60000); // TTL in ms
const cached = getCached('my-key');

// Automatic memoization
const memoizedFetch = memoize(async () => {
    return await expensiveOperation();
}, 'operation-cache-key');
```

### Persistent Cache (localStorage)

```javascript
import { PersistentCache } from '@monorepo/unified-api';

const cache = new PersistentCache({ prefix: 'myapp' });
cache.set('preferences', { theme: 'dark' });
const prefs = cache.get('preferences');
```

## Environment Variables

The following API keys should be set (typically as GitHub Secrets):

| Variable | Required | Used For |
|----------|----------|----------|
| `OPENROUTER_KEY` | For AI | AI/LLM analysis |
| `NEWS_API_KEY` | For news | NewsAPI |
| `FRED_API_KEY` | For FRED | Economic data |
| `ALPHA_VANTAGE_KEY` | Optional | Stock quotes |
| `COINMARKETCAP_KEY` | Optional | Crypto data |

## Python Unified Fetcher

The companion Python script `tools/fetchers/unified_fetcher.py` runs during CI/CD:

```bash
# Fetch data for all apps
python unified_fetcher.py --all

# Fetch for specific app
python unified_fetcher.py --app crash-detector

# Dry run
python unified_fetcher.py --dry-run
```

This script:
1. Runs once during GitHub Actions workflow
2. Outputs data to `data/{app-name}/latest.json`
3. Also outputs to app-specific locations (e.g., `mission_data.json`)
4. All apps share the fetched data (no redundant API calls!)

## Migration from data-layer

The old `@monorepo/data-layer` library still works but shows deprecation warnings:

```javascript
// Old (still works, but deprecated)
import { fetchData } from '@monorepo/data-layer';

// New (recommended)
import { fetchWithRetry } from '@monorepo/unified-api';
```

## Report Structure

All apps use a unified report format:

```javascript
import { createReport } from '@monorepo/unified-api';

const report = createReport('crash-detector', {
    metrics: [...],
    risk: { score: 75, level: 'ELEVATED' }
}, aiAnalysis);

// Output:
{
    meta: {
        app: 'crash-detector',
        version: '1.0.0',
        generatedAt: '2024-12-04T12:00:00.000Z',
        source: 'unified-api'
    },
    data: { metrics, risk },
    analysis: '...',
    timestamp: 1701691200000
}
```
