import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TradingAssistant:
    """AI-powered trading assistant chatbot"""
    
    def __init__(self):
        self.context = {}
        self.conversation_history = []
        
    def process_query(self, user_message, context_data=None):
        """
        Process user query and generate response
        
        Args:
            user_message: User's question
            context_data: Current market/portfolio data
        
        Returns:
            AI assistant response
        """
        
        message_lower = user_message.lower()
        
        # Update context
        if context_data:
            self.context.update(context_data)
        
        # Save to history
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user': user_message,
            'context': context_data
        })
        
        # Determine intent and generate response
        response = self._generate_response(message_lower)
        
        # Save assistant response
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'assistant': response
        })
        
        return response
    
    def _generate_response(self, message):
        """Generate appropriate response based on message intent"""
        
        # Greetings
        if any(word in message for word in ['hello', 'hi', 'hey', 'start']):
            return self._greeting_response()
        
        # Prediction queries
        elif any(word in message for word in ['predict', 'forecast', 'price', 'tomorrow']):
            return self._prediction_response()
        
        # Trading queries
        elif any(word in message for word in ['buy', 'sell', 'trade', 'should i']):
            return self._trading_advice_response()
        
        # Portfolio queries
        elif any(word in message for word in ['portfolio', 'holdings', 'profit', 'loss', 'returns']):
            return self._portfolio_response()
        
        # Risk queries
        elif any(word in message for word in ['risk', 'safe', 'volatile', 'danger']):
            return self._risk_response()
        
        # Technical analysis
        elif any(word in message for word in ['rsi', 'macd', 'indicator', 'technical', 'analysis']):
            return self._technical_analysis_response()
        
        # Help
        elif any(word in message for word in ['help', 'how', 'what can', 'guide']):
            return self._help_response()
        
        # Market queries
        elif any(word in message for word in ['market', 'trend', 'bullish', 'bearish']):
            return self._market_analysis_response()
        
        # Stop loss
        elif any(word in message for word in ['stop loss', 'stoploss', 'exit', 'cut loss']):
            return self._stop_loss_advice()
        
        # Learning
        elif any(word in message for word in ['learn', 'teach', 'explain', 'what is']):
            return self._educational_response(message)
        
        # Default
        else:
            return self._default_response()
    
    def _greeting_response(self):
        return {
            'message': "👋 Hello! I'm your TradeWise AI Assistant. I can help you with:\n\n"
                      "📊 Market predictions and analysis\n"
                      "💼 Portfolio management\n"
                      "📈 Trading recommendations\n"
                      "⚠️ Risk assessment\n"
                      "📚 Trading education\n\n"
                      "What would you like to know?",
            'quick_replies': [
                'What should I trade today?',
                'Show my portfolio',
                'Analyze market trends',
                'Explain RSI'
            ]
        }
    
    def _prediction_response(self):
        portfolio = self.context.get('portfolio', {})
        current_ticker = self.context.get('current_ticker', 'stocks')
        
        return {
            'message': f"🔮 Based on AI analysis of {current_ticker}:\n\n"
                      f"Our LSTM model analyzes 60 days of historical data, "
                      f"technical indicators (RSI, MACD, Bollinger Bands), "
                      f"and market sentiment to predict price movements.\n\n"
                      f"Check the **Prediction Panel** for detailed forecasts with confidence scores!",
            'action': 'show_prediction',
            'quick_replies': [
                'Explain the prediction',
                'Is it safe to trade?',
                'Show technical indicators'
            ]
        }
    
    def _trading_advice_response(self):
        return {
            'message': "💡 **Trading Recommendation**:\n\n"
                      "I analyze multiple factors:\n"
                      "✓ AI price predictions\n"
                      "✓ Technical indicators (RSI, MACD)\n"
                      "✓ Market trends\n"
                      "✓ Risk levels\n\n"
                      "Click **AI Auto-Trade** for automated decisions, "
                      "or review the signals yourself in the prediction panel.\n\n"
                      "⚠️ Always use stop-loss and proper position sizing!",
            'quick_replies': [
                'What\'s my risk level?',
                'Show me technical analysis',
                'When should I exit?'
            ]
        }
    
    def _portfolio_response(self):
        portfolio = self.context.get('portfolio', {})
        
        if not portfolio:
            return {
                'message': "💼 Your portfolio is currently empty.\n\n"
                          "Start trading to build your portfolio! "
                          "I recommend starting with stocks that have strong AI predictions "
                          "and favorable technical indicators.",
                'quick_replies': [
                    'Show best stocks',
                    'How to start trading?'
                ]
            }
        
        total_value = portfolio.get('total_value', 100000)
        returns = portfolio.get('returns', 0)
        
        return {
            'message': f"💼 **Your Portfolio**:\n\n"
                      f"Total Value: ₹{total_value:,.0f}\n"
                      f"Returns: {returns:+.2f}%\n"
                      f"Cash: ₹{portfolio.get('cash', 0):,.0f}\n"
                      f"Holdings: {len(portfolio.get('holdings', {}))}\n\n"
                      f"{'🎉 Great job! You\'re profitable!' if returns > 0 else '💪 Keep learning and improving!'}",
            'action': 'show_portfolio',
            'quick_replies': [
                'Show trade history',
                'Analyze my performance',
                'Rebalance suggestions'
            ]
        }
    
    def _risk_response(self):
        return {
            'message': "⚠️ **Risk Management Tips**:\n\n"
                      "1. **Never risk more than 2% per trade**\n"
                      "2. **Always use stop-loss orders**\n"
                      "3. **Diversify across multiple stocks**\n"
                      "4. **Check volatility levels** before trading\n"
                      "5. **Don't trade on emotions**\n\n"
                      "Current market volatility and risk levels are shown in the prediction panel.",
            'quick_replies': [
                'Calculate my risk',
                'Set stop-loss',
                'Position size calculator'
            ]
        }
    
    def _technical_analysis_response(self):
        return {
            'message': "📊 **Technical Analysis**:\n\n"
                      "I monitor key indicators:\n\n"
                      "**RSI (Relative Strength Index)**:\n"
                      "- Below 30: Oversold (potential buy)\n"
                      "- Above 70: Overbought (potential sell)\n\n"
                      "**MACD**: Momentum indicator\n"
                      "- Bullish crossover = Buy signal\n"
                      "- Bearish crossover = Sell signal\n\n"
                      "**Moving Averages**: Trend direction\n"
                      "**Bollinger Bands**: Volatility & price extremes\n\n"
                      "Check the chart for visual analysis!",
            'action': 'show_chart',
            'quick_replies': [
                'Explain RSI',
                'What is MACD?',
                'Show me the indicators'
            ]
        }
    
    def _market_analysis_response(self):
        return {
            'message': "🌍 **Market Analysis**:\n\n"
                      "Based on current data:\n"
                      "- Analyzing trend strength\n"
                      "- Monitoring volume patterns\n"
                      "- Tracking sector performance\n\n"
                      "The AI considers both technical patterns and "
                      "sentiment indicators for comprehensive analysis.",
            'quick_replies': [
                'Best sectors today',
                'Market sentiment',
                'Top movers'
            ]
        }
    
    def _stop_loss_advice(self):
        return {
            'message': "🛡️ **Stop-Loss Strategy**:\n\n"
                      "Recommended stop-loss levels:\n"
                      "1. **Conservative**: 2-3% below entry\n"
                      "2. **Moderate**: 5% below entry\n"
                      "3. **Aggressive**: 7-10% below entry\n\n"
                      "I recommend using the ATR (Average True Range) "
                      "to set dynamic stop-losses based on volatility.\n\n"
                      "Never trade without a stop-loss!",
            'quick_replies': [
                'Calculate stop-loss',
                'Set trailing stop',
                'Risk per trade'
            ]
        }
    
    def _educational_response(self, message):
        """Provide educational content"""
        
        if 'rsi' in message:
            return {
                'message': "📚 **RSI (Relative Strength Index)**:\n\n"
                          "RSI measures momentum on a 0-100 scale:\n"
                          "- **0-30**: Oversold (stock might be undervalued)\n"
                          "- **30-70**: Normal range\n"
                          "- **70-100**: Overbought (stock might be overvalued)\n\n"
                          "It helps identify potential reversal points!",
                'quick_replies': ['Explain MACD', 'What is support/resistance?']
            }
        
        elif 'macd' in message:
            return {
                'message': "📚 **MACD (Moving Average Convergence Divergence)**:\n\n"
                          "MACD shows trend changes:\n"
                          "- **Bullish**: MACD line crosses above signal line\n"
                          "- **Bearish**: MACD line crosses below signal line\n\n"
                          "The histogram shows the strength of the trend.",
                'quick_replies': ['Explain RSI', 'What are moving averages?']
            }
        
        else:
            return {
                'message': "📚 I can explain:\n"
                          "- Technical indicators (RSI, MACD, etc.)\n"
                          "- Trading strategies\n"
                          "- Risk management\n"
                          "- Market concepts\n\n"
                          "What would you like to learn about?",
                'quick_replies': [
                    'Explain RSI',
                    'What is MACD?',
                    'How to trade safely?'
                ]
            }
    
    def _help_response(self):
        return {
            'message': "🤖 **How I Can Help**:\n\n"
                      "**Trading**:\n"
                      "- Get AI predictions\n"
                      "- Receive buy/sell signals\n"
                      "- Auto-trade execution\n\n"
                      "**Analysis**:\n"
                      "- Technical indicators\n"
                      "- Market trends\n"
                      "- Risk assessment\n\n"
                      "**Learning**:\n"
                      "- Trading concepts\n"
                      "- Strategy tips\n"
                      "- Market education\n\n"
                      "Just ask me anything!",
            'quick_replies': [
                'Predict stock price',
                'Show my portfolio',
                'Teach me trading'
            ]
        }
    
    def _default_response(self):
        return {
            'message': "🤔 I'm not sure I understood that. I can help you with:\n\n"
                      "📊 Market predictions\n"
                      "💼 Portfolio analysis\n"
                      "📈 Trading recommendations\n"
                      "📚 Trading education\n\n"
                      "Try asking something like:\n"
                      "- 'Should I buy this stock?'\n"
                      "- 'Show my portfolio'\n"
                      "- 'What is RSI?'",
            'quick_replies': [
                'Help',
                'What can you do?',
                'Predict stock'
            ]
        }
    
    def get_conversation_history(self, limit=10):
        """Get recent conversation history"""
        return self.conversation_history[-limit:]