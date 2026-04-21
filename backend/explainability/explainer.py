import numpy as np
import pandas as pd
import shap
import logging

logger = logging.getLogger(__name__)

class TradingExplainer:
    """Explain trading decisions using SHAP and custom logic"""
    
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        
    def initialize_explainer(self, background_data):
        """Initialize SHAP explainer with background data"""
        try:
            # Use DeepExplainer for neural networks
            self.explainer = shap.DeepExplainer(self.model, background_data)
            logger.info("SHAP explainer initialized")
        except Exception as e:
            logger.warning(f"SHAP init failed: {e}. Using rule-based explanation.")
            self.explainer = None
    
    def explain_prediction(self, input_data, prediction_result, technical_data):
        """
        Generate comprehensive explanation for a prediction
        
        Returns:
            {
                'decision': 'BUY/SELL/HOLD',
                'confidence': 0.85,
                'key_factors': [...],
                'technical_analysis': {...},
                'risk_assessment': {...},
                'explanation_text': "..."
            }
        """
        
        # Feature importance (simplified without SHAP)
        features = {
            'price_trend': self._analyze_price_trend(technical_data),
            'momentum': self._analyze_momentum(technical_data),
            'volatility': self._analyze_volatility(technical_data),
            'volume': self._analyze_volume(technical_data),
            'technical_indicators': self._analyze_indicators(technical_data)
        }
        
        # Generate explanation text
        explanation = self._generate_explanation(
            prediction_result, 
            features, 
            technical_data
        )
        
        return {
            'decision': self._get_decision(prediction_result, technical_data),
            'confidence': prediction_result.get('confidence', 0.5),
            'key_factors': self._get_key_factors(features),
            'technical_analysis': features['technical_indicators'],
            'risk_assessment': self._assess_risk(technical_data),
            'explanation_text': explanation,
            'feature_importance': self._calculate_feature_importance(features)
        }
    
    def _analyze_price_trend(self, data):
        """Analyze price trend"""
        sma20 = data.get('Sma_20', 0)
        sma50 = data.get('Sma_50', 0)
        current = data.get('Close', 0)
        
        if current > sma20 > sma50:
            return {'signal': 'Strong Uptrend', 'strength': 0.9, 'positive': True}
        elif current > sma20:
            return {'signal': 'Uptrend', 'strength': 0.7, 'positive': True}
        elif current < sma20 < sma50:
            return {'signal': 'Strong Downtrend', 'strength': 0.9, 'positive': False}
        else:
            return {'signal': 'Downtrend', 'strength': 0.6, 'positive': False}
    
    def _analyze_momentum(self, data):
        """Analyze momentum indicators"""
        rsi = data.get('Rsi', 50)
        macd = data.get('Macd', 0)
        macd_signal = data.get('Macd_signal', 0)
        
        momentum_score = 0
        signals = []
        
        if rsi < 30:
            signals.append('Oversold - Bullish')
            momentum_score += 0.3
        elif rsi > 70:
            signals.append('Overbought - Bearish')
            momentum_score -= 0.3
        
        if macd > macd_signal:
            signals.append('MACD Bullish Crossover')
            momentum_score += 0.2
        else:
            signals.append('MACD Bearish')
            momentum_score -= 0.2
        
        return {
            'score': momentum_score,
            'signals': signals,
            'rsi': float(rsi),
            'positive': momentum_score > 0
        }
    
    def _analyze_volatility(self, data):
        """Analyze volatility"""
        atr = data.get('Atr', 0)
        volatility = data.get('Volatility', 0)
        
        if volatility > 0.03:
            level = 'High'
            risk = 'High Risk'
        elif volatility > 0.015:
            level = 'Medium'
            risk = 'Moderate Risk'
        else:
            level = 'Low'
            risk = 'Low Risk'
        
        return {
            'level': level,
            'value': float(volatility),
            'atr': float(atr),
            'risk': risk
        }
    
    def _analyze_volume(self, data):
        """Analyze volume patterns"""
        volume = data.get('Volume', 0)
        volume_sma = data.get('Volume_sma', 1)
        
        ratio = volume / volume_sma if volume_sma > 0 else 1
        
        if ratio > 1.5:
            return {'signal': 'High Volume', 'strength': 0.8, 'positive': True}
        elif ratio > 1.2:
            return {'signal': 'Above Average', 'strength': 0.6, 'positive': True}
        else:
            return {'signal': 'Normal Volume', 'strength': 0.4, 'positive': False}
    
    def _analyze_indicators(self, data):
        """Comprehensive technical analysis"""
        return {
            'rsi': {
                'value': float(data.get('Rsi', 50)),
                'signal': 'Oversold' if data.get('Rsi', 50) < 30 else 'Overbought' if data.get('Rsi', 50) > 70 else 'Neutral'
            },
            'macd': {
                'value': float(data.get('Macd', 0)),
                'signal': 'Bullish' if data.get('Macd', 0) > data.get('Macd_signal', 0) else 'Bearish'
            },
            'bollinger_bands': {
                'position': self._get_bb_position(data),
                'width': float(data.get('Bb_high', 0) - data.get('Bb_low', 0))
            },
            'moving_averages': {
                'trend': 'Uptrend' if data.get('Sma_20', 0) > data.get('Sma_50', 0) else 'Downtrend'
            }
        }
    
    def _get_bb_position(self, data):
        """Get position relative to Bollinger Bands"""
        close = data.get('Close', 0)
        bb_high = data.get('Bb_high', 0)
        bb_low = data.get('Bb_low', 0)
        
        if close > bb_high:
            return 'Above Upper Band (Overbought)'
        elif close < bb_low:
            return 'Below Lower Band (Oversold)'
        else:
            return 'Within Bands (Normal)'
    
    def _assess_risk(self, data):
        """Assess trading risk"""
        volatility = data.get('Volatility', 0)
        atr = data.get('Atr', 0)
        
        if volatility > 0.03:
            risk_level = 'High'
            recommendation = 'Use tight stop-loss. Consider smaller position size.'
        elif volatility > 0.015:
            risk_level = 'Medium'
            recommendation = 'Normal position size with standard stop-loss.'
        else:
            risk_level = 'Low'
            recommendation = 'Favorable conditions for trading.'
        
        return {
            'level': risk_level,
            'volatility': float(volatility),
            'atr': float(atr),
            'recommendation': recommendation
        }
    
    def _get_decision(self, prediction, technical_data):
        """Get trading decision"""
        pred_change = prediction.get('change_percent', 0)
        rsi = technical_data.get('Rsi', 50)
        
        if pred_change > 2 and rsi < 70:
            return 'BUY'
        elif pred_change < -2 or rsi > 70:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _get_key_factors(self, features):
        """Extract key factors influencing decision"""
        factors = []
        
        # Price trend
        trend = features['price_trend']
        factors.append({
            'factor': 'Price Trend',
            'value': trend['signal'],
            'impact': 'Positive' if trend['positive'] else 'Negative',
            'weight': trend['strength']
        })
        
        # Momentum
        momentum = features['momentum']
        factors.append({
            'factor': 'Momentum',
            'value': ', '.join(momentum['signals']),
            'impact': 'Positive' if momentum['positive'] else 'Negative',
            'weight': abs(momentum['score'])
        })
        
        # Volatility
        vol = features['volatility']
        factors.append({
            'factor': 'Volatility',
            'value': vol['level'],
            'impact': vol['risk'],
            'weight': 0.6
        })
        
        # Sort by weight
        factors.sort(key=lambda x: x['weight'], reverse=True)
        
        return factors[:5]  # Top 5 factors
    
    def _calculate_feature_importance(self, features):
        """Calculate feature importance scores"""
        importance = {}
        
        # Price trend
        importance['Price Trend'] = features['price_trend']['strength']
        
        # Momentum
        importance['RSI'] = abs(features['momentum']['rsi'] - 50) / 50
        importance['MACD'] = abs(features['momentum']['score'])
        
        # Volatility
        importance['Volatility'] = features['volatility']['value'] * 20
        
        # Volume
        importance['Volume'] = features['volume']['strength']
        
        return importance
    
    def _generate_explanation(self, prediction, features, technical_data):
        """Generate human-readable explanation"""
        
        pred_change = prediction.get('change_percent', 0)
        direction = prediction.get('direction', 'NEUTRAL')
        confidence = prediction.get('confidence', 0.5)
        
        explanation = f"**AI Prediction: {direction}** (Confidence: {confidence*100:.0f}%)\n\n"
        
        explanation += f"The AI predicts a **{abs(pred_change):.2f}% {'increase' if pred_change > 0 else 'decrease'}** "
        explanation += f"in price based on the following analysis:\n\n"
        
        # Price trend
        trend = features['price_trend']
        explanation += f"📈 **Price Trend**: {trend['signal']}\n"
        explanation += f"   - Current price is {'above' if trend['positive'] else 'below'} key moving averages\n\n"
        
        # Momentum
        momentum = features['momentum']
        explanation += f"⚡ **Momentum Indicators**:\n"
        for signal in momentum['signals']:
            explanation += f"   - {signal}\n"
        explanation += "\n"
        
        # Risk
        risk = features['volatility']
        explanation += f"⚠️ Risk Level: {risk['risk']}\n"
        explanation += f"   - Market volatility is {risk['level'].lower()}\n\n"
        
        # Recommendation
        explanation += "Recommendation:\n"
        if direction == 'UP' and confidence > 0.7:
            explanation += "✅ Strong buy signal. Consider entering a position with appropriate risk management."
        elif direction == 'UP':
            explanation += "⚠️ Moderate buy signal. Wait for confirmation or use smaller position size."
        elif direction == 'DOWN' and confidence > 0.7:
            explanation += "🔴 Strong sell signal. Consider exiting positions or taking profits."
        else:
            explanation += "⏸️ Weak signal. Better to wait for clearer market direction."
        
        return explanation

# Helper function for API
def get_trade_explanation(predictor, ticker, df):
    """Get complete explanation for a trade decision"""
    
    # Get prediction
    prediction = predictor.predict_confidence(df)
    
    # Get latest technical data
    latest_data = df.iloc[-1]
    
    # Create explainer
    explainer = TradingExplainer(predictor.model, predictor.feature_names)
    
    # Generate explanation
    explanation = explainer.explain_prediction(
        df.tail(60),
        prediction,
        latest_data
    )
    
    return explanation