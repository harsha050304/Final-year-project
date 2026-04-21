import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { BarChart3 } from 'lucide-react';
import api from '../services/api';

function PriceChart({ ticker }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('1mo');

  useEffect(() => {
    fetchChartData();
  }, [ticker, timeframe]);

  const fetchChartData = async () => {
    setLoading(true);
    try {
      const response = await api.getStockData(ticker);
      const chartData = response.data.data.map(item => ({
        date: new Date(item.Date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }),
        price: item.Close,
        volume: item.Volume,
        sma20: item.Sma_20,
        sma50: item.Sma_50,
      }));
      setData(chartData);
    } catch (error) {
      console.error('Chart error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold flex items-center">
          <BarChart3 className="w-6 h-6 mr-2 text-blue-400" />
          Price Chart - {ticker}
        </h2>
        
        {/* Timeframe Selector */}
        <div className="flex space-x-2">
          {['1mo', '3mo', '6mo', '1y'].map(tf => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-3 py-1 rounded-lg text-sm font-semibold transition-all ${
                timeframe === tf 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-white/10 text-gray-400 hover:bg-white/20'
              }`}
            >
              {tf.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={350}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
          <XAxis 
            dataKey="date" 
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
            domain={['auto', 'auto']}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1e1b4b', 
              border: '1px solid #6366f1',
              borderRadius: '8px',
              color: '#fff'
            }}
          />
          <Area 
            type="monotone" 
            dataKey="price" 
            stroke="#6366f1" 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorPrice)" 
          />
          <Line 
            type="monotone" 
            dataKey="sma20" 
            stroke="#10b981" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="sma50" 
            stroke="#f59e0b" 
            strokeWidth={2}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex items-center justify-center space-x-6 mt-4">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-indigo-600 rounded-full"></div>
          <span className="text-sm text-gray-400">Price</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-sm text-gray-400">SMA 20</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <span className="text-sm text-gray-400">SMA 50</span>
        </div>
      </div>
    </div>
  );
}

export default PriceChart;