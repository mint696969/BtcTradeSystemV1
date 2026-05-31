# path: ./btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_panel.py
# desc: Shared Streamlit component for read-only Health/WarRoom evidence presentation payloads.

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import streamlit as st


_BOUNDARY_KEYS: tuple[str, ...] = (
    "read_only_consumption",
    "diagnostic_evidence_only",
    "operator_support_only",
    "not_runtime_signal",
    "not_runtime_wiring",
    "not_ui_rendering",
    "not_market_engine_input",
    "not_collector_writer",
    "not_broker_or_order_automation",
    "not_inference_or_training",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) else ()


def _text(value: Any, *, fallback: str = "-") -> str:
    if value is None:
        return fallback
    raw = str(value).strip()
    return raw or fallback


def _boundary_text(boundary: Mapping[str, Any]) -> str:
    parts = []
    for key in _BOUNDARY_KEYS:
        if key in boundary:
            parts.append(f"{key}={bool(boundary.get(key))}")
    return " / ".join(parts) if parts else "boundary=unavailable"


def build_evidence_presentation_caption(payload: Mapping[str, Any] | None) -> str:
    data = _as_mapping(payload)
    boundary = _as_mapping(data.get("boundary"))
    return (
        "evidence_presentation "
        f"status={_text(data.get('status_key'), fallback='unknown')} / "
        f"severity={_text(data.get('severity_key'), fallback='unknown')} / "
        f"kind={_text(data.get('presentation_kind'), fallback='unknown')} / "
        f"version={_text(data.get('presentation_version'), fallback='unknown')} / "
        f"{_boundary_text(boundary)}"
    )


def build_evidence_presentation_lines(payload: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = _as_mapping(payload)
    counts = _as_mapping(data.get("counts"))
    summary_lines = tuple(str(line) for line in _as_sequence(data.get("summary_lines")))
    trace_refs = tuple(str(ref) for ref in _as_sequence(data.get("evidence_trace_refs")))

    lines = [
        f"title={_text(data.get('title'), fallback='Real-data validation evidence')}",
        f"status={_text(data.get('status_key'), fallback='unknown')}",
        f"severity={_text(data.get('severity_key'), fallback='unknown')}",
        f"health_line={_text(data.get('health_line'), fallback='-')}",
        f"warroom_line={_text(data.get('warroom_line'), fallback='-')}",
        f"replay_rows={int(counts.get('replay_row_count') or 0)}",
        f"board_rows={int(counts.get('board_row_count') or 0)}",
        f"trade_rows={int(counts.get('trade_row_count') or 0)}",
        f"diagnostic_notes={int(counts.get('diagnostic_note_count') or 0)}",
    ]
    lines.extend(f"summary={line}" for line in summary_lines)
    if trace_refs:
        lines.append("trace_refs=" + ",".join(trace_refs))
    lines.append(build_evidence_presentation_caption(data))
    return tuple(lines)


def render_evidence_presentation_panel(payload: Mapping[str, Any] | None, *, expanded: bool = False) -> None:
    """Render a provided read-only evidence presentation payload. Does not load data."""
    data = _as_mapping(payload)
    title = _text(data.get("title"), fallback="Real-data validation evidence")
    status = _text(data.get("status_key"), fallback="unknown")
    severity = _text(data.get("severity_key"), fallback="unknown")
    health_line = _text(data.get("health_line"), fallback="-")
    warroom_line = _text(data.get("warroom_line"), fallback="-")

    st.markdown(f"### {title}")
    st.caption(build_evidence_presentation_caption(data))

    c1, c2 = st.columns(2)
    c1.metric("Evidence status", status)
    c2.metric("Evidence severity", severity)
    st.caption(health_line)
    st.caption(warroom_line)

    if expanded:
        st.json({"evidence_presentation_lines": list(build_evidence_presentation_lines(data))})
