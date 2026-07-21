import { create } from 'zustand';
import { StockData, Sentiment } from '@/types';

interface AppState {
  selectedSymbol: string;
  stockData: StockData | null;
  sentiment: Sentiment | null;
  loading: boolean;
  setSymbol: (symbol: string) => void;
  setStockData: ( StockData) => void;
  setSentiment: ( Sentiment) => void;
  setLoading: (status: boolean) => void;
}

export const useStore = create<AppState>((set) => ({
  selectedSymbol: 'BBCA', // Default to Bank Central Asia
  stockData: null,
  sentiment: null,
  loading: false,
  setSymbol: (symbol) => set({ selectedSymbol: symbol }),
  setStockData: (data) => set({ stockData: data }),
  setSentiment: (data) => set({ sentiment: data }),
  setLoading: (status) => set({ loading: status }),
}));
