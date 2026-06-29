# path: ./tools/diagnose_phase4a_prediction_system_ps_q25g_warroom_prediction_artifact_horizon_freshness_expiry_visibility.py
# desc: Read-only diagnostic for PS-Q25G WarRoom prediction artifact horizon freshness/expiry visibility.

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
    WARROOM_PREDICTION_HORIZON_EXPIRY_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_horizon_expiry_packet,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
    TRUE_BOUNDARIES,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25g_warroom_prediction_artifact_horizon_freshness_expiry_visibility.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25G_WARROOM_PREDICTION_ARTIFACT_HORIZON_FRESHNESS_EXPIRY_VISIBILITY_2026-06-30.md"


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
    model["view_artifact_write_allowed"] = False
    model["runtime_artifact_write_allowed"] = False
    model["status_artifact_write_allowed"] = False
    model["prediction_artifact_write_allowed"] = False
    model["autotrade_trigger_allowed"] = False
    model["broker_private_api_allowed"] = False
    model["would_send_to_broker"] = False
    return model


def run_warroom_prediction_artifact_horizon_freshness_expiry_visibility_diagnostic() -> dict[str, Any]:
    fresh_model = _fake_read_model(age_sec=10)
    stale_model = _fake_read_model(age_sec=75)
    expired_model = _fake_read_model(age_sec=1000)
    fresh_expiry = latest_prediction_warroom_horizon_expiry_packet(fresh_model, lang="ja")
    stale_expiry = latest_prediction_warroom_horizon_expiry_packet(stale_model, lang="ja")
    expired_expiry = latest_prediction_warroom_horizon_expiry_packet(expired_model, lang="ja")
    panel_packet = build_latest_prediction_warroom_display_panel_packet(read_model=stale_model, fragment_enabled=True, lang="ja")
    panel_text = PANEL.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if fresh_expiry.get("horizon_expiry_version") != WARROOM_PREDICTION_HORIZON_EXPIRY_VERSION:
        blockers.append("horizon_expiry_version_required")
    if fresh_expiry.get("overall_horizon_expiry_state") != "all_selected_horizons_within_ttl":
        blockers.append("fresh_all_horizons_within_ttl_required")
    if stale_expiry.get("short_horizon_expired_or_stale") is not True:
        blockers.append("stale_short_horizon_flag_required")
    if expired_expiry.get("overall_horizon_expiry_state") not in {"short_horizon_expired_or_stale", "some_horizons_expired"}:
        blockers.append("expired_overall_state_required")
    rows = stale_expiry.get("horizon_expiry_rows") or []
    if len(rows) != 4:
        blockers.append("four_horizon_expiry_rows_required")
    row_text = json.dumps(rows, ensure_ascii=False)
    for marker in ("15s", "60s", "300s", "900s", "expired_by_sec", "time_to_expiry_sec"):
        if marker not in row_text:
            blockers.append(f"horizon_expiry_row_marker_required:{marker}")
    if panel_packet.get("operator_visible_horizon_expiry") is not True:
        blockers.append("panel_packet_operator_visible_horizon_expiry_required")
    if panel_packet.get("horizon_expiry_rendered") is not True:
        blockers.append("panel_packet_horizon_expiry_rendered_required")
    if panel_packet.get("short_horizon_expired_or_stale") is not True:
        blockers.append("panel_packet_short_horizon_expired_or_stale_required")
    for marker in ("WARROOM_PREDICTION_HORIZON_EXPIRY_VERSION", "latest_prediction_warroom_horizon_expiry_packet", "_render_prediction_horizon_expiry", "overall_horizon_expiry_state"):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in ("prediction_horizon_expiry_visibility_added=true", "horizon_expiry_rows_visible=true", "short_horizon_expired_or_stale_visible=true", "producer_cadence_changed=false"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("read_only", "non_executing", "display_only", "operator_visible_horizon_expiry"):
        if fresh_expiry.get(key) is not True:
            blockers.append(f"expiry_true_required:{key}")
    for key in ("prediction_artifact_write_allowed", "view_artifact_write_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "scheduler_action_changed", "scheduler_enabled", "producer_cadence_changed", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if fresh_expiry.get(key) is not False:
            blockers.append(f"expiry_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "fresh_expiry": fresh_expiry,
        "stale_expiry": stale_expiry,
        "expired_expiry": expired_expiry,
        "panel_packet": {
            "ok": panel_packet.get("ok"),
            "operator_visible_horizon_expiry": panel_packet.get("operator_visible_horizon_expiry"),
            "overall_horizon_expiry_state": panel_packet.get("overall_horizon_expiry_state"),
            "short_horizon_expired_or_stale": panel_packet.get("short_horizon_expired_or_stale"),
            "prediction_row_count": panel_packet.get("prediction_row_count"),
        },
        "safety": {
            "read_only_diagnostic": True,
            "warroom_display_only": True,
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
    result = run_warroom_prediction_artifact_horizon_freshness_expiry_visibility_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
