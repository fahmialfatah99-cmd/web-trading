"""Trading decision engine with multiple strategies - FIXED VERSION"""
import logging
from typing import Dict, Optional, List
import numpy as np
from config import *

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
        
        try:
            buy_signals = []
            sell_signals = []
            
            # RSI Analysis
            rsi = indicators.get('rsi_14')
            if rsi is not None:
                if rsi < 30:
                    buy_signals.append(("RSI Oversold", 2.0))
                elif rsi < 40:
                    buy_signals.append(("RSI Weak", 1.0))
                elif rsi > 70:
                    sell_signals.append(("RSI Overbought", 2.0))
                elif rsi > 60:
                    sell_signals.append(("RSI Strong", 1.0))
            
            # MACD Analysis
            macd = indicators.get('macd')
            signal = indicators.get('macd_signal')
            if macd is not None and signal is not None:
                if macd > signal:
                    buy_signals.append(("MACD Bullish", 2.0))
                else:
                    sell_signals.append(("MACD Bearish", 2.0))
            
            # Bollinger Bands Analysis
            bb_upper = indicators.get('bollinger_upper')
            bb_lower = indicators.get('bollinger_lower')
            if bb_lower is not None and bb_upper is not None:
                if current_price < bb_lower:
                    buy_signals.append(("Price Below BB", 1.5))
                elif current_price > bb_upper:
                    sell_signals.append(("Price Above BB", 1.5))
            
            # VWAP Analysis
            vwap = indicators.get('vwap')
            if vwap is not None:
                if current_price > vwap:
                    buy_signals.append(("Price > VWAP", 1.0))
                else:
                    sell_signals.append(("Price < VWAP", 1.0))
            
            # Stochastic Analysis
            stoch_k = indicators.get('stochastic_k')
            if stoch_k is not None:
                if stoch_k < 20:
                    buy_signals.append(("Stochastic Oversold", 1.0))
                elif stoch_k > 80:
                    sell_signals.append(("Stochastic Overbought", 1.0))
            
            # Support/Resistance
            support_1 = indicators.get('support_1')
            resistance_1 = indicators.get('resistance_1')
            if support_1 is not None and resistance_1 is not None:
                dist_to_support = current_price - support_1
                dist_to_resistance = resistance_1 - current_price
                
                if dist_to_support > 0 and dist_to_support < (dist_to_resistance * 0.5):
                    buy_signals.append(("Near Support", 0.5))
                elif dist_to_resistance > 0 and dist_to_resistance < (dist_to_support * 0.5):
                    sell_signals.append(("Near Resistance", 0.5))
            
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
        
        except Exception as e:
            logger.error(f"Error generating trading decision: {e}", exc_info=True)
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "reason": "Error in analysis",
                "target_price": current_price,
                "stop_loss": current_price * 0.97,
                "signals": {"buy": [], "sell": []}
            }
    
    @staticmethod
    def _make_decision(buy_strength: float, sell_strength: float,
                      buy_signals: list, sell_signals: list,
                      current_price: float, indicators: Dict,
                      candles: list, mode: str) -> Dict:
        """Make final trading decision"""
        
        try:
            total_strength = buy_strength + sell_strength
            
            if total_strength == 0:
                return {
                    "action": "HOLD",
                    "confidence": 0.5,
                    "reason": "No clear signals",
                    "target_price": round(current_price, 2),
                    "stop_loss": round(current_price * 0.97, 2),
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
                target_price = round(current_price, 2)
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
        
        except Exception as e:
            logger.error(f"Error making decision: {e}", exc_info=True)
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "reason": "Decision error",
                "target_price": round(current_price, 2),
                "stop_loss": round(current_price * 0.95, 2),
                "signals": {"buy": [], "sell": []}
            }
    
    @staticmethod
    def backtest_strategy(candles: list, strategy: str = "sma_crossover") -> Dict:
        """Backtest trading strategy"""
        try:
            if len(candles) < 50:
                return {
                    "total_return": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "win_rate": 0.0,
                    "trades_count": 0,
                    "profitable_trades": 0
                }
            
            closes = np.array([c['close'] for c in candles], dtype=np.float64)
            
            if strategy == "sma_crossover":
                # SMA 10/30 crossover
                sma10 = TradingEngine._sma(closes, 10)
                sma30 = TradingEngine._sma(closes, 30)
            else:
                return {
                    "total_return": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "win_rate": 0.0,
                    "trades_count": 0,
                    "profitable_trades": 0
                }
            
            balance = 10000.0
            position = 0.0
            peak = 10000.0
            max_dd = 0.0
            trades = 0
            profitable_trades = 0
            entry_price = 0
            
            for i in range(30, len(closes)):
                if sma10[i] is None or sma30[i] is None or sma10[i-1] is None or sma30[i-1] is None:
                    continue
                
                # Buy signal
                if sma10[i-1] <= sma30[i-1] and sma10[i] > sma30[i] and position == 0:
                    try:
                        position = balance / closes[i]
                        entry_price = closes[i]
                        balance = 0
                        trades += 1
                    except:
                        pass
                
                # Sell signal
                elif sma10[i-1] >= sma30[i-1] and sma10[i] < sma30[i] and position > 0:
                    try:
                        balance = position * closes[i]
                        if closes[i] > entry_price:
                            profitable_trades += 1
                        position = 0
                        trades += 1
                    except:
                        pass
                
                # Calculate drawdown
                try:
                    equity = position * closes[i] if position > 0 else balance
                    if equity > peak:
                        peak = equity
                    dd = (peak - equity) / peak if peak > 0 else 0
                    max_dd = max(max_dd, dd)
                except:
                    pass
            
            # Close position if still open
            try:
                if position > 0:
                    balance = position * closes[-1]
            except:
                pass
            
            total_return = (balance - 10000.0) / 10000.0 if balance > 0 else 0.0
            
            try:
                returns = np.diff(closes) / closes[:-1]
                sharpe = np.sqrt(252) * (np.mean(returns) / (np.std(returns) + 0.0001))
            except:
                sharpe = 0.0
            
            return {
                "total_return": round(float(total_return), 4),
                "sharpe_ratio": round(float(sharpe), 2),
                "max_drawdown": round(float(max_dd), 4),
                "win_rate": round(float(profitable_trades / max(trades, 1)), 2),
                "trades_count": trades,
                "profitable_trades": profitable_trades
            }
        
        except Exception as e:
            logger.error(f"Error in backtest: {e}", exc_info=True)
            return {
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "win_rate": 0.0,
                "trades_count": 0,
                "profitable_trades": 0
            }
    
    @staticmethod
    def _sma(prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average"""
        try:
            sma = np.full_like(prices, np.nan, dtype=np.float64)
            for i in range(len(prices)):
                if i < period - 1:
                    sma[i] = np.nan
                else:
                    sma[i] = np.mean(prices[i-period+1:i+1])
            return sma
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return np.full_like(prices, np.nan, dtype=np.float64)
