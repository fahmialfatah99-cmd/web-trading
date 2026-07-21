"""Real-time data fetching from multiple sources"""
import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import httpx
from config import *

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetch real-time stock data with fallback mechanisms"""
    
    @staticmethod
    async def fetch_yahoo_finance(symbol: str, period: str = "1mo") -> Optional[Dict]:
        """Fetch data from Yahoo Finance API"""
        ticker_symbol = f"{symbol}.JK" if not symbol.endswith(".JK") else symbol
        
        url = "https://query1.finance.yahoo.com/v8/finance/chart/{}"
        
        # Calculate time range
        end_time = int(datetime.now().timestamp())
        if period == "1mo":
            start_time = int((datetime.now() - timedelta(days=30)).timestamp())
            interval = "1d"
        elif period == "3mo":
            start_time = int((datetime.now() - timedelta(days=90)).timestamp())
            interval = "1d"
        elif period == "1y":
            start_time = int((datetime.now() - timedelta(days=365)).timestamp())
            interval = "1wk"
        elif period == "2y":
            start_time = int((datetime.now() - timedelta(days=730)).timestamp())
            interval = "1wk"
        else:
            start_time = int((datetime.now() - timedelta(days=60)).timestamp())
            interval = "1d"
        
        params = {
            "period1": start_time,
            "period2": end_time,
            "interval": interval,
            "includePrePost": "false",
            "events": "div|splits"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(
                    url.format(ticker_symbol),
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("chart", {}).get("error"):
                    logger.warning(f"Error fetching {symbol}: {data['chart']['error']}")
                    return None
                
                result = data["chart"]["result"][0]
                timestamps = result["timestamp"]
                quotes = result["indicators"]["quote"][0]
                
                candles = []
                for i in range(len(timestamps)):
                    if quotes['close'][i] is None:
                        continue
                    
                    candle = {
                        'timestamp': timestamps[i],
                        'date': datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d'),
                        'open': round(quotes['open'][i], 2) if quotes['open'][i] else 0,
                        'high': round(quotes['high'][i], 2) if quotes['high'][i] else 0,
                        'low': round(quotes['low'][i], 2) if quotes['low'][i] else 0,
                        'close': round(quotes['close'][i], 2),
                        'volume': int(quotes['volume'][i]) if quotes['volume'][i] else 0,
                        'adjclose': round(quotes.get('adjclose', [None] * len(timestamps))[i] or quotes['close'][i], 2)
                    }
                    candles.append(candle)
                
                if not candles:
                    return None
                
                meta = result.get("meta", {})
                current_price = candles[-1]['close']
                prev_close = meta.get('previousClose', candles[-2]['close'] if len(candles) > 1 else current_price)
                change_percent = ((current_price - prev_close) / prev_close * 100) if prev_close != 0 else 0
                
                return {
                    "symbol": symbol,
                    "current_price": current_price,
                    "prev_close": round(prev_close, 2),
                    "change_percent": round(change_percent, 2),
                    "candles": candles[-60:],  # Last 60 candles
                    "currency": meta.get('currency', 'IDR'),
                    "high_52w": round(meta.get('fiftyTwoWeekHigh', current_price), 2),
                    "low_52w": round(meta.get('fiftyTwoWeekLow', current_price), 2),
                    "market_cap": meta.get('marketCap', 0),
                    "volume_avg": round(np.mean([c['volume'] for c in candles if c['volume'] > 0]), 0) if candles else 0
                }
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    @staticmethod
    async def fetch_with_retry(symbol: str, period: str = "1mo", retries: int = MAX_RETRIES) -> Optional[Dict]:
        """Fetch data with retry mechanism"""
        for attempt in range(retries):
            try:
                data = await DataFetcher.fetch_yahoo_finance(symbol, period)
                if data:
                    logger.info(f"Successfully fetched {symbol} on attempt {attempt + 1}")
                    return data
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(1)  # Wait before retry
        
        logger.error(f"Failed to fetch {symbol} after {retries} attempts")
        return None

import numpy as np
