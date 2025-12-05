"""
Unified Data Fetcher V2
=======================
REFACTORED: Centralized data fetching with no duplicate API calls.
The Commander (orchestrator) uses all fetched data to generate Morning Brief.

Philosophy:
- Fetch each data point ONCE
- Store in centralized cache
- Each dashboard gets AI-analyzed JSON
- The Commander synthesizes everything

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
# Configuration
# ========================================

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

# API Keys
API_KEYS = {
    'OPENROUTER': os.environ.get('OPENROUTER_KEY') or os.environ.get('OPENROUTER_API_KEY'),
    'NEWS_API': os.environ.get('NEWS_API_KEY'),
    'FRED': os.environ.get('FRED_API_KEY'),
    'ALPHA_VANTAGE': os.environ.get('ALPHA_VANTAGE_KEY'),
}

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
# AI Analysis Functions
# ========================================

def call_ai(prompt: str, system_prompt: str, models: List[str], max_tokens: int = 1500) -> Optional[str]:
    """Call AI model with priority: Grok → Gemini → OpenRouter"""
    
    if not REQUESTS_AVAILABLE:
        logger.warning("AI not available (no requests library)")
        return None
    
    # Try Grok API first (X.AI) - FREE
    grok_key = os.environ.get('GROK_API_KEY') or os.environ.get('XAI_API_KEY')
    if grok_key:
        try:
            logger.info("  🤖 Calling Grok (X.AI)...")
            headers = {
                'Authorization': f'Bearer {grok_key}',
                'Content-Type': 'application/json'
            }
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            
            payload = {
                'model': 'grok-beta',  # Free tier model
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': max_tokens,
                'stream': False
            }
            
            response = requests.post(
                'https://api.x.ai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    logger.info("  ✅ Success with Grok!")
                    return content
            else:
                logger.warning(f"  Grok failed: {response.status_code}")
        
        except Exception as e:
            logger.warning(f"  ❌ Grok error: {e}")
    
    # Try Gemini API second (Google) - FREE
    gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if gemini_key:
        try:
            logger.info("  🤖 Calling Gemini (Google)...")
            
            # Gemini format: combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            payload = {
                'contents': [{
                    'parts': [{'text': full_prompt}]
                }],
                'generationConfig': {
                    'temperature': 0.7,
                    'maxOutputTokens': max_tokens,
                    'responseMimeType': 'application/json'
                }
            }
            
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}'
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    logger.info("  ✅ Success with Gemini!")
                    return content
            else:
                logger.warning(f"  Gemini failed: {response.status_code}")
        
        except Exception as e:
            logger.warning(f"  ❌ Gemini error: {e}")
    
    # Fallback to OpenRouter (has free models)
    openrouter_key = os.environ.get('OPENROUTER_KEY') or os.environ.get('OPENROUTER_API_KEY')
    if openrouter_key:
        model_map = {
            'llama-70b': 'meta-llama/llama-3.3-70b-instruct:free',
            'olmo-32b': 'allenai/olmo-3-32b-think:free',
            'mistral-24b': 'mistralai/mistral-small-3.1-24b-instruct:free',
            'dolphin-24b': 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
            'qwen-235b': 'qwen/qwen3-235b-a22b:free',
            'glm-4': 'z-ai/glm-4.5-air:free',
            'tongyi-30b': 'alibaba/tongyi-deepresearch-30b-a3b:free',
            'nemotron-12b': 'nvidia/nemotron-nano-12b-v2-vl:free',
            'chimera': 'tngtech/tng-r1t-chimera:free',
            'kimi': 'moonshotai/kimi-k2:free',
            'longcat': 'meituan/longcat-flash-chat:free',
            'gemma-2b': 'google/gemma-3n-e2b-it:free',
        }
        
        for model_key in models:
            model_id = model_map.get(model_key, model_key)
            try:
                logger.info(f"  🤖 Calling OpenRouter ({model_key})...")
                
                headers = {
                    'Authorization': f'Bearer {openrouter_key}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://kaledh4.github.io/daily-alpha-loop/',
                    'X-Title': 'Daily Alpha Loop'
                }
                
                messages = []
                if system_prompt:
                    messages.append({'role': 'system', 'content': system_prompt})
                messages.append({'role': 'user', 'content': prompt})
                
                payload = {
                    'model': model_id,
                    'messages': messages,
                    'temperature': 0.7,
                    'max_tokens': max_tokens,
                    'response_format': {'type': 'json_object'}
                }
                
                response = requests.post(
                    'https://openrouter.ai/api/v1/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    logger.info(f"  ✅ Success with {model_key}!")
                    return content
            
            except Exception as e:
                logger.warning(f"  ❌ Failed {model_key}: {e}")
                continue
    
    logger.error("  ❌ All AI providers failed")
    return None

# ========================================
# Dashboard Analysis Functions
# ========================================

def analyze_the_shield() -> Dict:
    """THE SHIELD - Market Fragility Monitor"""
    logger.info("=" * 50)
    logger.info("🛡️ ANALYZING: THE SHIELD")
    logger.info("=" * 50)
    
    # Calculate risk metrics
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
    
    if cbon:
        metrics.append({
            'name': 'CBON ETF',
            'value': f'${cbon:.2f}',
            'signal': 'NORMAL'
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
    
    # AI Analysis
    ai_analysis = "AI analysis unavailable"
    
    news_articles = store.get('news.articles') or []
    news_text = "\n".join([f"- {a['title']}" for a in news_articles[:5]])
    
    prompt = f"""Analyze systemic market fragility.

METRICS:
{json.dumps(metrics, indent=2)}

RISK LEVEL: {risk['level']} ({risk['score']})

RECENT NEWS:
{news_text}

Return JSON:
{{
  "analysis": "2-3 sentence AI analysis of current market fragility and what to watch"
}}"""
    
    system_prompt = "You are The Shield - a Market Fragility Monitor. Detect systemic stress early."
    
    result = call_ai(prompt, system_prompt, ['llama-70b', 'olmo-32b'])
    if result:
        try:
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end > start:
                parsed = json.loads(result[start:end])
                ai_analysis = parsed.get('analysis', ai_analysis)
        except:
            pass
    
    return {
        'dashboard': 'the-shield',
        'name': 'The Shield',
        'mission': 'Market Fragility Monitor',
        'last_update': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'risk_assessment': risk,
        'metrics': metrics,
        'ai_analysis': ai_analysis
    }

def analyze_the_coin() -> Dict:
    """THE COIN - Crypto Momentum Scanner"""
    logger.info("=" * 50)
    logger.info("🪙 ANALYZING: THE COIN")
    logger.info("=" * 50)
    
    btc_price = store.get('market.BTC')
    eth_price = store.get('market.ETH')
    btc_rsi = store.get('crypto.BTC.rsi')
    btc_trend = store.get('crypto.BTC.trend')
    fng_value = store.get('fng.value')
    fng_class = store.get('fng.classification')
    
    # AI Analysis
    momentum = "Neutral"
    analysis = "Analysis temporarily unavailable"
    
    prompt = f"""Analyze crypto momentum.

BTC Price: ${btc_price:,.0f}
ETH Price: ${eth_price:,.0f}
BTC RSI: {btc_rsi or 50}
BTC Trend: {btc_trend or 'Unknown'}
Fear & Greed: {fng_value or 50} ({fng_class or 'Neutral'})

Return JSON:
{{
  "momentum": "Bullish/Bearish/Neutral",
  "analysis": "2-3 sentence analysis of crypto momentum and key signals"
}}"""
    
    system_prompt = "You are The Coin - a Crypto Momentum Scanner. Track BTC/ETH momentum shifts."
    
    result = call_ai(prompt, system_prompt, ['mistral-24b', 'dolphin-24b'])
    if result:
        try:
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end > start:
                parsed = json.loads(result[start:end])
                momentum = parsed.get('momentum', momentum)
                analysis = parsed.get('analysis', analysis)
        except:
            pass
    
    return {
        'dashboard': 'the-coin',
        'name': 'The Coin',
        'mission': 'Crypto Momentum Scanner',
        'btc_price': btc_price,
        'eth_price': eth_price,
        'momentum': momentum,
        'rsi': btc_rsi,
        'trend': btc_trend,
        'fear_and_greed': {'value': fng_value, 'classification': fng_class},
        'ai_analysis': analysis
    }

def analyze_the_map() -> Dict:
    """THE MAP - Macro & TASI Trendsetter"""
    logger.info("=" * 50)
    logger.info("🗺️ ANALYZING: THE MAP")
    logger.info("=" * 50)
    
    oil = store.get('market.OIL')
    dxy = store.get('market.DXY')
    gold = store.get('market.GOLD')
    sp500 = store.get('market.SP500')
    tasi = store.get('market.TASI')
    tnx = store.get('market.TNX')
    
    # AI Analysis
    tasi_mood = "Neutral"
    analysis = "Analysis temporarily unavailable"
    drivers = []
    
    prompt = f"""Analyze macro trends and predict TASI mood.

Oil: ${oil:.2f}
DXY: {dxy:.2f}
Gold: ${gold:.2f}
SP500: {sp500:.2f}
TASI: {tasi:.2f}
US 10Y Yield: {tnx:.2f}%

Return JSON:
{{
  "tasi_mood": "Positive/Neutral/Negative",
  "drivers": ["Driver 1", "Driver 2", "Driver 3"],
  "analysis": "2-3 sentence analysis of macro trends affecting TASI"
}}"""
    
    system_prompt = "You are The Map - Macro & TASI Trendsetter. Align global macro with Saudi markets."
    
    result = call_ai(prompt, system_prompt, ['qwen-235b', 'glm-4'])
    if result:
        try:
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end > start:
                parsed = json.loads(result[start:end])
                tasi_mood = parsed.get('tasi_mood', tasi_mood)
                drivers = parsed.get('drivers', drivers)
                analysis = parsed.get('analysis', analysis)
        except:
            pass
    
    return {
        'dashboard': 'the-map',
        'name': 'The Map',
        'mission': 'Macro & TASI Trendsetter',
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
        'ai_analysis': analysis
    }

def analyze_the_frontier() -> Dict:
    """THE FRONTIER - Silicon Frontier Watch"""
    logger.info("=" * 50)
    logger.info("🚀 ANALYZING: THE FRONTIER")
    logger.info("=" * 50)
    
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
    
    # AI Analysis
    breakthroughs = []
    analysis = "AI analysis unavailable"
    
    # Build paper text
    papers_text = ""
    for domain_name, domain_data in domains.items():
        papers_text += f"\n## {domain_name}\n"
        for paper in domain_data['recent_papers'][:3]:
            papers_text += f"- {paper['title']}\n"
    
    news_articles = store.get('news.articles') or []
    news_text = "\n".join([f"- {a['title']}" for a in news_articles[:10]])
    
    prompt = f"""Identify real AI/tech breakthroughs (not hype).

RESEARCH PAPERS:
{papers_text}

NEWS:
{news_text}

Return JSON:
{{
  "breakthroughs": [
    {{"title": "Breakthrough title", "why_it_matters": "Why it matters"}}
  ],
  "analysis": "2-3 sentence analysis of the frontier status"
}}"""
    
    system_prompt = "You are The Frontier - Silicon Frontier Watch. Track AI/tech capability jumps."
    
    result = call_ai(prompt, system_prompt, ['tongyi-30b', 'nemotron-12b'], max_tokens=2000)
    if result:
        try:
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end > start:
                parsed = json.loads(result[start:end])
                breakthroughs = parsed.get('breakthroughs', breakthroughs)
                analysis = parsed.get('analysis', analysis)
        except:
            pass
    
    return {
        'dashboard': 'the-frontier',
        'name': 'The Frontier',
        'mission': 'Silicon Frontier Watch',
        'domains': domains,
        'breakthroughs': breakthroughs,
        'ai_analysis': analysis
    }

def analyze_the_strategy() -> Dict:
    """THE STRATEGY - Unified Opportunity Radar"""
    logger.info("=" * 50)
    logger.info("🎯 ANALYZING: THE STRATEGY")
    logger.info("=" * 50)
    
    # Get data from other dashboards (from data files if they exist)
    risk_level = "LOW"  # Will be populated from The Shield
    crypto_momentum = "Neutral"  # From The Coin
    macro_signal = "Neutral"  # From The Map
    frontier_signal = "Active"  # From The Frontier
    
    # Try to read from data files
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
    
    # AI Analysis
    stance = "Neutral"
    mindset = "Wait for clarity"
    analysis = "Analysis temporarily unavailable"
    
    prompt = f"""Synthesize cross-dashboard insights into a unified stance.

Risk Level: {risk_level}
Crypto Momentum: {crypto_momentum}
Macro Signal: {macro_signal}
Frontier: {frontier_signal}

Define today's stance: Defensive / Neutral / Accumulative / Opportunistic / Aggressive

Return JSON:
{{
  "stance": "Stance",
  "mindset": "One-line mindset for the user",
  "analysis": "2-3 sentence synthesis of all signals"
}}"""
    
    system_prompt = "You are The Strategy - Unified Opportunity Radar. Synthesize cross-dashboard insights."
    
    result = call_ai(prompt, system_prompt, ['chimera', 'kimi'])
    if result:
        try:
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end > start:
                parsed = json.loads(result[start:end])
                stance = parsed.get('stance', stance)
                mindset = parsed.get('mindset', mindset)
                analysis = parsed.get('analysis', analysis)
        except:
            pass
    
    return {
        'dashboard': 'the-strategy',
        'name': 'The Strategy',
        'mission': 'Unified Opportunity Radar',
        'stance': stance,
        'mindset': mindset,
        'inputs': {
            'risk': risk_level,
            'crypto': crypto_momentum,
            'macro': macro_signal,
            'frontier': frontier_signal
        },
        'ai_analysis': analysis
    }

def analyze_the_library() -> Dict:
    """THE LIBRARY - Alpha-Clarity Archive"""
    logger.info("=" * 50)
    logger.info("📚 ANALYZING: THE LIBRARY")
    logger.info("=" * 50)
    
    news_articles = store.get('news.articles') or []
    
    # AI Analysis
    summaries = []
    
    if news_articles:
        articles_text = "\n".join([f"{i+1}. {a['title']}" for i, a in enumerate(news_articles[:10])])
        
        prompt = f"""Pick 3 complex market/tech articles and simplify them.

HEADLINES:
{articles_text}

For each, provide an ELI5 summary and why it matters long-term.

Return JSON:
{{
  "summaries": [
    {{"title": "Title", "eli5": "Simple explanation", "long_term": "Why it matters long-term"}}
  ]
}}"""
        
        system_prompt = "You are The Library - Alpha-Clarity Archive. Simplify complex market knowledge."
        
        result = call_ai(prompt, system_prompt, ['longcat', 'gemma-2b'], max_tokens=2000)
        if result:
            try:
                start = result.find('{')
                end = result.rfind('}') + 1
                if start != -1 and end > start:
                    parsed = json.loads(result[start:end])
                    summaries = parsed.get('summaries', summaries)
            except:
                pass
    
    return {
        'dashboard': 'the-library',
        'name': 'The Library',
        'mission': 'Alpha-Clarity Archive',
        'summaries': summaries
    }

def analyze_the_commander() -> Dict:
    """THE COMMANDER - Morning Brief Generator"""
    logger.info("=" * 50)
    logger.info("⭐ GENERATING: THE COMMANDER (Morning Brief)")
    logger.info("=" * 50)
    
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
    
    # AI Generation of Morning Brief
    morning_brief = {}
    
    prompt = f"""Create a 30-Second Coffee Read Morning Brief.

DATA FROM ALL DASHBOARDS:

THE SHIELD (Risk):
{json.dumps(shield_data.get('risk_assessment', {}), indent=2)}
Top metric signals: {', '.join([m['name'] + ': ' + m['signal'] for m in shield_data.get('metrics', [])[:3]])}

THE COIN (Crypto):
Momentum: {coin_data.get('momentum', 'N/A')}
BTC: ${coin_data.get('btc_price', 0):,.0f}

THE MAP (Macro):
TASI Mood: {map_data.get('tasi_mood', 'N/A')}
Oil: ${map_data.get('macro', {}).get('oil', 0):.2f}
SP500: {map_data.get('macro', {}).get('sp500', 0):.2f}

THE FRONTIER (Breakthroughs):
{len(frontier_data.get('breakthroughs', []))} breakthroughs identified

THE STRATEGY (Stance):
{strategy_data.get('stance', 'N/A')} - {strategy_data.get('mindset', 'N/A')}

THE LIBRARY (Knowledge):
{len(library_data.get('summaries', []))} summaries available

INSTRUCTIONS:
Create a structured Morning Brief with these EXACT fields:

Return JSON:
{{
  "weather_of_the_day": "One word: Stormy / Cloudy / Sunny / Volatile / Foggy",
  "top_signal": "The single most important data point today",
  "why_it_matters": "2 sentences explaining why",
  "cross_dashboard_convergence": "How risk + crypto + macro + breakthroughs connect",
  "action_stance": "Sit tight / Accumulate / Cautious / Aggressive / Review markets",
  "optional_deep_insight": "One optional paragraph for advanced users",
  "clarity_level": "High / Medium / Low based on data convergence",
  "summary_sentence": "Risk shows the environment, crypto shows sentiment, macro shows the wind, breakthroughs show the future, strategy shows the stance, and knowledge shows the long-term signal — combine all six to guide the user clearly through today."
}}"""
    
    system_prompt = "You are The Commander - Master Orchestrator. Generate the ultimate daily Morning Brief."
    
    result = call_ai(prompt, system_prompt, ['llama-70b', 'olmo-32b'], max_tokens=2000)
    if result:
        try:
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end > start:
                morning_brief = json.loads(result[start:end])
        except:
            pass
    
    # Fallback
    if not morning_brief:
        risk_level = shield_data.get('risk_assessment', {}).get('level', 'UNKNOWN')
        crypto_momentum = coin_data.get('momentum', 'Neutral')
        stance = strategy_data.get('stance', 'Neutral')
        
        weather = "Cloudy"
        if risk_level == 'CRITICAL':
            weather = "Stormy"
        elif risk_level == 'LOW' and crypto_momentum == 'Bullish':
            weather = "Sunny"
        elif risk_level == 'ELEVATED':
            weather = "Foggy"
        
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
        'mission': 'Master Orchestrator - Morning Brief',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'morning_brief': morning_brief,
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
# Main Execution with Waterfall Logic
# ========================================

def main():
    logger.info("=" * 60)
    logger.info("🚀 DAILY ALPHA LOOP - UNIFIED FETCHER V2")
    logger.info(f"📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("=" * 60)
    
    # STEP 1: Fetch ALL data ONCE (centralized)
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1: CENTRALIZED DATA FETCHING")
    logger.info("=" * 60)
    
    fetch_market_data()
    time.sleep(1)  # Rate limiting
    
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
    
    # STEP 2: Generate dashboard analyses (waterfall pattern)
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: DASHBOARD ANALYSES (WATERFALL)")
    logger.info("=" * 60)
    
    dashboards = []
    
    # Load Risk (1) and Macro (3)
    logger.info("\n📊 Wave 1: Risk + Macro")
    shield = analyze_the_shield()
    dashboards.append(shield)
    (DATA_DIR / 'the-shield').mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'the-shield' / 'latest.json').write_text(json.dumps(shield, indent=2), encoding='utf-8')
    
    map_analysis = analyze_the_map()
    dashboards.append(map_analysis)
    (DATA_DIR / 'the-map').mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'the-map' / 'latest.json').write_text(json.dumps(map_analysis, indent=2), encoding='utf-8')
    
    time.sleep(2)  # Wait between waves
    
    # Load Crypto (2) and AI Race (4)
    logger.info("\n📊 Wave 2: Crypto + Frontier")
    coin = analyze_the_coin()
    dashboards.append(coin)
    (DATA_DIR / 'the-coin').mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'the-coin' / 'latest.json').write_text(json.dumps(coin, indent=2), encoding='utf-8')
    
    frontier = analyze_the_frontier()
    dashboards.append(frontier)
    (DATA_DIR / 'the-frontier').mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'the-frontier' / 'latest.json').write_text(json.dumps(frontier, indent=2), encoding='utf-8')
    
    time.sleep(2)
    
    # Load Free Knowledge (6)
    logger.info("\n📊 Wave 3: Library")
    library = analyze_the_library()
    dashboards.append(library)
    (DATA_DIR / 'the-library').mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'the-library' / 'latest.json').write_text(json.dumps(library, indent=2), encoding='utf-8')
    
    time.sleep(2)
    
    # Generate Strategy (5)
    logger.info("\n📊 Wave 4: Strategy")
    strategy = analyze_the_strategy()
    dashboards.append(strategy)
    (DATA_DIR / 'the-strategy').mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'the-strategy' / 'latest.json').write_text(json.dumps(strategy, indent=2), encoding='utf-8')
    
    time.sleep(2)
    
    # Finally, generate Master Orchestrator (7)
    logger.info("\n📊 Wave 5: The Commander")
    commander = analyze_the_commander()
    dashboards.append(commander)
    (DATA_DIR / 'the-commander').mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'the-commander' / 'latest.json').write_text(json.dumps(commander, indent=2), encoding='utf-8')
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 GENERATION COMPLETE")
    logger.info("=" * 60)
    
    for d in dashboards:
        logger.info(f"✅ {d['name']}: {d['mission']}")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 DAILY ALPHA LOOP - COMPLETE")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()
