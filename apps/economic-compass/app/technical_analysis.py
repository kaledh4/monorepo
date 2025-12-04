import pandas as pd
import numpy as np

def rsi(series, length=14):
    """
    Calculate Relative Strength Index (RSI)
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def sma(series, length):
    """
    Calculate Simple Moving Average (SMA)
    """
    return series.rolling(window=length).mean()

def ema(series, length):
    """
    Calculate Exponential Moving Average (EMA)
    """
    return series.ewm(span=length, adjust=False).mean()