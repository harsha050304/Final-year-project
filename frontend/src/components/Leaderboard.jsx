import React, { useState, useEffect } from 'react';
import { Trophy, Medal, Award, Star } from 'lucide-react';
import api from '../services/api';

function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    try {
      const response = await api.getLeaderboard();
      setLeaderboard(response.data.leaderboard);
    } catch (error) {
      console.error('Leaderboard error:', error);
    }
  };

  const getRankIcon = (rank) => {
    switch(rank) {
      case 1: return <Trophy className="w-6 h-6 text-yellow-400" />;
      case 2: return <Medal className="w-6 h-6 text-gray-400" />;
      case 3: return <Award className="w-6 h-6 text-orange-400" />;
      default: return <Star className="w-5 h-5 text-purple-400" />;
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-6 flex items-center">
        <Trophy className="w-6 h-6 mr-2 text-yellow-400" />
        Leaderboard
      </h2>

      <div className="space-y-3">
        {leaderboard.map((player, index) => (
          <div 
            key={index}
            className={`rounded-lg p-4 flex items-center justify-between transition-all ${
              player.name === 'You' 
                ? 'bg-gradient-to-r from-purple-600/30 to-indigo-600/30 border border-purple-500/50' 
                : 'bg-white/5 hover:bg-white/10'
            }`}
          >
            <div className="flex items-center space-x-4">
              <div className="flex items-center justify-center w-10">
                {getRankIcon(player.rank)}
              </div>
              
              <div>
                <p className="font-semibold">{player.name}</p>
                <p className="text-sm text-gray-400">{player.trades} trades</p>
              </div>
            </div>

            <div className="text-right">
              <p className={`text-lg font-bold ${
                player.returns >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {player.returns >= 0 ? '+' : ''}{player.returns?.toFixed(2)}%
              </p>
              <div className="flex items-center justify-end space-x-1">
                {[...Array(player.badges)].map((_, i) => (
                  <Star key={i} className="w-3 h-3 text-yellow-400 fill-current" />
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Leaderboard;