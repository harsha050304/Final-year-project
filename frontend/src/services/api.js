import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export const api = {
  getStocks: () => axios.get(`${API_BASE_URL}/stocks`),
  getStockData: (ticker) => axios.get(`${API_BASE_URL}/stock/${ticker}`),
  getPrediction: (ticker) => axios.get(`${API_BASE_URL}/predict/${ticker}`),
  executeTrade: (data) => axios.post(`${API_BASE_URL}/trade`, data),
  getPortfolio: () => axios.get(`${API_BASE_URL}/portfolio`),
  runBacktest: (ticker) => axios.get(`${API_BASE_URL}/backtest/${ticker}`),
  getLeaderboard: () => axios.get(`${API_BASE_URL}/leaderboard`),
  // ... existing methods ...
  
  // Explainability
  getExplanation: (ticker) => axios.get(`${API_BASE_URL}/explain/${ticker}`),
  
  // Chatbot
  chatbot: (data) => axios.post(`${API_BASE_URL}/chatbot`, data),
  
  // Paper Trading
  initPaperTrading: (capital) => axios.post(`${API_BASE_URL}/paper-trade/init`, { capital }),
  
  // Live Price
  getLivePrice: (ticker) => axios.get(`${API_BASE_URL}/live-price/${ticker}`),
  
  // Market Status
  getMarketStatus: () => axios.get(`${API_BASE_URL}/market-status`),
  
  // Watchlist
  getWatchlist: () => axios.get(`${API_BASE_URL}/watchlist`),
  addToWatchlist: (ticker) => axios.post(`${API_BASE_URL}/watchlist`, { action: 'add', ticker }),
  removeFromWatchlist: (ticker) => axios.post(`${API_BASE_URL}/watchlist`, { action: 'remove', ticker }),
  
  // Performance
  getPerformance: () => axios.get(`${API_BASE_URL}/performance`),
};

export default api;