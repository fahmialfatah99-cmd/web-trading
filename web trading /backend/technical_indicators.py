"""Advanced technical indicators calculation - FIXED VERSION"""
import numpy as np
from typing import List, Dict, Optional
from config import *

class TechnicalAnalyzer:
    """Complete technical analysis toolkit"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = RSI_PERIOD) -> Optional[float]:
        """Calculate Relative Strength Index"""
        try:
            if len(prices) < period + 1:
                return None
            
            prices = np.array(prices, dtype=np.float64)
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0 if avg_gain > 0 else 50.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return round(float(rsi), 2)
        except Exception as e:
            print(f"Error calculating RSI: {e}")
            return None
    
    @staticmethod
    def calculate_macd(prices: List[float], 
                      fast: int = MACD_FAST, 
                      slow: int = MACD_SLOW, 
                      signal: int = MACD_SIGNAL) -> Dict[str, Optional[float]]:
        """Calculate MACD and Signal line"""
        try:
            if len(prices) < slow:
                return {"macd": None, "signal": None, "histogram": None}
            
            prices = np.array(prices, dtype=np.float64)
            
            # EMA calculation
            ema_fast = TechnicalAnalyzer._ema(prices, fast)
            ema_slow = TechnicalAnalyzer._ema(prices, slow)
            
            macd_line = ema_fast - ema_slow
            signal_line = TechnicalAnalyzer._ema(macd_line, signal)
            histogram = macd_line - signal_line
            
            return {
                "macd": round(float(macd_line[-1]), 4),
                "signal": round(float(signal_line[-1]), 4),
                "histogram": round(float(histogram[-1]), 4)
            }
        except Exception as e:
            print(f"Error calculating MACD: {e}")
            return {"macd": None, "signal": None, "histogram": None}
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], 
                                 period: int = BOLLINGER_PERIOD,
                                 std_dev: float = BOLLINGER_STD) -> Dict[str, Optional[float]]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < period:
                return {"upper": None, "middle": None, "lower": None}
            
            prices = np.array(prices, dtype=np.float64)
            last_prices = prices[-period:]
            
            middle = np.mean(last_prices)
            std = np.std(last_prices)
            
            upper = middle + (std * std_dev)
            lower = middle - (std * std_dev)
            
            return {
                "upper": round(float(upper), 2),
                "middle": round(float(middle), 2),
                "lower": round(float(lower), 2)
            }
        except Exception as e:
            print(f"Error calculating Bollinger Bands: {e}")
            return {"upper": None, "middle": None, "lower": None}
    
    @staticmethod
    def calculate_vwap(candles: List[Dict], period: int = 20) -> Optional[float]:
        """Calculate Volume Weighted Average Price"""
        try:
            if not candles or len(candles) < period:
                return None
            
            total_volume = 0
            total_pv = 0
            
            for candle in candles[-period:]:
                volume = candle.get('volume', 0)
                if volume > 0:
                    typical_price = (candle['high'] + candle['low'] + candle['close']) / 3
                    total_pv += typical_price * volume
                    total_volume += volume
            
            if total_volume == 0:
                return None
            
            return round(total_pv / total_volume, 2)
        except Exception as e:
            print(f"Error calculating VWAP: {e}")
            return None
    
    @staticmethod
    def calculate_atr(candles: List[Dict], period: int = ATR_PERIOD) -> Optional[float]:
        """Calculate Average True Range"""
        try:
            if len(candles) < period + 1:
                return None
            
            tr_values = []
            for i in range(1, len(candles)):
                high = candles[i]['high']
                low = candles[i]['low']
                prev_close = candles[i-1]['close']
                
                tr = max(
                    high - low,
                    abs(high - prev_close),
                    abs(low - prev_close)
                )
                tr_values.append(tr)
            
            if not tr_values:
                return None
            
            atr = np.mean(tr_values[-period:])
            return round(float(atr), 2)
        except Exception as e:
            print(f"Error calculating ATR: {e}")
            return None
    
    @staticmethod
    def calculate_adx(candles: List[Dict], period: int = ADX_PERIOD) -> Optional[float]:
        """Calculate Average Directional Index (simplified)"""
        try:
            if len(candles) < period + 1:
                return None
            
            plus_dm = []
            minus_dm = []
            
            for i in range(1, len(candles)):
                up = candles[i]['high'] - candles[i-1]['high']
                down = candles[i-1]['low'] - candles[i]['low']
                
                if up > 0 and up > down:
                    plus_dm.append(up)
                else:
                    plus_dm.append(0)
                
                if down > 0 and down > up:
                    minus_dm.append(down)
                else:
                    minus_dm.append(0)
            
            plus_dm = np.array(plus_dm[-period:])
            minus_dm = np.array(minus_dm[-period:])
            
            tr_values = []
            for i in range(1, len(candles)):
                tr = max(
                    candles[i]['high'] - candles[i]['low'],
                    abs(candles[i]['high'] - candles[i-1]['close']),
                    abs(candles[i]['low'] - candles[i-1]['close'])
                )
                tr_values.append(tr)
            
            tr_sum = np.sum(tr_values[-period:])
            if tr_sum == 0:
                return None
            
            plus_di = (np.sum(plus_dm) / tr_sum) * 100
            minus_di = (np.sum(minus_dm) / tr_sum) * 100
            
            di_diff = abs(plus_di - minus_di)
            di_sum = plus_di + minus_di
            
            if di_sum == 0:
                return None
            
            dx = (di_diff / di_sum) * 100
            adx = dx  # Simplified, real ADX uses smoothing
            
            return round(float(adx), 2)
        except Exception as e:
            print(f"Error calculating ADX: {e}")
            return None
    
    @staticmethod
    def calculate_stochastic(prices: List[float], 
                            k_period: int = 14, 
                            d_period: int = 3) -> Dict[str, Optional[float]]:
        """Calculate Stochastic Oscillator"""
        try:
            if len(prices) < k_period:
                return {"k": None, "d": None}
            
            prices = np.array(prices, dtype=np.float64)
            
            highest = np.max(prices[-k_period:])
            lowest = np.min(prices[-k_period:])
            
            if highest == lowest:
                k = 50.0
            else:
                k = ((prices[-1] - lowest) / (highest - lowest)) * 100
            
            # D is SMA of K values (simplified: just use current K)
            d = k
            
            return {
                "k": round(float(k), 2),
                "d": round(float(d), 2)
            }
        except Exception as e:
            print(f"Error calculating Stochastic: {e}")
            return {"k": None, "d": None}
    
    @staticmethod
    def calculate_support_resistance(candles: List[Dict]) -> Dict[str, float]:
        """Calculate Support and Resistance levels"""
        try:
            if len(candles) < 20:
                return {
                    "pivot": 0,
                    "resistance_1": 0,
                    "resistance_2": 0,
                    "support_1": 0,
                    "support_2": 0
                }
            
            highs = np.array([c['high'] for c in candles[-20:]], dtype=np.float64)
            lows = np.array([c['low'] for c in candles[-20:]], dtype=np.float64)
            closes = np.array([c['close'] for c in candles[-20:]], dtype=np.float64)
            
            # Pivot Point
            pivot = (highs[-1] + lows[-1] + closes[-1]) / 3
            
            # Support and Resistance
            r1 = (2 * pivot) - lows[-1]
            r2 = pivot + (highs[-1] - lows[-1])
            s1 = (2 * pivot) - highs[-1]
            s2 = pivot - (highs[-1] - lows[-1])
            
            return {
                "pivot": round(float(pivot), 2),
                "resistance_1": round(float(r1), 2),
                "resistance_2": round(float(r2), 2),
                "support_1": round(float(s1), 2),
                "support_2": round(float(s2), 2)
            }
        except Exception as e:
            print(f"Error calculating Support/Resistance: {e}")
            return {
                "pivot": 0,
                "resistance_1": 0,
                "resistance_2": 0,
                "support_1": 0,
                "support_2": 0
            }
    
    @staticmethod
    def _ema(prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        try:
            prices = np.array(prices, dtype=np.float64)
            ema = np.zeros_like(prices)
            multiplier = 2.0 / (period + 1)
            
            # First value is SMA
            if period <= len(prices):
                ema[period-1] = np.mean(prices[:period])
                
                # Calculate EMA
                for i in range(period, len(prices)):
                    ema[i] = (prices[i] * multiplier) + (ema[i-1] * (1 - multiplier))
            
            return ema
        except Exception as e:
            print(f"Error calculating EMA: {e}")
            return np.zeros_like(prices)
