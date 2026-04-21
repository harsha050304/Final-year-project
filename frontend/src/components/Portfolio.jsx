import React, { useState, useEffect } from 'react';
import { Wallet, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import api from '../services/api';

function Portfolio({ onUpdate }) {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchPortfolio = async () => {
    try {
      const response = await api.getPortfolio();
      setPortfolio(response.data.portfolio);
      if (onUpdate) onUpdate(response.data.portfolio);
    } catch (error) {
      console.error('Portfolio error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
    const interval = setInterval(fetchPortfolio, 10000); // Update every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-white/20 rounded w-3/4"></div>
          <div className="h-8 bg-white/20 rounded"></div>
          <div className="h-4 bg-white/20 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const isProfit = portfolio?.returns >= 0;

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-6 flex items-center">
        <Wallet className="w-6 h-6 mr-2 text-indigo-400" />
        Portfolio Overview
      </h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Cash */}
        <div className="bg-gradient-to-br from-green-600/20 to-emerald-600/20 rounded-xl p-4 border border-green-500/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Available Cash</span>
            <DollarSign className="w-5 h-5 text-green-400" />
          </div>
          <p className="text-2xl font-bold text-green-400">
            ₹{portfolio?.cash?.toLocaleString() || '0'}
          </p>
        </div>

        {/* Holdings Value */}
        <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 rounded-xl p-4 border border-purple-500/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Holdings Value</span>
            <TrendingUp className="w-5 h-5 text-purple-400" />
          </div>
          <p className="text-2xl font-bold text-purple-400">
            ₹{portfolio?.holdings_value?.toLocaleString() || '0'}
          </p>
        </div>

        {/* Total Value */}
        <div className="bg-gradient-to-br from-indigo-600/20 to-blue-600/20 rounded-xl p-4 border border-indigo-500/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Total Portfolio</span>
            <Wallet className="w-5 h-5 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-indigo-400">
            ₹{portfolio?.total_value?.toLocaleString() || '1,00,000'}
          </p>
        </div>

        {/* Returns */}
        <div className={`bg-gradient-to-br ${isProfit ? 'from-green-600/20 to-emerald-600/20 border-green-500/30' : 'from-red-600/20 to-rose-600/20 border-red-500/30'} rounded-xl p-4 border`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Total Returns</span>
            {isProfit ? <TrendingUp className="w-5 h-5 text-green-400" /> : <TrendingDown className="w-5 h-5 text-red-400" />}
          </div>
          <p className={`text-2xl font-bold ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
            {isProfit ? '+' : ''}{portfolio?.returns?.toFixed(2) || '0.00'}%
          </p>
        </div>
      </div>

      {/* Holdings Details */}
      {portfolio?.holdings && Object.keys(portfolio.holdings).length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-3">Current Holdings</h3>
          <div className="space-y-2">
            {Object.entries(portfolio.holdings).map(([ticker, data]) => (
              <div key={ticker} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                <div>
                  <p className="font-semibold">{ticker}</p>
                  <p className="text-sm text-gray-400">{data.shares} shares @ ₹{data.buy_price?.toFixed(2)}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-purple-400">₹{(data.shares * data.buy_price).toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="mt-6 pt-6 border-t border-white/10">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-indigo-400">{portfolio?.num_trades || 0}</p>
            <p className="text-sm text-gray-400">Total Trades</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-purple-400">
              {Object.keys(portfolio?.holdings || {}).length}
            </p>
            <p className="text-sm text-gray-400">Active Positions</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Portfolio;