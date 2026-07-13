# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/frontend_assets/selection_js.py
# desc: Selection, range copy, and GPT clipboard fallback JavaScript for WarRoom interactive chart.

from __future__ import annotations

CHART_SELECTION_JS = r"""
const chartEl = document.getElementById('chart');
const statusEl = document.getElementById('status');
const copiedEl = document.getElementById('copied');
const copyBtn = document.getElementById('copy');
const packetPreviewEl = document.getElementById('packet-preview');
const copyPanelEl = document.getElementById('copy-panel');
const selectionSummaryEl = document.getElementById('selection-summary');
const copyHintEl = document.getElementById('copy-hint');
const copySafetyEl = document.getElementById('copy-safety');
const SELECTION_ANCHOR_TTL_MS = 30000;
const SELECTION_FINALIZED_TTL_MS = 10000;
const SELECTION_ANCHOR_STORAGE_KEY = `warroom_v2_interactive_chart_anchor.${BASE.component_version || 'v1'}.${BASE.mode || 'live'}`;
const SELECTION_FINALIZED_STORAGE_KEY = `warroom_v2_interactive_chart_finalized.${BASE.component_version || 'v1'}.${BASE.mode || 'live'}`;
let selectedStart = null;
let selectedEnd = null;
let selectionAnchor = null;
let selectionRangeFinalized = false;
let selectionAnchorTimer = null;
let finalizedMarkerTimer = null;
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
function setCopyPanelState(state, summary, hint) {
  copyPanelEl.className = state;
  selectionSummaryEl.textContent = summary;
  copyHintEl.textContent = hint;
  copySafetyEl.textContent = 'read-only / broker_send=false / order_intent=false / prediction=false / classifier=false';
}
function selectionSummaryText(s, e, count) {
  return `GPTコピー対象: ${s.time_jst} ～ ${e.time_jst} / ${count}本 / ${selectionType(s, e)} / ${BASE.mode}`;
}
function clearSelectionAnchorTimer() {
  if (selectionAnchorTimer) clearTimeout(selectionAnchorTimer);
  selectionAnchorTimer = null;
}
function clearFinalizedMarkerTimer() {
  if (finalizedMarkerTimer) clearTimeout(finalizedMarkerTimer);
  finalizedMarkerTimer = null;
}
function clearFinalizedSelectionPresentation() {
  selectionAnchor = null;
  selectionRangeFinalized = false;
  selectedStart = null;
  selectedEnd = null;
  clearSelectionMarkers();
  clearStoredFinalizedSelection();
  clearFinalizedMarkerTimer();
  updateStatus();
}
function clearSelectionStateAfterAnchorExpiry() {
  selectionAnchor = null;
  selectionRangeFinalized = false;
  selectedStart = null;
  selectedEnd = null;
  clearSelectionAnchorTimer();
  clearStoredSelectionAnchor();
  clearSelectionMarkers();
  updateStatus();
}
function scheduleFinalizedMarkerExpiry(expiresAtMs) {
  clearFinalizedMarkerTimer();
  const remaining = Math.max(0, Number(expiresAtMs) - Date.now());
  finalizedMarkerTimer = setTimeout(() => {
    clearFinalizedSelectionPresentation();
  }, remaining);
}
function clearStoredSelectionAnchor() {
  try { localStorage.removeItem(SELECTION_ANCHOR_STORAGE_KEY); } catch (err) { console.debug(err); }
}
function clearStoredFinalizedSelection() {
  try { localStorage.removeItem(SELECTION_FINALIZED_STORAGE_KEY); } catch (err) { console.debug(err); }
}
function storeFinalizedSelection(copyState) {
  if (!selectedStart || !selectedEnd || !selectionRangeFinalized) return;
  const expiresAtMs = Date.now() + SELECTION_FINALIZED_TTL_MS;
  try {
    localStorage.setItem(SELECTION_FINALIZED_STORAGE_KEY, JSON.stringify({ start_time: selectedStart.time, end_time: selectedEnd.time, copy_state: copyState || 'ready', expires_at_ms: expiresAtMs }));
  } catch (err) { console.debug(err); }
  scheduleFinalizedMarkerExpiry(expiresAtMs);
}
function restoreFinalizedSelection(series) {
  try {
    const raw = localStorage.getItem(SELECTION_FINALIZED_STORAGE_KEY);
    if (!raw) return false;
    const saved = JSON.parse(raw);
    if (!saved || Number(saved.expires_at_ms) <= Date.now()) { clearStoredFinalizedSelection(); return false; }
    const start = candleByTime(saved.start_time);
    const end = candleByTime(saved.end_time);
    if (!start || !end) { clearStoredFinalizedSelection(); return false; }
    selectionAnchor = null;
    selectionRangeFinalized = true;
    selectedStart = start;
    selectedEnd = end;
    updateStatus();
    markSelection(series);
    scheduleFinalizedMarkerExpiry(Number(saved.expires_at_ms));
    if (saved.copy_state === 'copied') {
      copiedEl.textContent = 'コピーしました';
      setCopyPanelState('copied', selectionSummaryEl.textContent, 'コピー成功: 下のJSONと同じ内容をクリップボードへ保存しました。');
    } else if (saved.copy_state === 'manual') {
      copiedEl.textContent = '手動コピー待ち';
      setCopyPanelState('manual', selectionSummaryEl.textContent, '自動コピー不可: 下のJSONをCtrl+Cで手動コピーしてください。');
    }
    return true;
  } catch (err) { console.debug(err); clearStoredFinalizedSelection(); return false; }
}
function scheduleSelectionAnchorExpiry(series, expiresAtMs) {
  clearSelectionAnchorTimer();
  const remaining = Math.max(0, expiresAtMs - Date.now());
  selectionAnchorTimer = setTimeout(() => clearSelectionStateAfterAnchorExpiry(series), remaining);
}
function storeSelectionAnchor(c, series) {
  clearStoredFinalizedSelection();
  clearFinalizedMarkerTimer();
  const expiresAtMs = Date.now() + SELECTION_ANCHOR_TTL_MS;
  try { localStorage.setItem(SELECTION_ANCHOR_STORAGE_KEY, JSON.stringify({ time: c.time, expires_at_ms: expiresAtMs })); } catch (err) { console.debug(err); }
  scheduleSelectionAnchorExpiry(series, expiresAtMs);
}
function restoreSelectionAnchor(series) {
  try {
    const raw = localStorage.getItem(SELECTION_ANCHOR_STORAGE_KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    if (!saved || Number(saved.expires_at_ms) <= Date.now()) { clearSelectionStateAfterAnchorExpiry(); return; }
    const c = candleByTime(saved.time);
    if (!c) { clearStoredSelectionAnchor(); return; }
    selectionAnchor = c;
    selectionRangeFinalized = false;
    selectedStart = c;
    selectedEnd = c;
    updateStatus();
    markSelection(series);
    scheduleSelectionAnchorExpiry(series, Number(saved.expires_at_ms));
  } catch (err) { console.debug(err); clearStoredSelectionAnchor(); }
}
function selectionHintText(s, e) {
  if (!selectionRangeFinalized) return '開始点を選択中: 30秒以内に同じローソク再クリックで単ポイント確定、別ローソククリックで範囲確定。';
  return Number(s.time) === Number(e.time) ? '単ポイント確定: ボタンでJSONをコピーできます。' : '範囲確定: ボタンでJSONをコピーできます。';
}
function handleCandleClick(c, series) {
  let finalizedNow = false;
  if (!selectionAnchor || selectionRangeFinalized) {
    selectionAnchor = c;
    selectionRangeFinalized = false;
    selectedStart = c;
    selectedEnd = c;
    storeSelectionAnchor(c, series);
  } else {
    selectedStart = selectionAnchor;
    selectedEnd = c;
    selectionAnchor = null;
    selectionRangeFinalized = true;
    clearSelectionAnchorTimer();
    clearStoredSelectionAnchor();
    finalizedNow = true;
  }
  copiedEl.textContent = '';
  updateStatus();
  markSelection(series);
  if (finalizedNow) copySelection();
}
function updateStatus() {
  if (!selectedStart || !selectedEnd) {
    statusEl.textContent = 'ローソクをクリックしてください。2回クリックで範囲を確定できます。';
    copyBtn.disabled = true;
    packetPreviewEl.style.display = 'none';
    packetPreviewEl.value = '';
    copiedEl.textContent = '';
    setCopyPanelState('pending', '未選択: ローソクをクリックしてください。', '1回目クリックで開始点、2回目クリックで単ポイントまたは範囲を確定します。');
    return;
  }
  const [s, e] = orderSelection(selectedStart, selectedEnd);
  const count = candleCount(s, e);
  statusEl.textContent = `選択: ${s.time_jst} ～ ${e.time_jst} / ${count}本 / ${selectionType(s, e)}`;
  packetPreviewEl.value = selectionPacketText();
  packetPreviewEl.style.display = 'block';
  setCopyPanelState('ready', selectionSummaryText(s, e, count), selectionHintText(s, e));
  copyBtn.disabled = false;
}
function selectionTimeframeSec() {
  return { Live: 60, '1分足': 60, '5分足': 300, '15分足': 900, '30分足': 1800, '1時間足': 3600, '日足': 86400 }[BASE.mode] || 60;
}
function selectionTimeframeKey() {
  return { Live: 'live', '1分足': '1m', '5分足': '5m', '15分足': '15m', '30分足': '30m', '1時間足': '1h', '日足': '1d' }[BASE.mode] || 'live';
}
function candleStoreRelPath(timeframeSec) {
  return `data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=${timeframeSec}s`;
}
function selectedCandlesBetween(s, e) {
  return CANDLES.filter(c => Number(c.time) >= Number(s.time) && Number(c.time) <= Number(e.time));
}
function isFormingCandle(c) {
  return String((c && (c.candle_status || c.status)) || '').toLowerCase() === 'forming';
}
function buildPacket() {
  const [s, e] = orderSelection(selectedStart, selectedEnd);
  const selectedCandles = selectedCandlesBetween(s, e);
  const timeframe = selectionTimeframeKey();
  const timeframeSec = selectionTimeframeSec();
  const storeRelPath = candleStoreRelPath(timeframeSec);
  return {
    schema_version: 'warroom_chart_analysis_request.2026_07_06.v2_interactive_selection',
    selection_origin: 'warroom_v2_interactive_candlestick_chart',
    selection_type: selectionType(s, e),
    purpose: 'manual review only; use Actions/data tools for deeper evidence; no order action',
    timeframe: timeframe,
    timeframe_label: BASE.mode,
    timeframe_sec: timeframeSec,
    market: { exchange: 'bitflyer', symbol: 'FX_BTC_JPY' },
    selected_range: {
      start_ts_utc: s.time_utc,
      end_ts_utc: e.time_utc,
      start_ts_jst: s.time_jst,
      end_ts_jst: e.time_jst,
      start_candle_index: s.candle_index,
      end_candle_index: e.candle_index,
      candle_count: candleCount(s, e),
      inclusive: true,
      lookup_key: 'time_utc',
      candle_index_role: 'frontend_tail_record_index_not_store_index',
      candle_ts_semantics: 'bucket_start_utc',
      start_candle_status: s.candle_status || null,
      end_candle_status: e.candle_status || null,
      contains_forming_candle: selectedCandles.some(isFormingCandle)
    },
    viewport: {
      right_edge_is_now_or_latest: true,
      future_space_is_visual_blank_only: true,
      visible_candle_count: BASE.visible_candle_count,
      viewport_label: BASE.chart_context.viewport_label || null,
      viewport_minutes: BASE.chart_context.viewport_minutes || null,
      chart_axis_timezone: 'Asia/Tokyo'
    },
    source: {
      hot_data_root: 'D:/btc_ts_hot',
      cold_data_root: 'E:/btc_ts',
      cold_root_policy: 'Use cold archive only when the operator explicitly asks for archive/replay/historical validation.',
      primary_market_trade_path: BASE.chart_context.primary_market_trade_path || null,
      dhot_bootstrap: BASE.chart_context.dhot_bootstrap || {},
      input_source: BASE.chart_context.input_source || 'warroom_l4_candle_store_plus_retained_market_state_overlay',
      candle_store_family: 'warroom_l4_candle_store',
      candle_store_relpath: storeRelPath,
      closed_candles_relpath: `${storeRelPath}/closed.jsonl`,
      forming_candle_relpath: `${storeRelPath}/forming.json`,
      timeframe_meta_relpath: `${storeRelPath}/meta.json`,
      update_state_relpath: 'data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/update_state.json',
      gap_policy: 'absent_candles_no_synthetic_null',
      preferred_analysis_source: 'D-hot derived L4 candle store first; use E-cold only when explicitly requested.'
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
    copiedEl.textContent = 'コピーしました';
    setCopyPanelState('copied', selectionSummaryEl.textContent, 'コピー成功: 下のJSONと同じ内容をクリップボードへ保存しました。');
    storeFinalizedSelection('copied');
  } catch (err) {
    selectPreviewForManualCopy();
    copiedEl.textContent = '手動コピー待ち';
    setCopyPanelState('manual', selectionSummaryEl.textContent, '自動コピー不可: 下のJSONをCtrl+Cで手動コピーしてください。');
    storeFinalizedSelection('manual');
    console.error(err);
  }
}
""".strip()
