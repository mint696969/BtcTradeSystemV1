# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/html_assets.py
# desc: Frontend CSS/JS template for WarRoom v2 interactive chart. No Python-side runtime behavior.

from __future__ import annotations

CHART_CSS = """
html, body { margin: 0; padding: 0; background: transparent; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f172a; }
#wrap { width: 100%; box-sizing: border-box; }
#toolbar { display:flex; align-items:center; gap:8px; flex-wrap:wrap; padding: 2px 0 8px 0; font-size: 12px; }
#chart { width:100%; height:390px; border: 1px solid rgba(148,163,184,.35); border-radius: 10px; overflow:hidden; background: #ffffff; }
button { border:1px solid rgba(37,99,235,.35); background:#eff6ff; color:#1d4ed8; border-radius:8px; padding:5px 10px; font-weight:700; cursor:pointer; }
button:disabled { opacity:.45; cursor:not-allowed; }
.badge { border:1px solid rgba(148,163,184,.4); border-radius:999px; padding:4px 8px; background:#f8fafc; }
#status { color:#334155; }
#copied { color:#15803d; font-weight:700; }
#fallback { color:#b91c1c; padding: 10px; display:none; }
#packet-preview { display:none; width:100%; min-height:96px; box-sizing:border-box; margin-top:8px; padding:8px; border:1px solid rgba(37,99,235,.25); border-radius:8px; background:#f8fafc; color:#0f172a; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size:11px; white-space:pre; }
""".strip()

CHART_JS = r"""
const chartEl = document.getElementById('chart');
const statusEl = document.getElementById('status');
const copiedEl = document.getElementById('copied');
const copyBtn = document.getElementById('copy');
const packetPreviewEl = document.getElementById('packet-preview');
let selectedStart = null;
let selectedEnd = null;
let mouseDownTime = null;
let markersApi = null;

function candleByTime(t) {
  if (t === undefined || t === null) return null;
  const raw = (typeof t === 'object' && t.timestamp) ? t.timestamp : t;
  let best = null;
  let bestDiff = Number.MAX_SAFE_INTEGER;
  for (const candle of CANDLES) {
    const diff = Math.abs(Number(candle.time) - Number(raw));
    if (diff < bestDiff) { best = candle; bestDiff = diff; }
  }
  return best;
}
function orderSelection(a, b) {
  if (!a || !b) return [a, b];
  return Number(a.time) <= Number(b.time) ? [a, b] : [b, a];
}
function candleCount(a, b) {
  if (!a || !b) return 0;
  const [s, e] = orderSelection(a, b);
  return CANDLES.filter(c => Number(c.time) >= Number(s.time) && Number(c.time) <= Number(e.time)).length;
}
function selectionType(a, b) { return a && b && Number(a.time) !== Number(b.time) ? 'range' : 'single_candle'; }
function updateStatus() {
  if (!selectedStart || !selectedEnd) {
    statusEl.textContent = 'ローソクをクリック、または範囲ドラッグしてください。';
    copyBtn.disabled = true;
    packetPreviewEl.style.display = 'none';
    packetPreviewEl.value = '';
    return;
  }
  const [s, e] = orderSelection(selectedStart, selectedEnd);
  const count = candleCount(s, e);
  statusEl.textContent = `選択: ${s.time_jst} ～ ${e.time_jst} / ${count}本 / ${selectionType(s, e)}`;
  packetPreviewEl.value = selectionPacketText();
  packetPreviewEl.style.display = 'block';
  copyBtn.disabled = false;
}
function buildPacket() {
  const [s, e] = orderSelection(selectedStart, selectedEnd);
  return {
    schema_version: 'warroom_chart_analysis_request.2026_07_06.v2_interactive_selection',
    selection_origin: 'warroom_v2_interactive_candlestick_chart',
    selection_type: selectionType(s, e),
    purpose: 'manual review only; use Actions/data tools for deeper evidence; no order action',
    timeframe: { Live: 'live', '1分足': '1m', '1時間足': '1h', '日足': '1d' }[BASE.mode] || 'live',
    timeframe_label: BASE.mode,
    selected_range: {
      start_ts_utc: s.time_utc,
      end_ts_utc: e.time_utc,
      start_ts_jst: s.time_jst,
      end_ts_jst: e.time_jst,
      start_candle_index: s.candle_index,
      end_candle_index: e.candle_index,
      candle_count: candleCount(s, e),
      inclusive: true
    },
    viewport: {
      right_edge_is_now_or_latest: true,
      future_space_is_visual_blank_only: true,
      visible_candle_count: BASE.visible_candle_count
    },
    source: {
      hot_data_root: 'D:/btc_ts_hot',
      cold_data_root: 'E:/btc_ts',
      cold_root_policy: 'Use cold archive only when the operator explicitly asks for archive/replay/historical validation.',
      primary_market_trade_path: BASE.chart_context.primary_market_trade_path || null,
      dhot_bootstrap: BASE.chart_context.dhot_bootstrap || {},
      input_source: BASE.chart_context.input_source || 'retained_market_state_rows_plus_dhot_market_trade_bootstrap'
    },
    display_timezone: 'Asia/Tokyo',
    canonical_timezone: 'UTC',
    safety: {
      read_only: true,
      manual_review_only: true,
      websocket_send_enabled: false,
      broker_send_enabled: false,
      order_intent_submitted: false,
      ledger_append_allowed: false,
      prediction_invoked: false,
      classifier_invoked: false
    }
  };
}
function selectionPacketText() {
  return JSON.stringify(buildPacket(), null, 2);
}
function selectPreviewForManualCopy() {
  packetPreviewEl.style.display = 'block';
  packetPreviewEl.focus();
  packetPreviewEl.select();
}
async function copySelection() {
  const text = packetPreviewEl.value || selectionPacketText();
  packetPreviewEl.value = text;
  packetPreviewEl.style.display = 'block';
  try {
    await navigator.clipboard.writeText(text);
    copiedEl.textContent = 'コピーしました: 下の内容と同じJSONをクリップボードへ保存';
  } catch (err) {
    selectPreviewForManualCopy();
    copiedEl.textContent = '自動コピー不可: 下のJSONをCtrl+Cで手動コピー';
    console.error(err);
  }
}
function lineStyleValue(value) {
  if (value === 'dotted' && LightweightCharts.LineStyle) return LightweightCharts.LineStyle.Dotted;
  if (value === 'solid' && LightweightCharts.LineStyle) return LightweightCharts.LineStyle.Solid;
  if (LightweightCharts.LineStyle) return LightweightCharts.LineStyle.LargeDashed;
  return 2;
}
function renderLineOverlay(chart, layer) {
  if (!Array.isArray(layer.points) || layer.points.length < 2) return;
  let series = null;
  const options = { color: layer.color || '#7c3aed', lineWidth: layer.line_width || 2, lineStyle: lineStyleValue(layer.line_style || 'dashed'), priceLineVisible: false, lastValueVisible: false, title: layer.label || layer.layer_id || 'overlay' };
  if (chart.addSeries && LightweightCharts.LineSeries) {
    series = chart.addSeries(LightweightCharts.LineSeries, options);
  } else if (chart.addLineSeries) {
    series = chart.addLineSeries(options);
  }
  if (series) series.setData(layer.points.map(p => ({ time: p.time, value: p.value })));
}
function renderMarkerOverlay(baseSeries, layer) {
  if (!baseSeries || !Array.isArray(layer.markers) || !layer.markers.length) return;
  try {
    const markers = layer.markers.map(m => ({ time: m.time, position: m.position || 'aboveBar', color: m.color || layer.color || '#0f766e', shape: m.shape || 'circle', text: m.text || layer.label || '' }));
    if (LightweightCharts.createSeriesMarkers) LightweightCharts.createSeriesMarkers(baseSeries, markers);
    else if (baseSeries.setMarkers) baseSeries.setMarkers(markers);
  } catch (err) { console.debug(err); }
}
function renderBoardBandOverlay(chart, layer) {
  if (!Array.isArray(layer.points) || layer.points.length < 2) return;
  renderLineOverlay(chart, { layer_id: `${layer.layer_id || 'board_band'}_bid`, label: `${layer.label || 'board'} bid`, color: layer.bid_color || '#60a5fa', line_width: layer.line_width || 1, line_style: 'solid', points: layer.points.map(p => ({ time: p.time, value: p.bid })) });
  renderLineOverlay(chart, { layer_id: `${layer.layer_id || 'board_band'}_ask`, label: `${layer.label || 'board'} ask`, color: layer.ask_color || '#fb7185', line_width: layer.line_width || 1, line_style: 'solid', points: layer.points.map(p => ({ time: p.time, value: p.ask })) });
  renderLineOverlay(chart, { layer_id: `${layer.layer_id || 'board_band'}_mid`, label: `${layer.label || 'board'} mid`, color: layer.mid_color || '#64748b', line_width: layer.line_width || 1, line_style: 'dashed', points: layer.points.map(p => ({ time: p.time, value: p.mid })) });
}
function renderOverlayLayers(chart, baseSeries) {
  const layers = Array.isArray(BASE.overlay_layers) ? BASE.overlay_layers : [];
  for (const layer of layers) {
    if (!layer || layer.rendered_now === false) continue;
    if (layer.kind === 'line') renderLineOverlay(chart, layer);
    if (layer.kind === 'marker') renderMarkerOverlay(baseSeries, layer);
    if (layer.kind === 'board_band') renderBoardBandOverlay(chart, layer);
  }
}
function markSelection(series) {
  if (!selectedStart || !selectedEnd) return;
  const [s, e] = orderSelection(selectedStart, selectedEnd);
  const markers = [
    { time: s.time, position: 'belowBar', color: '#2563eb', shape: 'arrowUp', text: 'start' },
  ];
  if (Number(e.time) !== Number(s.time)) markers.push({ time: e.time, position: 'aboveBar', color: '#dc2626', shape: 'arrowDown', text: 'end' });
  try {
    if (LightweightCharts.createSeriesMarkers) {
      if (markersApi && markersApi.setMarkers) markersApi.setMarkers(markers); else markersApi = LightweightCharts.createSeriesMarkers(series, markers);
    }
  } catch (err) { console.debug(err); }
}
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
    selectedStart = c;
    selectedEnd = c;
    copiedEl.textContent = '';
    updateStatus();
    markSelection(series);
  });
  chartEl.addEventListener('mousedown', ev => {
    const rect = chartEl.getBoundingClientRect();
    const coordinate = ev.clientX - rect.left;
    if (chart.timeScale().coordinateToTime) mouseDownTime = candleByTime(chart.timeScale().coordinateToTime(coordinate));
  });
  chartEl.addEventListener('mouseup', ev => {
    if (!mouseDownTime || !chart.timeScale().coordinateToTime) return;
    const rect = chartEl.getBoundingClientRect();
    const coordinate = ev.clientX - rect.left;
    const end = candleByTime(chart.timeScale().coordinateToTime(coordinate));
    if (!end) return;
    selectedStart = mouseDownTime;
    selectedEnd = end;
    mouseDownTime = null;
    copiedEl.textContent = '';
    updateStatus();
    markSelection(series);
  });
  copyBtn.addEventListener('click', copySelection);
  window.addEventListener('resize', () => chart.applyOptions({ width: chartEl.clientWidth }));
}
boot();
""".strip()
