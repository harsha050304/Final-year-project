import React, { useState, useEffect } from 'react';
import { Lightbulb, TrendingUp, AlertTriangle, BarChart3 } from 'lucide-react';
import api from '../services/api';

function ExplainPanel({ ticker }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchExplanation();
  }, [ticker]);

  const fetchExplanation = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/explain/${ticker}`);
      const data = await response.json();
      setExplanation(data.explanation);
    } catch (error) {
      console.error('Explanation error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-white/20 rounded w-3/4"></div>
          <div className="h-20 bg-white/20 rounded"></div>
        </div>
      </div>
    );
  }

  if (!explanation) return null;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold flex items-center">
          <Lightbulb className="w-6 h-6 mr-2 text-yellow-400" />
          AI Explanation
        </h2>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
          explanation.decision === 'BUY' ? 'bg-green-600/20 text-green-400' :
          explanation.decision === 'SELL' ? 'bg-red-600/20 text-red-400' :
          'bg-gray-600/20 text-gray-400'
        }`}>
          {explanation.decision}
        </span>
      </div>

      {/* Confidence Score */}
      <div className="mb-6">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-400">AI Confidence</span>
          <span className="font-semibold">{(explanation.confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-4">
          <div
            className={`h-4 rounded-full transition-all duration-500 ${
              explanation.confidence > 0.7 ? 'bg-gradient-to-r from-green-500 to-emerald-400' :
              explanation.confidence > 0.5 ? 'bg-gradient-to-r from-yellow-500 to-orange-400' :
              'bg-gradient-to-r from-red-500 to-rose-400'
            }`}
            style={{ width: `${explanation.confidence * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Key Factors */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center">
          <BarChart3 className="w-4 h-4 mr-2" />
          Key Influencing Factors
        </h3>
        <div className="space-y-2">
          {explanation.key_factors.map((factor, index) => (
            <div key={index} className="bg-white/5 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-sm">{factor.factor}</span>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  factor.impact === 'Positive' ? 'bg-green-600/20 text-green-400' :
                  factor.impact === 'Negative' ? 'bg-red-600/20 text-red-400' :
                  'bg-gray-600/20 text-gray-400'
                }`}>
                  {factor.impact}
                </span>
              </div>
              <p className="text-sm text-gray-400">{factor.value}</p>
              <div className="mt-2 w-full bg-gray-700 rounded-full h-1">
                <div
                  className="bg-purple-500 h-1 rounded-full"
                  style={{ width: `${factor.weight * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Assessment */}
      <div className="bg-gradient-to-r from-orange-600/20 to-red-600/20 rounded-xl p-4 border border-orange-500/30 mb-6">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-orange-400 mt-1" />
          <div>
            <h3 className="font-semibold text-orange-400 mb-1">Risk Assessment</h3>
            <p className="text-sm text-gray-300">{explanation.risk_assessment.recommendation}</p>
            <div className="mt-2 flex items-center space-x-4 text-xs">
              <span>Level: <strong>{explanation.risk_assessment.level}</strong></span>
              <span>Volatility: <strong>{(explanation.risk_assessment.volatility * 100).toFixed(2)}%</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Explanation */}
      <div className="bg-white/5 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Detailed Analysis</h3>
        <div className="text-sm text-gray-300 whitespace-pre-line">
          {explanation.explanation_text}
        </div>
      </div>

      <button
        onClick={fetchExplanation}
        className="w-full mt-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold py-3 rounded-lg transition-all"
      >
        Refresh Explanation
      </button>
    </div>
  );
}

export default ExplainPanel;