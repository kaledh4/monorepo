"""
Unified Data Fetcher
=====================
Single Python script that fetches data for ALL apps in the monorepo.
Eliminates duplicate fetching code across apps.

REPLACES:
- tools/fetchers/fetch_crash_data.py
- tools/fetchers/fetch_all.py
- apps/ai-race/AI_RACE_CLEAN-main/scraper.py
- apps/economic-compass/app/data_fetcher.py
- apps/hyper-analytical/macro_analysis.py (data fetching parts)
- apps/intelligence-platform/market_analysis.py

USAGE:
    python unified_fetcher.py --all              # Fetch everything
    python unified_fetcher.py --app crash-detector
    python unified_fetcher.py --app ai-race
    python unified_fetcher.py --type market,news,crypto

Author: Unified Monorepo Team
"""

import os
import sys
import json
import logging
import argparse
import pathlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party imports (with graceful degradation)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests not available - HTTP fetching disabled")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logging.warning("yfinance not available - market data disabled")

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    logging.warning("feedparser not available - RSS feeds disabled")

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("pandas not available - analysis disabled")

# ===========================================
# Configuration
# ===========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Base paths
ROOT_DIR = pathlib.Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / 'data'
APPS_DIR = ROOT_DIR / 'apps'

# API Keys from environment
API_KEYS = {
    'OPENROUTER': os.environ.get('OPENROUTER_KEY') or os.environ.get('OPENROUTER_API_KEY'),
    'NEWS_API': os.environ.get('NEWS_API_KEY'),
    'FRED': os.environ.get('FRED_API_KEY'),
    'ALPHA_VANTAGE': os.environ.get('ALPHA_VANTAGE_KEY'),
}

# Stress thresholds (from crash-detector)
JPY_STRESS_THRESHOLD = 150.0
JPY_CRITICAL_THRESHOLD = 155.0
CNH_STRESS_THRESHOLD = 7.25
CNH_CRITICAL_THRESHOLD = 7.4
MOVE_PROXY_HIGH = 90.0
MOVE_PROXY_CRITICAL = 120.0
AUCTION_BTC_STRESS = 2.3

# arXiv queries (from ai-race)
ARXIV_DOMAINS = {
    "Advanced Manufacturing": "cat:cs.RO OR cat:cs.SY",
    "Biotechnology": "cat:q-bio.BM OR cat:q-bio.GN",
    "Critical Materials": 'all:"rare earth" OR all:"critical materials"',
    "Nuclear Energy": "cat:nucl-ex OR cat:nucl-th",
    "Quantum Info Science": "cat:quant-ph",
    "Semiconductors": "cat:cond-mat.mes-hall OR cat:cs.ET"
}

# ===========================================
# Data Classes
# ===========================================

@dataclass
class FetchResult:
    """Standard result structure for all fetchers"""
    success: bool
    data: Any
    source: str
    fetched_at: str
    error: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

# ===========================================
# Base Fetcher Class
# ===========================================

class BaseFetcher:
    """Base class for all fetchers with caching"""
    
    def __init__(self, cache_dir: pathlib.Path = None):
        self.cache_dir = cache_dir or DATA_DIR / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cached(self, key: str, max_age_seconds: int = 300) -> Optional[Dict]:
        """Get cached data if fresh enough"""
        cache_file = self.cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None
        
        try:
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            fetched_at = datetime.fromisoformat(data.get('fetched_at', '2000-01-01').replace('Z', '+00:00'))
            age = (datetime.now(timezone.utc) - fetched_at).total_seconds()
            if age < max_age_seconds:
                logger.info(f"[CACHE HIT] {key} (age: {age:.0f}s)")
                return data
        except Exception as e:
            logger.debug(f"Cache read error for {key}: {e}")
        return None
    
    def set_cache(self, key: str, data: Dict):
        """Save data to cache"""
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')

# ===========================================
# Market Data Fetcher
# ===========================================

class MarketFetcher(BaseFetcher):
    """Fetches market data via yfinance - UNIFIED for all apps"""
    
    def fetch_ticker(self, ticker: str, period: str = '1d') -> FetchResult:
        """Fetch single ticker current price"""
        if not YFINANCE_AVAILABLE:
            return FetchResult(False, None, 'yfinance', datetime.now(timezone.utc).isoformat(), 'yfinance not available')
        
        cache_key = f"market_{ticker}_{period}".replace('=', '_').replace('^', '_')
        cached = self.get_cached(cache_key, max_age_seconds=60)
        if cached:
            return FetchResult(True, cached['data'], 'yfinance', cached['fetched_at'])
        
        try:
            logger.info(f"[MARKET] Fetching {ticker}...")
            ticker_obj = yf.Ticker(ticker)
            
            price = None
            try:
                price = ticker_obj.fast_info.last_price
            except:
                pass
            
            if price is None:
                hist = ticker_obj.history(period=period)
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
            
            if price is not None:
                data = {'ticker': ticker, 'price': float(price), 'period': period}
                self.set_cache(cache_key, {'data': data, 'fetched_at': datetime.now(timezone.utc).isoformat()})
                logger.info(f"[MARKET] {ticker}: {price}")
                return FetchResult(True, data, 'yfinance', datetime.now(timezone.utc).isoformat())
            
            return FetchResult(False, None, 'yfinance', datetime.now(timezone.utc).isoformat(), 'No data found')
        except Exception as e:
            logger.error(f"[MARKET] Error fetching {ticker}: {e}")
            return FetchResult(False, None, 'yfinance', datetime.now(timezone.utc).isoformat(), str(e))
    
    def fetch_multi(self, tickers: Dict[str, str]) -> Dict[str, FetchResult]:
        """Fetch multiple tickers in parallel"""
        results = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.fetch_ticker, ticker): name for name, ticker in tickers.items()}
            for future in as_completed(futures):
                name = futures[future]
                results[name] = future.result()
        return results
    
    def fetch_with_indicators(self, ticker: str, period: str = '5y', interval: str = '1wk') -> FetchResult:
        """Fetch ticker with technical indicators (for crypto analysis)"""
        if not YFINANCE_AVAILABLE or not PANDAS_AVAILABLE:
            return FetchResult(False, None, 'yfinance', datetime.now(timezone.utc).isoformat(), 'Dependencies not available')
        
        cache_key = f"market_full_{ticker}".replace('-', '_')
        cached = self.get_cached(cache_key, max_age_seconds=300)
        if cached:
            return FetchResult(True, cached['data'], 'yfinance', cached['fetched_at'])
        
        try:
            logger.info(f"[MARKET] Fetching {ticker} with indicators...")
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            
            if df.empty:
                return FetchResult(False, None, 'yfinance', datetime.now(timezone.utc).isoformat(), 'No data')
            
            # Flatten MultiIndex if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Calculate indicators
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            df['RSI'] = self._calculate_rsi(df['Close'])
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            data = {
                'ticker': ticker,
                'price': float(latest['Close']),
                'sma_20': float(latest['SMA_20']) if not pd.isna(latest['SMA_20']) else None,
                'ema_21': float(latest['EMA_21']) if not pd.isna(latest['EMA_21']) else None,
                'ma50': float(latest['MA50']) if not pd.isna(latest['MA50']) else None,
                'ma200': float(latest['MA200']) if not pd.isna(latest['MA200']) else None,
                'rsi': float(latest['RSI']) if not pd.isna(latest['RSI']) else None,
                'trend': 'Bullish' if latest['Close'] > latest['SMA_20'] else 'Bearish',
                'prev_close': float(prev['Close'])
            }
            
            self.set_cache(cache_key, {'data': data, 'fetched_at': datetime.now(timezone.utc).isoformat()})
            return FetchResult(True, data, 'yfinance', datetime.now(timezone.utc).isoformat())
        except Exception as e:
            logger.error(f"[MARKET] Error fetching {ticker}: {e}")
            return FetchResult(False, None, 'yfinance', datetime.now(timezone.utc).isoformat(), str(e))
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

# ===========================================
# Treasury Fetcher
# ===========================================

class TreasuryFetcher(BaseFetcher):
    """Fetches Treasury auction data"""
    
    BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query"
    
    def fetch_auction(self, term: str = '10-Year', security_type: str = 'Note') -> FetchResult:
        """Fetch Treasury auction data"""
        if not REQUESTS_AVAILABLE:
            return FetchResult(False, None, 'treasury', datetime.now(timezone.utc).isoformat(), 'requests not available')
        
        cache_key = f"treasury_{term}_{security_type}".replace('-', '_').replace(' ', '_')
        cached = self.get_cached(cache_key, max_age_seconds=300)
        if cached:
            return FetchResult(True, cached['data'], 'treasury', cached['fetched_at'])
        
        try:
            logger.info(f"[TREASURY] Fetching {term} {security_type}...")
            params = {
                'filter': f'security_term:eq:{term},security_type:eq:{security_type}',
                'sort': '-auction_date',
                'page[size]': 1
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                result = data['data'][0]
                self.set_cache(cache_key, {'data': result, 'fetched_at': datetime.now(timezone.utc).isoformat()})
                return FetchResult(True, result, 'treasury', datetime.now(timezone.utc).isoformat())
            
            return FetchResult(False, None, 'treasury', datetime.now(timezone.utc).isoformat(), 'No data')
        except Exception as e:
            logger.error(f"[TREASURY] Error: {e}")
            return FetchResult(False, None, 'treasury', datetime.now(timezone.utc).isoformat(), str(e))

# ===========================================
# News Fetcher
# ===========================================

class NewsFetcher(BaseFetcher):
    """Fetches news from various sources"""
    
    def fetch_rss(self, feeds: List[str] = None) -> FetchResult:
        """Fetch from RSS feeds"""
        if not FEEDPARSER_AVAILABLE:
            # Fallback to requests-based RSS parsing
            return self._fetch_rss_simple(feeds)
        
        default_feeds = [
            'https://finance.yahoo.com/news/rssindex',
            'https://cointelegraph.com/rss',
            'https://www.marketwatch.com/rss/topstories'
        ]
        feeds = feeds or default_feeds
        
        cache_key = "rss_news"
        cached = self.get_cached(cache_key, max_age_seconds=600)
        if cached:
            return FetchResult(True, cached['data'], 'rss', cached['fetched_at'])
        
        try:
            logger.info(f"[RSS] Fetching from {len(feeds)} feeds...")
            articles = []
            for feed_url in feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:
                        articles.append({
                            'title': entry.get('title', 'No title'),
                            'source': feed.feed.get('title', 'Unknown'),
                            'url': entry.get('link'),
                            'publishedAt': entry.get('published')
                        })
                except Exception as e:
                    logger.debug(f"Feed error {feed_url}: {e}")
                    continue
            
            data = {'articles': articles[:15]}
            self.set_cache(cache_key, {'data': data, 'fetched_at': datetime.now(timezone.utc).isoformat()})
            return FetchResult(True, data, 'rss', datetime.now(timezone.utc).isoformat())
        except Exception as e:
            logger.error(f"[RSS] Error: {e}")
            return FetchResult(False, {'articles': []}, 'rss', datetime.now(timezone.utc).isoformat(), str(e))
    
    def _fetch_rss_simple(self, feeds: List[str] = None) -> FetchResult:
        """Simple RSS fetch without feedparser"""
        if not REQUESTS_AVAILABLE:
            return FetchResult(False, {'articles': []}, 'rss', datetime.now(timezone.utc).isoformat(), 'No HTTP available')
        
        import xml.etree.ElementTree as ET
        
        default_feeds = ['https://cointelegraph.com/rss']
        feeds = feeds or default_feeds
        
        articles = []
        for feed_url in feeds:
            try:
                r = requests.get(feed_url, timeout=10)
                root = ET.fromstring(r.content)
                for item in root.findall('.//item')[:5]:
                    title = item.find('title')
                    articles.append({
                        'title': title.text if title is not None else 'No title',
                        'source': 'RSS',
                        'url': '',
                        'publishedAt': ''
                    })
            except:
                continue
        
        return FetchResult(True, {'articles': articles[:10]}, 'rss', datetime.now(timezone.utc).isoformat())

# ===========================================
# Crypto Fetcher
# ===========================================

class CryptoFetcher(BaseFetcher):
    """Fetches crypto-specific data"""
    
    def fetch_fear_and_greed(self) -> FetchResult:
        """Fetch Fear & Greed Index"""
        if not REQUESTS_AVAILABLE:
            return FetchResult(False, {'value': 50, 'classification': 'Neutral'}, 'fng', datetime.now(timezone.utc).isoformat(), 'requests not available')
        
        cache_key = 'fng'
        cached = self.get_cached(cache_key, max_age_seconds=900)
        if cached:
            return FetchResult(True, cached['data'], 'fng', cached['fetched_at'])
        
        try:
            logger.info("[FNG] Fetching Fear & Greed Index...")
            response = requests.get('https://api.alternative.me/fng/?limit=1', timeout=10)
            data = response.json()
            
            result = {
                'value': int(data['data'][0]['value']),
                'value_classification': data['data'][0]['value_classification'],
                'timestamp': data['data'][0]['timestamp']
            }
            
            self.set_cache(cache_key, {'data': result, 'fetched_at': datetime.now(timezone.utc).isoformat()})
            return FetchResult(True, result, 'fng', datetime.now(timezone.utc).isoformat())
        except Exception as e:
            logger.error(f"[FNG] Error: {e}")
            return FetchResult(False, {'value': 50, 'value_classification': 'Neutral'}, 'fng', datetime.now(timezone.utc).isoformat(), str(e))

# ===========================================
# arXiv Fetcher
# ===========================================

class ArxivFetcher(BaseFetcher):
    """Fetches arXiv research papers"""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def fetch_papers(self, query: str, max_results: int = 10) -> FetchResult:
        """Fetch arXiv papers by query"""
        import ssl
        import urllib.request
        import urllib.parse
        import xml.etree.ElementTree as ET
        
        cache_key = f"arxiv_{hash(query)}_{max_results}"
        cached = self.get_cached(cache_key, max_age_seconds=3600)
        if cached:
            return FetchResult(True, cached['data'], 'arxiv', cached['fetched_at'])
        
        try:
            logger.info(f"[ARXIV] Fetching papers: {query[:50]}...")
            params = {
                'search_query': query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
            
            context = ssl._create_unverified_context()
            response = urllib.request.urlopen(url, context=context, timeout=30)
            xml_data = response.read().decode('utf-8')
            
            root = ET.fromstring(xml_data)
            
            # Namespaces
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
            
            data = {'total_results': total_results, 'papers': papers, 'query': query}
            self.set_cache(cache_key, {'data': data, 'fetched_at': datetime.now(timezone.utc).isoformat()})
            return FetchResult(True, data, 'arxiv', datetime.now(timezone.utc).isoformat())
        except Exception as e:
            logger.error(f"[ARXIV] Error: {e}")
            return FetchResult(False, {'papers': [], 'total_results': 0}, 'arxiv', datetime.now(timezone.utc).isoformat(), str(e))

# ===========================================
# AI/LLM Fetcher
# ===========================================

class AIFetcher(BaseFetcher):
    """Fetches AI analysis using OpenRouter"""
    
    MODELS = {
        'gpt': 'openai/gpt-4o-mini',
        'grok': 'x-ai/grok-beta',
        'chimera': 'google/gemini-flash-1.5'
    }
    
    def call_ai(self, prompt: str, system_prompt: str = None, model: str = 'gpt', max_tokens: int = 1000, response_format: str = None) -> FetchResult:
        """Call AI model"""
        api_key = API_KEYS.get('OPENROUTER')
        
        if not api_key:
            logger.warning("[AI] OpenRouter API key not configured")
            return FetchResult(False, {'content': 'AI analysis temporarily unavailable.'}, 'openrouter', datetime.now(timezone.utc).isoformat(), 'API key not configured')
        
        try:
            logger.info(f"[AI] Calling {model} model...")
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://kaledh4.github.io/monorepo/',
                'X-Title': 'Unified Dashboard'
            }
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            
            payload = {
                'model': self.MODELS.get(model, model),
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': max_tokens
            }
            
            if response_format:
                payload['response_format'] = {'type': response_format}
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            logger.info("[AI] Response received successfully")
            return FetchResult(True, {'content': content, 'model': model}, 'openrouter', datetime.now(timezone.utc).isoformat())
        except Exception as e:
            logger.error(f"[AI] Error: {e}")
            return FetchResult(False, {'content': 'AI analysis temporarily unavailable.'}, 'openrouter', datetime.now(timezone.utc).isoformat(), str(e))

# ===========================================
# Signal Determination (from crash-detector)
# ===========================================

def determine_signal(metric_name: str, value: float) -> str:
    """Determine stress signal based on metric value"""
    if value is None:
        return "DATA ERROR"
    
    if "JPY" in metric_name:
        if value >= JPY_CRITICAL_THRESHOLD: return "CRITICAL SHOCK"
        if value >= JPY_STRESS_THRESHOLD: return "HIGH STRESS"
        if value > 145.0: return "RISING STRESS"
    elif "CNH" in metric_name:
        if value >= CNH_CRITICAL_THRESHOLD: return "CRITICAL SHOCK"
        if value >= CNH_STRESS_THRESHOLD: return "HIGH STRESS"
        if value > 7.15: return "RISING STRESS"
    elif "Treasury Yield" in metric_name or "TNX" in metric_name:
        if value >= 5.0: return "CRITICAL SHOCK"
        if value >= 4.5: return "HIGH STRESS"
        if value >= 4.2: return "RISING STRESS"
    elif "MOVE" in metric_name or "VIX" in metric_name:
        if value >= MOVE_PROXY_CRITICAL: return "CRITICAL SHOCK"
        if value >= MOVE_PROXY_HIGH: return "HIGH STRESS"
        if value > 80.0: return "RISING STRESS"
    elif "Bid-to-Cover" in metric_name:
        if value < 2.0: return "CRITICAL SHOCK"
        if value < AUCTION_BTC_STRESS: return "HIGH STRESS"
        if value < 2.4: return "RISING STRESS"
    
    return "NORMAL"

def calculate_composite_risk(metrics: List[Dict]) -> Dict:
    """Calculate overall risk score from metrics"""
    score = 0
    count = 0
    weights = {"CRITICAL SHOCK": 100, "HIGH STRESS": 75, "RISING STRESS": 40, "NORMAL": 0, "DATA ERROR": 25}
    
    for m in metrics:
        signal = m.get('signal', 'NORMAL')
        if signal in weights:
            score += weights[signal]
            count += 1
    
    if count == 0:
        return {"score": 0, "level": "UNKNOWN", "color": "#6c757d"}
    
    avg = score / count
    if avg >= 60:
        return {"score": round(avg, 1), "level": "CRITICAL", "color": "#dc3545"}
    if avg >= 35:
        return {"score": round(avg, 1), "level": "ELEVATED", "color": "#ffc107"}
    return {"score": round(avg, 1), "level": "LOW", "color": "#28a745"}

# ===========================================
# APP-SPECIFIC FETCH FUNCTIONS
# ===========================================

def fetch_for_crash_detector() -> Dict:
    """
    Fetch all data needed by crash-detector app.
    Output: data/crash-detector/latest.json
    """
    logger.info("=" * 50)
    logger.info("CRASH-DETECTOR: Starting data fetch")
    logger.info("=" * 50)
    
    market = MarketFetcher()
    treasury = TreasuryFetcher()
    news = NewsFetcher()
    ai = AIFetcher()
    
    # Fetch market data
    tickers = {
        'USD/JPY': 'JPY=X',
        'USD/CNH': 'CNH=X',
        '10Y Treasury Yield': '^TNX',
        'MOVE Index': '^MOVE',
        'VIX': '^VIX',
        'CBON ETF': 'CBON'
    }
    
    market_data = market.fetch_multi(tickers)
    
    # Fetch treasury auctions
    auction_10y = treasury.fetch_auction('10-Year', 'Note')
    auction_30y = treasury.fetch_auction('30-Year', 'Bond')
    
    # Build metrics list
    metrics = []
    
    # Treasury auction metrics
    if auction_10y.success and auction_10y.data:
        btc_10y = float(auction_10y.data.get('bid_to_cover_ratio', 0))
        metrics.append({
            'name': '10Y Treasury Auction Bid-to-Cover',
            'value': f'{btc_10y:.2f}x' if btc_10y else 'N/A',
            'signal': determine_signal('Bid-to-Cover', btc_10y),
            'desc': 'Demand strength'
        })
    
    if auction_30y.success and auction_30y.data:
        try:
            tail = (float(auction_30y.data.get('high_yield', 0)) - 
                   float(auction_30y.data.get('average_median_yield', 0))) * 100
            metrics.append({
                'name': '30Y Auction Tail',
                'value': f'{tail:.1f} bps',
                'signal': 'HIGH STRESS' if tail >= 3.0 else 'NORMAL',
                'desc': 'Dealer reluctance'
            })
        except:
            pass
    
    # Market metrics
    for name, result in market_data.items():
        if result.success and result.data:
            price = result.data['price']
            
            # Format value based on type
            if 'JPY' in name:
                value = f'{price:.2f}'
            elif 'CNH' in name:
                value = f'{price:.4f}'
            elif 'Yield' in name:
                value = f'{price:.2f}%'
            elif 'CBON' in name:
                value = f'${price:.2f}'
            else:
                value = f'{price:.2f}'
            
            metrics.append({
                'name': name,
                'value': value,
                'signal': determine_signal(name, price),
                'desc': f'{name} current level'
            })
    
    # Fetch news
    news_result = news.fetch_rss()
    
    # Calculate risk
    risk = calculate_composite_risk(metrics)
    
    # Generate AI analysis
    ai_insights = {'crash_analysis': 'AI analysis unavailable', 'news_summary': 'Check latest news sources'}
    
    if API_KEYS['OPENROUTER']:
        news_text = "\n".join([f"- {a['title']}" for a in (news_result.data or {}).get('articles', [])[:5]])
        prompt = f"""Analyze these market stress metrics for a "Global Financial Fault Lines" assessment:
METRICS: {json.dumps(metrics, indent=2)}
RISK LEVEL: {risk}
RECENT NEWS: {news_text}
Return JSON: {{ "crash_analysis": "HTML formatted analysis", "news_summary": "HTML formatted news summary" }}"""
        
        ai_result = ai.call_ai(prompt, 
                                system_prompt="You are a financial risk analyst. Provide concise HTML-formatted analysis.",
                                model='chimera',
                                response_format='json_object')
        if ai_result.success:
            try:
                content = ai_result.data['content']
                # Try to parse JSON from response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    ai_insights = json.loads(content[start:end])
            except Exception as e:
                logger.warning(f"Could not parse AI response: {e}")
                ai_insights = {'crash_analysis': ai_result.data['content'], 'news_summary': ''}
    
    # Build final data structure
    data = {
        'last_update': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'risk_assessment': risk,
        'convergence_score': {'score': 0, 'status': 'Initializing', 'details': 'Building history'},
        'metrics': metrics,
        'ai_insights': ai_insights,
        'days_remaining': (datetime(2026, 11, 28) - datetime.now()).days
    }
    
    return data


def fetch_for_ai_race() -> Dict:
    """
    Fetch all data needed by ai-race app.
    Output: apps/ai-race/AI_RACE_CLEAN-main/mission_data.json
    """
    logger.info("=" * 50)
    logger.info("AI-RACE: Starting data fetch")
    logger.info("=" * 50)
    
    arxiv = ArxivFetcher()
    ai = AIFetcher()
    
    # Fetch arXiv papers for each domain
    domains = {}
    for domain_name, query in ARXIV_DOMAINS.items():
        result = arxiv.fetch_papers(query, max_results=10)
        if result.success:
            domains[domain_name] = {
                'total_volume': result.data['total_results'],
                'recent_papers': result.data['papers']
            }
            logger.info(f"[ARXIV] {domain_name}: {result.data['total_results']} papers")
    
    # Generate AI strategic briefing
    ai_briefing = "*AI analysis unavailable. Research data is current.*"
    
    if API_KEYS['OPENROUTER'] and domains:
        # Build the data for AI
        data_text = ""
        for domain_name, domain_data in domains.items():
            data_text += f"\n## {domain_name}\nTotal Papers: {domain_data['total_volume']}\n"
            for i, paper in enumerate(domain_data['recent_papers'][:5], 1):
                data_text += f"Paper #{i}: {paper['title']} ({paper['date']})\n"
        
        system_prompt = """You are a strategic research analyst. Analyze research data and provide:
1. KEY TAKEAWAY (one critical sentence)
2. INDUSTRY BREAKDOWNS by domain
3. CROSS-DOMAIN CONNECTIONS
4. KEY PREDICTIONS with confidence scores
5. STOCK PICKS (5 companies that benefit)
6. RISKS & LIMITATIONS
Format in clean markdown."""
        
        ai_result = ai.call_ai(
            f"Analyze this research data:\n{data_text}",
            system_prompt=system_prompt,
            model='grok',
            max_tokens=3000
        )
        
        if ai_result.success:
            ai_briefing = ai_result.data['content']
    
    return {
        'generated_at': datetime.now().isoformat(),
        'domains': domains,
        'ai_briefing': ai_briefing
    }


def fetch_for_economic_compass() -> Dict:
    """
    Fetch all data needed by economic-compass app.
    Output: data/economic-compass/latest.json
    """
    logger.info("=" * 50)
    logger.info("ECONOMIC-COMPASS: Starting data fetch")
    logger.info("=" * 50)
    
    market = MarketFetcher()
    crypto = CryptoFetcher()
    news = NewsFetcher()
    
    # Fetch crypto data with indicators
    btc = market.fetch_with_indicators('BTC-USD')
    eth = market.fetch_with_indicators('ETH-USD')
    
    # Fetch macro data
    macro_tickers = {
        'treasury_10y': '^TNX',
        'dxy': 'DX-Y.NYB',
        'gold': 'GC=F',
        'oil': 'CL=F',
        'sp500': '^GSPC',
        'tasi': '^TASI.SR'
    }
    macro_data = market.fetch_multi(macro_tickers)
    
    # Format macro data
    macro = {}
    for name, result in macro_data.items():
        if result.success:
            macro[name] = {
                'price': result.data['price'],
                'change_7d': 0  # Would need historical calc
            }
        else:
            macro[name] = {'price': 0, 'change_7d': 0}
    
    # Fetch Fear & Greed
    fng = crypto.fetch_fear_and_greed()
    
    # Fetch news
    news_result = news.fetch_rss()
    news_headlines = [a['title'] for a in (news_result.data or {}).get('articles', [])[:5]]
    
    return {
        'btc': btc.data if btc.success else None,
        'eth': eth.data if eth.success else None,
        'macro': macro,
        'fng': fng.data if fng.success else {'value': 50, 'value_classification': 'Neutral'},
        'news': news_headlines,
        'timestamp': datetime.now().isoformat()
    }


def fetch_for_hyper_analytical() -> Dict:
    """
    Fetch all data needed by hyper-analytical app.
    Output: apps/hyper-analytical/dashboard_data.json
    """
    logger.info("=" * 50)
    logger.info("HYPER-ANALYTICAL: Starting data fetch")
    logger.info("=" * 50)
    
    market = MarketFetcher()
    ai = AIFetcher()
    
    # Fetch crypto data
    btc = market.fetch_with_indicators('BTC-USD')
    eth = market.fetch_with_indicators('ETH-USD')
    dxy = market.fetch_ticker('DX-Y.NYB')
    
    # Calculate risk metric (simplified log regression proxy)
    risk_current = 0.5
    risk_prev = 0.48
    risk_history = [0.5] * 52
    
    if btc.success and btc.data.get('sma_20'):
        price = btc.data['price']
        sma = btc.data['sma_20']
        # Simple deviation-based risk
        deviation = (price - sma) / sma if sma > 0 else 0
        risk_current = min(1.0, max(0.0, 0.5 + deviation))
        risk_prev = risk_current - 0.02
        risk_history = [max(0, min(1, 0.5 + (i - 26) * 0.01)) for i in range(52)]
        risk_history[-1] = risk_current
    
    # Macro data
    macro = {
        'dxy': dxy.data['price'] if dxy.success else 104.0,
        'yield_inversion': -0.35,  # Would need FRED data
        'fed_rate': 5.33  # Would need FRED data
    }
    
    # Generate AI commentary
    commentary = "Analysis temporarily unavailable."
    
    if API_KEYS['OPENROUTER'] and btc.success:
        sma_20 = btc.data.get('sma_20', 0)
        ema_21 = btc.data.get('ema_21', 0)
        
        prompt = f"""Provide a professional crypto market analysis:

Bitcoin: ${btc.data['price']:,.0f}
Bull Market Support Band: 20W SMA ${sma_20:,.0f}, 21W EMA ${ema_21:,.0f}
Risk Metric: {risk_current:.2f}/1.0
DXY: {macro['dxy']:.2f}

Cover: Valuation, Risk Analysis, Macro Picture, Altcoin Dynamics, What to Expect, Actionable Verdict.
Be specific with numbers. Keep under 500 words."""
        
        ai_result = ai.call_ai(prompt, 
                                system_prompt="You are a crypto market analyst at Hyper Analytical.",
                                model='gpt')
        if ai_result.success:
            commentary = ai_result.data['content']
    
    return {
        'date': datetime.now().strftime('%B %d, %Y'),
        'btc_price': btc.data['price'] if btc.success else 0,
        'eth_btc': (eth.data['price'] / btc.data['price']) if (btc.success and eth.success and btc.data['price'] > 0) else 0,
        'bmsb': {
            'sma_20': btc.data.get('sma_20', 0) if btc.success else 0,
            'ema_21': btc.data.get('ema_21', 0) if btc.success else 0
        },
        'risk_metric': {
            'current': risk_current,
            'previous': risk_prev,
            'history': risk_history
        },
        'macro': macro,
        'commentary': commentary,
        'generated_at': datetime.now().isoformat()
    }


def fetch_for_intelligence_platform() -> Dict:
    """
    Fetch all data needed by intelligence-platform app.
    Output: apps/intelligence-platform/market_analysis.json
    """
    logger.info("=" * 50)
    logger.info("INTELLIGENCE-PLATFORM: Starting data fetch")
    logger.info("=" * 50)
    
    market = MarketFetcher()
    arxiv = ArxivFetcher()
    ai = AIFetcher()
    
    # Fetch market data
    btc = market.fetch_ticker('BTC-USD')
    eth = market.fetch_ticker('ETH-USD')
    sp500 = market.fetch_ticker('^GSPC')
    
    # Fetch arXiv AI papers
    arxiv_result = arxiv.fetch_papers('cat:cs.AI OR cat:cs.LG', max_results=5)
    
    # Generate analysis
    analysis = "Market analysis temporarily unavailable."
    
    if API_KEYS['OPENROUTER']:
        papers_text = "\n".join([p['title'] for p in arxiv_result.data.get('papers', [])]) if arxiv_result.success else "No papers"
        
        prompt = f"""Market Intelligence Brief:
BTC: ${btc.data['price']:,.0f if btc.success else 0}
ETH: ${eth.data['price']:,.0f if eth.success else 0}
S&P 500: {sp500.data['price']:,.0f if sp500.success else 0}

Latest AI Research:
{papers_text}

Provide a brief market intelligence summary."""
        
        ai_result = ai.call_ai(prompt, model='grok')
        if ai_result.success:
            analysis = ai_result.data['content']
    
    return {
        'timestamp': datetime.now().isoformat(),
        'markets': {
            'btc': btc.data['price'] if btc.success else 0,
            'eth': eth.data['price'] if eth.success else 0,
            'sp500': sp500.data['price'] if sp500.success else 0
        },
        'ai_research': arxiv_result.data.get('papers', []) if arxiv_result.success else [],
        'analysis': analysis
    }


def fetch_for_free_knowledge() -> Dict:
    """
    Fetch all data needed by free-knowledge app.
    Acts as a meta-analyst over other dashboards.
    Output: data/free-knowledge/latest.json
    """
    logger.info("=" * 50)
    logger.info("FREE-KNOWLEDGE: Starting data fetch")
    logger.info("=" * 50)
    
    ai = AIFetcher()
    
    # Helper to load JSON safely
    def load_json(path: pathlib.Path) -> Dict:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            logger.warning(f"Could not load {path}: {e}")
        return {}

    # Gather inputs from other dashboards
    # 1. Research Dashboard (AI Race)
    research_data = load_json(APPS_DIR / 'ai-race' / 'AI_RACE_CLEAN-main' / 'mission_data.json')
    
    # 2. Compute Tracker (Intelligence Platform)
    compute_data = load_json(APPS_DIR / 'intelligence-platform' / 'market_analysis.json')
    
    # 3. Capability Dashboard (Hyper Analytical)
    capability_data = load_json(APPS_DIR / 'hyper-analytical' / 'dashboard_data.json')
    
    # 4. Socio Impact Dashboard (Crash Detector)
    socio_data = load_json(DATA_DIR / 'crash-detector' / 'latest.json')
    
    daily_inputs = {
        "research_dashboard": research_data,
        "compute_tracker": compute_data,
        "capability_dashboard": capability_data,
        "socio_impact_dashboard": socio_data,
    }
    
    # Generate Daily Conclusion
    conclusion = {
        "signal_map": {},
        "trend_estimate": {"direction": "stable", "percent_change": 0},
        "meaning": "Analysis unavailable",
        "confidence": 0
    }
    
    if API_KEYS['OPENROUTER']:
        try:
            # Read system prompt
            prompt_path = APPS_DIR / 'free-knowledge' / 'system_prompt.txt'
            if prompt_path.exists():
                system_prompt = prompt_path.read_text(encoding='utf-8')
            else:
                # Fallback prompt if file missing
                system_prompt = """You are a meta-analyst. Fuse inputs into a daily AI advancement conclusion.
Output JSON: { "signal_map": {}, "trend_estimate": {}, "meaning": "", "confidence": 0-1 }"""
            
            user_message = json.dumps(daily_inputs, default=str)
            
            # Truncate if too long (simple safety)
            if len(user_message) > 100000:
                user_message = user_message[:100000] + "...(truncated)"
                
            ai_result = ai.call_ai(
                user_message,
                system_prompt=system_prompt,
                model='grok', # Using Grok for synthesis
                response_format='json_object'
            )
            
            if ai_result.success:
                content = ai_result.data['content']
                # Clean up markdown if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].strip()
                
                conclusion = json.loads(content)
                
        except Exception as e:
            logger.error(f"[FREE-KNOWLEDGE] Error generating conclusion: {e}")
            
    return {
        'timestamp': datetime.now().isoformat(),
        'daily_conclusion': conclusion,
        'inputs_snapshot': {k: 'Captured' for k in daily_inputs} # Don't duplicate all data
    }


def fetch_for_dashboard_orchestrator() -> Dict:
    """
    Fetch all data needed by dashboard-orchestrator app.
    Output: data/dashboard-orchestrator/latest.json
    """
    logger.info("=" * 50)
    logger.info("DASHBOARD-ORCHESTRATOR: Starting data fetch")
    logger.info("=" * 50)
    
    market = MarketFetcher()
    
    # Fetch key metrics for dashboard overview
    tickers = {
        'BTC': 'BTC-USD',
        'ETH': 'ETH-USD',
        'SP500': '^GSPC',
        'DXY': 'DX-Y.NYB',
        'Gold': 'GC=F'
    }
    
    data = market.fetch_multi(tickers)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'overview': {name: result.data['price'] if result.success else 0 for name, result in data.items()},
        'apps_status': {
            'ai-race': 'active',
            'crash-detector': 'active',
            'economic-compass': 'active',
            'hyper-analytical': 'active',
            'intelligence-platform': 'active',
            'free-knowledge': 'active'
        }
    }

# ===========================================
# SAVE FUNCTIONS
# ===========================================

def save_data(app_name: str, data: Dict):
    """Save fetched data to the appropriate location(s)"""
    
    # App-specific output paths
    output_paths = {
        'crash-detector': [
            DATA_DIR / 'crash-detector' / 'latest.json',
        ],
        'ai-race': [
            APPS_DIR / 'ai-race' / 'AI_RACE_CLEAN-main' / 'mission_data.json',
            DATA_DIR / 'ai-race' / 'latest.json',
        ],
        'economic-compass': [
            DATA_DIR / 'economic-compass' / 'latest.json',
        ],
        'hyper-analytical': [
            APPS_DIR / 'hyper-analytical' / 'dashboard_data.json',
            DATA_DIR / 'hyper-analytical' / 'latest.json',
        ],
        'intelligence-platform': [
            APPS_DIR / 'intelligence-platform' / 'market_analysis.json',
            DATA_DIR / 'intelligence-platform' / 'latest.json',
        ],
        'free-knowledge': [
            DATA_DIR / 'free-knowledge' / 'latest.json',
        ],
        'dashboard-orchestrator': [
            DATA_DIR / 'dashboard-orchestrator' / 'latest.json',
        ],
    }
    
    paths = output_paths.get(app_name, [DATA_DIR / app_name / 'latest.json'])
    
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')
        logger.info(f"✅ Saved: {path}")
    
    # Also save history for crash-detector
    if app_name == 'crash-detector':
        history_path = DATA_DIR / 'crash-detector' / 'history.json'
        try:
            if history_path.exists():
                history = json.loads(history_path.read_text(encoding='utf-8'))
            else:
                history = []
            history.append(data)
            history = history[-30:]  # Keep last 30
            history_path.write_text(json.dumps(history, indent=2), encoding='utf-8')
        except Exception as e:
            logger.warning(f"Could not update history: {e}")

# ===========================================
# MAIN ENTRY POINT
# ===========================================

def main():
    parser = argparse.ArgumentParser(description='Unified Data Fetcher for Monorepo')
    parser.add_argument('--all', action='store_true', help='Fetch data for all apps')
    parser.add_argument('--app', type=str, help='Fetch data for specific app')
    parser.add_argument('--apps', type=str, help='Comma-separated list of apps')
    parser.add_argument('--dry-run', action='store_true', help='Print what would be fetched')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("🚀 UNIFIED DATA FETCHER - Starting")
    logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Available fetch functions
    fetch_functions = {
        'crash-detector': fetch_for_crash_detector,
        'ai-race': fetch_for_ai_race,
        'economic-compass': fetch_for_economic_compass,
        'hyper-analytical': fetch_for_hyper_analytical,
        'intelligence-platform': fetch_for_intelligence_platform,
        'free-knowledge': fetch_for_free_knowledge,
        'dashboard-orchestrator': fetch_for_dashboard_orchestrator,
    }
    
    # Determine which apps to fetch for
    if args.all:
        apps_to_fetch = list(fetch_functions.keys())
    elif args.app:
        apps_to_fetch = [args.app]
    elif args.apps:
        apps_to_fetch = [a.strip() for a in args.apps.split(',')]
    else:
        # Default: all apps
        apps_to_fetch = list(fetch_functions.keys())
    
    logger.info(f"📦 Apps to process: {', '.join(apps_to_fetch)}")
    
    if args.dry_run:
        for app in apps_to_fetch:
            logger.info(f"[DRY RUN] Would fetch for: {app}")
        return
    
    # Fetch data for each app
    results = {'success': [], 'failed': []}
    
    for app in apps_to_fetch:
        if app in fetch_functions:
            try:
                logger.info(f"\n{'='*50}")
                logger.info(f"Processing: {app}")
                logger.info(f"{'='*50}")
                
                data = fetch_functions[app]()
                save_data(app, data)
                results['success'].append(app)
                
            except Exception as e:
                logger.error(f"❌ {app} - Error: {e}")
                import traceback
                traceback.print_exc()
                results['failed'].append(app)
        else:
            logger.warning(f"⚠️ {app} - No fetch function defined")
            results['failed'].append(app)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Successful: {len(results['success'])} - {', '.join(results['success'])}")
    if results['failed']:
        logger.info(f"❌ Failed: {len(results['failed'])} - {', '.join(results['failed'])}")
    logger.info("=" * 60)
    logger.info("🎉 UNIFIED DATA FETCHER - Complete")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
