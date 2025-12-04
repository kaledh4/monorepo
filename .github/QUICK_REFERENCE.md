# Daily Alpha Loop - Quick Reference

## 🚀 Quick Commands

### Development
```bash
# Install dependencies
npm install
cd tools && pip install -r requirements.txt

# Fetch data for all apps
python tools/fetchers/unified_fetcher.py --all

# Fetch for specific app
python tools/fetchers/unified_fetcher.py --app the-shield

# Build all apps
npm run build

# Build specific app
npm run build:the-shield
npm run build:the-coin
# ...etc
```

### Git Operations
```bash
# Check status
git status

# Add and commit changes
git add .
git commit -m "Your message"

# Push to repository
git push origin master

# Pull latest changes
git pull origin master
```

---

## 📦 App Name Mapping

| Display Name | Folder Name | Mission |
|-------------|-------------|---------|
| The Shield | `the-shield` | Market Fragility Monitor |
| The Coin | `the-coin` | Crypto Momentum Scanner |
| The Map | `the-map` | Macro & TASI Trendsetter |
| The Frontier | `the-frontier` | Silicon Frontier Watch |
| The Strategy | `the-strategy` | Unified Opportunity Radar |
| The Library | `the-library` | Alpha-Clarity Archive |
| The Commander | `the-commander` | Master Orchestrator |

---

## 🔑 Required Environment Variables

```bash
# For local development
export OPENROUTER_KEY="your_openrouter_api_key"
export NEWS_API_KEY="your_news_api_key"
export FRED_API_KEY="your_fred_api_key"

# Optional
export ALPHA_VANTAGE_KEY="your_alpha_vantage_key"
export COINMARKETCAP_KEY="your_coinmarketcap_key"
export COINGECKO_KEY="your_coingecko_key"
```

---

## 🔄 Data Fetcher Usage

```bash
# Fetch everything
python tools/fetchers/unified_fetcher.py --all

# Fetch specific apps
python tools/fetchers/unified_fetcher.py --app the-shield
python tools/fetchers/unified_fetcher.py --app the-coin
python tools/fetchers/unified_fetcher.py --app the-map
python tools/fetchers/unified_fetcher.py --app the-frontier
python tools/fetchers/unified_fetcher.py --app the-strategy
python tools/fetchers/unified_fetcher.py --app the-library
python tools/fetchers/unified_fetcher.py --app the-commander

# Dry run (see what would be fetched)
python tools/fetchers/unified_fetcher.py --dry-run

# Fetch specific data types
python tools/fetchers/unified_fetcher.py --type market,news,crypto
python tools/fetchers/unified_fetcher.py --type arxiv
```

---

## 🌐 Live URLs

**Base:** https://kaledh4.github.io/daily-alpha-loop/

- 🛡️ **The Shield:** https://kaledh4.github.io/daily-alpha-loop/the-shield/
- 🪙 **The Coin:** https://kaledh4.github.io/daily-alpha-loop/the-coin/
- 🗺️ **The Map:** https://kaledh4.github.io/daily-alpha-loop/the-map/
- 🚀 **The Frontier:** https://kaledh4.github.io/daily-alpha-loop/the-frontier/
- 📊 **The Strategy:** https://kaledh4.github.io/daily-alpha-loop/the-strategy/
- 📚 **The Library:** https://kaledh4.github.io/daily-alpha-loop/the-library/
- 🎖️ **The Commander:** https://kaledh4.github.io/daily-alpha-loop/the-commander/

---

## 🔐 GitHub Secrets Setup

1. Go to repository **Settings**
2. Navigate to **Secrets and variables** → **Actions**
3. Add the following secrets:

### Required Secrets
- `OPENROUTER_KEY` - Get from https://openrouter.ai/keys
- `NEWS_API_KEY` - Get from https://newsapi.org/
- `FRED_API_KEY` - Get from https://fred.stlouisfed.org/docs/api/api_key.html

### Optional Secrets
- `ALPHA_VANTAGE_KEY` - Get from https://www.alphavantage.co/support/#api-key
- `COINMARKETCAP_KEY` - Get from https://coinmarketcap.com/api/
- `COINGECKO_KEY` - Get from https://www.coingecko.com/en/api/pricing

---

## 📂 Important Files

### Configuration
- `nx.json` - Nx workspace configuration
- `package.json` - Node dependencies and scripts
- `tools/requirements.txt` - Python dependencies

### Workflows
- `.github/workflows/build-deploy.yml` - Main CI/CD pipeline
- `.github/workflows/daily_alpha_loop.yml` - Scheduled data updates

### Core Scripts
- `tools/fetchers/unified_fetcher.py` - Central data fetching
- `scripts/build-all.js` - Build orchestration
- `scripts/build-app.mjs` - Individual app builder
- `scripts/build-vite-app.mjs` - Vite app builder

### Shared Libraries
- `libs/shared-keys/index.js` - API key management
- `libs/shared-pwa/index.js` - PWA utilities
- `libs/unified-api/index.js` - Data fetching API
- `libs/data-layer/index.js` - Legacy compatibility

---

## 🐛 Common Issues & Solutions

### Issue: Build fails with "API key not found"
**Solution:** Add keys to GitHub Secrets (for CI/CD) or environment variables (for local)

### Issue: Data not updating
**Solution:** 
```bash
# Manually run the fetcher
python tools/fetchers/unified_fetcher.py --all

# Check if data files are created
ls -la data/*/
```

### Issue: PWA not installing
**Solution:**
- Ensure you're on HTTPS
- Clear browser cache
- Check browser console for manifest errors
- Verify `manifest.json` and service worker are accessible

### Issue: Git push rejected
**Solution:**
```bash
# Pull latest changes first
git pull origin master --allow-unrelated-histories

# Resolve conflicts if any
git add .
git commit -m "Merge conflicts resolved"
git push origin master
```

---

## 📊 Monitoring & Logs

### GitHub Actions
- Go to repository → **Actions** tab
- View workflow runs
- Check individual job logs
- Download artifacts

### Local Testing
```bash
# Test data fetcher
python tools/fetchers/unified_fetcher.py --app the-shield

# Serve app locally
npx http-server apps/the-shield -p 8080

# Check build output
npm run build:the-shield
ls -la apps/the-shield/dist/
```

---

## ⏰ Scheduled Operations

### Data Updates
- **Frequency:** Hourly
- **Time Window:** 1:00 AM - 6:00 AM UTC
- **Trigger:** GitHub Actions cron schedule
- **Script:** `unified_fetcher.py --all`

### Build & Deploy
- **On push** to `master` branch
- **Manual trigger** via GitHub Actions
- **Scheduled** during update window

---

## 🔄 Update Workflow

1. **Local Development:**
   ```bash
   # Make changes to app
   cd apps/the-shield
   # Edit files...
   
   # Test locally
   cd ../..
   python tools/fetchers/unified_fetcher.py --app the-shield
   npm run build:the-shield
   ```

2. **Commit & Push:**
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push origin master
   ```

3. **Verify Deployment:**
   - Go to GitHub Actions tab
   - Wait for workflow completion
   - Check live URL

---

## 📞 Support Resources

- **Nx Documentation:** https://nx.dev/getting-started/intro
- **OpenRouter API:** https://openrouter.ai/docs
- **yfinance Docs:** https://pypi.org/project/yfinance/
- **NewsAPI Docs:** https://newsapi.org/docs
- **FRED API Docs:** https://fred.stlouisfed.org/docs/api/

---

## 🎯 Dashboard Priorities

### Must-Have Data Sources
- ✅ Market data (yfinance)
- ✅ Treasury data (fiscal API)
- ✅ News feeds (RSS/NewsAPI)
- ✅ AI analysis (OpenRouter)

### Nice-to-Have
- arXiv research papers
- Fear & Greed Index
- Alternative data sources
- Social sentiment

---

**Last Updated:** 2025-12-04  
**Repository:** https://github.com/kaledh4/daily-alpha-loop
