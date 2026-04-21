import React from 'react';
import { TrendingUp, Trophy, Award } from 'lucide-react';

function Header({ portfolio, level, badges }) {
  return (
    <header className="bg-white/10 backdrop-blur-lg border-b border-white/20 sticky top-0 z-40">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-3 rounded-xl shadow-lg">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                TradeWise AI
              </h1>
              <p className="text-xs text-gray-400">Your AI Trading Companion</p>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <div className="text-right">
              <p className="text-sm text-gray-400">Portfolio Value</p>
              <p className="text-xl font-bold text-white">
                ₹{portfolio?.total_value?.toLocaleString() || '1,00,000'}
              </p>
              <p className={`text-sm ${portfolio?.returns >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {portfolio?.returns >= 0 ? '+' : ''}{portfolio?.returns?.toFixed(2) || '0.00'}%
              </p>
            </div>

            <div className="flex items-center space-x-2 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 px-4 py-2 rounded-lg border border-yellow-500/30">
              <Trophy className="w-5 h-5 text-yellow-400" />
              <div>
                <p className="text-xs text-gray-400">Level</p>
                <p className="text-sm font-bold text-yellow-400">{level || 'Beginner'}</p>
              </div>
            </div>

            <div className="flex items-center space-x-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 px-4 py-2 rounded-lg border border-purple-500/30">
              <Award className="w-5 h-5 text-purple-400" />
              <div>
                <p className="text-xs text-gray-400">Badges</p>
                <p className="text-sm font-bold text-purple-400">{badges || 0}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;