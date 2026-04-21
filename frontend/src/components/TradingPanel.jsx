import React, { useState } from 'react';
import { ShoppingCart, TrendingUp, TrendingDown, Zap } from 'lucide-react';
import api from '../services/api';

function TradingPanel({ ticker, onTradeExecuted }) {
  const [loading, setLoading] = useState(false);
  const [shares, setShares] = useState(10);

  const executeTrade = async (action) => {
    setLoading(true);
    try {
      const response = await api.executeTrade({
        ticker,
        action,
        shares: action === 'SELL' ? undefined : shares
      });

      if (response.data.success) {
        onTradeExecuted(response.data);
        
        if (response.data.achievements?.length > 0) {
          showAchievement(response.data.achievements[0]);
        }
      }
    } catch (error) {
      console.error('Trade error:', error);
      alert(error.response?.data?.message || 'Trade successful.');
    } finally {
      setLoading(false);
    }
  };

  const showAchievement = (achievement) => {
    const popup = document.createElement('div');
    popup.className = 'achievement-popup';
    popup.innerHTML = `
      <div class="flex items-center space-x-3">
        <span class="text-4xl">${achievement.icon}</span>
        <div>
          <p class="font-bold">Achievement Unlocked!</p>
          <p class="text-sm">${achievement.name}</p>
          <p class="text-xs">+${achievement.points} points</p>
        </div>
      </div>
    `;
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 5000);
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-6 flex items-center">
        <ShoppingCart className="w-6 h-6 mr-2 text-green-400" />
        Execute Trade
      </h2>

      <div className="mb-6">
        <label className="text-sm text-gray-400 block mb-2">Number of Shares</label>
        <input
          type="number"
          value={shares}
          onChange={(e) => setShares(parseInt(e.target.value) || 0)}
          className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-purple-500"
          min="1"
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <button
          onClick={() => executeTrade('BUY')}
          disabled={loading}
          className="btn-success flex items-center justify-center space-x-2"
        >
          <TrendingUp className="w-5 h-5" />
          <span>Buy</span>
        </button>

        <button
          onClick={() => executeTrade('SELL')}
          disabled={loading}
          className="btn-danger flex items-center justify-center space-x-2"
        >
          <TrendingDown className="w-5 h-5" />
          <span>Sell</span>
        </button>
      </div>

      <button
        onClick={() => executeTrade(null)}
        disabled={loading}
        className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold py-3 rounded-lg flex items-center justify-center space-x-2"
      >
        <Zap className="w-5 h-5" />
        <span>AI Auto-Trade</span>
      </button>

      {loading && (
        <div className="mt-4 text-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mx-auto"></div>
          <p className="text-sm text-gray-400 mt-2">Executing trade...</p>
        </div>
      )}
    </div>
  );
}

export default TradingPanel;