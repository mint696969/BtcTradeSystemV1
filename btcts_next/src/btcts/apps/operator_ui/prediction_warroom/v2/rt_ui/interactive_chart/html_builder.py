# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/html_builder.py
# desc: Assemble WarRoom interactive chart HTML document from frontend assets and backend records.

from __future__ import annotations

from html import escape
import json
from typing import Any, Mapping

from .constants import INTERACTIVE_CHART_COMPONENT_VERSION, LIGHTWEIGHT_CHARTS_CDN, recommended_visible_candle_count
from .frontend_assets import CHART_CSS, CHART_JS
from .overlays import normalize_interactive_overlay_layers


def json_for_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")


def component_height(candle_count: int) -> int:
    _ = candle_count
    return 640


def build_interactive_chart_html(
    *,
    candles: list[dict[str, Any]],
    mode: str,
    chart_context: Mapping[str, Any] | None = None,
    visible_candle_count: int | None = None,
) -> str:
    visible_count = int(visible_candle_count or recommended_visible_candle_count(mode))
    context = dict(chart_context or {})
    overlay_layers = normalize_interactive_overlay_layers(context.get("overlay_layers"))
    selection_base = {
        "mode": mode,
        "visible_candle_count": visible_count,
        "chart_context": context,
        "overlay_layers": overlay_layers,
        "component_version": INTERACTIVE_CHART_COMPONENT_VERSION,
    }
    title = escape(f"Interactive candlestick / {mode} / read-only")
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
{CHART_CSS}
</style>
</head>
<body>
<div id="wrap">
  <div id="toolbar">
    <span class="badge base-focus">Base OHLC + Volume</span>
    <span class="badge">{title}</span>
    <span class="badge">click1=開始点</span>
    <span class="badge">click2=範囲確定</span>
    <span class="badge">wheel=zoom / drag blank=pan</span>
    <button id="reset-range" class="secondary" type="button">表示範囲へ戻す</button>
    <button id="copy" disabled>この範囲をGPTへコピー</button>
    <span id="base-meta"></span>
    <span id="status">ローソクをクリックしてください。2回クリックで範囲を確定できます。</span>
    <span id="copied"></span>
  </div>
  <div id="chart"></div>
  <div id="copy-panel" class="pending" aria-live="polite">
    <div id="selection-summary">未選択: ローソクをクリックしてください。</div>
    <div id="copy-hint">1回目クリックで開始点、2回目クリックで単ポイントまたは範囲を確定します。</div>
    <div id="copy-safety">read-only / no broker send / no order / no prediction</div>
  </div>
  <textarea id="packet-preview" readonly aria-label="GPT選択範囲JSONプレビュー"></textarea>
  <div id="fallback">Lightweight Charts の読み込みに失敗しました。既存のWarRoom表示はPython側フォールバックで維持されます。</div>
</div>
<script src="{LIGHTWEIGHT_CHARTS_CDN}"></script>
<script>
const CANDLES = {json_for_script(candles)};
const BASE = {json_for_script(selection_base)};
{CHART_JS}
</script>
</body>
</html>"""
