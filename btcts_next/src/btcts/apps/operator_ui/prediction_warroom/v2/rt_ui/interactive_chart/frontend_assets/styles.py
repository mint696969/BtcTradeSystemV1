# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/frontend_assets/styles.py
# desc: CSS for WarRoom interactive chart frontend component.

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
#copy-panel { margin-top:8px; padding:9px 10px; border:1px solid rgba(148,163,184,.34); border-radius:10px; background:#ffffff; box-shadow:0 1px 2px rgba(15,23,42,.05); font-size:12px; }
#copy-panel.pending { background:#f8fafc; color:#475569; }
#copy-panel.ready { border-color:rgba(37,99,235,.28); background:#eff6ff; }
#copy-panel.copied { border-color:rgba(21,128,61,.28); background:#f0fdf4; }
#copy-panel.manual { border-color:rgba(185,28,28,.30); background:#fef2f2; }
#selection-summary { font-weight:700; color:#0f172a; }
#copy-hint { margin-top:4px; color:#475569; }
#copy-safety { margin-top:4px; color:#64748b; font-size:11px; }
#fallback { color:#b91c1c; padding: 10px; display:none; }
#packet-preview { display:none; width:100%; min-height:112px; max-height:180px; box-sizing:border-box; margin-top:8px; padding:8px; border:1px solid rgba(37,99,235,.25); border-radius:8px; background:#f8fafc; color:#0f172a; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size:11px; white-space:pre; }
""".strip()
