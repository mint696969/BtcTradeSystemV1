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
function setCopyPanelState(state, summary, hint) {
  copyPanelEl.className = state;
  selectionSummaryEl.textContent = summary;
  copyHintEl.textContent = hint;
  copySafetyEl.textContent = 'read-only / broker_send=false / order_intent=false / prediction=false / classifier=false';
}
function selectionSummaryText(s, e, count) {
  return `GPTコピー対象: ${s.time_jst} ～ ${e.time_jst} / ${count}本 / ${selectionType(s, e)} / ${BASE.mode}`;
}
function updateStatus() {
  if (!selectedStart || !selectedEnd) {
    statusEl.textContent = 'ローソクをクリック、または範囲ドラッグしてください。';
    copyBtn.disabled = true;
    packetPreviewEl.style.display = 'none';
    packetPreviewEl.value = '';
    copiedEl.textContent = '';
    setCopyPanelState('pending', '未選択: ローソクをクリック、または範囲ドラッグしてください。', '選択後にGPT分析用JSONを自動コピーできます。');
    return;
  }
  const [s, e] = orderSelection(selectedStart, selectedEnd);
  const count = candleCount(s, e);
  statusEl.textContent = `選択: ${s.time_jst} ～ ${e.time_jst} / ${count}本 / ${selectionType(s, e)}`;
  packetPreviewEl.value = selectionPacketText();
  packetPreviewEl.style.display = 'block';
  setCopyPanelState('ready', selectionSummaryText(s, e, count), 'ボタンでJSONをコピー。ブラウザが拒否した場合は下のJSONが自動選択されます。');
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
    copiedEl.textContent = 'コピーしました';
    setCopyPanelState('copied', selectionSummaryEl.textContent, 'コピー成功: 下のJSONと同じ内容をクリップボードへ保存しました。');
  } catch (err) {
    selectPreviewForManualCopy();
    copiedEl.textContent = '手動コピー待ち';
    setCopyPanelState('manual', selectionSummaryEl.textContent, '自動コピー不可: 下のJSONをCtrl+Cで手動コピーしてください。');
    console.error(err);
  }
}
""".strip()
