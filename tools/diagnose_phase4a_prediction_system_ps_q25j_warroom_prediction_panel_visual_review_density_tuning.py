# path: ./tools/diagnose_phase4a_prediction_system_ps_q25j_warroom_prediction_panel_visual_review_density_tuning.py
# desc: Read-only diagnostic for PS-Q25J WarRoom prediction panel visual review and density tuning.

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
    WARROOM_PREDICTION_DENSITY_TUNING_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_density_tuning_packet,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
    TRUE_BOUNDARIES,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25j_warroom_prediction_panel_visual_review_density_tuning.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25J_WARROOM_PREDICTION_PANEL_VISUAL_REVIEW_DENSITY_TUNING_2026-06-30.md"


def _fake_read_model(*, age_sec: int) -> dict[str, Any]:
    selected = {"15": [{"family": "trend_bias", "primary_label": "neutral_bias", "confidence": "low", "score": 0.3, "usable": True, "warnings": [], "drivers": [], "read_only": True, "non_executing": True, "would_send_to_broker": False, "would_write_runtime_artifact": False, "would_append_ledger": False}], "60": [], "300": [], "900": []}
    model = {"ok": True, "read_model_version": LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION, "source_artifact_mode": "distributed", "source_artifact_relative_path": "prediction/latest_manifest.json", "distributed_reader_ready": True, "distributed_stale_vs_legacy": False, "legacy_fallback_ready": True, "generated_at": "2026-06-29T17:40:20Z", "age_sec": age_sec, "freshness_state": "stale", "warning_reason_codes": [], "blocker_reason_codes": [], "record_count": 1, "selected_horizon_sec": [15, 60, 300, 900], "selected_records_by_horizon": selected, "market_snapshot": {}, "safety_flags": {"records_all_safe": True}, "read_only": True, "non_executing": True, "display_only": True}
    model.update({key: True for key in TRUE_BOUNDARIES})
    model.update({key: False for key in FALSE_BOUNDARIES})
    for key in ("view_artifact_write_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed", "would_send_to_broker"):
        model[key] = False
    return model


def run_warroom_prediction_panel_visual_review_density_tuning_diagnostic() -> dict[str, Any]:
    packet = build_latest_prediction_warroom_display_panel_packet(read_model=_fake_read_model(age_sec=75), fragment_enabled=True, lang="ja")
    density = packet.get("density_tuning_packet") if isinstance(packet.get("density_tuning_packet"), dict) else {}
    standalone = latest_prediction_warroom_density_tuning_packet(packet, lang="ja")
    panel_text = PANEL.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if density.get("density_tuning_version") != WARROOM_PREDICTION_DENSITY_TUNING_VERSION:
        blockers.append("density_tuning_version_required")
    if packet.get("operator_visible_density_tuning") is not True or packet.get("density_tuning_rendered") is not True:
        blockers.append("packet_density_tuning_visible_required")
    for key in ("compact_header_kept_top", "detail_checks_folded_default", "detail_checks_still_available", "reading_guide_folded_default", "metrics_still_visible", "prediction_rows_still_visible", "layout_only_change"):
        if density.get(key) is not True:
            blockers.append(f"density_true_required:{key}")
    if density.get("detail_sections_folded_count") != 5:
        blockers.append("five_detail_sections_folded_required")
    for marker in ("WARROOM_PREDICTION_DENSITY_TUNING_VERSION", "latest_prediction_warroom_density_tuning_packet", "_render_prediction_detail_checks_foldout", "density_tuning_rendered", "detail_checks_folded_default=True"):
        if marker not in panel_text:
            blockers.append(f"panel_marker_required:{marker}")
    render_body_start = panel_text.find("def _render_panel_body")
    render_body_end = panel_text.find("\ndef render_latest_prediction_warroom_display_panel", render_body_start)
    render_body_text = panel_text[render_body_start:render_body_end] if render_body_start >= 0 and render_body_end > render_body_start else ""
    expected_order = ["_render_prediction_compact_operator_header", "_render_prediction_detail_checks_foldout", "with st.expander(_t(lang, \"reading_title\"), expanded=False)"]
    positions = [render_body_text.find(item) for item in expected_order]
    if any(item < 0 for item in positions) or positions != sorted(positions):
        blockers.append("render_density_order_required")
    for direct_call in ("_render_refresh_status_strip(packet, lang=lang)", "_render_prediction_data_freshness_badge(packet, lang=lang)", "_render_prediction_horizon_expiry(packet, lang=lang)", "_render_prediction_operator_action_guidance(packet, lang=lang)", "_render_prediction_update_visibility_strip(packet, lang=lang)"):
        if direct_call in render_body_text:
            blockers.append(f"direct_detail_call_not_folded:{direct_call}")
    for marker in ("prediction_density_tuning_added=true", "detail_checks_folded_default=true", "detail_checks_still_available=true", "layout_only_change=true"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("prediction_artifact_write_allowed", "view_artifact_write_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "scheduler_action_changed", "scheduler_enabled", "producer_cadence_changed", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if density.get(key) is not False:
            blockers.append(f"density_false_required:{key}")
    return {"ok": True, "diagnostic_version": DIAGNOSTIC_VERSION, "ready": not blockers, "blockers": blockers, "density_tuning": density, "standalone_density_tuning": standalone, "panel_packet": {"ok": packet.get("ok"), "operator_visible_density_tuning": packet.get("operator_visible_density_tuning"), "density_tuning_rendered": packet.get("density_tuning_rendered"), "operator_visible_compact_layout": packet.get("operator_visible_compact_layout")}, "safety": {"read_only_diagnostic": True, "warroom_display_only": True, "layout_only_change": True, "producer_cadence_changed": False, "runtime_artifact_write_allowed": False, "status_artifact_write_allowed": False, "prediction_artifact_write_allowed": False, "view_artifact_write_allowed": False, "scheduler_action_changed": False, "scheduler_enabled": False, "autotrade_trigger_allowed": False, "broker_private_api_allowed": False, "ledger_append_allowed": False, "mode_apply_allowed": False, "parameter_apply_allowed": False, "would_send_to_broker": False}}


def main() -> int:
    result = run_warroom_prediction_panel_visual_review_density_tuning_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
