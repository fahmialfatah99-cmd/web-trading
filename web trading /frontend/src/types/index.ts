export interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Indicators {
  rsi_14: number | null;
  macd: number | null;
  macd_signal: number | null;
  vwap: number | null;
  ichimoku_conversion: number | null;
  ichimoku_base: number | null;
  pivot_point: number | null;
  resistance_1: number | null;
  support_1: number | null;
}

export interface StockData {
  symbol: string;
  current_price: number;
  change_percent: number;
  candles: Candle[];
  indicators: Indicators;
  prediction_interval: { lower_95: number; upper_95: number };
}

export interface Sentiment {
  label: string;
  score: number;
  confidence: number;
}
