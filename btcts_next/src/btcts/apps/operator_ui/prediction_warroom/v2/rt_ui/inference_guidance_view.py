# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/inference_guidance_view.py
# desc: Observational scenario guidance strip. Heuristic, read-only, no model/prediction/classifier invocation.

from __future__ import annotations

import re
from typing import Any, Mapping

_PRICE_RE = re.compile(r"(?:last_price|best_bid|best_ask)=([0-9]+(?:\.[0-9]+)?)")
_SPREAD_RE = re.compile(r"spread_bps=([0-9]+(?:\.[0-9]+)?)")


def _prices(chart_packet: Mapping[str, Any]) -> list[float]:
    out: list[float] = []
    for row in chart_packet.get("chart_rows", []):
        if not isinstance(row, Mapping):
            continue
        price = row.get("price")
        if isinstance(price, (int, float)):
            out.append(float(price))
        for match in _PRICE_RE.finditer(str(row.get("value_label") or "")):
            out.append(float(match.group(1)))
    return out


def _spread_bps(chart_packet: Mapping[str, Any]) -> float | None:
    for row in chart_packet.get("chart_rows", []):
        if isinstance(row, Mapping):
            match = _SPREAD_RE.search(str(row.get("value_label") or ""))
            if match:
                return float(match.group(1))
    return None


def build_inference_guidance_packet(chart_packet: Mapping[str, Any], widgets_packet: Mapping[str, Any]) -> dict[str, Any]:
    display_source = str(chart_packet.get("display_source") or widgets_packet.get("display_source") or "live")
    prices = _prices(chart_packet)
    spread_bps = _spread_bps(chart_packet)
    live_count = int(widgets_packet.get("live_widget_count") or 0)
    if not prices or display_source == "waiting":
        scenario, confidence, rationale = "waiting", "low", "live market observations are not ready yet"
    else:
        drift = prices[-1] - prices[0]
        if spread_bps is not None and spread_bps > 20:
            scenario, confidence, rationale = "caution / wide spread", "medium", f"spread_bps={spread_bps:.2f}; avoid over-reading direction"
        elif drift > 0:
            scenario, confidence, rationale = "upside pressure watch", "low-medium", f"latest price is above first observed price by {drift:.2f}"
        elif drift < 0:
            scenario, confidence, rationale = "downside pressure watch", "low-medium", f"latest price is below first observed price by {abs(drift):.2f}"
        else:
            scenario, confidence, rationale = "range / wait", "low", "observed prices are flat in current packet"
    return {"ok": True, "packet_kind": "warroom_v2_rt_observational_scenario_guidance_packet", "display_source": display_source, "scenario": scenario, "confidence": confidence, "rationale": rationale, "live_widget_count": live_count, "price_observation_count": len(prices), "read_only": True, "observational_scenario_only": True, "prediction_invoked": False, "classifier_invoked": False, "broker_send_enabled": False, "order_intent_submitted": False}


def render_inference_guidance(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("Inference guidance: observational scenario only / updates from market liquidity and trade context / not prophecy")
    c1, c2, c3 = st_api.columns(3)
    c1.metric("Scenario", str(packet.get("scenario") or "waiting"))
    c2.metric("Confidence", str(packet.get("confidence") or "low"))
    c3.metric("Live widgets", int(packet.get("live_widget_count") or 0))
    st_api.caption(str(packet.get("rationale") or ""))
    st_api.caption("observation_only=true / prediction_invoked=false / classifier_invoked=false / broker_send_enabled=false")
    return {"ok": True, "inference_guidance_rendered": True, "read_only": True, "prediction_invoked": False, "classifier_invoked": False}
