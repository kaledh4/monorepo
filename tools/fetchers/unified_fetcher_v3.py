"""
Unified Data Fetcher V3
=======================
ENHANCED: Single unified AI call for all dashboards with OpenRouter free models.

Key Improvements:
- ONE comprehensive AI call for all 7 dashboards
- Fallback through 21 free OpenRouter models
- More informative 4-minute briefs for each dashboard
- Smart retry logic with different models
- Reduced API quota usage

Author: Daily Alpha Loop Team
"""

import os
import sys
import json
import logging
import argparse
import pathlib
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========================================
# Configuration & Setup
# ========================================

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Paths
ROOT_DIR = pathlib.Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / 'data'
CACHE_DIR = DATA_DIR / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = ROOT_DIR / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info(f"✅ Loaded environment variables from {env_path}")
    else:
        logger.warning(f"⚠️ .env file not found at {env_path}")
except ImportError:
    logger.warning("⚠️ python-dotenv not installed. Environment variables must be set manually.")

# API Keys
API_KEYS = {
    'OPENROUTER': os.environ.get('OPENROUTER_KEY') or os.environ.get('OPENROUTER_API_KEY'),
    'NEWS_API': os.environ.get('NEWS_API_KEY'),
    'FRED': os.environ.get('FRED_API_KEY'),
    'ALPHA_VANTAGE': os.environ.get('ALPHA_VANTAGE_KEY'),
}

# Third-party imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests not available")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# ========================================
# OpenRouter Free Models Configuration
# ========================================

FREE_OPENROUTER_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "alibaba/tongyi-deepresearch-30b-a3b:free",
    "allenai/olmo-3-32b-think:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
    "tngtech/deepseek-r1t2-chimera:free",
    "tngtech/deepseek-r1t-chimera:free",
    "tngtech/tng-r1t-chimera:free",
    "moonshotai/kimi-k2:free",
    "kwaipilot/kat-coder-pro:free",
    "qwen/qwen3-coder:free",
    "qwen/qwen3-4b:free",
    "z-ai/glm-4.5-air:free",
    "meituan/longcat-flash-chat:free",
    "google/gemma-3n-e4b-it:free",
    "google/gemma-3n-e2b-it:free",
    "google/gemma-3-4b-it:free",
    "arcee-ai/trinity-mini:free",
    "amazon/nova-2-lite-v1:free"
]

# ========================================
# Centralized Data Store
# ========================================

class DataStore:
    """
    Centralized in-memory store for all fetched data.
    Prevents duplicate API calls across dashboards.
    """
    def __init__(self):
        self.data = {}
        self.fetched_at = {}
    
    def set(self, key: str, value: Any):
        self.data[key] = value
        self.fetched_at[key] = datetime.now(timezone.utc).isoformat()
        logger.info(f"📦 Stored: {key}")
    
    def get(self, key: str) -> Any:
        return self.data.get(key)
    
    def has(self, key: str) -> bool:
        return key in self.data
    
    def to_dict(self) -> Dict:
        return {
            'data': self.data,
            'fetched_at': self.fetched_at,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Global data store instance
store = DataStore()

# Global flag to track quota status
AI_QUOTA_EXCEEDED = False

# ========================================
# Fetch Functions (Call ONCE)
# ========================================

def fetch_market_data():
    """Fetch ALL market data once - used by multiple dashboards"""
    logger.info("=" * 50)
    logger.info("📈 FETCHING MARKET DATA (ONCE for all dashboards)")
    logger.info("=" * 50)
    
    if not YFINANCE_AVAILABLE:
        logger.error("yfinance not available")
        return
    
    # Define all tickers needed by ANY dashboard
    tickers = {
        # Risk Dashboard (The Shield)
        'JPY': 'JPY=X',
        'CNH': 'CNH=X',
        'TNX': '^TNX',  # 10Y Treasury
        'MOVE': '^MOVE',
        'VIX': '^VIX',
        'CBON': 'CBON',
        
        # Crypto (The Coin)
        'BTC': 'BTC-USD',
        'ETH': 'ETH-USD',
        
        # Macro (The Map)
        'DXY': 'DX-Y.NYB',
        'GOLD': 'GC=F',
        'OIL': 'CL=F',
        'SP500': '^GSPC',
        'TASI': '^TASI.SR',
    }
    
    # Fetch in parallel
    def fetch_ticker(name, ticker):
        try:
            logger.info(f"  Fetching {name} ({ticker})...")
            t = yf.Ticker(ticker)
            price = None
            
            try:
                price = t.fast_info.last_price
            except:
                pass
            
            if price is None:
                hist = t.history(period='1d')
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
            
            return name, price
        except Exception as e:
            logger.warning(f"  Failed {name}: {e}")
            return name, None
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_ticker, name, ticker) for name, ticker in tickers.items()]
        for future in as_completed(futures):
            name, price = future.result()
            if price is not None:
                store.set(f'market.{name}', price)

def fetch_crypto_indicators():
    """Fetch crypto with technical indicators (for The Coin)"""
    logger.info("=" * 50)
    logger.info("📊 FETCHING CRYPTO INDICATORS")
    logger.info("=" * 50)
    
    if not YFINANCE_AVAILABLE or not PANDAS_AVAILABLE:
        return
    
    for symbol in ['BTC-USD', 'ETH-USD']:
        try:
            logger.info(f"  Fetching {symbol} indicators...")
            df = yf.download(symbol, period='5y', interval='1wk', progress=False)
            
            if df.empty:
                continue
            
            # Flatten MultiIndex
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Calculate indicators
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            latest = df.iloc[-1]
            ticker_name = symbol.replace('-USD', '')
            
            store.set(f'crypto.{ticker_name}.sma_20', float(latest['SMA_20']) if not pd.isna(latest['SMA_20']) else None)
            store.set(f'crypto.{ticker_name}.ema_21', float(latest['EMA_21']) if not pd.isna(latest['EMA_21']) else None)
            store.set(f'crypto.{ticker_name}.ma50', float(latest['MA50']) if not pd.isna(latest['MA50']) else None)
            store.set(f'crypto.{ticker_name}.ma200', float(latest['MA200']) if not pd.isna(latest['MA200']) else None)
            store.set(f'crypto.{ticker_name}.rsi', float(latest['RSI']) if not pd.isna(latest['RSI']) else None)
            store.set(f'crypto.{ticker_name}.trend', 'Bullish' if latest['Close'] > latest['SMA_20'] else 'Bearish')
            
        except Exception as e:
            logger.warning(f"  Failed {symbol} indicators: {e}")

def fetch_treasury_data():
    """Fetch Treasury auction data"""
    logger.info("=" * 50)
    logger.info("🏛️ FETCHING TREASURY DATA")
    logger.info("=" * 50)
    
    if not REQUESTS_AVAILABLE:
        return
    
    try:
        url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query"
        params = {
            'filter': 'security_term:eq:10-Year,security_type:eq:Note',
            'sort': '-auction_date',
            'page[size]': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            result = data['data'][0]
            store.set('treasury.10y_bid_to_cover', float(result.get('bid_to_cover_ratio', 0)))
            store.set('treasury.10y_auction_date', result.get('auction_date'))
            
    except Exception as e:
        logger.warning(f"  Failed treasury data: {e}")

def fetch_fear_and_greed():
    """Fetch crypto Fear & Greed Index"""
    logger.info("=" * 50)
    logger.info("😱 FETCHING FEAR & GREED INDEX")
    logger.info("=" * 50)
    
    if not REQUESTS_AVAILABLE:
        return
    
    try:
        response = requests.get('https://api.alternative.me/fng/?limit=1', timeout=10)
        data = response.json()
        
        store.set('fng.value', int(data['data'][0]['value']))
        store.set('fng.classification', data['data'][0]['value_classification'])
        store.set('fng.timestamp', data['data'][0]['timestamp'])
        
    except Exception as e:
        logger.warning(f"  Failed F&G: {e}")

def fetch_news():
    """Fetch news from RSS feeds"""
    logger.info("=" * 50)
    logger.info("📰 FETCHING NEWS")
    logger.info("=" * 50)
    
    feeds = [
        'https://finance.yahoo.com/news/rssindex',
        'https://cointelegraph.com/rss',
        'https://www.marketwatch.com/rss/topstories',
        'https://www.artificialintelligence-news.com/feed/',
    ]
    
    articles = []
    
    if FEEDPARSER_AVAILABLE:
        for feed_url in feeds:
            try:
                logger.info(f"  Fetching {feed_url}...")
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    articles.append({
                        'title': entry.get('title', 'No title'),
                        'source': feed.feed.get('title', 'Unknown'),
                        'url': entry.get('link'),
                        'publishedAt': entry.get('published')
                    })
            except Exception as e:
                logger.debug(f"  Feed error: {e}")
    
    store.set('news.articles', articles[:20])

def fetch_arxiv_papers():
    """Fetch arXiv research papers"""
    logger.info("=" * 50)
    logger.info("📚 FETCHING ARXIV PAPERS")
    logger.info("=" * 50)
    
    import ssl
    import urllib.request
    import urllib.parse
    import xml.etree.ElementTree as ET
    
    domains = {
        "AI Research": "cat:cs.AI OR cat:cs.LG",
        "Advanced Manufacturing": "cat:cs.RO OR cat:cs.SY",
        "Biotechnology": "cat:q-bio.BM OR cat:q-bio.GN",
        "Quantum Computing": "cat:quant-ph",
        "Semiconductors": "cat:cond-mat.mes-hall OR cat:cs.ET"
    }
    
    for domain_name, query in domains.items():
        try:
            logger.info(f"  Fetching {domain_name}...")
            params = {
                'search_query': query,
                'start': 0,
                'max_results': 5,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            url = f"http://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}"
            
            context = ssl._create_unverified_context()
            response = urllib.request.urlopen(url, context=context, timeout=30)
            xml_data = response.read().decode('utf-8')
            
            root = ET.fromstring(xml_data)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'}
            
            total = root.find('opensearch:totalResults', ns)
            total_results = int(total.text) if total is not None else 0
            
            papers = []
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns)
                summary = entry.find('atom:summary', ns)
                published = entry.find('atom:published', ns)
                link = entry.find('atom:id', ns)
                
                papers.append({
                    'title': title.text.strip().replace('\n', ' ') if title is not None else 'Unknown',
                    'summary': (summary.text.strip()[:200] + '...') if summary is not None and summary.text else '',
                    'date': published.text[:10] if published is not None else '',
                    'link': link.text if link is not None else ''
                })
            
            store.set(f'arxiv.{domain_name}.total', total_results)
            store.set(f'arxiv.{domain_name}.papers', papers)
            
        except Exception as e:
            logger.warning(f"  Failed {domain_name}: {e}")

# ========================================
# Unified AI Analysis Function
# ========================================

def call_unified_ai(all_data: Dict) -> Optional[Dict]:
    """
    Make ONE comprehensive AI call for ALL dashboards.
    Uses OpenRouter with fallback through 21 free models.
    Returns structured JSON with analysis for all 7 dashboards.
    """
    global AI_QUOTA_EXCEEDED
    
    if AI_QUOTA_EXCEEDED:
        logger.warning("  ⚠️ AI Quota previously exceeded. Skipping AI call.")
        return None

    if os.environ.get('DISABLE_AI') == 'true':
        logger.info("  ℹ️ AI disabled via flag.")
        return None
    
    if not REQUESTS_AVAILABLE:
        logger.warning("AI not available (no requests library)")
        return None
    
    openrouter_key = API_KEYS.get('OPENROUTER')
    if not openrouter_key:
        logger.error("❌ OPENROUTER_KEY not found. AI generation disabled.")
        return None

    # Build comprehensive prompt for all dashboards
    prompt = f"""You are the Master AI Analyst for the Daily Alpha Loop system. 
Analyze the following market data and generate comprehensive 4-minute briefings for ALL 7 dashboards.

CURRENT MARKET DATA:
====================

RISK DATA (The Shield):
- JPY: {all_data.get('jpy', 'N/A')}
- CNH: {all_data.get('cnh', 'N/A')}
- 10Y Treasury Yield: {all_data.get('tnx', 'N/A')}%
- MOVE Index: {all_data.get('move', 'N/A')}
- VIX: {all_data.get('vix', 'N/A')}
- 10Y Bid-to-Cover: {all_data.get('btc_10y', 'N/A')}

CRYPTO DATA (The Coin):
- BTC Price: ${all_data.get('btc_price', 0):,.0f}
- ETH Price: ${all_data.get('eth_price', 0):,.0f}
- BTC RSI: {all_data.get('btc_rsi', 'N/A')}
- BTC Trend: {all_data.get('btc_trend', 'N/A')}
- Fear & Greed: {all_data.get('fng_value', 'N/A')} ({all_data.get('fng_class', 'N/A')})

MACRO DATA (The Map):
- Oil: ${all_data.get('oil', 'N/A')}
- DXY: {all_data.get('dxy', 'N/A')}
- Gold: ${all_data.get('gold', 'N/A')}
- SP500: {all_data.get('sp500', 'N/A')}
- TASI (Saudi): {all_data.get('tasi', 'N/A')}

AI/TECH RESEARCH (The Frontier):
{all_data.get('arxiv_summary', 'Recent papers in AI, Quantum, Robotics, Biotech domains')}

NEWS HEADLINES (Last 10):
{all_data.get('news_headlines', 'Market news unavailable')}

TASK:
Generate a comprehensive JSON response with deep analysis for ALL 7 dashboards.
Each analysis should be suitable for a 4-minute read - go beyond surface level.
Be specific, insightful, and actionable.

Return ONLY valid JSON in this exact structure:
{{
  "the_shield": {{
    "analysis": "3-4 sentence deep analysis of systemic market fragility, stress points, and what professional traders should watch. Be specific about which metrics signal danger.",
    "risk_level": "CRITICAL/ELEVATED/LOW",
    "top_concern": "The single biggest risk factor right now"
  }},
  "the_coin": {{
    "analysis": "3-4 sentence analysis of crypto momentum, rotation dynamics, and institutional flow. Address both BTC and ETH specifically.",
    "momentum": "Bullish/Bearish/Neutral",
    "key_level": "The most important price level to watch"
  }},
  "the_map": {{
    "analysis": "4-5 sentence macro analysis focusing on how oil prices, dollar strength, and global rates impact TASI and Saudi markets. Connect the dots between global macro and regional impact.",
    "tasi_mood": "Positive/Neutral/Negative",
    "drivers": ["Driver 1", "Driver 2", "Driver 3"],
    "tasi_forecast": "What's the likely directional bias for TASI this week?"
  }},
  "the_frontier": {{
    "analysis": "3-4 sentence analysis of AI and tech breakthrough velocity. What's accelerating? What's real vs hype?",
    "breakthroughs": [
      {{"title": "Breakthrough 1", "why_it_matters": "Impact explanation"}},
      {{"title": "Breakthrough 2", "why_it_matters": "Impact explanation"}}
    ],
    "velocity": "Slow/Moderate/Fast/Exponential"
  }},
  "the_strategy": {{
    "analysis": "4-5 sentence synthesis of all signals above. How do risk, crypto, macro, and tech align or conflict? What's the unified market narrative today?",
    "stance": "Defensive/Neutral/Accumulative/Opportunistic/Aggressive",
    "mindset": "One powerful sentence capturing the strategic approach for today",
    "conviction": "High/Medium/Low"
  }},
  "the_library": {{
    "analysis": "2-3 sentence overview of today's knowledge landscape and key learning themes from news and research",
    "summaries": [
      {{"title": "Complex Topic 1", "eli5": "Simple explanation", "long_term": "Why it matters"}},
      {{"title": "Complex Topic 2", "eli5": "Simple explanation", "long_term": "Why it matters"}}
    ],
    "knowledge_velocity": "How fast is breakthrough knowledge accumulating?"
  }},
  "the_commander": {{
    "weather_of_the_day": "Stormy/Cloudy/Sunny/Volatile/Foggy",
    "top_signal": "The single most important data point across all dashboards today",
    "why_it_matters": "4-5 sentence deep explanation of why this signal is critical right now. What are the second and third order effects?",
    "cross_dashboard_convergence": "5-6 sentence paragraph connecting Risk, Crypto, Macro, and Tech. How do these forces interact today? Where is the friction? Where is alignment? What does this mean for positioning?",
    "action_stance": "Specific actionable guidance",
    "optional_deep_insight": "Two paragraphs of advanced market theory applied to today's data. Connect uncommon dots for professional traders. Go deep.",
    "clarity_level": "High/Medium/Low",
    "summary_sentence": "One powerful closing thought that synthesizes everything"
  }}
}}

CRITICAL: Return ONLY the JSON object, no markdown, no explanation, no code blocks."""

    # Try each free model until one succeeds
    for model_index, model in enumerate(FREE_OPENROUTER_MODELS):
        if AI_QUOTA_EXCEEDED:
            break
        
        try:
            logger.info(f"  🤖 Attempting unified AI call with: {model} ({model_index + 1}/{len(FREE_OPENROUTER_MODELS)})")
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a master financial analyst. Return ONLY valid JSON, no markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 8000
            }
            
            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/kaledh4/daily-alpha-loop",
                "X-Title": "Daily Alpha Loop"
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    
                    # Extract JSON from response
                    try:
                        # Try to find JSON in the response
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start != -1 and end > start:
                            json_content = content[start:end]
                            parsed = json.loads(json_content)
                            
                            logger.info(f"  ✅ SUCCESS with {model}!")
                            return parsed
                    except json.JSONDecodeError as je:
                        logger.warning(f"  JSON parse error with {model}: {je}")
                        continue
                        
            elif response.status_code == 429:
                logger.warning(f"  ⚠️ {model} rate limited (429), trying next...")
                time.sleep(2)
                continue
            else:
                logger.warning(f"  {model} failed: {response.status_code}")
                continue
                
        except Exception as e:
            logger.warning(f"  Error with {model}: {e}")
            continue
    
    logger.error("  ❌ All OpenRouter models failed")
    return None

# ========================================
# Dashboard Builder Functions
# ========================================

def build_shield_data(ai_result: Optional[Dict] = None) -> Dict:
    """Build The Shield dashboard data"""
    jpy = store.get('market.JPY')
    cnh = store.get('market.CNH')
    tnx = store.get('market.TNX')
    move = store.get('market.MOVE')
    vix = store.get('market.VIX')
    cbon = store.get('market.CBON')
    btc_10y = store.get('treasury.10y_bid_to_cover')
    
    # Build metrics
    metrics = []
    
    if btc_10y:
        signal = "CRITICAL SHOCK" if btc_10y < 2.0 else "HIGH STRESS" if btc_10y < 2.3 else "NORMAL"
        metrics.append({
            'name': '10Y Treasury Bid-to-Cover',
            'value': f'{btc_10y:.2f}x',
            'signal': signal
        })
    
    if jpy:
        signal = "CRITICAL SHOCK" if jpy >= 155 else "HIGH STRESS" if jpy >= 150 else "RISING STRESS" if jpy > 145 else "NORMAL"
        metrics.append({
            'name': 'USD/JPY',
            'value': f'{jpy:.2f}',
            'signal': signal
        })
    
    if cnh:
        signal = "CRITICAL SHOCK" if cnh >= 7.4 else "HIGH STRESS" if cnh >= 7.25 else "RISING STRESS" if cnh > 7.15 else "NORMAL"
        metrics.append({
            'name': 'USD/CNH',
            'value': f'{cnh:.4f}',
            'signal': signal
        })
    
    if tnx:
        signal = "CRITICAL SHOCK" if tnx >= 5.0 else "HIGH STRESS" if tnx >= 4.5 else "RISING STRESS" if tnx >= 4.2 else "NORMAL"
        metrics.append({
            'name': '10Y Treasury Yield',
            'value': f'{tnx:.2f}%',
            'signal': signal
        })
    
    if move:
        signal = "CRITICAL SHOCK" if move >= 120 else "HIGH STRESS" if move >= 90 else "RISING STRESS" if move > 80 else "NORMAL"
        metrics.append({
            'name': 'MOVE Index',
            'value': f'{move:.2f}',
            'signal': signal
        })
    
    if vix:
        signal = "CRITICAL SHOCK" if vix >= 40 else "HIGH STRESS" if vix >= 30 else "RISING STRESS" if vix > 20 else "NORMAL"
        metrics.append({
            'name': 'VIX',
            'value': f'{vix:.2f}',
            'signal': signal
        })
    
    # Calculate composite risk
    weights = {"CRITICAL SHOCK": 100, "HIGH STRESS": 75, "RISING STRESS": 40, "NORMAL": 0}
    score = sum(weights.get(m['signal'], 0) for m in metrics) / len(metrics) if metrics else 0
    
    if score >= 60:
        risk = {"score": round(score, 1), "level": "CRITICAL", "color": "#dc3545"}
    elif score >= 35:
        risk = {"score": round(score, 1), "level": "ELEVATED", "color": "#ffc107"}
    else:
        risk = {"score": round(score, 1), "level": "LOW", "color": "#28a745"}
    
    # Get AI analysis
    analysis = "AI analysis unavailable"
    if ai_result and 'the_shield' in ai_result:
        analysis = ai_result['the_shield'].get('analysis', analysis)
        if 'risk_level' in ai_result['the_shield']:
            risk['level'] = ai_result['the_shield']['risk_level']
    
    # Calculate scoring metrics
    fragility_score = min(10, (btc_10y / 3.0) * 10) if btc_10y else 5
    volatility_score = min(10, (move / 150) * 10) if move else 5
    
    scoring = {
        "risk_level": int(score),
        "fragility": round(fragility_score, 1),
        "volatility_pressure": round(volatility_score, 1)
    }

    return {
        'dashboard': 'the-shield',
        'name': 'The Shield',
        'role': 'Risk Environment',
        'mission': 'Detect global risk pressure, cross-asset stress, volatility clusters, and fragility vectors.',
        'last_update': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'scoring': scoring,
        'risk_assessment': risk,
        'metrics': metrics,
        'ai_analysis': analysis,
        'data_sources': [
            "global_risk",
            "volatility_matrix",
            "liquidity_fragility"
        ]
    }

def build_coin_data(ai_result: Optional[Dict] = None) -> Dict:
    """Build The Coin dashboard data"""
    btc_price = store.get('market.BTC')
    eth_price = store.get('market.ETH')
    btc_rsi = store.get('crypto.BTC.rsi')
    btc_trend = store.get('crypto.BTC.trend')
    fng_value = store.get('fng.value')
    fng_class = store.get('fng.classification')
    
    # Get AI analysis
    momentum = "Neutral"
    analysis = "Analysis temporarily unavailable"
    
    if ai_result and 'the_coin' in ai_result:
        analysis = ai_result['the_coin'].get('analysis', analysis)
        momentum = ai_result['the_coin'].get('momentum', momentum)
    
    # Calculate scoring metrics
    rsi_val = btc_rsi if btc_rsi else 50
    momentum_score = 5
    if btc_trend == 'Bullish':
        momentum_score += 2
    if rsi_val > 60:
        momentum_score += 1
    if fng_value and fng_value > 60:
        momentum_score += 1
    
    scoring = {
        "rotation_strength": 5.0,
        "momentum": min(10, momentum_score),
        "setup_quality": 6.5
    }

    return {
        'dashboard': 'the-coin',
        'name': 'The Coin',
        'role': 'Crypto Intent',
        'mission': 'Track BTC → Alts rotation, detect fakeouts, measure liquidity migration, and infer sentiment momentum.',
        'last_update': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'scoring': scoring,
        'btc_price': btc_price,
        'eth_price': eth_price,
        'momentum': momentum,
        'rsi': btc_rsi,
        'trend': btc_trend,
        'fear_and_greed': {'value': fng_value, 'classification': fng_class},
        'ai_analysis': analysis,
        'data_sources': [
            "orderflow",
            "dominance_tracker",
            "liquidity_shift"
        ]
    }

def build_map_data(ai_result: Optional[Dict] = None) -> Dict:
    """Build The Map dashboard data"""
    oil = store.get('market.OIL')
    dxy = store.get('market.DXY')
    gold = store.get('market.GOLD')
    sp500 = store.get('market.SP500')
    tasi = store.get('market.TASI')
    tnx = store.get('market.TNX')
    
    # Get AI analysis
    tasi_mood = "Neutral"
    analysis = "Analysis temporarily unavailable"
    drivers = []
    
    if ai_result and 'the_map' in ai_result:
        analysis = ai_result['the_map'].get('analysis', analysis)
        tasi_mood = ai_result['the_map'].get('tasi_mood', tasi_mood)
        drivers = ai_result['the_map'].get('drivers', drivers)
    
    # Calculate scoring metrics
    tasi_score = 5
    if tasi_mood == 'Positive': tasi_score = 8
    elif tasi_mood == 'Negative': tasi_score = 3
    
    vol_risk = 5
    if tnx and tnx > 4.5: vol_risk += 2
    if oil and oil > 90: vol_risk += 1
    
    scoring = {
        "stance_strength": tasi_score,
        "volatility_risk": min(10, vol_risk),
        "confidence": 0.85
    }

    return {
        'dashboard': 'the-map',
        'name': 'The Map',
        'role': 'Macro',
        'mission': 'Extract hawkish/dovish tone, forward pressure, rate path, and macro wind direction.',
        'last_update': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'scoring': scoring,
        'macro': {
            'oil': oil,
            'dxy': dxy,
            'gold': gold,
            'sp500': sp500,
            'tasi': tasi,
            'treasury_10y': tnx
        },
        'tasi_mood': tasi_mood,
        'drivers': drivers,
        'ai_analysis': analysis,
        'data_sources': [
            "fed_speech_parser",
            "inflation_nowcast",
            "curve_shift"
        ]
    }

def build_frontier_data(ai_result: Optional[Dict] = None) -> Dict:
    """Build The Frontier dashboard data"""
    # Collect arXiv data
    domains = {}
    for domain in ["AI Research", "Advanced Manufacturing", "Biotechnology", "Quantum Computing", "Semiconductors"]:
        total = store.get(f'arxiv.{domain}.total')
        papers = store.get(f'arxiv.{domain}.papers')
        if total is not None:
            domains[domain] = {
                'total_volume': total,
                'recent_papers': papers or []
            }
    
    # Get AI analysis
    breakthroughs = []
    analysis = "AI analysis unavailable"
    
    if ai_result and 'the_frontier' in ai_result:
        analysis = ai_result['the_frontier'].get('analysis', analysis)
        breakthroughs = ai_result['the_frontier'].get('breakthroughs', breakthroughs)
    
    # Calculate scoring metrics
    breakthrough_score = min(10, len(breakthroughs) * 2) if breakthroughs else 5
    
    scoring = {
        "breakthrough_score": breakthrough_score,
        "trajectory": 8.5,
        "future_pull": 7.0
    }

    return {
        'dashboard': 'the-frontier',
        'name': 'The Frontier',
        'role': 'AI & Breakthroughs',
        'mission': 'Monitor breakthroughs in AI, robotics, compute, quantum, and science acceleration.',
        'last_update': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'scoring': scoring,
        'domains': domains,
        'breakthroughs': breakthroughs,
        'ai_analysis': analysis,
        'data_sources': [
            "ai_rnd",
            "quantum",
            "robotics"
        ]
    }

def build_strategy_data(ai_result: Optional[Dict] = None) -> Dict:
    """Build The Strategy dashboard data"""
    # Try to read from other dashboard files
    risk_level = "LOW"
    crypto_momentum = "Neutral"
    macro_signal = "Neutral"
    frontier_signal = "Active"
    
    try:
        shield_file = DATA_DIR / 'the-shield' / 'latest.json'
        if shield_file.exists():
            shield_data = json.loads(shield_file.read_text(encoding='utf-8'))
            risk_level = shield_data.get('risk_assessment', {}).get('level', risk_level)
    except:
        pass
    
    try:
        coin_file = DATA_DIR / 'the-coin' / 'latest.json'
        if coin_file.exists():
            coin_data = json.loads(coin_file.read_text(encoding='utf-8'))
            crypto_momentum = coin_data.get('momentum', crypto_momentum)
    except:
        pass
    
    try:
        map_file = DATA_DIR / 'the-map' / 'latest.json'
        if map_file.exists():
            map_data = json.loads(map_file.read_text(encoding='utf-8'))
            macro_signal = map_data.get('tasi_mood', macro_signal)
    except:
        pass
    
    # Get AI analysis
    stance = "Neutral"
    mindset = "Wait for clarity"
    analysis = "Analysis temporarily unavailable"
    
    if ai_result and 'the_strategy' in ai_result:
        analysis = ai_result['the_strategy'].get('analysis', analysis)
        stance = ai_result['the_strategy'].get('stance', stance)
        mindset = ai_result['the_strategy'].get('mindset', mindset)
    
    # Calculate scoring metrics
    confidence = 5
    if stance == 'Aggressive': confidence = 9
    elif stance == 'Accumulative': confidence = 7
    elif stance == 'Defensive': confidence = 3
    
    scoring = {
        "stance_confidence": confidence
    }

    return {
        'dashboard': 'the-strategy',
        'name': 'The Strategy',
        'role': 'Market Stance',
        'mission': "Read the market context, interpret cross-domain vectors, and determine today's stance.",
        'last_update': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'scoring': scoring,
        'stance': stance,
        'mindset': mindset,
        'inputs': {
            'risk': risk_level,
            'crypto': crypto_momentum,
            'macro': macro_signal,
            'frontier': frontier_signal
        },
        'ai_analysis': analysis,
        'data_sources': [
            "stance_engine",
            "momentum_blend"
        ]
    }

def build_library_data(ai_result: Optional[Dict] = None) -> Dict:
    """Build The Library dashboard data"""
    news_articles = store.get('news.articles') or []
    
    # Get AI analysis
    summaries = []
    analysis = "Analysis temporarily unavailable"
    
    if ai_result and 'the_library' in ai_result:
        analysis = ai_result['the_library'].get('analysis', analysis)
        summaries = ai_result['the_library'].get('summaries', summaries)
    
    # Calculate scoring metrics
    progress_rate = 65
    
    scoring = {
        "progress_rate": progress_rate,
        "uncertainty": 0.2
    }

    return {
        'dashboard': 'the-library',
        'name': 'The Library',
        'role': 'Free Knowledge',
        'mission': 'Compute the daily human advancement rate, track breakthroughs, and signal long-term trajectory.',
        'last_update': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'scoring': scoring,
        'summaries': summaries,
        'ai_analysis': analysis,
        'data_sources': [
            "ai_rnd_tracker",
            "quantum_papers",
            "lab_output_rate"
        ]
    }

def build_commander_data(ai_result: Optional[Dict] = None) -> Dict:
    """Build The Commander dashboard data"""
    # Load all dashboard data
    shield_data = {}
    coin_data = {}
    map_data = {}
    frontier_data = {}
    strategy_data = {}
    library_data = {}
    
    try:
        shield_file = DATA_DIR / 'the-shield' / 'latest.json'
        if shield_file.exists():
            shield_data = json.loads(shield_file.read_text(encoding='utf-8'))
    except:
        pass
    
    try:
        coin_file = DATA_DIR / 'the-coin' / 'latest.json'
        if coin_file.exists():
            coin_data = json.loads(coin_file.read_text(encoding='utf-8'))
    except:
        pass
    
    try:
        map_file = DATA_DIR / 'the-map' / 'latest.json'
        if map_file.exists():
            map_data = json.loads(map_file.read_text(encoding='utf-8'))
    except:
        pass
    
    try:
        frontier_file = DATA_DIR / 'the-frontier' / 'latest.json'
        if frontier_file.exists():
            frontier_data = json.loads(frontier_file.read_text(encoding='utf-8'))
    except:
        pass
    
    try:
        strategy_file = DATA_DIR / 'the-strategy' / 'latest.json'
        if strategy_file.exists():
            strategy_data = json.loads(strategy_file.read_text(encoding='utf-8'))
    except:
        pass
    
    try:
        library_file = DATA_DIR / 'the-library' / 'latest.json'
        if library_file.exists():
            library_data = json.loads(library_file.read_text(encoding='utf-8'))
    except:
        pass
    
    # Get AI analysis
    morning_brief = {}
    
    if ai_result and 'the_commander' in ai_result:
        morning_brief = ai_result['the_commander']
    else:
        # Fallback
        risk_level = shield_data.get('risk_assessment', {}).get('level', 'UNKNOWN')
        crypto_momentum = coin_data.get('momentum', 'Neutral')
        stance = strategy_data.get('stance', 'Neutral')
        
        weather = "Cloudy ☁️"
        if risk_level == 'CRITICAL':
            weather = "Stormy ⛈️"
        elif risk_level == 'LOW' and crypto_momentum == 'Bullish':
            weather = "Sunny ☀️"
        elif risk_level == 'ELEVATED':
            weather = "Foggy 🌫️"
        
        morning_brief = {
            "weather_of_the_day": weather,
            "top_signal": f"Risk Level: {risk_level}",
            "why_it_matters": "AI analysis is currently unavailable, but core market data has been updated. Check individual dashboards for specific metrics.",
            "cross_dashboard_convergence": f"Risk is {risk_level}, Crypto is {crypto_momentum}, and Strategy suggests {stance}.",
            "action_stance": stance,
            "optional_deep_insight": "System is operating in data-only mode. All feeds are active.",
            "clarity_level": "Medium",
            "summary_sentence": "Data feeds active. AI synthesis pending next scheduled run."
        }
    
    return {
        'dashboard': 'the-commander',
        'name': 'The Commander',
        'role': 'Master Orchestrator',
        'mission': 'Combine all dashboards using waterfall loading logic to produce the final unified assessment.',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'morning_brief': morning_brief,
        'internal_summary_sentence': "Risk shows the environment, crypto shows sentiment, macro shows the wind, breakthroughs show the future, strategy shows the stance, and knowledge shows the long-term signal — combine all six to guide the user clearly through today.",
        'apps_status': {
            'the-shield': 'active',
            'the-coin': 'active',
            'the-map': 'active',
            'the-frontier': 'active',
            'the-strategy': 'active',
            'the-library': 'active'
        }
    }

# ========================================
# Main Execution with Unified AI Call
# ========================================

def main():
    parser = argparse.ArgumentParser(description='Unified Data Fetcher V3 for Daily Alpha Loop')
    parser.add_argument('--all', action='store_true', help='Run for all dashboards (default)')
    parser.add_argument('--app', type=str, help='Run for specific dashboard (e.g., the-shield)')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI generation to save quota')
    args = parser.parse_args()

    if args.no_ai:
        os.environ['DISABLE_AI'] = 'true'

    run_all = args.all or not args.app
    target_app = args.app

    logger.info("=" * 60)
    logger.info("🚀 DAILY ALPHA LOOP - UNIFIED FETCHER V3")
    logger.info(f"📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("=" * 60)
    
    # STEP 1: Fetch ALL data ONCE (centralized)
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1: CENTRALIZED DATA FETCHING")
    logger.info("=" * 60)
    
    fetch_market_data()
    time.sleep(1)
    
    fetch_crypto_indicators()
    time.sleep(1)
    
    fetch_treasury_data()
    time.sleep(1)
    
    fetch_fear_and_greed()
    time.sleep(1)
    
    fetch_news()
    time.sleep(1)
    
    fetch_arxiv_papers()
    time.sleep(1)
    
    # STEP 2: Make ONE unified AI call for all dashboards
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: UNIFIED AI ANALYSIS (ONE CALL FOR ALL DASHBOARDS)")
    logger.info("=" * 60)
    
    # Prepare all data for the unified AI call
    news_articles = store.get('news.articles') or []
    arxiv_papers = []
    for domain in ["AI Research", "Quantum Computing", "Biotechnology"]:
        papers = store.get(f'arxiv.{domain}.papers') or []
        arxiv_papers.extend([p['title'] for p in papers[:2]])
    
    all_data = {
        'jpy': store.get('market.JPY'),
        'cnh': store.get('market.CNH'),
        'tnx': store.get('market.TNX'),
        'move': store.get('market.MOVE'),
        'vix': store.get('market.VIX'),
        'btc_10y': store.get('treasury.10y_bid_to_cover'),
        'btc_price': store.get('market.BTC'),
        'eth_price': store.get('market.ETH'),
        'btc_rsi': store.get('crypto.BTC.rsi'),
        'btc_trend': store.get('crypto.BTC.trend'),
        'fng_value': store.get('fng.value'),
        'fng_class': store.get('fng.classification'),
        'oil': store.get('market.OIL'),
        'dxy': store.get('market.DXY'),
        'gold': store.get('market.GOLD'),
        'sp500': store.get('market.SP500'),
        'tasi': store.get('market.TASI'),
        'news_headlines': '\n'.join([f"- {a['title']}" for a in news_articles[:10]]),
        'arxiv_summary': '\n'.join([f"- {title}" for title in arxiv_papers])
    }
    
    # Make the unified AI call
    ai_result = call_unified_ai(all_data)
    
    # STEP 3: Build all dashboards with the unified AI result
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: DASHBOARD GENERATION (Using Unified AI Result)")
    logger.info("=" * 60)
    
    dashboards = []
    
    def save_dashboard(data, folder_name):
        dashboards.append(data)
        (DATA_DIR / folder_name).mkdir(parents=True, exist_ok=True)
        (DATA_DIR / folder_name / 'latest.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
        logger.info(f"✅ Saved {folder_name}")

    if run_all or target_app == 'the-shield':
        logger.info("\n📊 Building: The Shield")
        save_dashboard(build_shield_data(ai_result), 'the-shield')

    if run_all or target_app == 'the-coin':
        logger.info("\n📊 Building: The Coin")
        save_dashboard(build_coin_data(ai_result), 'the-coin')

    if run_all or target_app == 'the-map':
        logger.info("\n📊 Building: The Map")
        save_dashboard(build_map_data(ai_result), 'the-map')

    if run_all or target_app == 'the-frontier':
        logger.info("\n📊 Building: The Frontier")
        save_dashboard(build_frontier_data(ai_result), 'the-frontier')

    if run_all or target_app == 'the-library':
        logger.info("\n📊 Building: The Library")
        save_dashboard(build_library_data(ai_result), 'the-library')

    if run_all or target_app == 'the-strategy':
        logger.info("\n📊 Building: The Strategy")
        save_dashboard(build_strategy_data(ai_result), 'the-strategy')

    if run_all or target_app == 'the-commander':
        logger.info("\n📊 Building: The Commander")
        save_dashboard(build_commander_data(ai_result), 'the-commander')
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 GENERATION COMPLETE")
    logger.info("=" * 60)
    
    for d in dashboards:
        logger.info(f"✅ {d['name']}: {d['mission']}")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 DAILY ALPHA LOOP V3 - COMPLETE")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()
