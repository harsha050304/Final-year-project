import numpy as np
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TradingAgent:
    """Rule-based trading agent with LSTM predictions"""
    
    def __init__(self, initial_capital=100000):
        self.cash = initial_capital
        self.holdings = {}
        self.trade_history = []
        self.portfolio_value_history = []
        
    def make_decision(self, ticker, current_price, prediction_data, technical_data):
        """
        Decide: BUY, SELL, or HOLD
        
        Strategy:
        - BUY if: Predicted UP + RSI < 40 (oversold) + Price above SMA20
        - SELL if: Predicted DOWN + RSI > 70 (overbought)
        - HOLD otherwise
        """
        pred_change = prediction_data['change_percent']
        confidence = prediction_data['confidence']
        direction = prediction_data['direction']
        
        rsi = technical_data['Rsi']
        price_to_sma = current_price / technical_data['Sma_20']
        
        # BUY conditions
        if (direction == 'UP' and 
            confidence > 0.6 and
            rsi < 40 and
            price_to_sma > 0.98 and
            ticker not in self.holdings):
            
            shares = int((self.cash * 0.95) / current_price)  # Use 95% of cash
            if shares > 0:
                return {
                    'action': 'BUY',
                    'shares': shares,
                    'price': current_price,
                    'reason': f'Predicted {pred_change:+.1f}%, RSI={rsi:.0f} (oversold)',
                    'confidence': confidence
                }
        
        # SELL conditions
        elif (ticker in self.holdings and (
            (direction == 'DOWN' and confidence > 0.6) or
            rsi > 70 or
            pred_change < -2)):
            
            shares = self.holdings[ticker]['shares']
            return {
                'action': 'SELL',
                'shares': shares,
                'price': current_price,
                'reason': f'Predicted {pred_change:+.1f}%, RSI={rsi:.0f}',
                'confidence': confidence
            }
        
        return {'action': 'HOLD', 'reason': 'No strong signal'}
    
    def execute_trade(self, ticker, decision):
        """Execute buy/sell"""
        if decision['action'] == 'BUY':
            cost = decision['shares'] * decision['price']
            self.cash -= cost
            self.holdings[ticker] = {
                'shares': decision['shares'],
                'buy_price': decision['price'],
                'buy_date': datetime.now()
            }
            
        elif decision['action'] == 'SELL':
            revenue = decision['shares'] * decision['price']
            self.cash += revenue
            buy_price = self.holdings[ticker]['buy_price']
            profit = (decision['price'] - buy_price) * decision['shares']
            profit_pct = (profit / (buy_price * decision['shares'])) * 100
            
            decision['profit'] = profit
            decision['profit_percent'] = profit_pct
            
            del self.holdings[ticker]
        
        # Log trade
        trade_record = {
            'timestamp': datetime.now(),
            'ticker': ticker,
            **decision
        }
        self.trade_history.append(trade_record)
        
        return trade_record
    
    def get_portfolio_value(self, current_prices):
        """Calculate total portfolio value"""
        holdings_value = sum(
            self.holdings[ticker]['shares'] * current_prices.get(ticker, 0)
            for ticker in self.holdings
        )
        return self.cash + holdings_value
    
    def get_stats(self, current_prices):
        """Get portfolio statistics"""
        total_value = self.get_portfolio_value(current_prices)
        
        return {
            'cash': self.cash,
            'holdings_value': total_value - self.cash,
            'total_value': total_value,
            'returns': ((total_value - 100000) / 100000) * 100,
            'num_trades': len(self.trade_history),
            'holdings': self.holdings
        }

# Backtesting
class Backtester:
    """Backtest trading strategy"""
    
    def __init__(self, agent, predictor):
        self.agent = agent
        self.predictor = predictor
        
    def run(self, df, ticker='RELIANCE.NS'):
        """Run backtest on historical data"""
        logger.info(f"Running backtest on {len(df)} days...")
        
        results = []
        
        # Start from day 60 (need lookback data)
        for i in range(60, len(df)):
            current_data = df.iloc[:i+1]
            current_price = current_data['Close'].iloc[-1]
            
            # Get prediction
            pred_data = self.predictor.predict_confidence(current_data)
            
            # Get technical indicators
            tech_data = current_data.iloc[-1]
            
            # Make decision
            decision = self.agent.make_decision(ticker, current_price, pred_data, tech_data)
            
            # Execute if not HOLD
            if decision['action'] != 'HOLD':
                trade = self.agent.execute_trade(ticker, decision)
                results.append(trade)
            
            # Track portfolio value
            portfolio_value = self.agent.get_portfolio_value({ticker: current_price})
            self.agent.portfolio_value_history.append({
                'date': current_data['Date'].iloc[-1],
                'value': portfolio_value
            })
        
        return results
    
    def get_metrics(self):
        """Calculate performance metrics"""
        if not self.agent.portfolio_value_history:
            return {}
        
        values = [p['value'] for p in self.agent.portfolio_value_history]
        returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values))]
        
        final_value = values[-1]
        total_return = ((final_value - 100000) / 100000) * 100
        
        # Sharpe ratio (simplified)
        avg_return = np.mean(returns) if returns else 0
        std_return = np.std(returns) if returns else 1
        sharpe = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        
        # Win rate
        trades = [t for t in self.agent.trade_history if 'profit' in t]
        wins = [t for t in trades if t['profit'] > 0]
        win_rate = (len(wins) / len(trades)) * 100 if trades else 0
        
        return {
            'final_value': final_value,
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'total_trades': len(self.agent.trade_history),
            'win_rate': win_rate,
            'max_drawdown': self._calculate_max_drawdown(values)
        }
    
    def _calculate_max_drawdown(self, values):
        """Calculate maximum drawdown"""
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd * 100

# Run backtest
if __name__ == "__main__":
    import sys
    sys.path.append('..')
    
    from data.fetcher import StockDataFetcher
    from data.processor import DataProcessor
    from lstm_model import LSTMPredictor
    
    # Load data
    fetcher = StockDataFetcher()
    df = fetcher.fetch_historical('RELIANCE.NS', '1y')
    
    processor = DataProcessor()
    df = processor.add_technical_indicators(df)
    
    # Load trained model
    predictor = LSTMPredictor()
    predictor.load()
    
    # Run backtest
    agent = TradingAgent()
    backtester = Backtester(agent, predictor)
    
    trades = backtester.run(df)
    metrics = backtester.get_metrics()
    
    print("\n📊 BACKTEST RESULTS")
    print("="*50)
    print(f"Total Trades: {metrics['total_trades']}")
    print(f"Win Rate: {metrics['win_rate']:.1f}%")
    print(f"Final Value: ₹{metrics['final_value']:,.0f}")
    print(f"Total Return: {metrics['total_return']:+.2f}%")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
    
    print(f"\n📝 Recent Trades:")
    for trade in trades[-5:]:
        print(f"{trade['action']} {trade.get('shares', 0)} @ ₹{trade['price']:.2f}")
        if 'profit' in trade:
            print(f"  Profit: ₹{trade['profit']:,.0f} ({trade['profit_percent']:+.1f}%)")