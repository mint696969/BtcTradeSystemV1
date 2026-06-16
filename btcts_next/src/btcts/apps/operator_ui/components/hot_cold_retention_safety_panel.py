# path: ./btcts_next/src/btcts/apps/operator_ui/components/hot_cold_retention_safety_panel.py
# desc: Shared Streamlit component for provided Hot/Cold retention safety payloads.

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import streamlit as st


_BOUNDARY_KEYS: tuple[str, ...] = (
    "read_only_display",
    "already_built_payload_only",
    "not_filesystem_scan",
    "not_copy_executor",
    "not_delete_executor",
    "not_runtime_state_writer",
    "not_collector_state_mutation",
    "not_market_engine_input",
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


def _number(value: Any, *, decimals: int = 0, fallback: str = "-") -> str:
    if value is None or value == "":
        return fallback
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)
    if decimals <= 0:
        return str(int(round(num)))
    return f"{num:.{decimals}f}"


def _boundary_text(boundary: Mapping[str, Any]) -> str:
    parts = []
    for key in _BOUNDARY_KEYS:
        if key in boundary:
            parts.append(f"{key}={bool(boundary.get(key))}")
    return " / ".join(parts) if parts else "boundary=unavailable"


def build_hot_cold_retention_safety_caption(payload: Mapping[str, Any] | None) -> str:
    data = _as_mapping(payload)
    boundary = _as_mapping(data.get("boundary"))
    return (
        "hot_cold_retention_safety "
        f"status={_text(data.get('status_key'), fallback='unknown')} / "
        f"severity={_text(data.get('severity_key'), fallback='unknown')} / "
        f"hot_retention_days={_number(data.get('hot_retention_days'), fallback='unknown')} / "
        f"delete_readiness={_text(data.get('delete_readiness_key'), fallback='unknown')} / "
        f"copy_verification={_text(data.get('copy_verification_key'), fallback='unknown')} / "
        f"{_boundary_text(boundary)}"
    )


def build_hot_cold_retention_safety_lines(payload: Mapping[str, Any] | None) -> tuple[str, ...]:
    data = _as_mapping(payload)
    counts = _as_mapping(data.get("counts"))
    plan = _as_mapping(data.get("plan"))
    summary_lines = tuple(str(line) for line in _as_sequence(data.get("summary_lines")))

    lines = [
        f"title={_text(data.get('title'), fallback='Hot/Cold retention safety')}",
        f"status={_text(data.get('status_key'), fallback='unknown')}",
        f"severity={_text(data.get('severity_key'), fallback='unknown')}",
        f"hot_retention_days={_number(data.get('hot_retention_days'), fallback='unknown')}",
        f"min_delete_age_hours={_number(data.get('min_delete_age_hours'), decimals=1, fallback='unknown')}",
        f"copy_verification={_text(data.get('copy_verification_key'), fallback='unknown')}",
        f"delete_readiness={_text(data.get('delete_readiness_key'), fallback='unknown')}",
        f"candidate_files={_number(counts.get('candidate_files'), fallback='0')}",
        f"candidate_gb={_number(counts.get('candidate_gb'), decimals=6, fallback='0')}",
        f"newest_candidate_age_hours={_number(counts.get('newest_candidate_age_hours'), decimals=3, fallback='unknown')}",
        f"plan_hash={_text(plan.get('plan_hash'), fallback='-')}",
        f"plan_path={_text(plan.get('plan_path'), fallback='-')}",
        f"operator_next_step={_text(data.get('operator_next_step'), fallback='-')}",
    ]
    lines.extend(f"summary={line}" for line in summary_lines)
    lines.append(build_hot_cold_retention_safety_caption(data))
    return tuple(lines)


def render_hot_cold_retention_safety_panel(payload: Mapping[str, Any] | None, *, expanded: bool = False) -> None:
    """Render a provided Hot/Cold retention safety payload. Does not scan files or execute copy/delete."""
    data = _as_mapping(payload)
    counts = _as_mapping(data.get("counts"))
    plan = _as_mapping(data.get("plan"))

    title = _text(data.get("title"), fallback="Hot/Cold retention safety")
    status = _text(data.get("status_key"), fallback="unknown")
    severity = _text(data.get("severity_key"), fallback="unknown")
    delete_readiness = _text(data.get("delete_readiness_key"), fallback="unknown")
    copy_verification = _text(data.get("copy_verification_key"), fallback="unknown")

    st.markdown(f"### {title}")
    st.caption(build_hot_cold_retention_safety_caption(data))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Retention status", status)
    c2.metric("Delete readiness", delete_readiness)
    c3.metric("Copy verification", copy_verification)
    c4.metric("Hot retention days", _number(data.get("hot_retention_days"), fallback="unknown"))

    c5, c6, c7 = st.columns(3)
    c5.metric("Candidate files", _number(counts.get("candidate_files"), fallback="0"))
    c6.metric("Candidate GB", _number(counts.get("candidate_gb"), decimals=3, fallback="0"))
    c7.metric("Newest candidate age h", _number(counts.get("newest_candidate_age_hours"), decimals=1, fallback="unknown"))

    st.caption(_text(data.get("operator_next_step"), fallback="No Hot/Cold retention safety payload is available."))
    if plan.get("plan_hash"):
        st.caption("plan_hash=" + _text(plan.get("plan_hash")))

    if expanded:
        st.json({"hot_cold_retention_safety_lines": list(build_hot_cold_retention_safety_lines(data))})
