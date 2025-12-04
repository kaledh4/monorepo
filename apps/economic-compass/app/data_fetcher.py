import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from app.technical_analysis import rsi, sma, ema

def get_crypto_data(ticker="BTC-USD"):
    # Fetch 5 years of data to ensure enough for 200W MA
    df = yf.download(ticker, period="5y", interval="1wk")
    
    # Ensure we have data
    if df.empty:
        return None

    # Flatten MultiIndex columns if they exist (yfinance update)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Calculate Indicators
    # RSI 14
    df['RSI'] = rsi(df['Close'], length=14)
    
    # Moving Averages (Weekly)
    df['MA50'] = sma(df['Close'], length=50)
    df['MA200'] = sma(df['Close'], length=200)
    
    # Bull Market Support Band
    df['SMA20'] = sma(df['Close'], length=20)
    df['EMA21'] = ema(df['Close'], length=21)
    
    # Get latest valid row
    latest = df.iloc[-1]
    prev_week = df.iloc[-2]
    
    current_price = latest['Close']
    
    return {
        "price": float(current_price),
        "rsi": float(latest['RSI']) if not pd.isna(latest['RSI']) else 0,
        "ma50": float(latest['MA50']) if not pd.isna(latest['MA50']) else 0,
        "ma200": float(latest['MA200']) if not pd.isna(latest['MA200']) else 0,
        "bull_band_sma20": float(latest['SMA20']) if not pd.isna(latest['SMA20']) else 0,
        "bull_band_ema21": float(latest['EMA21']) if not pd.isna(latest['EMA21']) else 0,
        "trend_weekly": "Bullish" if current_price > latest['MA50'] else "Bearish"
    }

def get_macro_data():
    tickers = {
        "treasury_10y": "^TNX",
        "dxy": "DX-Y.NYB",
        "gold": "GC=F",
        "oil": "CL=F",
        "sp500": "^GSPC",
        "tasi": "^TASI.SR"
    }
    
    data = {}
    
    # Fetch all at once for efficiency
    tickers_str = " ".join(tickers.values())
    try:
        df = yf.download(tickers_str, period="1y", interval="1d", progress=False)
    except Exception as e:
        print(f"Error downloading macro data: {e}")
        return {k: {"price": 0, "change_7d": 0} for k in tickers}
    
    # Handle yfinance structure
    # If multiple tickers, df.columns is MultiIndex (Price, Ticker) or just Ticker if flattened?
    # Usually it's (Price, Ticker). We want 'Close'.
    
    close_data = pd.DataFrame()
    
    if isinstance(df.columns, pd.MultiIndex):
        try:
            close_data = df['Close']
        except KeyError:
            # Maybe it's already flattened or different structure
             print("Could not find 'Close' in MultiIndex")
             return {k: {"price": 0, "change_7d": 0} for k in tickers}
    else:
        # If single level, it might be just Price columns if we downloaded only one ticker, 
        # but we downloaded multiple. 
        # Or maybe yfinance failed to group.
        # Let's assume it's usable if we can access by ticker.
        if 'Close' in df.columns:
             close_data = df[['Close']] # This would be wrong for multiple tickers
        else:
             close_data = df # Assume columns are tickers if 'Close' isn't a level
        
    for name, ticker in tickers.items():
        try:
            # Get series for this ticker
            if ticker in close_data.columns:
                series = close_data[ticker]
            else:
                # Try finding it if columns are not exact matches (sometimes ^ is stripped)
                # But yfinance usually keeps it.
                # Fallback: check if we have data at all
                data[name] = {"price": 0, "change_7d": 0}
                continue
            
            series = series.dropna()
            if series.empty:
                data[name] = {"price": 0, "change_7d": 0}
                continue
                
            latest = series.iloc[-1]
            # Get 7 days ago (approx 5 trading days)
            if len(series) >= 6:
                seven_days_ago = series.iloc[-6]
            else:
                seven_days_ago = series.iloc[0]
            
            if seven_days_ago == 0:
                change = 0
            else:
                change = ((latest - seven_days_ago) / seven_days_ago) * 100
            
            data[name] = {
                "price": float(latest),
                "change_7d": float(change)
            }
        except Exception as e:
            print(f"Error processing {name}: {e}")
            data[name] = {"price": 0, "change_7d": 0}
            
    return data

def get_fear_and_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1")
        data = r.json()
        return data['data'][0]
    except:
        return {"value": 50, "value_classification": "Neutral"}

def get_news_headlines():
    # Simple RSS fetcher for crypto news
    rss_url = "https://cointelegraph.com/rss"
    try:
        r = requests.get(rss_url)
        # Very simple XML parse to avoid extra deps if possible, or just grab titles
        from xml.etree import ElementTree
        root = ElementTree.fromstring(r.content)
        
        items = []
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text
            items.append(title)
        return items
    except Exception as e:
        print(f"News error: {e}")
        return ["No news available."]

def get_all_data():
    btc = get_crypto_data("BTC-USD")
    eth = get_crypto_data("ETH-USD")
    macro = get_macro_data()
    fng = get_fear_and_greed()
    news = get_news_headlines()
    
    return {
        "btc": btc,
        "eth": eth,
        "macro": macro,
        "fng": fng,
        "news": news,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_all_data(), indent=2))
