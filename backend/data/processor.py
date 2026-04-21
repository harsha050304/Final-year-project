import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange

class DataProcessor:
    """Add technical indicators and features"""
    
    @staticmethod
    def add_technical_indicators(df):
        """Add all technical indicators"""
        df = df.copy()
        
        # Moving Averages
        df['Sma_20'] = SMAIndicator(df['Close'], window=20).sma_indicator()
        df['Sma_50'] = SMAIndicator(df['Close'], window=50).sma_indicator()
        df['Ema_12'] = EMAIndicator(df['Close'], window=12).ema_indicator()
        
        # MACD
        macd = MACD(df['Close'])
        df['Macd'] = macd.macd()
        df['Macd_signal'] = macd.macd_signal()
        
        # RSI
        df['Rsi'] = RSIIndicator(df['Close']).rsi()
        
        # Bollinger Bands
        bb = BollingerBands(df['Close'])
        df['Bb_high'] = bb.bollinger_hband()
        df['Bb_low'] = bb.bollinger_lband()
        
        # ATR (Volatility)
        df['Atr'] = AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
        
        # Price features
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(20).std()
        
        # Volume
        df['Volume_sma'] = df['Volume'].rolling(20).mean()
        
        return df.dropna()
    
    @staticmethod
    def prepare_lstm_data(df, lookback=60):
        """Prepare data for LSTM"""
        features = [
            'Close', 'Volume', 'Rsi', 'Macd', 'Sma_20', 'Sma_50',
            'Bb_high', 'Bb_low', 'Atr', 'Volatility'
        ]
        
        data = df[features].values
        
        X, y = [], []
        for i in range(lookback, len(data)):
            X.append(data[i-lookback:i])
            y.append(data[i, 0])  # Predict Close price
        
        return np.array(X), np.array(y), features

# Test
if __name__ == "__main__":
    from fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    df = fetcher.fetch_historical('RELIANCE.NS', '2y')
    
    processor = DataProcessor()
    df_processed = processor.add_technical_indicators(df)
    
    print(f"Processed {len(df_processed)} rows")
    print(f"Features: {df_processed.columns.tolist()}")
    
    X, y, features = processor.prepare_lstm_data(df_processed)
    print(f"LSTM data shape: X={X.shape}, y={y.shape}")