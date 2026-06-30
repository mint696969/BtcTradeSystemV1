# path: ./tools/diagnose_phase4a_prediction_system_ps_q25i_warroom_prediction_panel_section_order_compact_layout_polish.py
# desc: Read-only diagnostic for PS-Q25I WarRoom prediction panel section order and compact layout polish.

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_COMPACT_LAYOUT_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_compact_layout_packet,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
    TRUE_BOUNDARIES,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25i_warroom_prediction_panel_section_order_compact_layout_polish.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25I_WARROOM_PREDICTION_PANEL_SECTION_ORDER_COMPACT_LAYOUT_POLISH_2026-06-30.md"


def _fake_read_model(*, age_sec: int) -> dict[str, Any]:
    selected = {
        "15": [{"family": "trend_bias", "primary_label": "neutral_bias", "confidence": "low", "score": 0.3, "usable": True, "warnings": [], "drivers": [], "read_only": True, "non_executing": True, "would_send_to_broker": False, "would_write_runtime_artifact": False, "would_append_ledger": False}],
        "60": [{"family": "market_regime", "primary_label": "range_candidate", "confidence": "medium", "score": 0.5, "usable": True, "warnings": [], "drivers": [], "read_only": True, "non_executing": True, "would_send_to_broker": False, "would_write_runtime_artifact": False, "would_append_ledger": False}],
        "300": [],
        "900": [],
    }
    model = {
        "ok": True,
        "read_model_version": LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
        "source_artifact_mode": "distributed",
        "source_artifact_relative_path": "prediction/latest_manifest.json",
        "distributed_reader_ready": True,
        "distributed_stale_vs_legacy": False,
        "legacy_fallback_ready": True,
        "generated_at": "2026-06-29T17:40:20Z",
        "age_sec": age_sec,
        "freshness_state": "fresh" if age_sec <= 60 else "stale",
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "record_count": 2,
        "selected_horizon_sec": [15, 60, 300, 900],
        "selected_records_by_horizon": selected,
        "market_snapshot": {},
        "safety_flags": {"records_all_safe": True},
        "read_only": True,
        "non_executing": True,
        "display_only": True,
    }
    model.update({key: True for key in TRUE_BOUNDARIES})
    model.update({key: False for key in FALSE_BOUNDARIES})
    for key in ("view_artifact_write_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed", "would_send_to_broker"):
        model[key] = False
    return model


def run_warroom_prediction_panel_section_order_compact_layout_polish_diagnostic() -> dict[str, Any]:
    packet = build_latest_prediction_warroom_display_panel_packet(read_model=_fake_read_model(age_sec=75), fragment_enabled=True, lang="ja")
    compact = packet.get("compact_layout_packet") if isinstance(packet.get("compact_layout_packet"), dict) else {}
    standalone = latest_prediction_warroom_compact_layout_packet(packet, lang="ja")
    rows = compact.get("compact_layout_rows") or []
    panel_text = PANEL.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if compact.get("compact_layout_version") != WARROOM_PREDICTION_COMPACT_LAYOUT_VERSION:
        blockers.append("compact_layout_version_required")
    if packet.get("operator_visible_compact_layout") is not True or packet.get("compact_layout_rendered") is not True:
        blockers.append("packet_compact_layout_visible_required")
    if compact.get("compact_layout_top_priority") != "operator_action_guidance_first":
        blockers.append("compact_layout_top_priority_required")
    if compact.get("compact_layout_detail_tables_still_visible") is not True:
        blockers.append("detail_tables_still_visible_required")
    if len(rows) != 5:
        blockers.append("five_compact_layout_rows_required")
    row_text = json.dumps(rows, ensure_ascii=False)
    for marker in ("operator_action", "prediction_data_age", "horizon_expiry", "generated_at", "panel_heartbeat"):
        if marker not in row_text:
            blockers.append(f"compact_row_required:{marker}")
    if standalone.get("layout_only_change") is not True:
        blockers.append("layout_only_change_required")
    for marker in ("WARROOM_PREDICTION_COMPACT_LAYOUT_VERSION", "latest_prediction_warroom_compact_layout_packet", "_render_prediction_compact_operator_header", "compact_layout_rendered"):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    render_body_start = panel_text.find("def _render_panel_body")
    render_body_end = panel_text.find("\ndef render_latest_prediction_warroom_display_panel", render_body_start)
    render_body_text = panel_text[render_body_start:render_body_end] if render_body_start >= 0 and render_body_end > render_body_start else ""
    expected_order = ["_render_prediction_compact_operator_header", "_render_refresh_status_strip", "_render_prediction_data_freshness_badge", "_render_prediction_horizon_expiry", "_render_prediction_operator_action_guidance"]
    positions = [render_body_text.find(item) for item in expected_order]
    if any(item < 0 for item in positions) or positions != sorted(positions):
        blockers.append("render_section_order_required")
    for marker in ("prediction_compact_layout_added=true", "compact_layout_top_priority=operator_action_guidance_first", "compact_layout_detail_tables_still_visible=true", "layout_only_change=true"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("read_only", "non_executing", "display_only", "layout_only_change", "operator_visible_compact_layout"):
        if compact.get(key) is not True:
            blockers.append(f"compact_true_required:{key}")
    for key in ("prediction_artifact_write_allowed", "view_artifact_write_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "scheduler_action_changed", "scheduler_enabled", "producer_cadence_changed", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if compact.get(key) is not False:
            blockers.append(f"compact_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "compact_layout": compact,
        "panel_packet": {
            "ok": packet.get("ok"),
            "operator_visible_compact_layout": packet.get("operator_visible_compact_layout"),
            "compact_layout_rendered": packet.get("compact_layout_rendered"),
            "operator_action_severity": packet.get("operator_action_severity"),
            "prediction_tactical_readiness": packet.get("prediction_tactical_readiness"),
        },
        "safety": {
            "read_only_diagnostic": True,
            "warroom_display_only": True,
            "layout_only_change": True,
            "producer_cadence_changed": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_action_changed": False,
            "scheduler_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_warroom_prediction_panel_section_order_compact_layout_polish_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
