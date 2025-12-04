import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_insight(data):
    """
    Generates a market insight based on the provided data using OpenRouter.
    """
    
    # Configure OpenRouter (initialized here to ensure env vars are loaded)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_KEY") or os.getenv("OPENROUTER_API_KEY"),
    )
    
    # Use the Alibaba Tongyi DeepResearch model
    MODEL = os.getenv("OPENROUTER_MODEL", "alibaba/tongyi-deepresearch-30b-a3b:free")
    
    # Construct the prompt
    prompt = f"""
    You are a professional Crypto Market Strategist and Macro Analyst.
    Analyze the following market data and provide a daily insight report.
    
    DATA:
    {json.dumps(data, indent=2)}
    
    INSTRUCTIONS:
    1. **Macro Context**: Analyze Treasury Yields, DXY, Gold, Oil, and S&P 500. Are we Risk-On or Risk-Off?
    2. **Crypto Structure (Meso)**: Look at BTC's relation to its 50W and 200W Moving Averages and the Bull Market Support Band (SMA20/EMA21). Is the trend bullish or bearish?
    3. **Micro Pulse**: Look at RSI and Fear & Greed. Is the market overextended?
    4. **TASI Insight**: Briefly mention the Saudi TASI market direction based on the data.
    5. **Actionable Advice**: Give a clear recommendation: Accumulate, Hold, or De-risk/Step Back.
    6. **Weekly Watchlist**: Provide 3-5 important things to follow this week including:
       - Key economic events and data releases
       - Central bank meetings or announcements
       - Hashtags for social sentiment tracking (format as #hashtag)
       - Microeconomic factors affecting specific sectors
       - Calendar events that could impact markets
       - Format each item on a separate line with clear numbering (1., 2., 3., etc.)
       - Make each item copyable as a single line
       - Use bullet points for better readability
    
    FORMAT:
    Return the response in HTML format (just the body content, no <html> tags) with nice formatting (<h2>, <ul>, <p>, <strong>).
    Use a "Premium" tone: calm, objective, professional.
    For the Weekly Watchlist section, ensure each item is on its own line and easily copyable.
    
    Structure:
    <h2>🦅 Macro View</h2>
    <p>...</p>
    
    <h2>BTC Market Structure</h2>
    <p>...</p>
    
    <h2>🇸🇦 TASI & Global Markets</h2>
    <p>...</p>
    
    <h2>🎯 Actionable Verdict</h2>
    <p><strong>[ACCUMULATE / HOLD / DE-RISK]</strong></p>
    <p>...</p>
    
    <h2>📅 Weekly Watchlist</h2>
    <ul>
      <li>1. ...</li>
      <li>2. ...</li>
      <li>3. ...</li>
    </ul>
    """
    
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful and insightful crypto market analyst. Always respond in English, regardless of any language preferences."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"<p>Error generating insight: {str(e)}</p>"

if __name__ == "__main__":
    # Test run
    from data_fetcher import get_all_data
    data = get_all_data()
    print(generate_insight(data))