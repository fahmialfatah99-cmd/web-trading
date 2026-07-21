'use client';

import { useEffect, useRef, useMemo } from 'react';
import { createChart, ColorType, IChartApi, ISeriesApi } from 'lightweight-charts';
import { StockData } from '@/types';

interface ChartProps {
   StockData | null;
}

export default function ChartComponent({ data }: ChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const vwapSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Initialize Chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0a0a0a' },
        textColor: '#e5e5e5',
      },
      grid: {
        vertLines: { color: '#333333' },
        horzLines: { color: '#333333' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Candlestick Series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#00c853',
      downColor: '#ff3d00',
      borderDownColor: '#ff3d00',
      borderUpColor: '#00c853',
      wickDownColor: '#ff3d00',
      wickUpColor: '#00c853',
    });
    candleSeriesRef.current = candleSeries;

    // VWAP Overlay
    const vwapSeries = chart.addLineSeries({
      color: '#f59e0b',
      lineWidth: 2,
      title: 'VWAP',
    });
    vwapSeriesRef.current = vwapSeries;

    // Resize Handler
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Update Data when props change - optimized with useMemo
  const chartData = useMemo(() => {
    if (!data) return { candles: [], vwapData: [] };

    const candles = data.candles.map((c) => ({
      time: c.timestamp as any,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    }));

    const vwapData = data.candles.map((c) => ({
      time: c.timestamp as any,
      value: c.volume > 0 ? (c.open + c.high + c.low + c.close) / 4 : 0,
    }));

    return { candles, vwapData };
  }, [data]);

  useEffect(() => {
    if (!chartData.candles.length || !candleSeriesRef.current) return;

    candleSeriesRef.current.setData(chartData.candles);
    
    // Fit Content
    chartRef.current?.timeScale().fitContent();

  }, [chartData]);

  return <div ref={chartContainerRef} className="w-full h-[500px]" />;
}
