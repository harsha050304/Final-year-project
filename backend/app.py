from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database.db import Database
from data.fetcher import StockDataFetcher
from data.processor import DataProcessor
from models.lstm_model import LSTMPredictor
from models.trading_agent import TradingAgent, Backtester
from explainability.explainer import TradingExplainer, get_trade_explanation
from chatbot.trading_assistant import TradingAssistant

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
db = Database()
fetcher = StockDataFetcher()
processor = DataProcessor()
predictor = LSTMPredictor()
agent = TradingAgent()
assistant = TradingAssistant()

# Load trained model
try:
    predictor.load('models/saved')
    logger.info("✅ LSTM model loaded")
except Exception as e:
    logger.warning(f"⚠️ Model not found: {e}. Train it first!")

# Global state
active_ticker = 'RELIANCE.NS'
latest_data = {}

# Enable CORS for all routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def home():
    """API Home - Status Check"""
    return jsonify({
        'app': 'TradeWise AI',
        'status': 'operational',
        'version': '1.0.0',
        'tagline': 'Your AI-Powered Trading Companion',
        'endpoints': {
            'stocks': '/api/stocks',
            'stock_data': '/api/stock/<ticker>',
            'prediction': '/api/predict/<ticker>',
            'trade': '/api/trade',
            'portfolio': '/api/portfolio',
            'backtest': '/api/backtest/<ticker>',
            'leaderboard': '/api/leaderboard',
            'explanation': '/api/explain/<ticker>',
            'chatbot': '/api/chatbot',
            'live_price': '/api/live-price/<ticker>',
            'market_status': '/api/market-status',
            'watchlist': '/api/watchlist',
            'performance': '/api/performance',
            'paper_trade_init': '/api/paper-trade/init'
        }
    })

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Get available stocks"""
    return jsonify({
        'success': True,
        'stocks': [
            {
                'ticker': t, 
                'name': t.replace('.NS', ''), 
                'active': t == active_ticker,
                'exchange': 'NSE'
            }
            for t in Config.SUPPORTED_TICKERS
        ]
    })

@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_data(ticker):
    """Get stock historical data with indicators"""
    try:
        logger.info(f"Fetching data for {ticker}")
        
        # Fetch data
        df = fetcher.fetch_historical(ticker, period='6mo')
        df = processor.add_technical_indicators(df)
        
        # Convert to JSON
        data = df.tail(100).to_dict('records')
        
        # Get current price
        current_price = fetcher.fetch_live_price(ticker)
        if not current_price:
            current_price = df['Close'].iloc[-1]
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'current_price': float(current_price),
            'data': data,
            'last_update': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching {ticker}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predict/<ticker>', methods=['GET'])
def predict_price(ticker):
    """Get AI prediction for stock"""
    try:
        logger.info(f"Predicting {ticker}")
        
        # Fetch and process data
        df = fetcher.fetch_historical(ticker, period='1y')
        df = processor.add_technical_indicators(df)
        
        # Get prediction
        prediction = predictor.predict_confidence(df)
        
        # Save to database
        db.save_prediction(
            ticker=ticker,
            current_price=prediction['current_price'],
            predicted_price=prediction['predicted_price'],
            confidence=prediction['confidence']
        )
        
        # Get technical signals
        latest = df.iloc[-1]
        signals = {
            'rsi': {
                'value': float(latest['Rsi']),
                'signal': 'Oversold' if latest['Rsi'] < 30 else 'Overbought' if latest['Rsi'] > 70 else 'Neutral'
            },
            'macd': {
                'value': float(latest['Macd']),
                'signal': 'Bullish' if latest['Macd'] > latest['Macd_signal'] else 'Bearish'
            },
            'trend': {
                'sma20': float(latest['Sma_20']),
                'sma50': float(latest['Sma_50']),
                'signal': 'Uptrend' if latest['Sma_20'] > latest['Sma_50'] else 'Downtrend'
            }
        }
        
        logger.info(f"Prediction complete: {prediction['direction']} with {prediction['confidence']:.2%} confidence")
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'prediction': prediction,
            'signals': signals,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Prediction error for {ticker}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    """Execute a trade"""
    try:
        data = request.json
        ticker = data.get('ticker')
        action = data.get('action')  # BUY, SELL, or None for AI decision
        
        logger.info(f"Trade request: {action} {ticker}")
        
        # Get current data
        df = fetcher.fetch_historical(ticker, period='6mo')
        df = processor.add_technical_indicators(df)
        current_price = fetcher.fetch_live_price(ticker) or df['Close'].iloc[-1]
        
        # Get prediction
        prediction = predictor.predict_confidence(df)
        
        # Make decision
        decision = agent.make_decision(
            ticker, current_price, prediction, df.iloc[-1]
        )
        
        # If user forced action, override
        if action:
            decision['action'] = action
            decision['shares'] = data.get('shares', decision.get('shares', 0))
            decision['price'] = current_price
        
        # Execute trade
        if decision['action'] != 'HOLD':
            trade = agent.execute_trade(ticker, decision)
            
            # Save to database
            db.save_trade(trade)
            
            # Update portfolio
            portfolio = agent.get_stats({ticker: current_price})
            db.update_portfolio(portfolio)
            
            # Check for achievements
            achievements = check_achievements(agent, trade)
            
            # Emit to websocket
            socketio.emit('trade_executed', {
                'trade': trade,
                'portfolio': portfolio,
                'achievements': achievements
            })
            
            logger.info(f"Trade executed: {trade['action']} {trade.get('shares', 0)} shares @ ₹{trade['price']:.2f}")
            
            return jsonify({
                'success': True,
                'trade': trade,
                'portfolio': portfolio,
                'achievements': achievements
            })
        else:
            return jsonify({
                'success': False,
                'message': decision['reason']
            })
            
    except Exception as e:
        logger.error(f"Trade execution error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio"""
    try:
        portfolio = db.get_portfolio()
        
        # Get current prices for holdings
        current_prices = {}
        holdings_details = []
        
        for ticker in portfolio.get('holdings', {}).keys():
            price = fetcher.fetch_live_price(ticker)
            if not price:
                df = fetcher.fetch_historical(ticker, period='1d')
                price = df['Close'].iloc[-1] if not df.empty else 0
            
            current_prices[ticker] = price
            
            info = portfolio['holdings'][ticker]
            holdings_details.append({
                'ticker': ticker,
                'shares': info['shares'],
                'buy_price': info['buy_price'],
                'current_price': float(price),
                'profit_loss': (price - info['buy_price']) * info['shares'],
                'profit_loss_pct': ((price - info['buy_price']) / info['buy_price']) * 100
            })
        
        # Update stats
        stats = agent.get_stats(current_prices)
        
        return jsonify({
            'success': True,
            'portfolio': stats,
            'holdings_details': holdings_details
        })
        
    except Exception as e:
        logger.error(f"Portfolio error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backtest/<ticker>', methods=['GET'])
def run_backtest(ticker):
    """Run backtest on historical data"""
    try:
        logger.info(f"Running backtest for {ticker}")
        
        # Get data
        df = fetcher.fetch_historical(ticker, period='1y')
        df = processor.add_technical_indicators(df)
        
        # Create new agent for backtest
        test_agent = TradingAgent()
        backtester = Backtester(test_agent, predictor)
        
        # Run backtest
        trades = backtester.run(df, ticker)
        metrics = backtester.get_metrics()
        
        # Portfolio value history
        value_history = test_agent.portfolio_value_history
        
        logger.info(f"Backtest complete: {metrics['total_return']:.2f}% return, {metrics['total_trades']} trades")
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'metrics': metrics,
            'trades': trades[-20:],  # Last 20 trades
            'portfolio_history': value_history
        })
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get gamification leaderboard"""
    try:
        current_stats = agent.get_stats({})
        
        # Mock leaderboard (in production, fetch from database)
        leaderboard = [
            {
                'rank': 1, 
                'name': 'You', 
                'returns': current_stats.get('returns', 0), 
                'trades': len(agent.trade_history), 
                'badges': 5
            },
            {'rank': 2, 'name': 'ProTrader', 'returns': 15.2, 'trades': 45, 'badges': 8},
            {'rank': 3, 'name': 'StockGuru', 'returns': 12.8, 'trades': 38, 'badges': 6},
            {'rank': 4, 'name': 'BullRunner', 'returns': 10.5, 'trades': 32, 'badges': 4},
            {'rank': 5, 'name': 'MarketMaster', 'returns': 8.3, 'trades': 28, 'badges': 3},
        ]
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard,
            'your_rank': 1
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/explain/<ticker>', methods=['GET'])
def explain_decision(ticker):
    """Get detailed explanation for trading decision"""
    try:
        logger.info(f"Generating explanation for {ticker}")
        
        # Fetch and process data
        df = fetcher.fetch_historical(ticker, period='1y')
        df = processor.add_technical_indicators(df)
        
        # Get explanation
        explanation = get_trade_explanation(predictor, ticker, df)
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'explanation': explanation
        })
        
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """AI Trading Assistant Chatbot"""
    try:
        data = request.json
        message = data.get('message', '')
        
        logger.info(f"Chatbot query: {message}")
        
        # Get context
        context = {
            'portfolio': db.get_portfolio(),
            'current_ticker': data.get('ticker', 'RELIANCE.NS')
        }
        
        # Process query
        response = assistant.process_query(message, context)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paper-trade/init', methods=['POST'])
def initialize_paper_trading():
    """Initialize paper trading session"""
    try:
        data = request.json
        capital = data.get('capital', 100000)
        
        logger.info(f"Initializing paper trading with ₹{capital:,.0f}")
        
        # Reset agent with new capital
        global agent
        agent = TradingAgent(initial_capital=capital)
        
        # Save to database
        db.update_portfolio({
            'cash': capital,
            'holdings': {},
            'total_value': capital,
            'returns': 0,
            'trades': []
        })
        
        return jsonify({
            'success': True,
            'message': f'Paper trading initialized with ₹{capital:,.0f}',
            'portfolio': {
                'cash': capital,
                'total_value': capital
            }
        })
        
    except Exception as e:
        logger.error(f"Paper trading init error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/live-price/<ticker>', methods=['GET'])
def get_live_price(ticker):
    """Get real-time price updates"""
    try:
        price = fetcher.fetch_live_price(ticker)
        
        if price:
            # Get additional data
            df = fetcher.fetch_historical(ticker, period='1d')
            change = 0
            if len(df) > 1:
                prev_close = df['Close'].iloc[-2]
                change = ((price - prev_close) / prev_close) * 100
            
            return jsonify({
                'success': True,
                'ticker': ticker,
                'price': float(price),
                'change': float(change),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'success': False, 'error': 'Price not available'}), 404
            
    except Exception as e:
        logger.error(f"Live price error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/market-status', methods=['GET'])
def market_status():
    """Get market status (open/closed)"""
    now = datetime.now()
    
    # Check if it's a weekday (Monday = 0, Sunday = 6)
    is_weekday = now.weekday() < 5
    
    # Market hours: 9:15 AM - 3:30 PM IST
    market_open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    is_market_hours = market_open_time <= now <= market_close_time
    
    status = 'OPEN' if (is_weekday and is_market_hours) else 'CLOSED'
    
    return jsonify({
        'success': True,
        'status': status,
        'is_trading_hours': is_weekday and is_market_hours,
        'next_open': 'Next trading day at 9:15 AM IST' if status == 'CLOSED' else None,
        'current_time': now.isoformat(),
        'market_hours': '9:15 AM - 3:30 PM IST'
    })

@app.route('/api/watchlist', methods=['GET', 'POST'])
def manage_watchlist():
    """Manage stock watchlist"""
    try:
        if request.method == 'GET':
            watchlist = db.get_collection('watchlist').find_one() or {'stocks': []}
            return jsonify({
                'success': True,
                'watchlist': watchlist.get('stocks', [])
            })
        
        elif request.method == 'POST':
            data = request.json
            action = data.get('action')  # 'add' or 'remove'
            ticker = data.get('ticker')
            
            watchlist = db.get_collection('watchlist')
            current = watchlist.find_one() or {'stocks': []}
            stocks = current.get('stocks', [])
            
            if action == 'add' and ticker not in stocks:
                stocks.append(ticker)
                logger.info(f"Added {ticker} to watchlist")
            elif action == 'remove' and ticker in stocks:
                stocks.remove(ticker)
                logger.info(f"Removed {ticker} from watchlist")
            
            watchlist.replace_one({}, {'stocks': stocks}, upsert=True)
            
            return jsonify({
                'success': True,
                'watchlist': stocks
            })
            
    except Exception as e:
        logger.error(f"Watchlist error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get detailed performance metrics"""
    try:
        portfolio = db.get_portfolio()
        trades_cursor = db.get_collection('trades').find().sort('timestamp', -1).limit(100)
        trades = list(trades_cursor)
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.get('profit', 0) > 0]
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(t.get('profit', 0) for t in trades)
        avg_profit = total_profit / total_trades if total_trades > 0 else 0
        
        # Best and worst trades
        best_trade = max(trades, key=lambda x: x.get('profit', 0)) if trades else None
        worst_trade = min(trades, key=lambda x: x.get('profit', 0)) if trades else None
        
        return jsonify({
            'success': True,
            'metrics': {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'total_profit': total_profit,
                'avg_profit': avg_profit,
                'best_trade': {
                    'ticker': best_trade.get('ticker'),
                    'profit': best_trade.get('profit'),
                    'date': str(best_trade.get('timestamp'))
                } if best_trade else None,
                'worst_trade': {
                    'ticker': worst_trade.get('ticker'),
                    'profit': worst_trade.get('profit'),
                    'date': str(worst_trade.get('timestamp'))
                } if worst_trade else None,
                'portfolio_value': portfolio.get('total_value', 100000),
                'returns': portfolio.get('returns', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Performance error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# WEBSOCKET EVENTS
# ============================================

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected to WebSocket')
    emit('connected', {'message': 'Connected to TradeWise AI', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected from WebSocket')

@socketio.on('subscribe')
def handle_subscribe(data):
    ticker = data.get('ticker', 'RELIANCE.NS')
    logger.info(f'Client subscribed to {ticker}')
    
    # Send initial data
    try:
        df = fetcher.fetch_historical(ticker, period='1d')
        if not df.empty:
            current_price = df['Close'].iloc[-1]
            
            emit('price_update', {
                'ticker': ticker,
                'price': float(current_price),
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Subscribe error: {e}")

# ============================================
# GAMIFICATION HELPERS
# ============================================

def check_achievements(agent, trade):
    """Check if trade unlocked any achievements"""
    achievements = []
    
    # First trade
    if len(agent.trade_history) == 1:
        achievements.append(Config.BADGES['first_trade'])
    
    # Profitable trade
    if trade.get('profit', 0) > 0:
        achievements.append(Config.BADGES['profitable'])
    
    # Win streak
    recent_trades = [t for t in agent.trade_history[-3:] if 'profit' in t]
    if len(recent_trades) == 3 and all(t['profit'] > 0 for t in recent_trades):
        achievements.append(Config.BADGES['streak_3'])
    
    return achievements

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎮 TRADEWISE AI - BACKEND SERVER")
    print("="*70)
    print("✅ Server starting on http://localhost:5000")
    print("✅ WebSocket enabled for real-time updates")
    print("✅ CORS enabled for frontend communication")
    print("✅ All endpoints operational")
    print("="*70)
    print("\n📊 Available Endpoints:")
    print("   - Home: http://localhost:5000/")
    print("   - API: http://localhost:5000/api/*")
    print("   - WebSocket: ws://localhost:5000")
    print("\n🚀 Starting server...\n")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
