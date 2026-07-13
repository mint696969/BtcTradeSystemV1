# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/frontend_assets/boot_js.py
# desc: Lightweight Charts boot and mouse interaction JavaScript for WarRoom interactive chart.

from __future__ import annotations

CHART_BOOT_JS = r"""
const WARROOM_CHART_DISPLAY_TIMEZONE = 'Asia/Tokyo';
function chartDisplayTimestamp(time) {
  if (time === undefined || time === null) return null;
  if (typeof time === 'object' && time.timestamp) return Number(time.timestamp) * 1000;
  if (typeof time === 'object' && time.year && time.month && time.day) return Date.UTC(Number(time.year), Number(time.month) - 1, Number(time.day));
  const seconds = Number(time);
  if (!Number.isFinite(seconds)) return null;
  return seconds * 1000;
}
function formatChartTimeJst(time, includeDate) {
  const ts = chartDisplayTimestamp(time);
  if (ts === null) return '';
  const options = includeDate
    ? { timeZone: WARROOM_CHART_DISPLAY_TIMEZONE, month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }
    : { timeZone: WARROOM_CHART_DISPLAY_TIMEZONE, hour: '2-digit', minute: '2-digit', hourCycle: 'h23' };
  return new Intl.DateTimeFormat('ja-JP', options).format(new Date(ts));
}
function isCalendarBoundaryTick(tickMarkType) {
  const type = Number(tickMarkType);
  return Number.isFinite(type) && type <= 2;
}
function formatChartTickJst(time, tickMarkType) {
  const ts = chartDisplayTimestamp(time);
  if (ts === null) return '';
  const parts = new Intl.DateTimeFormat('ja-JP', {
    timeZone: WARROOM_CHART_DISPLAY_TIMEZONE,
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(new Date(ts));
  const values = Object.fromEntries(parts.map(part => [part.type, part.value]));
  const isMidnight = values.hour === '00' && values.minute === '00';
  if (isMidnight || isCalendarBoundaryTick(tickMarkType)) return `${values.month}/${values.day}`;
  return `${values.hour}:${values.minute}`;
}
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
    localization: { locale: 'ja-JP', priceFormatter: price => Number(price).toLocaleString('ja-JP', { maximumFractionDigits: 0 }), timeFormatter: time => formatChartTimeJst(time, true) },
    crosshair: { mode: LightweightCharts.CrosshairMode ? LightweightCharts.CrosshairMode.Normal : 0 },
    rightPriceScale: { borderVisible: false, scaleMargins: { top: 0.08, bottom: 0.24 } },
    timeScale: { borderVisible: false, rightOffset: 14, barSpacing: 1, minBarSpacing: 0.5, fixLeftEdge: false, fixRightEdge: false, timeVisible: true, secondsVisible: false, tickMarkFormatter: (time, tickMarkType) => formatChartTickJst(time, tickMarkType) },
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
  let operatorViewportLocked = false;
  const FIXED_BAR_SPACING = 8;
  const FIXED_MIN_BAR_SPACING = 0.5;
  const BAR_SPACING_STORAGE_KEY = 'warroom:base-candle-bar-spacing:v1';
  function clampBarSpacing(value) {
    const spacing = Number(value);
    if (!Number.isFinite(spacing)) return FIXED_BAR_SPACING;
    return Math.max(FIXED_MIN_BAR_SPACING, Math.min(80, spacing));
  }
  function loadPreferredBarSpacing() {
    try {
      const stored = window.localStorage.getItem(BAR_SPACING_STORAGE_KEY);
      return stored === null ? FIXED_BAR_SPACING : clampBarSpacing(stored);
    } catch (err) {
      return FIXED_BAR_SPACING;
    }
  }
  function savePreferredBarSpacing() {
    try {
      const options = chart.timeScale().options ? chart.timeScale().options() : null;
      const spacing = clampBarSpacing(options && options.barSpacing);
      window.localStorage.setItem(BAR_SPACING_STORAGE_KEY, String(spacing));
    } catch (err) {
      // localStorage or chart options may be unavailable; the chart remains usable.
    }
  }
  function applyPreferredBarSpacing() {
    chart.timeScale().applyOptions({
      barSpacing: loadPreferredBarSpacing(),
      minBarSpacing: FIXED_MIN_BAR_SPACING,
    });
  }
  function resetPreferredBarSpacing() {
    try { window.localStorage.removeItem(BAR_SPACING_STORAGE_KEY); } catch (err) { /* ignore unavailable storage */ }
    chart.timeScale().applyOptions({
      barSpacing: FIXED_BAR_SPACING,
      minBarSpacing: FIXED_MIN_BAR_SPACING,
    });
  }
  function setVisibleLogicalRangeFixed(range) {
    chart.timeScale().setVisibleLogicalRange(range);
    applyPreferredBarSpacing();
  }
  let plotBarCount = Array.isArray(CANDLES) ? CANDLES.length : 0;
  const MAX_WHITESPACE_BARS = Number(ctx.max_whitespace_bars || 200000);
  function candleBar(c) { return { time: c.time, open: c.open, high: c.high, low: c.low, close: c.close }; }
  function volumeBar(c) { return { time: c.time, value: Number(c.volume || 0), color: c.close >= c.open ? 'rgba(22,163,74,.28)' : 'rgba(220,38,38,.28)' }; }
  function chartTimeframeSec(candles) {
    const configured = Number(ctx.candle_store_timeframe_sec || ctx.timeframe_sec || 0);
    if (Number.isFinite(configured) && configured > 0) return configured;
    if (!Array.isArray(candles) || candles.length < 2) return 60;
    for (let i = 1; i < candles.length; i += 1) {
      const diff = Number(candles[i].time) - Number(candles[i - 1].time);
      if (Number.isFinite(diff) && diff > 0) return diff;
    }
    return 60;
  }
  function chartCandleBars(candles) {
    const bars = [];
    const step = Math.max(1, chartTimeframeSec(candles));
    let whitespaceCount = 0;
    for (let i = 0; i < candles.length; i += 1) {
      const candle = candles[i];
      if (i > 0) {
        const prev = candles[i - 1];
        const prevTime = Number(prev.time);
        const nextTime = Number(candle.time);
        const missing = Math.floor((nextTime - prevTime) / step) - 1;
        if (Number.isFinite(missing) && missing > 0) {
          const available = Math.max(0, MAX_WHITESPACE_BARS - whitespaceCount);
          const addCount = Math.min(missing, available);
          for (let n = 1; n <= addCount; n += 1) {
            bars.push({ time: prevTime + (step * n) });
          }
          whitespaceCount += addCount;
        }
      }
      bars.push(candleBar(candle));
    }
    plotBarCount = bars.length;
    return bars;
  }
  function setSeriesCandles(candles) {
    const bars = chartCandleBars(candles);
    series.setData(bars);
    return bars;
  }
  function candleStatus(candle) {
    return String((candle && (candle.candle_status || candle.status)) || '').toLowerCase();
  }
  function shouldReplaceExistingCandle(previous, incoming) {
    if (!previous) return true;
    const previousStatus = candleStatus(previous);
    const incomingStatus = candleStatus(incoming);
    if (previousStatus === 'closed') return false;
    if (incomingStatus === 'forming') return true;
    if (previousStatus === 'forming' && incomingStatus === 'closed') return true;
    return previousStatus !== 'closed';
  }
  function mergeCandlesByTime(nextCandles) {
    const byTime = new Map();
    for (const candle of CANDLES) {
      const key = Number(candle && candle.time);
      if (Number.isFinite(key)) byTime.set(key, candle);
    }
    for (const candle of nextCandles) {
      const key = Number(candle && candle.time);
      if (!Number.isFinite(key)) continue;
      const previous = byTime.get(key) || null;
      if (shouldReplaceExistingCandle(previous, candle)) {
        byTime.set(key, { ...(previous || {}), ...candle, time: key });
      }
    }
    return Array.from(byTime.values()).sort((a, b) => Number(a.time) - Number(b.time));
  }

  function updateBaseMeta(candles, meta) {
    if (!baseMetaEl || !Array.isArray(candles) || !candles.length) return;
    const last = candles[candles.length - 1];
    const close = Number(last.close).toLocaleString('ja-JP', { maximumFractionDigits: 0 });
    const lag = meta.cache_lag_vs_live || meta.cache_lag || ctx.cache_lag_vs_live || '--';
    const rows = meta.rows_returned || meta.candles_returned || meta.candles_written || candles.length;
    const pollMode = ctx.chart_engine_polling_enabled === false ? 'review' : 'live';
    const server = meta.server_poll_ok === false ? ` / engine=${pollMode}-waiting` : ` / engine=${pollMode}-polling`;
    baseMetaEl.textContent = `base close=${close} / cache遅延=${lag} / rows=${rows}${server}`;
  }
  function applyCandlePayload(payload, preserveRange) {
    const nextCandles = payload && Array.isArray(payload.candles) ? payload.candles : [];
    if (!nextCandles.length) return false;
    const previousRange = preserveRange && chart.timeScale().getVisibleLogicalRange ? chart.timeScale().getVisibleLogicalRange() : null;
    const previousTotal = plotBarCount || CANDLES.length;
    const wasFollowingLatest = !previousRange || previousRange.to >= previousTotal + 4;
    const mergedCandles = mergeCandlesByTime(nextCandles);
    CANDLES.splice(0, CANDLES.length, ...mergedCandles);
    setSeriesCandles(CANDLES);
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
      if (previousRange && (operatorViewportLocked || !wasFollowingLatest)) {
        setVisibleLogicalRangeFixed(previousRange);
      } else {
        const liveVisible = Math.max(visible || 120, Math.ceil((visible || 120) * 8.0));
        const latestPlotBar = plotBarCount || CANDLES.length;
        setVisibleLogicalRangeFixed({ from: latestPlotBar - liveVisible, to: latestPlotBar + 8 });
      }
    }
    return true;
  }
  applyCandlePayload({ candles: CANDLES, meta: ctx }, false);
  renderOverlayLayers(chart, series);
  const liveFollowLatestOnLoad = ctx.chart_engine_polling_enabled !== false;
  const visible = Math.max(12, BASE.visible_candle_count || 120);
  const thinVisible = Math.max(visible, Math.ceil(visible * 8.0));
  const total = Math.max(plotBarCount || 0, CANDLES.length);
  const rangeStorageKey = ['warroom', 'base-candle-range', BASE.component_version || 'v1', BASE.mode || 'live', ctx.viewport_label || BASE.chart_context?.viewport_label || 'window', visible, thinVisible, total].join(':');
  const defaultVisibleRange = { from: total - thinVisible, to: total + 10 };
  function clampVisibleRange(range) {
    if (!range || !Number.isFinite(range.from) || !Number.isFinite(range.to)) return null;
    const width = Math.max(5, Math.min(thinVisible * 4, range.to - range.from));
    const maxTo = total + 16;
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
    operatorViewportLocked = false;
    try { window.localStorage.removeItem(rangeStorageKey); } catch (err) { /* ignore unavailable storage */ }
    resetPreferredBarSpacing();
    const latestTotal = Math.max(plotBarCount || 0, CANDLES.length, total);
    const latestRange = { from: latestTotal - thinVisible, to: latestTotal + 10 };
    chart.timeScale().setVisibleLogicalRange(latestRange);
  }
  const loadedVisibleRange = liveFollowLatestOnLoad ? null : loadVisibleRange();
  if (loadedVisibleRange) operatorViewportLocked = true;
  setVisibleLogicalRangeFixed(loadedVisibleRange || defaultVisibleRange);
  if (chart.timeScale().subscribeVisibleLogicalRangeChange) {
    chart.timeScale().subscribeVisibleLogicalRangeChange(saveVisibleRange);
  }
  chartEl.addEventListener('wheel', () => {
    operatorViewportLocked = true;
    window.requestAnimationFrame(() => window.requestAnimationFrame(savePreferredBarSpacing));
  }, { passive: true });
  chartEl.addEventListener('pointerdown', () => { operatorViewportLocked = true; });
  if (resetRangeBtn) resetRangeBtn.addEventListener('click', resetVisibleRange);
  async function pollChartDataEndpoint() {
    const endpoint = ctx.chart_data_endpoint || '';
    if (!endpoint || endpoint === 'disabled' || ctx.chart_engine_polling_enabled === false) {
      updateBaseMeta(CANDLES, { ...ctx, server_poll_ok: true, cache_lag: ctx.cache_lag_vs_live });
      return;
    }
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
  window.addEventListener('resize', () => { chart.applyOptions({ width: chartEl.clientWidth }); applyPreferredBarSpacing(); });
}
boot();
""".strip()
