# path: ./tools/diagnose_phase4a_prediction_system_ps_q25h_warroom_prediction_data_age_severity_operator_action_guidance.py
# desc: Read-only diagnostic for PS-Q25H WarRoom prediction data age severity and operator action guidance.

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
    WARROOM_PREDICTION_OPERATOR_ACTION_GUIDANCE_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_horizon_expiry_packet,
    latest_prediction_warroom_operator_action_guidance_packet,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
    TRUE_BOUNDARIES,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25h_warroom_prediction_data_age_severity_operator_action_guidance.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25H_WARROOM_PREDICTION_DATA_AGE_SEVERITY_OPERATOR_ACTION_GUIDANCE_2026-06-30.md"


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


def _guidance(*, age_sec: int) -> dict[str, Any]:
    model = _fake_read_model(age_sec=age_sec)
    expiry = latest_prediction_warroom_horizon_expiry_packet(model, lang="ja")
    source = {"horizon_expiry_packet": expiry, "freshness_state": model.get("freshness_state"), "age_sec": model.get("age_sec")}
    return latest_prediction_warroom_operator_action_guidance_packet(source, lang="ja")


def run_warroom_prediction_data_age_severity_operator_action_guidance_diagnostic() -> dict[str, Any]:
    fresh_guidance = _guidance(age_sec=10)
    stale_guidance = _guidance(age_sec=75)
    expired_guidance = _guidance(age_sec=1000)
    panel_packet = build_latest_prediction_warroom_display_panel_packet(read_model=_fake_read_model(age_sec=75), fragment_enabled=True, lang="ja")
    panel_text = PANEL.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if fresh_guidance.get("operator_action_guidance_version") != WARROOM_PREDICTION_OPERATOR_ACTION_GUIDANCE_VERSION:
        blockers.append("operator_action_guidance_version_required")
    if fresh_guidance.get("operator_action_severity") != "ok":
        blockers.append("fresh_guidance_ok_required")
    if stale_guidance.get("operator_action_severity") != "critical":
        blockers.append("stale_guidance_critical_required")
    if stale_guidance.get("prediction_tactical_readiness") != "tactical_predictions_not_ready":
        blockers.append("stale_tactical_not_ready_required")
    if "15s" not in stale_guidance.get("ignore_live_tactical_horizons", []):
        blockers.append("stale_ignore_15s_required")
    if stale_guidance.get("wait_for_new_prediction_artifact") is not True:
        blockers.append("stale_wait_for_new_artifact_required")
    if expired_guidance.get("operator_action_severity") != "critical":
        blockers.append("expired_guidance_critical_required")
    if panel_packet.get("operator_visible_action_guidance") is not True:
        blockers.append("panel_packet_action_guidance_visible_required")
    if panel_packet.get("operator_action_severity") != "critical":
        blockers.append("panel_packet_action_severity_critical_required")
    if panel_packet.get("prediction_tactical_readiness") != "tactical_predictions_not_ready":
        blockers.append("panel_packet_tactical_not_ready_required")
    action_text = json.dumps(stale_guidance.get("action_rows") or [], ensure_ascii=False)
    for marker in ("ignore_live_tactical_horizons", "context_only_horizons", "wait_for_new_prediction_artifact", "prioritize_current_state_nowcast", "do_not_confuse_ui_heartbeat_with_prediction_update"):
        if marker not in action_text:
            blockers.append(f"action_row_required:{marker}")
    for marker in ("WARROOM_PREDICTION_OPERATOR_ACTION_GUIDANCE_VERSION", "latest_prediction_warroom_operator_action_guidance_packet", "_render_prediction_operator_action_guidance", "prediction_tactical_readiness"):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    for marker in ("prediction_operator_action_guidance_added=true", "operator_action_severity_visible=true", "wait_for_new_prediction_artifact_visible=true", "producer_cadence_changed=false"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("read_only", "non_executing", "display_only", "operator_visible_action_guidance"):
        if fresh_guidance.get(key) is not True:
            blockers.append(f"guidance_true_required:{key}")
    for key in ("prediction_artifact_write_allowed", "view_artifact_write_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "scheduler_action_changed", "scheduler_enabled", "producer_cadence_changed", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if fresh_guidance.get(key) is not False:
            blockers.append(f"guidance_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "fresh_guidance": fresh_guidance,
        "stale_guidance": stale_guidance,
        "expired_guidance": expired_guidance,
        "panel_packet": {
            "ok": panel_packet.get("ok"),
            "operator_visible_action_guidance": panel_packet.get("operator_visible_action_guidance"),
            "operator_action_severity": panel_packet.get("operator_action_severity"),
            "prediction_tactical_readiness": panel_packet.get("prediction_tactical_readiness"),
            "wait_for_new_prediction_artifact": panel_packet.get("wait_for_new_prediction_artifact"),
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
    result = run_warroom_prediction_data_age_severity_operator_action_guidance_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
