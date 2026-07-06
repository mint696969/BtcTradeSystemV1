# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/frontend_assets/__init__.py
# desc: Public frontend asset assembly for WarRoom interactive chart.

from __future__ import annotations

from .boot_js import CHART_BOOT_JS
from .overlay_js import CHART_OVERLAY_JS
from .selection_js import CHART_SELECTION_JS
from .styles import CHART_CSS

CHART_JS = "\n".join([CHART_SELECTION_JS, CHART_OVERLAY_JS, CHART_BOOT_JS])

__all__ = ["CHART_CSS", "CHART_JS"]
