import React, { useState } from 'react';
import Header from './components/Header';
import PredictionCard from './components/PredictionCard';
import TradingPanel from './components/TradingPanel';
import Portfolio from './components/Portfolio';
import PriceChart from './components/PriceChart';
import TradeHistory from './components/TradeHistory';
import Leaderboard from './components/Leaderboard';
import { RefreshCw } from 'lucide-react';
import Chatbot from './components/Chatbot';
import ExplainPanel from './components/ExplainPanel';

function App() {
  const [selectedTicker, setSelectedTicker] = useState('RELIANCE.NS');
  const [portfolio, setPortfolio] = useState(null);
  const [trades, setTrades] = useState([]);
  const [level, setLevel] = useState('Beginner');
  const [badges, setBadges] = useState(0);

  const tickers = [
    { symbol: 'RELIANCE.NS', name: 'Reliance' },
    { symbol: 'TCS.NS', name: 'TCS' },
    { symbol: 'HDFCBANK.NS', name: 'HDFC Bank' },
    { symbol: 'INFY.NS', name: 'Infosys' },
    { symbol: 'ICICIBANK.NS', name: 'ICICI Bank' },
    { symbol: 'ITC.NS', name: 'ITC' },
    { symbol: 'SBIN.NS', name: 'SBI' },
    { symbol: 'BHARTIARTL.NS', name: 'Airtel' },
  ];

  const handleTradeExecuted = (data) => {
    if (data.trade) {
      setTrades(prev => [data.trade, ...prev]);
    }
    if (data.portfolio) {
      setPortfolio(data.portfolio);
    }
    if (data.achievements) {
      setBadges(prev => prev + data.achievements.length);
    }
  };

  return (
    <div className="min-h-screen">
      <Header portfolio={portfolio} level={level} badges={badges} />

      <div className="container mx-auto px-6 py-8">
        {/* Stock Selector */}
        <div className="mb-8">
          <div className="card">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Select Stock</h3>
              <div className="flex flex-wrap gap-2">
                {tickers.map(ticker => (
                  <button
                    key={ticker.symbol}
                    onClick={() => setSelectedTicker(ticker.symbol)}
                    className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                      selectedTicker === ticker.symbol
                        ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
                        : 'bg-white/10 text-gray-300 hover:bg-white/20'
                    }`}
                  >
                    {ticker.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Chart */}
            <PriceChart ticker={selectedTicker} />

            {/* Prediction */}
            <PredictionCard ticker={selectedTicker} />

            {/* Trade History */}
            <TradeHistory trades={trades} />
          </div>
          <ExplainPanel ticker={selectedTicker} />

          {/* Right Column */}
          <div className="space-y-6">
            {/* Portfolio */}
            <Portfolio onUpdate={setPortfolio} />

            {/* Trading Panel */}
            <TradingPanel 
              ticker={selectedTicker} 
              onTradeExecuted={handleTradeExecuted}
            />

            {/* Leaderboard */}
            <Leaderboard />
            <Chatbot ticker={selectedTicker} />
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>🎮 TradeWise AI - Your AI-Powered Trading Companion</p>
          
        </div>
      </div>
    </div>
  );
}

export default App;