"""IDX Stock Terminal - Advanced Real-time Trading Analysis"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np

from config import *
from data_fetcher import DataFetcher
from technical_indicators import TechnicalAnalyzer
from trading_engine import TradingEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class StockCandle(BaseModel):
    timestamp: int
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjclose: Optional[float] = None

class TechnicalIndicators(BaseModel):
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    vwap: Optional[float] = None
    atr: Optional[float] = None
    adx: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    pivot_point: Optional[float] = None
    resistance_1: Optional[float] = None
    resistance_2: Optional[float] = None
    support_1: Optional[float] = None
    support_2: Optional[float] = None

class SentimentAnalysis(BaseModel):
    label: str
    score: float
    confidence: float
    keywords: List[str] = []

class TradingDecision(BaseModel):
    action: str  # BUY, SELL, HOLD
    confidence: float
    reason: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    signals: Dict[str, List[str]] = {}
    mode: str = "daily"

class StockAnalysisResponse(BaseModel):
    symbol: str
    current_price: float
    prev_close: float
    change_percent: float
    high_52w: float
    low_52w: float
    candles: List[StockCandle]
    indicators: TechnicalIndicators
    trading_decision: TradingDecision
    sentiment: Optional[SentimentAnalysis] = None
    prediction_interval: Dict[str, float]
    market_cap: Optional[int] = None
    volume_avg: Optional[float] = None
    timestamp: str

class BacktestResult(BaseModel):
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades_count: int
    profitable_trades: int

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 IDX Stock Terminal Backend started")
    logger.info(f"📊 Configuration: RSI={RSI_PERIOD}, MACD=({MACD_FAST},{MACD_SLOW},{MACD_SIGNAL})")
    yield
    logger.info("✅ IDX Stock Terminal Backend stopped")

app = FastAPI(
    title="IDX Stock Terminal",
    description="Real-time trading analysis untuk saham Indonesia (IDX)",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "service": "IDX Stock Terminal"
    }

@app.get("/api/stock/{symbol}", response_model=StockAnalysisResponse)
async def get_stock_analysis(
    symbol: str,
    period: str = Query("1mo", regex="^(1mo|3mo|1y|2y)$"),
    mode: str = Query("daily", regex="^(daily|monthly)$")
):
    """
    Get complete stock analysis with technical indicators and trading decision
    
    Parameters:
    - symbol: Stock symbol (e.g., BBCA, BBRI)
    - period: Time period (1mo, 3mo, 1y, 2y)
    - mode: Analysis mode (daily or monthly)
    """
    
    try:
        # Fetch data
        logger.info(f"Fetching data for {symbol}...")
        data = await DataFetcher.fetch_with_retry(symbol, period)
        
        if not data or not data.get('candles'):
            raise HTTPException(
                status_code=404,
                detail=f"Stock data not found for {symbol}"
            )
        
        # Prepare candles
        candles_data = data['candles']
        candles_obj = [
            StockCandle(
                timestamp=c['timestamp'],
                date=c['date'],
                open=c['open'],
                high=c['high'],
                low=c['low'],
                close=c['close'],
                volume=c['volume'],
                adjclose=c.get('adjclose', c['close'])
            )
            for c in candles_data
        ]
        
        # Calculate indicators
        logger.info(f"Calculating indicators for {symbol}...")
        analyzer = TechnicalAnalyzer()
        
        closes = [c['close'] for c in candles_data]
        
        # RSI
        rsi = analyzer.calculate_rsi(closes)
        
        # MACD
        macd_data = analyzer.calculate_macd(closes)
        
        # Bollinger Bands
        bb = analyzer.calculate_bollinger_bands(closes)
        
        # VWAP
        vwap = analyzer.calculate_vwap(candles_data)
        
        # ATR
        atr = analyzer.calculate_atr(candles_data)
        
        # ADX
        adx = analyzer.calculate_adx(candles_data)
        
        # Stochastic
        stoch = analyzer.calculate_stochastic(closes)
        
        # Support & Resistance
        sr = analyzer.calculate_support_resistance(candles_data)
        
        indicators = TechnicalIndicators(
            rsi_14=rsi,
            macd=macd_data['macd'],
            macd_signal=macd_data['signal'],
            macd_histogram=macd_data['histogram'],
            vwap=vwap,
            atr=atr,
            adx=adx,
            bollinger_upper=bb['upper'],
            bollinger_middle=bb['middle'],
            bollinger_lower=bb['lower'],
            stochastic_k=stoch['k'],
            stochastic_d=stoch['d'],
            pivot_point=sr['pivot'],
            resistance_1=sr['resistance_1'],
            resistance_2=sr['resistance_2'],
            support_1=sr['support_1'],
            support_2=sr['support_2']
        )
        
        # Calculate prediction interval
        returns = np.diff(closes) / np.array(closes[:-1])
        volatility = np.std(returns) if len(returns) > 0 else 0.02
        current_price = data['current_price']
        prediction_interval = {
            "lower_95": round(current_price * (1 - 1.96 * volatility), 2),
            "upper_95": round(current_price * (1 + 1.96 * volatility), 2)
        }
        
        # Generate trading decision
        logger.info(f"Generating trading decision for {symbol}...")
        indicators_dict = indicators.dict()
        indicators_dict['support_resistance'] = sr
        indicators_dict['bollinger_bands'] = bb
        indicators_dict['stochastic'] = stoch
        
        decision_data = TradingEngine.generate_decision(
            indicators_dict,
            current_price,
            candles_data,
            mode
        )
        
        trading_decision = TradingDecision(
            action=decision_data['action'],
            confidence=decision_data['confidence'],
            reason=decision_data['reason'],
            target_price=decision_data['target_price'],
            stop_loss=decision_data['stop_loss'],
            signals=decision_data['signals'],
            mode=mode
        )
        
        return StockAnalysisResponse(
            symbol=symbol,
            current_price=current_price,
            prev_close=data['prev_close'],
            change_percent=data['change_percent'],
            high_52w=data['high_52w'],
            low_52w=data['low_52w'],
            candles=candles_obj,
            indicators=indicators,
            trading_decision=trading_decision,
            prediction_interval=prediction_interval,
            market_cap=data.get('market_cap'),
            volume_avg=data.get('volume_avg'),
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing stock: {str(e)}"
        )

@app.post("/api/sentiment", response_model=SentimentAnalysis)
async def analyze_news_sentiment(text: str = Query(..., min_length=10)):
    """
    Analyze sentiment from financial news text
    
    Parameters:
    - text: Financial news text to analyze
    """
    
    positive_words = [
        'naik', 'positif', 'untung', 'growth', 'bullish', 'optimis', 'baik',
        'kuat', 'meningkat', 'membeli', 'buy', 'upgrade', 'outperform'
    ]
    negative_words = [
        'turun', 'negatif', 'rugi', 'bearish', 'pesimis', 'buruk', 'lemah',
        'menurun', 'menjual', 'sell', 'downgrade', 'underperform'
    ]
    
    text_lower = text.lower()
    
    pos_words_found = [w for w in positive_words if w in text_lower]
    neg_words_found = [w for w in negative_words if w in text_lower]
    
    pos_count = len(pos_words_found)
    neg_count = len(neg_words_found)
    
    if pos_count > neg_count:
        label = "Positive"
        score = min(0.95, 0.5 + (pos_count - neg_count) * 0.15)
    elif neg_count > pos_count:
        label = "Negative"
        score = min(0.95, 0.5 + (neg_count - pos_count) * 0.15)
    else:
        label = "Neutral"
        score = 0.5
    
    return SentimentAnalysis(
        label=label,
        score=round(score, 2),
        confidence=round(score, 2),
        keywords=pos_words_found + neg_words_found
    )

@app.get("/api/backtest/{symbol}", response_model=BacktestResult)
async def run_backtest(
    symbol: str,
    period: str = Query("2y", regex="^(1mo|3mo|1y|2y)$"),
    strategy: str = Query("sma_crossover", regex="^(sma_crossover)$")
):
    """
    Run backtest on historical data
    
    Parameters:
    - symbol: Stock symbol
    - period: Historical period
    - strategy: Trading strategy to backtest
    """
    
    try:
        logger.info(f"Backtesting {symbol} with {strategy}...")
        data = await DataFetcher.fetch_with_retry(symbol, period)
        
        if not data or not data.get('candles'):
            raise HTTPException(
                status_code=404,
                detail=f"Data not found for backtest: {symbol}"
            )
        
        candles = data['candles']
        backtest_result = TradingEngine.backtest_strategy(candles, strategy)
        
        return BacktestResult(**backtest_result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest error for {symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Backtest error: {str(e)}"
        )

@app.get("/api/symbols")
async def get_available_symbols():
    """
    Get list of available IDX symbols
    """
    return {
        "symbols": IDX_SYMBOLS,
        "count": len(IDX_SYMBOLS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )
