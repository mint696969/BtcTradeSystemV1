# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/frontend_assets/boot_js.py
# desc: Lightweight Charts boot and mouse interaction JavaScript for WarRoom interactive chart.

from __future__ import annotations

CHART_BOOT_JS = r"""
function boot() {
  if (!window.LightweightCharts || !CANDLES.length) { document.getElementById('fallback').style.display = 'block'; return; }
  const chart = LightweightCharts.createChart(chartEl, {
    layout: { background: { type: 'solid', color: '#ffffff' }, textColor: '#334155' },
    grid: { vertLines: { color: '#e2e8f0' }, horzLines: { color: '#e2e8f0' } },
    localization: { locale: 'ja-JP' },
    rightPriceScale: { borderVisible: false },
    timeScale: { borderVisible: false, rightOffset: 16, fixLeftEdge: false, fixRightEdge: false, timeVisible: true, secondsVisible: false },
    handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: false },
    handleScale: { mouseWheel: true, pinch: true, axisPressedMouseMove: true },
  });
  let series = null;
  if (chart.addSeries && LightweightCharts.CandlestickSeries) {
    series = chart.addSeries(LightweightCharts.CandlestickSeries, { upColor: '#f59e0b', downColor: '#ef4444', borderVisible: false, wickUpColor: '#f59e0b', wickDownColor: '#ef4444' });
  } else if (chart.addCandlestickSeries) {
    series = chart.addCandlestickSeries({ upColor: '#f59e0b', downColor: '#ef4444', borderVisible: false, wickUpColor: '#f59e0b', wickDownColor: '#ef4444' });
  }
  if (!series) { document.getElementById('fallback').style.display = 'block'; return; }
  series.setData(CANDLES.map(c => ({ time: c.time, open: c.open, high: c.high, low: c.low, close: c.close })));
  renderOverlayLayers(chart, series);
  const total = CANDLES.length;
  const visible = Math.min(total, BASE.visible_candle_count || 90);
  chart.timeScale().setVisibleLogicalRange({ from: Math.max(0, total - visible), to: total + 10 });
  chart.subscribeClick(param => {
    const c = candleByTime(param.time);
    if (!c) return;
    handleCandleClick(c, series);
  });
  copyBtn.addEventListener('click', copySelection);
  if (!restoreFinalizedSelection(series)) restoreSelectionAnchor(series);
  window.addEventListener('resize', () => chart.applyOptions({ width: chartEl.clientWidth }));
}
boot();
""".strip()
