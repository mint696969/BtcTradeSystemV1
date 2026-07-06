# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/frontend_assets/boot_js.py
# desc: Lightweight Charts boot and mouse interaction JavaScript for WarRoom interactive chart.

from __future__ import annotations

CHART_BOOT_JS = r"""
function boot() {
  if (!window.LightweightCharts || !CANDLES.length) { document.getElementById('fallback').style.display = 'block'; return; }
  const resetRangeBtn = document.getElementById('reset-range');
  const baseMetaEl = document.getElementById('base-meta');
  const ctx = BASE.chart_context || {};
  if (baseMetaEl) {
    const freshness = ctx.cache_lag_vs_live ? `cache遅延=${ctx.cache_lag_vs_live}` : 'cache遅延=--';
    const close = ctx.base_latest_close ? Number(ctx.base_latest_close).toLocaleString('ja-JP', { maximumFractionDigits: 0 }) : '--';
    const rows = ctx.cache_rows || ctx.interactive_candle_count || CANDLES.length;
    baseMetaEl.textContent = `base close=${close} / ${freshness} / rows=${rows}`;
  }
  const chart = LightweightCharts.createChart(chartEl, {
    layout: { background: { type: 'solid', color: '#ffffff' }, textColor: '#334155', fontSize: 12 },
    grid: { vertLines: { color: 'rgba(148,163,184,.18)' }, horzLines: { color: 'rgba(148,163,184,.20)' } },
    localization: { locale: 'ja-JP', priceFormatter: price => Number(price).toLocaleString('ja-JP', { maximumFractionDigits: 0 }) },
    crosshair: { mode: LightweightCharts.CrosshairMode ? LightweightCharts.CrosshairMode.Normal : 0 },
    rightPriceScale: { borderVisible: false, scaleMargins: { top: 0.08, bottom: 0.24 } },
    timeScale: { borderVisible: false, rightOffset: 12, barSpacing: 4, minBarSpacing: 2, fixLeftEdge: false, fixRightEdge: false, timeVisible: true, secondsVisible: false },
    handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: false },
    handleScale: { mouseWheel: true, pinch: true, axisPressedMouseMove: true },
  });
  let series = null;
  if (chart.addSeries && LightweightCharts.CandlestickSeries) {
    series = chart.addSeries(LightweightCharts.CandlestickSeries, { upColor: '#16a34a', downColor: '#dc2626', borderUpColor: '#16a34a', borderDownColor: '#dc2626', wickUpColor: '#15803d', wickDownColor: '#b91c1c', priceLineVisible: true, lastValueVisible: true });
  } else if (chart.addCandlestickSeries) {
    series = chart.addCandlestickSeries({ upColor: '#16a34a', downColor: '#dc2626', borderUpColor: '#16a34a', borderDownColor: '#dc2626', wickUpColor: '#15803d', wickDownColor: '#b91c1c', priceLineVisible: true, lastValueVisible: true });
  }
  if (!series) { document.getElementById('fallback').style.display = 'block'; return; }
  let volumeSeries = null;
  let lastClosePriceLine = null;
  function candleBar(c) { return { time: c.time, open: c.open, high: c.high, low: c.low, close: c.close }; }
  function volumeBar(c) { return { time: c.time, value: Number(c.volume || 0), color: c.close >= c.open ? 'rgba(22,163,74,.28)' : 'rgba(220,38,38,.28)' }; }
  function updateBaseMeta(candles, meta) {
    if (!baseMetaEl || !Array.isArray(candles) || !candles.length) return;
    const last = candles[candles.length - 1];
    const close = Number(last.close).toLocaleString('ja-JP', { maximumFractionDigits: 0 });
    const lag = meta.cache_lag_vs_live || meta.cache_lag || ctx.cache_lag_vs_live || '--';
    const rows = meta.rows_returned || meta.candles_returned || meta.candles_written || candles.length;
    const server = meta.server_poll_ok === false ? ' / engine=waiting' : ' / engine=polling';
    baseMetaEl.textContent = `base close=${close} / cache遅延=${lag} / rows=${rows}${server}`;
  }
  function applyCandlePayload(payload, preserveRange) {
    const nextCandles = payload && Array.isArray(payload.candles) ? payload.candles : [];
    if (!nextCandles.length) return false;
    const previousRange = preserveRange && chart.timeScale().getVisibleLogicalRange ? chart.timeScale().getVisibleLogicalRange() : null;
    const previousTotal = CANDLES.length;
    const wasFollowingLatest = !previousRange || previousRange.to >= previousTotal - 2;
    CANDLES.splice(0, CANDLES.length, ...nextCandles);
    series.setData(CANDLES.map(candleBar));
    if (lastClosePriceLine && series.removePriceLine) {
      try { series.removePriceLine(lastClosePriceLine); } catch (err) { console.debug(err); }
    }
    const lastCandle = CANDLES[CANDLES.length - 1];
    if (lastCandle && series.createPriceLine) {
      lastClosePriceLine = series.createPriceLine({ price: lastCandle.close, color: '#2563eb', lineWidth: 1, lineStyle: LightweightCharts.LineStyle ? LightweightCharts.LineStyle.Dashed : 2, axisLabelVisible: true, title: 'last close' });
    }
    const volumeData = CANDLES.filter(c => Number(c.volume || 0) > 0).map(volumeBar);
    if (volumeData.length) {
      const volumeOptions = { priceFormat: { type: 'volume' }, priceScaleId: '', lastValueVisible: false, priceLineVisible: false };
      if (!volumeSeries && chart.addSeries && LightweightCharts.HistogramSeries) volumeSeries = chart.addSeries(LightweightCharts.HistogramSeries, volumeOptions);
      else if (!volumeSeries && chart.addHistogramSeries) volumeSeries = chart.addHistogramSeries(volumeOptions);
      if (volumeSeries) {
        volumeSeries.setData(volumeData);
        if (volumeSeries.priceScale) volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
      }
    }
    updateBaseMeta(CANDLES, payload.meta || {});
    if (preserveRange && chart.timeScale().setVisibleLogicalRange) {
      if (previousRange && !wasFollowingLatest) {
        chart.timeScale().setVisibleLogicalRange(previousRange);
      } else {
        const liveVisible = Math.min(CANDLES.length, Math.max(visible || 90, Math.ceil((visible || 90) * 3)));
        chart.timeScale().setVisibleLogicalRange({ from: Math.max(0, CANDLES.length - liveVisible), to: CANDLES.length + 8 });
      }
    }
    return true;
  }
  applyCandlePayload({ candles: CANDLES, meta: ctx }, false);
  renderOverlayLayers(chart, series);
  const total = CANDLES.length;
  const visible = Math.min(total, BASE.visible_candle_count || 90);
  const thinVisible = Math.min(total, Math.max(visible, Math.ceil(visible * 3)));
  const rangeStorageKey = ['warroom', 'base-candle-range', BASE.component_version || 'v1', BASE.mode || 'live', ctx.viewport_label || BASE.chart_context?.viewport_label || 'window', visible, thinVisible, total].join(':');
  const defaultVisibleRange = { from: Math.max(0, total - thinVisible), to: total + 8 };
  function clampVisibleRange(range) {
    if (!range || !Number.isFinite(range.from) || !Number.isFinite(range.to)) return null;
    const width = Math.max(5, Math.min(thinVisible * 4, range.to - range.from));
    const maxTo = total + 10;
    const minFrom = Math.min(0, total - width);
    let from = Math.max(minFrom, Math.min(range.from, maxTo - 1));
    let to = Math.max(from + 1, Math.min(range.to, maxTo));
    if ((to - from) < Math.min(5, total)) {
      to = Math.min(maxTo, from + Math.min(thinVisible, Math.max(1, total)));
    }
    return { from, to };
  }
  function loadVisibleRange() {
    try {
      const raw = window.localStorage.getItem(rangeStorageKey);
      return clampVisibleRange(JSON.parse(raw));
    } catch (err) {
      return null;
    }
  }
  function saveVisibleRange(range) {
    const clamped = clampVisibleRange(range);
    if (!clamped) return;
    try {
      window.localStorage.setItem(rangeStorageKey, JSON.stringify(clamped));
    } catch (err) {
      // localStorage can be unavailable in some embedded browsers; chart remains usable.
    }
  }
  function resetVisibleRange() {
    try { window.localStorage.removeItem(rangeStorageKey); } catch (err) { /* ignore unavailable storage */ }
    chart.timeScale().setVisibleLogicalRange(defaultVisibleRange);
  }
  chart.timeScale().setVisibleLogicalRange(loadVisibleRange() || defaultVisibleRange);
  if (chart.timeScale().subscribeVisibleLogicalRangeChange) {
    chart.timeScale().subscribeVisibleLogicalRangeChange(saveVisibleRange);
  }
  if (resetRangeBtn) resetRangeBtn.addEventListener('click', resetVisibleRange);
  async function pollChartDataEndpoint() {
    const endpoint = ctx.chart_data_endpoint || '';
    if (!endpoint || endpoint === 'disabled') return;
    try {
      const response = await fetch(endpoint, { cache: 'no-store' });
      if (!response.ok) throw new Error(`chart data HTTP ${response.status}`);
      const payload = await response.json();
      if (payload && payload.ok) applyCandlePayload(payload, true);
      else updateBaseMeta(CANDLES, { server_poll_ok: false, cache_lag: ctx.cache_lag_vs_live });
    } catch (err) {
      updateBaseMeta(CANDLES, { server_poll_ok: false, cache_lag: ctx.cache_lag_vs_live });
      console.debug('warroom chart data poll waiting', err);
    }
  }
  const pollIntervalMs = Math.max(1000, Number(ctx.chart_data_poll_interval_ms || 3000));
  pollChartDataEndpoint();
  window.setInterval(pollChartDataEndpoint, pollIntervalMs);
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
