"""Trading decision engine with multiple strategies"""
import logging
from typing import Dict, Optional
from technical_indicators import TechnicalAnalyzer
from config import *
import numpy as np

logger = logging.getLogger(__name__)

class TradingEngine:
    """Generate trading decisions based on multiple indicators"""
    
    @staticmethod
    def generate_decision(indicators: Dict, 
                         current_price: float,
                         candles: list,
                         mode: str = "daily") -> Dict:
        """
        Generate trading decision (BUY, SELL, HOLD)
        
        Args:
            indicators: Dict of technical indicators
            current_price: Current stock price
            candles: List of price candles
            mode: "daily" or "monthly"
        
        Returns:
            Trading decision with action, confidence, reason, targets
        """
        
        buy_signals = []
        sell_signals = []
        signal_strength = {}
        
        # RSI Analysis
        if indicators.get('rsi_14') is not None:
            rsi = indicators['rsi_14']
            if rsi < 30:
                buy_signals.append(("RSI Oversold", 2.0))
                signal_strength['rsi'] = 2.0
            elif rsi < 40:
                buy_signals.append(("RSI Weak", 1.0))
                signal_strength['rsi'] = 1.0
            elif rsi > 70:
                sell_signals.append(("RSI Overbought", 2.0))
                signal_strength['rsi'] = -2.0
            elif rsi > 60:
                sell_signals.append(("RSI Strong", 1.0))
                signal_strength['rsi'] = -1.0
        
        # MACD Analysis
        if indicators.get('macd') and indicators.get('macd_signal'):
            macd = indicators['macd']
            signal = indicators['macd_signal']
            if macd > signal:
                buy_signals.append(("MACD Bullish Crossover", 2.0))
                signal_strength['macd'] = 2.0
            else:
                sell_signals.append(("MACD Bearish Crossover", 2.0))
                signal_strength['macd'] = -2.0
        
        # Bollinger Bands Analysis
        if indicators.get('bollinger_bands'):
            bb = indicators['bollinger_bands']
            if current_price < bb['lower']:
                buy_signals.append(("Price Below Lower BB", 1.5))
                signal_strength['bb'] = 1.5
            elif current_price > bb['upper']:
                sell_signals.append(("Price Above Upper BB", 1.5))
                signal_strength['bb'] = -1.5
        
        # VWAP Analysis
        if indicators.get('vwap'):
            vwap = indicators['vwap']
            if current_price > vwap:
                buy_signals.append(("Price Above VWAP", 1.0))
                signal_strength['vwap'] = 1.0
            else:
                sell_signals.append(("Price Below VWAP", 1.0))
                signal_strength['vwap'] = -1.0
        
        # ATR for volatility
        if indicators.get('atr'):
            atr = indicators['atr']
            atr_pct = (atr / current_price) * 100
            if atr_pct > 3:
                # High volatility, more cautious
                signal_strength['volatility'] = -0.5
        
        # Stochastic Oscillator
        if indicators.get('stochastic'):
            stoch = indicators['stochastic']
            if stoch.get('k') and stoch.get('k') < 20:
                buy_signals.append(("Stochastic Oversold", 1.0))
                signal_strength['stoch'] = 1.0
            elif stoch.get('k') and stoch.get('k') > 80:
                sell_signals.append(("Stochastic Overbought", 1.0))
                signal_strength['stoch'] = -1.0
        
        # Support/Resistance
        if indicators.get('support_resistance'):
            sr = indicators['support_resistance']
            dist_to_support = current_price - sr['support_1']
            dist_to_resistance = sr['resistance_1'] - current_price
            
            if dist_to_support < (dist_to_resistance * 0.5):
                buy_signals.append(("Near Support", 0.5))
                signal_strength['support'] = 0.5
            elif dist_to_resistance < (dist_to_support * 0.5):
                sell_signals.append(("Near Resistance", 0.5))
                signal_strength['support'] = -0.5
        
        # Calculate total signal strength
        buy_strength = sum(strength for _, strength in buy_signals)
        sell_strength = sum(strength for _, strength in sell_signals)
        
        # Mode adjustment
        if mode == "monthly":
            buy_strength *= 1.3
            sell_strength *= 1.3
        
        # Generate decision
        decision = TradingEngine._make_decision(
            buy_strength, sell_strength, buy_signals, 
            sell_signals, current_price, indicators, candles, mode
        )
        
        return decision
    
    @staticmethod
    def _make_decision(buy_strength: float, sell_strength: float,
                      buy_signals: list, sell_signals: list,
                      current_price: float, indicators: Dict,
                      candles: list, mode: str) -> Dict:
        """Make final trading decision"""
        
        total_strength = buy_strength + sell_strength
        
        if total_strength == 0:
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "reason": "No clear signals",
                "target_price": current_price,
                "stop_loss": current_price * 0.97,
                "signals": {
                    "buy": [],
                    "sell": []
                }
            }
        
        # Determine action and confidence
        if buy_strength > sell_strength:
            confidence = min(0.95, 0.5 + (buy_strength / (buy_strength + sell_strength + 1)))
            action = "BUY"
            signals = buy_signals
            
            # Calculate target price (10-20% above current for daily, 5-15% for monthly)
            if mode == "daily":
                target_factor = 1.12  # 12% target
                stop_factor = 0.97    # 3% stop loss
            else:
                target_factor = 1.08  # 8% target
                stop_factor = 0.95    # 5% stop loss
            
            target_price = round(current_price * target_factor, 2)
            stop_loss = round(current_price * stop_factor, 2)
        
        elif sell_strength > buy_strength:
            confidence = min(0.95, 0.5 + (sell_strength / (buy_strength + sell_strength + 1)))
            action = "SELL"
            signals = sell_signals
            
            # Calculate target price (10-20% below current)
            if mode == "daily":
                target_factor = 0.88  # 12% downside
                stop_factor = 1.03    # 3% stop loss
            else:
                target_factor = 0.92  # 8% downside
                stop_factor = 1.05    # 5% stop loss
            
            target_price = round(current_price * target_factor, 2)
            stop_loss = round(current_price * stop_factor, 2)
        
        else:
            action = "HOLD"
            confidence = 0.5
            target_price = current_price
            stop_loss = round(current_price * 0.95, 2)
            signals = []
        
        # Format reasons
        reasons = [f"{sig[0]}" for sig in signals[:3]]
        
        return {
            "action": action,
            "confidence": round(confidence, 2),
            "reason": "; ".join(reasons) if reasons else "Mixed signals",
            "target_price": target_price,
            "stop_loss": stop_loss,
            "signals": {
                "buy": [sig[0] for sig in buy_signals],
                "sell": [sig[0] for sig in sell_signals]
            },
            "mode": mode
        }
    
    @staticmethod
    def backtest_strategy(candles: list, strategy: str = "sma_crossover") -> Dict:
        """Backtest trading strategy"""
        if len(candles) < 50:
            return {
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "win_rate": 0.0,
                "trades_count": 0,
                "profitable_trades": 0
            }
        
        closes = np.array([c['close'] for c in candles])
        
        if strategy == "sma_crossover":
            # SMA 10/30 crossover
            sma10 = TradingEngine._sma(closes, 10)
            sma30 = TradingEngine._sma(closes, 30)
        else:
            return {}
        
        balance = 10000.0
        position = 0.0
        peak = 10000.0
        max_dd = 0.0
        trades = 0
        profitable_trades = 0
        entry_price = 0
        
        for i in range(30, len(closes)):
            if sma10[i] is None or sma30[i] is None:
                continue
            
            # Buy signal
            if sma10[i-1] <= sma30[i-1] and sma10[i] > sma30[i] and position == 0:
                position = balance / closes[i]
                entry_price = closes[i]
                balance = 0
                trades += 1
            
            # Sell signal
            elif sma10[i-1] >= sma30[i-1] and sma10[i] < sma30[i] and position > 0:
                balance = position * closes[i]
                if closes[i] > entry_price:
                    profitable_trades += 1
                position = 0
                trades += 1
            
            # Calculate drawdown
            equity = position * closes[i] if position > 0 else balance
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        # Close position if still open
        if position > 0:
            balance = position * closes[-1]
        
        total_return = (balance - 10000.0) / 10000.0
        returns = np.diff(closes) / closes[:-1]
        sharpe = np.sqrt(252) * (np.mean(returns) / (np.std(returns) + 0.0001))
        
        return {
            "total_return": round(total_return, 4),
            "sharpe_ratio": round(float(sharpe), 2),
            "max_drawdown": round(max_dd, 4),
            "win_rate": round(profitable_trades / max(trades, 1), 2),
            "trades_count": trades,
            "profitable_trades": profitable_trades
        }
    
    @staticmethod
    def _sma(prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average"""
        sma = np.zeros_like(prices)
        for i in range(len(prices)):
            if i < period - 1:
                sma[i] = None
            else:
                sma[i] = np.mean(prices[i-period+1:i+1])
        return sma
