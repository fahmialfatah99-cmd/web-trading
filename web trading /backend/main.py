import asyncio
import logging
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Data Models
# =============================================================================

class StockCandle(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: int

class TechnicalIndicators(BaseModel):
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    vwap: Optional[float] = None
    ichimoku_conversion: Optional[float] = None
    ichimoku_base: Optional[float] = None
    pivot_point: Optional[float] = None
    resistance_1: Optional[float] = None
    support_1: Optional[float] = None

class SentimentAnalysis(BaseModel):
    label: str
    score: float
    confidence: float

class TradingDecision(BaseModel):
    action: str
    confidence: float
    reason: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None

class StockAnalysisResponse(BaseModel):
    symbol: str
    current_price: float
    change_percent: float
    candles: List[StockCandle]
    indicators: TechnicalIndicators
    sentiment: Optional[SentimentAnalysis] = None
    prediction_interval: Dict[str, float]
    trading_decision: Optional[TradingDecision] = None

class BacktestResult(BaseModel):
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades_count: int

# =============================================================================
# Application Setup
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup complete.")
    yield

app = FastAPI(title="IDX Stock Terminal", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Technical Indicator Calculations
# =============================================================================

def calculate_rsi(prices: list, period: int = 14) -> Optional[float]:
    """Calculate Relative Strength Index (RSI)."""
    if len(prices) < period + 1:
        return None
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [max(0, d) for d in deltas]
    losses = [max(0, -d) for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def calculate_macd(prices: list) -> tuple:
    """Calculate MACD and Signal Line."""
    if len(prices) < 26:
        return None, None
    ema12 = prices.copy()
    ema26 = prices.copy()
    for i in range(12, len(prices)):
        ema12[i] = (prices[i] * 2/13) + (ema12[i-1] * 11/13)
    for i in range(26, len(prices)):
        ema26[i] = (prices[i] * 2/27) + (ema26[i-1] * 25/27)
    macd_line = [ema12[i] - ema26[i] for i in range(len(prices))]
    signal_line = macd_line.copy()
    for i in range(9, len(macd_line)):
        if i == 9:
            signal_line[i] = sum(macd_line[:9]) / 9
        else:
            signal_line[i] = (macd_line[i] * 2/10) + (signal_line[i-1] * 8/10)
    return round(macd_line[-1], 4), round(signal_line[-1], 4)

def calculate_vwap(candles: list) -> Optional[float]:
    """Calculate Volume Weighted Average Price (VWAP)."""
    if not candles:
        return None
    total_volume = 0
    total_pv = 0
    for c in candles[-20:]:
        if c['volume'] > 0:
            typical_price = (c['high'] + c['low'] + c['close']) / 3
            total_pv += typical_price * c['volume']
            total_volume += c['volume']
    if total_volume == 0:
        return None
    return round(total_pv / total_volume, 2)

def calculate_indicators(df: list) -> TechnicalIndicators:
    """Calculate all technical indicators."""
    if not df:
        return TechnicalIndicators()
    closes = [c['close'] for c in df]
    rsi = calculate_rsi(closes)
    macd, macd_signal = calculate_macd(closes)
    vwap = calculate_vwap(df)
    last = df[-1]
    pivot = (last['high'] + last['low'] + last['close']) / 3
    r1 = (2 * pivot) - last['low']
    s1 = (2 * pivot) - last['high']
    period9_high = max(c['high'] for c in df[-9:]) if len(df) >= 9 else last['high']
    period9_low = min(c['low'] for c in df[-9:]) if len(df) >= 9 else last['low']
    conv = (period9_high + period9_low) / 2
    period26_high = max(c['high'] for c in df[-26:]) if len(df) >= 26 else last['high']
    period26_low = min(c['low'] for c in df[-26:]) if len(df) >= 26 else last['low']
    base = (period26_high + period26_low) / 2
    return TechnicalIndicators(
        rsi_14=rsi, macd=macd, macd_signal=macd_signal, vwap=vwap,
        ichimoku_conversion=round(conv, 2), ichimoku_base=round(base, 2),
        pivot_point=round(pivot, 2), resistance_1=round(r1, 2), support_1=round(s1, 2)
    )

# =============================================================================
# Trading Decision Logic
# =============================================================================

def generate_trading_decision(
    indicators: TechnicalIndicators, 
    current_price: float, 
    prediction_interval: Dict[str, float], 
    mode: str = "daily"
) -> TradingDecision:
    """Generate trading decision based on technical indicators."""
    buy_score = 0
    sell_score = 0
    reasons = []
    
    # RSI Analysis
    if indicators.rsi_14 is not None:
        if indicators.rsi_14 < 30:
            buy_score += 2
            reasons.append(f"RSI oversold at {indicators.rsi_14}")
        elif indicators.rsi_14 < 40:
            buy_score += 1
            reasons.append(f"RSI approaching oversold at {indicators.rsi_14}")
        elif indicators.rsi_14 > 70:
            sell_score += 2
            reasons.append(f"RSI overbought at {indicators.rsi_14}")
        elif indicators.rsi_14 > 60:
            sell_score += 1
            reasons.append(f"RSI approaching overbought at {indicators.rsi_14}")
    
    # MACD Analysis
    if indicators.macd is not None and indicators.macd_signal is not None:
        if indicators.macd > indicators.macd_signal:
            buy_score += 2
            reasons.append(f"MACD bullish ({indicators.macd:.2f} > {indicators.macd_signal:.2f})")
        else:
            sell_score += 2
            reasons.append(f"MACD bearish ({indicators.macd:.2f} < {indicators.macd_signal:.2f})")
    
    # VWAP Analysis
    if indicators.vwap is not None:
        if current_price > indicators.vwap:
            buy_score += 1
            reasons.append(f"Price above VWAP ({current_price} > {indicators.vwap:.2f})")
        else:
            sell_score += 1
            reasons.append(f"Price below VWAP ({current_price} < {indicators.vwap:.2f})")
    
    # Ichimoku Analysis
    if indicators.ichimoku_conversion is not None and indicators.ichimoku_base is not None:
        if indicators.ichimoku_conversion > indicators.ichimoku_base:
            buy_score += 1
            reasons.append("Ichimoku conversion above base (bullish)")
        else:
            sell_score += 1
            reasons.append("Ichimoku conversion below base (bearish)")
    
    # Support/Resistance Analysis
    if indicators.support_1 is not None and indicators.resistance_1 is not None:
        if current_price <= indicators.support_1 * 1.02:
            buy_score += 1
            reasons.append(f"Price near support at {indicators.support_1:.2f}")
        elif current_price >= indicators.resistance_1 * 0.98:
            sell_score += 1
            reasons.append(f"Price near resistance at {indicators.resistance_1:.2f}")
    
    # Adjust for monthly mode
    if mode == "monthly":
        buy_score = int(buy_score * 1.2)
        sell_score = int(sell_score * 1.2)
    
    # Determine final decision
    total_score = buy_score + sell_score
    if total_score == 0:
        action = "HOLD"
        confidence = 0.5
        reasons.append("Mixed signals - maintaining neutral position")
        return TradingDecision(action=action, confidence=confidence, reason="; ".join(reasons[:5]))
    elif buy_score > sell_score:
        action = "BUY"
        confidence = min(0.95, 0.5 + (buy_score - sell_score) / 10.0)
        target_price = prediction_interval.get("upper_95", current_price * 1.05)
        stop_loss = indicators.support_1 if indicators.support_1 else current_price * 0.95
    else:
        action = "SELL"
        confidence = min(0.95, 0.5 + (sell_score - buy_score) / 10.0)
        target_price = indicators.support_1 if indicators.support_1 else current_price * 0.95
        stop_loss = indicators.resistance_1 if indicators.resistance_1 else current_price * 1.05
    
    return TradingDecision(
        action=action, 
        confidence=round(confidence, 2),
        reason="; ".join(reasons[:5]),
        target_price=round(target_price, 2),
        stop_loss=round(stop_loss, 2)
    )

# =============================================================================
# Data Fetching
# =============================================================================

async def fetch_yahoo_data(symbol: str, period: str = "1mo") -> dict:
    """Fetch stock data from Yahoo Finance API."""
    ticker_symbol = f"{symbol}.JK" if not symbol.endswith(".JK") else symbol
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_symbol}"
    params = {
        "period1": "0", 
        "period2": "9999999999", 
        "interval": "1d" if period == "1mo" else "1wk", 
        "includePrePost": "false"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("chart", {}).get("error"):
                raise HTTPException(status_code=404, detail="Stock data not found")
            
            result = data["chart"]["result"][0]
            quote = result.get("meta", {})
            timestamps = result["timestamp"]
            quotes = result["indicators"]["quote"][0]
            
            candles = []
            for i in range(len(timestamps)):
                if quotes['close'][i] is None:
                    continue
                candles.append({
                    'timestamp': timestamps[i],
                    'open': round(quotes['open'][i], 2) if quotes['open'][i] else 0,
                    'high': round(quotes['high'][i], 2) if quotes['high'][i] else 0,
                    'low': round(quotes['low'][i], 2) if quotes['low'][i] else 0,
                    'close': round(quotes['close'][i], 2) if quotes['close'][i] else 0,
                    'volume': int(quotes['volume'][i]) if quotes['volume'][i] else 0
                })
            
            current_price = candles[-1]['close'] if candles else 0
            prev_close = quote.get('previousClose', current_price)
            change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            
            return {
                "symbol": symbol, 
                "current_price": current_price, 
                "change_percent": round(change_pct, 2), 
                "candles": candles[-60:], 
                "currency": quote.get('currency', 'IDR')
            }
    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/api/stock/{symbol}", response_model=StockAnalysisResponse)
async def get_stock_analysis(symbol: str, period: str = "1mo", mode: str = "daily"):
    """Get comprehensive stock analysis including indicators and trading decision."""
    data = await fetch_yahoo_data(symbol, period)
    
    # Convert candles to Pydantic models
    candles_obj = [
        StockCandle(
            timestamp=c['timestamp'], 
            open=c['open'], 
            high=c['high'], 
            low=c['low'], 
            close=c['close'], 
            volume=c['volume']
        ) 
        for c in data['candles']
    ]
    
    # Calculate technical indicators
    indicators = calculate_indicators(data['candles'])
    
    # Calculate volatility and prediction interval
    closes = [c['close'] for c in data['candles']]
    if len(closes) > 1:
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        volatility = np.std(returns) if returns else 0.02
    else:
        volatility = 0.02
    
    current_price = data['current_price']
    prediction_interval = {
        "lower_95": round(current_price * (1 - 1.96 * volatility), 2),
        "upper_95": round(current_price * (1 + 1.96 * volatility), 2)
    }
    
    # Generate trading decision
    trading_decision = generate_trading_decision(indicators, current_price, prediction_interval, mode)
    
    return StockAnalysisResponse(
        symbol=data['symbol'], 
        current_price=current_price, 
        change_percent=data['change_percent'], 
        candles=candles_obj, 
        indicators=indicators, 
        prediction_interval=prediction_interval, 
        trading_decision=trading_decision
    )

@app.post("/api/sentiment", response_model=SentimentAnalysis)
async def analyze_news_sentiment(text: str = Query(...)):
    """Analyze sentiment of Indonesian financial news text."""
    positive_words = ['naik', 'positif', 'untung', 'growth', 'bullish', 'optimis', 'baik']
    negative_words = ['turun', 'negatif', 'rugi', 'bearish', 'pesimis', 'buruk', 'jelek']
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        label, score = "Positive", min(0.95, 0.5 + (pos_count - neg_count) * 0.15)
    elif neg_count > pos_count:
        label, score = "Negative", min(0.95, 0.5 + (neg_count - pos_count) * 0.15)
    else:
        label, score = "Neutral", 0.5
    
    return SentimentAnalysis(label=label, score=round(score, 2), confidence=round(score, 2))

@app.get("/api/backtest/{symbol}", response_model=BacktestResult)
async def run_backtest(symbol: str, period: str = "2y"):
    """Run backtest using SMA crossover strategy."""
    data = await fetch_yahoo_data(symbol, "2y")
    candles = data['candles']
    
    if len(candles) < 50:
        return BacktestResult(
            total_return=0.0, 
            sharpe_ratio=0.0, 
            max_drawdown=0.0, 
            win_rate=0.0, 
            trades_count=0
        )
    
    closes = [c['close'] for c in candles]
    
    # Calculate SMAs
    sma10, sma30 = [], []
    for i in range(len(closes)):
        sma10.append(sum(closes[i-9:i+1]) / 10 if i >= 9 else None)
        sma30.append(sum(closes[i-29:i+1]) / 30 if i >= 29 else None)
    
    # Run backtest
    balance, position, peak, max_dd, trades = 10000.0, 0.0, 10000.0, 0.0, 0
    for i in range(30, len(candles)):
        if sma10[i] and sma30[i] and sma10[i-1] and sma30[i-1]:
            price = closes[i]
            # Buy signal: SMA10 crosses above SMA30
            if sma10[i-1] <= sma30[i-1] and sma10[i] > sma30[i] and position == 0:
                position = balance / price
                balance = 0
                trades += 1
            # Sell signal: SMA10 crosses below SMA30
            elif sma10[i-1] >= sma30[i-1] and sma10[i] < sma30[i] and position > 0:
                balance = position * price
                position = 0
                trades += 1
            
            # Track drawdown
            equity = position * price if position > 0 else balance
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)
    
    # Calculate final metrics
    equity = position * closes[-1] if position > 0 else balance
    total_return = (equity - 10000.0) / 10000.0
    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
    sharpe = np.sqrt(252) * (np.mean(returns) / np.std(returns)) if np.std(returns) > 0 else 0
    
    return BacktestResult(
        total_return=round(total_return, 4), 
        sharpe_ratio=round(sharpe, 2), 
        max_drawdown=round(max_dd, 4), 
        win_rate=0.5, 
        trades_count=trades
    )


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
