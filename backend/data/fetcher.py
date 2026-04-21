import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockDataFetcher:
    """Fetch and cache stock data"""
    
    NIFTY50_TICKERS = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS'
    ]
    
    def __init__(self):
        self.cache = {}
    
    def fetch_historical(self, ticker='RELIANCE.NS', period='2y'):
        """Fetch historical data"""
        try:
            logger.info(f"Fetching {ticker} data...")
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                raise ValueError(f"No data for {ticker}")
            
            df = df.reset_index()
            df.columns = [col.capitalize() for col in df.columns]
            
            logger.info(f"✅ Fetched {len(df)} rows for {ticker}")
            self.cache[ticker] = df
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {e}")
            return None
    
    def fetch_live_price(self, ticker):
        """Get current price"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period='1d', interval='1m')
            return float(data['Close'].iloc[-1]) if not data.empty else None
        except:
            return None
    
    def get_stock_info(self, ticker):
        """Get stock metadata"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0)
            }
        except:
            return {'name': ticker}