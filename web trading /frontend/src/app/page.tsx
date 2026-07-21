'use client';

import { useEffect, useState } from 'react';
import { useStore } from '@/store/useStore';
import ChartComponent from '@/components/ChartComponent';
import axios from 'axios';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const { selectedSymbol, setSymbol, stockData, setStockData, loading, setLoading } = useStore();
  const [newsText, setNewsText] = useState("");
  const [sentimentRes, setSentimentRes] = useState<any>(null);

  // Debounce function to prevent rapid API calls
  const debounce = (fn: Function, ms: number) => {
    let timeoutId: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn(...args), ms);
    };
  };

  const fetchStockData = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/api/stock/${selectedSymbol}`);
      setStockData(res.data);
    } catch (error) {
      console.error("Failed to fetch stock", error);
    } finally {
      setLoading(false);
    }
  };

  // Memoized fetch to prevent unnecessary re-fetches
  const debouncedFetchStockData = useMemo(
    () => debounce(fetchStockData, 300),
    [selectedSymbol]
  );

  const handleSentimentAnalysis = async () => {
    if(!newsText) return;
    try {
      const res = await axios.post(`http://localhost:8000/api/sentiment?text=${encodeURIComponent(newsText)}`);
      setSentimentRes(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchStockData();
  }, [selectedSymbol]);

  return (
    <div className="min-h-screen bg-bloomberg-bg text-bloomberg-text font-mono p-6">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-bloomberg-border pb-4">
        <h1 className="text-2xl font-bold text-bloomberg-accent">IDX QUANT TERMINAL</h1>
        <div className="flex gap-4">
          <input 
            type="text" 
            value={selectedSymbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            className="bg-bloomberg-panel border border-bloomberg-border p-2 rounded text-white focus:outline-none focus:border-bloomberg-accent"
            placeholder="Symbol (e.g., BBCA)"
          />
          <button onClick={fetchStockData} className="bg-bloomberg-accent text-black px-4 py-2 rounded font-bold hover:bg-yellow-600">
            LOAD
          </button>
        </div>
      </header>

      {loading ? (
        <div className="flex justify-center items-center h-64">Initializing Quant Engine...</div>
      ) : stockData ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Main Chart Area */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-2 bg-bloomberg-panel border border-bloomberg-border rounded-lg p-4"
          >
            <div className="flex justify-between mb-4">
              <h2 className="text-xl font-bold">{stockData.symbol} - IDR {stockData.current_price.toLocaleString()}</h2>
              <span className={`font-bold ${stockData.change_percent >= 0 ? 'text-bloomberg-bull' : 'text-bloomberg-bear'}`}>
                {stockData.change_percent >= 0 ? '+' : ''}{stockData.change_percent.toFixed(2)}%
              </span>
            </div>
            <ChartComponent data={stockData} />
            
            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4 mt-4 text-sm">
              <div className="bg-black/30 p-2 rounded">
                <span className="text-gray-500">RSI (14)</span>
                <div className={stockData.indicators.rsi_14! > 70 ? "text-bloomberg-bear" : "text-bloomberg-bull"}>
                  {stockData.indicators.rsi_14?.toFixed(2)}
                </div>
              </div>
              <div className="bg-black/30 p-2 rounded">
                <span className="text-gray-500">VWAP</span>
                <div>{stockData.indicators.vwap?.toFixed(2)}</div>
              </div>
              <div className="bg-black/30 p-2 rounded">
                <span className="text-gray-500">Pivot Point</span>
                <div>{stockData.indicators.pivot_point?.toFixed(2)}</div>
              </div>
            </div>
          </motion.div>

          {/* Sidebar: AI & Tools */}
          <div className="space-y-6">
            
            {/* Sentiment Analysis */}
            <div className="bg-bloomberg-panel border border-bloomberg-border rounded-lg p-4">
              <h3 className="text-lg font-bold mb-2 text-bloomberg-accent">AI Sentiment (FinBERT)</h3>
              <textarea 
                className="w-full bg-black/50 border border-bloomberg-border rounded p-2 text-sm text-white mb-2"
                rows={4}
                placeholder="Paste Indonesian financial news here..."
                value={newsText}
                onChange={(e) => setNewsText(e.target.value)}
              />
              <button 
                onClick={handleSentimentAnalysis}
                className="w-full bg-blue-900 hover:bg-blue-800 text-white py-2 rounded text-sm"
              >
                Analyze Sentiment
              </button>
              
              {sentimentRes && (
                <div className="mt-4 p-3 bg-black/50 rounded border-l-4 border-bloomberg-accent">
                  <div className="flex justify-between">
                    <span>Label:</span>
                    <span className="font-bold">{sentimentRes.label}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Confidence:</span>
                    <span>{(sentimentRes.confidence * 100).toFixed(1)}%</span>
                  </div>
                </div>
              )}
            </div>

            {/* Prediction Interval */}
            <div className="bg-bloomberg-panel border border-bloomberg-border rounded-lg p-4">
              <h3 className="text-lg font-bold mb-2">Probabilistic Forecast (95% CI)</h3>
              <div className="flex justify-between text-sm">
                <span className="text-bloomberg-bear">Lower: {stockData.prediction_interval.lower_95.toFixed(0)}</span>
                <span className="text-bloomberg-bull">Upper: {stockData.prediction_interval.upper_95.toFixed(0)}</span>
              </div>
              <p className="text-xs text-gray-500 mt-2">Based on historical volatility bootstrap.</p>
            </div>

          </div>
        </div>
      ) : (
        <div className="text-center text-gray-500">Select a stock to begin analysis.</div>
      )}
    </div>
  );
}
