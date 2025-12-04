# 📊 Dashboard Orchestrator Pro

Your centralized AI-powered command center for tracking crypto, markets, economics, research, and AI breakthroughs. Now with PWA support!

## 🚀 Features

- **Daily AI Briefs** - Automated analysis at 1 PM UTC using OpenRouter AI
- **Multi-Dashboard Integration** - Aggregates 6+ data sources
- **GitHub Pages Hosting** - Fast, reliable, and free
- **PWA Support** - Install as a native app on mobile and desktop
- **Historical Archive** - All briefs saved in `/briefs` directory
- **One-Click Access** - Links to all source dashboards

## 📋 Setup Instructions

1. **Create GitHub Repository**
   ```bash
   git clone https://github.com/kaledh4/Dashboard-Orchestrator-Pro
   cd Dashboard-Orchestrator-Pro
   ```

2. **Add OpenRouter API Key**
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `OPENROUTER_API_KEY`
   - Value: Your OpenRouter API key

3. **Configure Dashboard URLs**
   - Edit `scripts/generate-brief.js`
   - Update the `DASHBOARDS` object with your actual URLs

4. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: main / (root)
   - Save

5. **Test the Workflow**
   ```bash
   npm install
   npm run test
   ```

## 📱 PWA Installation

1. Open the deployed site in your browser
2. Click the "Install" icon in the address bar (Desktop) or "Add to Home Screen" (Mobile)
3. Enjoy the native app experience!

## 🔧 Manual Trigger

Go to Actions → Daily Dashboard Orchestrator → Run workflow

## 📅 Schedule

Runs automatically every day at 1 PM UTC (adjust cron in `.github/workflows/daily-brief.yml`)

## 📁 Project Structure

```
dashboard-orchestrator-pro/
├── .github/workflows/
│   └── daily-brief.yml
├── scripts/
│   └── generate-brief.js
├── briefs/
│   └── ...
├── index.html
├── manifest.json
├── sw.js
├── package.json
└── README.md
```

## 🛠️ Customization

- **Change AI Model**: Edit `model` in generate-brief.js
- **Adjust Schedule**: Modify cron expression in workflow
- **Styling**: Update HTML template in generate-brief.js

## 📝 License

MIT License - Free to use and modify
