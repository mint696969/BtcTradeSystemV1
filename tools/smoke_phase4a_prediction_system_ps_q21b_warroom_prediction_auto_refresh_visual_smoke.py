# path: ./tools/smoke_phase4a_prediction_system_ps_q21b_warroom_prediction_auto_refresh_visual_smoke.py
# desc: PS-Q21B minimal smoke helper for WarRoom prediction auto-refresh heartbeat visibility. No UI automation, no writes, no runtime enablement.

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_DISPLAY_AUTO_REFRESH_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
)

SMOKE_VERSION = "prediction_warroom.warroom_prediction_auto_refresh_visual_smoke.ps_q21b.v1"
PANEL_PATH = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
WARROOM_PAGE_PATH = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
OPERATOR_UI_LAUNCHER = REPO_ROOT / "tools/run_operator_ui_sr_fx_dhot.ps1"


def _fixture_read_model() -> dict[str, Any]:
    return {
        "ok": True,
        "read_model_version": "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1",
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "generated_at": "2026-06-26T01:18:12Z",
        "age_sec": 5,
        "freshness_state": "fresh",
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "record_count": 1,
        "selected_horizon_sec": [15],
        "selected_records_by_horizon": {
            "15": [
                {
                    "family": "market_regime",
                    "primary_label": "range_candidate",
                    "confidence": "medium",
                    "score": 0.52,
                    "usable": True,
                    "warnings": [],
                    "drivers": [],
                }
            ]
        },
        "market_snapshot": {
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "freshness": "LIVE",
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "best_bid": 9631209.0,
            "best_ask": 9632797.0,
            "spread": 1588.0,
        },
        "safety_flags": {"records_all_safe": True},
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def _source_markers() -> dict[str, bool]:
    panel = PANEL_PATH.read_text(encoding="utf-8")
    page = WARROOM_PAGE_PATH.read_text(encoding="utf-8")
    launcher = OPERATOR_UI_LAUNCHER.read_text(encoding="utf-8") if OPERATOR_UI_LAUNCHER.exists() else ""
    return {
        "panel_declares_ps_q21a_auto_refresh_version": "WARROOM_PREDICTION_DISPLAY_AUTO_REFRESH_VERSION" in panel,
        "panel_footer_shows_auto_refresh": "auto_refresh={packet.get('warroom_prediction_display_auto_refresh_enabled')}" in panel,
        "panel_footer_shows_refresh_heartbeat_utc": "refresh_heartbeat_utc={packet.get('refresh_heartbeat_utc')}" in panel,
        "warroom_page_uses_prediction_specific_fragment_flag": "prediction_fragment_enabled = _prediction_warroom_display_fragment_enabled(page_fragment_enabled=fragment_enabled)" in page,
        "warroom_page_prediction_display_uses_prediction_fragment_flag": "render_latest_prediction_warroom_display_panel(fragment_enabled=prediction_fragment_enabled)" in page,
        "warroom_page_quick_status_uses_prediction_fragment_flag": "_render_prediction_warroom_latest_prediction_observation_cleanup_summary_section(fragment_enabled=prediction_fragment_enabled)" in page,
        "operator_ui_launcher_exists": OPERATOR_UI_LAUNCHER.exists(),
        "operator_ui_launcher_streamlit_app": all(
            token in launcher
            for token in (
                "streamlit",
                "run",
                "btcts_next\\src\\btcts\\apps\\operator_ui\\app.py",
            )
        ),
    }


def run_smoke(*, sleep_sec: float = 1.05) -> dict[str, Any]:
    first = build_latest_prediction_warroom_display_panel_packet(
        read_model=_fixture_read_model(),
        fragment_enabled=True,
        lang="ja",
    )
    time.sleep(max(0.0, float(sleep_sec)))
    second = build_latest_prediction_warroom_display_panel_packet(
        read_model=_fixture_read_model(),
        fragment_enabled=True,
        lang="ja",
    )
    markers = _source_markers()
    first_heartbeat = str(first.get("refresh_heartbeat_utc") or "")
    second_heartbeat = str(second.get("refresh_heartbeat_utc") or "")
    unsafe_flags = [
        key
        for key in (
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "prediction_artifact_write_allowed",
            "view_artifact_write_allowed",
            "scheduler_enabled",
            "producer_enabled",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
            "would_send_to_broker",
        )
        if first.get(key) is not False or second.get(key) is not False
    ]
    failures: list[str] = []
    if first.get("auto_refresh_version") != WARROOM_PREDICTION_DISPLAY_AUTO_REFRESH_VERSION:
        failures.append("auto_refresh_version_mismatch")
    if first.get("warroom_prediction_display_auto_refresh_enabled") is not True:
        failures.append("first_packet_auto_refresh_not_enabled")
    if second.get("warroom_prediction_display_auto_refresh_enabled") is not True:
        failures.append("second_packet_auto_refresh_not_enabled")
    if first.get("refresh_interval_sec") != 5 or second.get("refresh_interval_sec") != 5:
        failures.append("refresh_interval_not_5_sec")
    if not first_heartbeat.endswith("Z") or not second_heartbeat.endswith("Z"):
        failures.append("heartbeat_not_utc_z")
    if first_heartbeat == second_heartbeat:
        failures.append("heartbeat_did_not_change_between_packets")
    if unsafe_flags:
        failures.append("unsafe_flag_true_or_missing_false")
    missing_markers = [key for key, value in markers.items() if value is not True]
    if missing_markers:
        failures.append("source_marker_missing")
    ok = not failures
    return {
        "ok": ok,
        "smoke_version": SMOKE_VERSION,
        "smoke_state": "warroom_prediction_auto_refresh_smoke_ready" if ok else "warroom_prediction_auto_refresh_smoke_blocked",
        "non_ui_packet_heartbeat_changed": first_heartbeat != second_heartbeat,
        "first_refresh_heartbeat_utc": first_heartbeat,
        "second_refresh_heartbeat_utc": second_heartbeat,
        "refresh_interval_sec": second.get("refresh_interval_sec"),
        "refresh_target": second.get("refresh_target"),
        "warroom_prediction_display_auto_refresh_enabled": second.get("warroom_prediction_display_auto_refresh_enabled") is True,
        "operator_visible_refresh_heartbeat": second.get("operator_visible_refresh_heartbeat") is True,
        "broad_page_reload_disabled": second.get("broad_page_reload_disabled") is True,
        "source_markers": markers,
        "manual_ui_smoke_required": True,
        "manual_ui_smoke_command": ".\\tools\\run_operator_ui_sr_fx_dhot.ps1 -Port 501",
        "manual_ui_smoke_expected_path": "Open the Operator UI, select the WarRoom tab, expand PS-Q19D realtime prediction display, and confirm auto_refresh=True plus refresh_heartbeat_utc changes roughly every 5 seconds.",
        "runtime_enablement_allowed": False,
        "loader_binding_runtime_allowed": False,
        "component_runtime_binding_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "unsafe_flags": unsafe_flags,
        "missing_markers": missing_markers,
        "failures": failures,
    }


def main() -> int:
    result = run_smoke()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
