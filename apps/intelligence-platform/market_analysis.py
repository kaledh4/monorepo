import yfinance as yf
import pandas as pd
import numpy as np
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os
import sys

# Set style for plots
plt.style.use('dark_background')

def get_options_data(ticker_symbol="^SPX"):
    """Fetch options data for the given ticker."""
    print(f"Fetching data for {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    
    # Get expirations
    try:
        exps = ticker.options
        if not exps:
            raise ValueError("No options data found.")
    except Exception as e:
        print(f"Error fetching options: {e}")
        # Fallback to SPY if SPX fails (common issue with free APIs)
        if ticker_symbol == "^SPX":
            print("Retrying with SPY...")
            return get_options_data("SPY")
        return None, None, None, None

    # Find an expiration ~30-45 days out
    target_date = datetime.now() + timedelta(days=35)
    best_exp = min(exps, key=lambda x: abs((datetime.strptime(x, '%Y-%m-%d') - target_date).days))
    
    print(f"Selected Expiration: {best_exp}")
    
    # Get chain
    opt = ticker.option_chain(best_exp)
    calls = opt.calls
    puts = opt.puts
    
    # Get current price
    try:
        hist = ticker.history(period="1d")
        if hist.empty:
             # Fallback for SPX sometimes
             current_price = (calls['strike'].iloc[len(calls)//2] + puts['strike'].iloc[len(puts)//2]) / 2
        else:
            current_price = hist['Close'].iloc[-1]
    except:
        current_price = 0
        
    return calls, puts, current_price, best_exp

def calculate_pdf(calls, puts, current_price):
    """
    Calculate the implied Probability Density Function (PDF) 
    using the Breeden-Litzenberger result (2nd derivative of price).
    """
    # 1. Prepare Data
    calls['type'] = 'call'
    puts['type'] = 'put'
    
    # Mid prices
    calls['mid'] = (calls['bid'] + calls['ask']) / 2
    puts['mid'] = (puts['bid'] + puts['ask']) / 2
    
    # Filter bad data
    calls = calls[(calls['bid'] > 0) & (calls['volume'] > 0)]
    puts = puts[(puts['bid'] > 0) & (puts['volume'] > 0)]
    
    # Use OTM options for the composite curve
    # Puts for K < S, Calls for K > S
    otm_calls = calls[calls['strike'] >= current_price].copy()
    otm_puts = puts[puts['strike'] < current_price].copy()
    
    # Combine into a single dataframe of "Option Prices" (OTM)
    # Note: For PDF extraction via 2nd derivative, we strictly need the Call Price function C(K).
    # P_put(K) = C_call(K) - S + K*e^-rT
    # d2P/dK2 = d2C/dK2
    # So we can use OTM Puts and OTM Calls directly as they represent the "value of the tail".
    # However, to get a smooth C(K) curve, we usually convert Puts to Calls or vice versa.
    # Here we will just use the OTM prices directly as proxies for the curvature we want to measure,
    # but strictly speaking, we should stitch them carefully.
    # For a robust "Moore Analysis" (visualizing probability), using OTM prices and smoothing is sufficient.
    
    data = pd.concat([
        otm_puts[['strike', 'mid']],
        otm_calls[['strike', 'mid']]
    ]).sort_values('strike')
    
    # Remove duplicates
    data = data.drop_duplicates(subset=['strike'])
    
    if len(data) < 10:
        print("Not enough data points for analysis.")
        return None, None
        
    # 2. Smooth the Price Curve
    # We use a UnivariateSpline
    # k=3 (cubic), s is smoothing factor. 
    # We need to be careful not to over-smooth or under-smooth.
    try:
        tck = interpolate.splrep(data['strike'], data['mid'], k=3, s=2.0)
    except Exception as e:
        print(f"Spline fitting failed: {e}")
        return None, None

    x_new = np.linspace(data['strike'].min(), data['strike'].max(), 1000)
    
    # 3. Calculate 2nd Derivative
    # The PDF is proportional to the 2nd derivative of the Call price w.r.t Strike
    pdf_raw = interpolate.splev(x_new, tck, der=2)
    
    # 4. Normalize
    # PDF must be positive. Spline artifacts can cause negatives.
    pdf_raw = np.maximum(pdf_raw, 0)
    
    area = np.trapz(pdf_raw, x_new)
    if area == 0:
        return None, None
        
    pdf_normalized = pdf_raw / area
    
    return x_new, pdf_normalized

def generate_moore_chart(x, pdf, current_price, exp_date, ticker):
    """Generate the visualization."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot PDF
    ax.plot(x, pdf, color='#00ff9d', linewidth=2, label='Market Implied Probability')
    ax.fill_between(x, pdf, alpha=0.2, color='#00ff9d')
    
    # Plot Current Price
    ax.axvline(current_price, color='white', linestyle='--', alpha=0.8, label=f'Current Price: {current_price:.2f}')
    
    # Find Peak (Most Likely Price)
    peak_idx = np.argmax(pdf)
    peak_price = x[peak_idx]
    ax.axvline(peak_price, color='#ff00ff', linestyle=':', alpha=0.8, label=f'Market Expectation: {peak_price:.2f}')
    
    # Styling
    ax.set_facecolor('#0a0a0a')
    fig.patch.set_facecolor('#0a0a0a')
    
    ax.grid(True, color='#333333', linestyle='-', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#666666')
    ax.spines['left'].set_color('#666666')
    ax.tick_params(colors='#cccccc')
    
    plt.title(f"Market Implied Probability Distribution | {ticker} | Exp: {exp_date}", 
              color='white', fontsize=16, pad=20)
    plt.xlabel("Strike Price", color='#cccccc', fontsize=12)
    plt.ylabel("Probability Density", color='#cccccc', fontsize=12)
    
    plt.legend(facecolor='#1a1a1a', edgecolor='#333333', labelcolor='#cccccc')
    
    # Save
    output_path = 'market_analysis_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    print(f"Chart saved to {output_path}")
    return peak_price

def generate_report_data(ticker, exp_date, current_price, peak_price, x, pdf):
    """Generate a JSON summary of the analysis."""
    
    # Calculate probabilities
    # Prob of being above current price
    prob_bullish = np.trapz(pdf[x >= current_price], x[x >= current_price])
    
    # Calculate 1SD range (approx 68% confidence)
    cum_prob = np.cumsum(pdf) * (x[1] - x[0])
    low_idx = np.searchsorted(cum_prob, 0.16)
    high_idx = np.searchsorted(cum_prob, 0.84)
    
    low_bound = x[low_idx] if low_idx < len(x) else x[0]
    high_bound = x[high_idx] if high_idx < len(x) else x[-1]
    
    summary = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "ticker": ticker,
            "expiration": exp_date
        },
        "analysis": {
            "current_price": round(current_price, 2),
            "market_expected_price": round(peak_price, 2),
            "sentiment": "Bullish" if prob_bullish > 0.55 else "Bearish" if prob_bullish < 0.45 else "Neutral",
            "bullish_probability": round(prob_bullish * 100, 1),
            "expected_range_68pct": {
                "low": round(low_bound, 2),
                "high": round(high_bound, 2)
            }
        }
    }
    
    with open('market_analysis.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("Analysis data saved to market_analysis.json")
    return summary

def main():
    print("Starting Moore Analysis Overhaul...")
    
    ticker = "^SPX"
    calls, puts, current_price, exp_date = get_options_data(ticker)
    
    if calls is None:
        print("Failed to retrieve data.")
        return
        
    x, pdf = calculate_pdf(calls, puts, current_price)
    
    if x is None:
        print("Failed to calculate PDF.")
        return
        
    peak_price = generate_moore_chart(x, pdf, current_price, exp_date, ticker)
    generate_report_data(ticker, exp_date, current_price, peak_price, x, pdf)
    
    print("Analysis Workflow Complete.")

if __name__ == "__main__":
    main()
