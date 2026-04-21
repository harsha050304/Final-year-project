import React from 'react';
import { History, TrendingUp, TrendingDown } from 'lucide-react';

function TradeHistory({ trades = [] }) {
  if (!trades || trades.length === 0) {
    return (
      <div className="card">
        <h2 className="text-xl font-bold mb-6 flex items-center">
          <History className="w-6 h-6 mr-2 text-orange-400" />
          Trade History
        </h2>
        <div className="text-center py-12">
          <p className="text-gray-400">No trades yet. Start trading to see your history!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-6 flex items-center">
        <History className="w-6 h-6 mr-2 text-orange-400" />
        Recent Trades
      </h2>

      <div className="space-y-3">
        {trades.slice(0, 10).map((trade, index) => (
          <div 
            key={index}
            className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${
                  trade.action === 'BUY' 
                    ? 'bg-green-600/20 text-green-400' 
                    : 'bg-red-600/20 text-red-400'
                }`}>
                  {trade.action === 'BUY' ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
                </div>
                
                <div>
                  <p className="font-semibold">{trade.ticker}</p>
                  <p className="text-sm text-gray-400">
                    {trade.shares} shares @ ₹{trade.price?.toFixed(2)}
                  </p>
                  {trade.reason && (
                    <p className="text-xs text-gray-500 mt-1">{trade.reason}</p>
                  )}
                </div>
              </div>

              <div className="text-right">
                <p className={`text-lg font-bold ${
                  trade.action === 'BUY' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {trade.action}
                </p>
                {trade.profit !== undefined && (
                  <div>
                    <p className={`text-sm font-semibold ${
                      trade.profit >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {trade.profit >= 0 ? '+' : ''}₹{trade.profit?.toFixed(2)}
                    </p>
                    <p className={`text-xs ${
                      trade.profit_percent >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      ({trade.profit_percent >= 0 ? '+' : ''}{trade.profit_percent?.toFixed(2)}%)
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TradeHistory;