import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import api from '../services/api';

function PredictionCard({ ticker }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchPrediction = async () => {
    setLoading(true);
    try {
      const response = await api.getPrediction(ticker);
      setPrediction(response.data);
    } catch (error) {
      console.error('Prediction error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrediction();
  }, [ticker]);

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>
      </div>
    );
  }

  if (!prediction) return null;

  const pred = prediction.prediction;
  const isUp = pred.direction === 'UP';

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold flex items-center">
          <Brain className="w-6 h-6 mr-2 text-purple-400" />
          AI Prediction
        </h2>
        <span className="text-sm text-gray-400">{ticker}</span>
      </div>

      <div className="bg-gradient-to-br from-indigo-600/30 to-purple-600/30 rounded-xl p-6 mb-6 border border-indigo-500/30">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-gray-400">Current Price</p>
            <p className="text-3xl font-bold">₹{pred.current_price.toFixed(2)}</p>
          </div>
          <div className={`flex items-center space-x-2 ${isUp ? 'text-green-400' : 'text-red-400'}`}>
            {isUp ? <TrendingUp className="w-8 h-8" /> : <TrendingDown className="w-8 h-8" />}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400">Predicted Price</p>
            <p className="text-3xl font-bold text-purple-400">₹{pred.predicted_price.toFixed(2)}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-400">Expected Change</p>
            <p className={`text-2xl font-bold ${isUp ? 'text-green-400' : 'text-red-400'}`}>
              {pred.change_percent >= 0 ? '+' : ''}{pred.change_percent.toFixed(2)}%
            </p>
          </div>
        </div>

        <div className="mt-4">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">Confidence</span>
            <span className="font-semibold">{(pred.confidence * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-green-500 to-emerald-400 h-3 rounded-full transition-all duration-500"
              style={{ width: `${pred.confidence * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">RSI</p>
          <p className="text-lg font-bold">{prediction.signals.rsi.value.toFixed(0)}</p>
          <p className={`text-xs ${
            prediction.signals.rsi.signal === 'Oversold' ? 'text-green-400' : 
            prediction.signals.rsi.signal === 'Overbought' ? 'text-red-400' : 'text-gray-400'
          }`}>
            {prediction.signals.rsi.signal}
          </p>
        </div>

        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">MACD</p>
          <p className="text-lg font-bold">{prediction.signals.macd.value.toFixed(2)}</p>
          <p className={`text-xs ${
            prediction.signals.macd.signal === 'Bullish' ? 'text-green-400' : 'text-red-400'
          }`}>
            {prediction.signals.macd.signal}
          </p>
        </div>

        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Trend</p>
          <p className="text-lg font-bold">
            <Activity className="w-5 h-5 inline" />
          </p>
          <p className={`text-xs ${
            prediction.signals.trend.signal === 'Uptrend' ? 'text-green-400' : 'text-red-400'
          }`}>
            {prediction.signals.trend.signal}
          </p>
        </div>
      </div>

      <button 
        onClick={fetchPrediction}
        className="w-full mt-4 btn-primary"
      >
        Refresh Prediction
      </button>
    </div>
  );
}

export default PredictionCard;