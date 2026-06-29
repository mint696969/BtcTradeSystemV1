# path: ./tools/diagnose_phase4a_prediction_system_ps_q25a_warroom_prediction_refresh_visibility.py
# desc: Read-only diagnostic for PS-Q25A WarRoom prediction refresh visibility packet fields.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_VERSION,
    WARROOM_PREDICTION_UPDATE_VISIBILITY_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_update_visibility_rows,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25a_warroom_prediction_refresh_visibility.v1"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _fake_read_model() -> dict[str, Any]:
    return {
        "ok": True,
        "read_model_version": LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "source_artifact_mode": "distributed",
        "source_artifact_relative_path": "prediction/latest_manifest.json",
        "distributed_reader_ready": True,
        "distributed_stale_vs_legacy": False,
        "legacy_fallback_ready": True,
        "generated_at": "2026-06-29T17:40:20Z",
        "age_sec": 12,
        "freshness_state": "fresh",
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "record_count": 110,
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
                    "drivers": ["range_boundary_visible"],
                }
            ]
        },
        "market_snapshot": {"market_uid": "FX_BTC_JPY", "freshness": "LIVE"},
        "safety_flags": {"records_all_safe": True},
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def run_warroom_prediction_refresh_visibility_diagnostic() -> dict[str, Any]:
    panel_text = PANEL.read_text(encoding="utf-8")
    warroom_text = WARROOM_PAGE.read_text(encoding="utf-8")
    packet = build_latest_prediction_warroom_display_panel_packet(read_model=_fake_read_model(), fragment_enabled=True, lang="ja")
    rows = latest_prediction_warroom_update_visibility_rows(packet, lang="ja")
    blockers: list[str] = []
    if packet.get("display_panel_version") != LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_VERSION:
        blockers.append("display_panel_version_required")
    if packet.get("prediction_update_visibility_version") != WARROOM_PREDICTION_UPDATE_VISIBILITY_VERSION:
        blockers.append("prediction_update_visibility_version_required")
    if packet.get("operator_visible_prediction_update_visibility") is not True:
        blockers.append("operator_visible_prediction_update_visibility_required")
    if packet.get("prediction_update_visibility_rendered") is not True:
        blockers.append("prediction_update_visibility_rendered_required")
    if packet.get("prediction_data_generated_at_utc") != "2026-06-29T17:40:20Z":
        blockers.append("prediction_data_generated_at_utc_required")
    if "JST" not in str(packet.get("prediction_data_generated_at_jst") or ""):
        blockers.append("prediction_data_generated_at_jst_required")
    if "JST" not in str(packet.get("refresh_heartbeat_jst") or ""):
        blockers.append("refresh_heartbeat_jst_required")
    if "prediction_data_generated_at_changes_only_when_producer_writes_new_artifact" not in str(packet.get("prediction_update_visibility_note") or ""):
        blockers.append("visibility_note_required")
    row_text = json.dumps(rows, ensure_ascii=False)
    for marker in ("予測データ生成 UTC", "予測データ生成 JST", "パネル heartbeat JST", "UI更新間隔", "自動更新経路", "読込元"):
        if marker not in row_text:
            blockers.append(f"visibility_row_missing:{marker}")
    if "def _render_panel_body(*, fragment_enabled: bool = True)" not in panel_text:
        blockers.append("render_panel_body_fragment_argument_required")
    if "fragment_enabled=bool(fragment_enabled)" not in panel_text:
        blockers.append("packet_fragment_flag_must_use_render_argument")
    if "live_shell.supports_streamlit_fragment()" in panel_text.split("def _render_panel_body", 1)[-1].split("def render_latest_prediction_warroom_display_panel", 1)[0]:
        blockers.append("render_panel_body_must_not_report_support_as_enabled")
    if "render_latest_prediction_warroom_display_panel(fragment_enabled=prediction_fragment_enabled)" not in warroom_text:
        blockers.append("warroom_page_prediction_panel_mount_required")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "ready": not blockers,
        "blockers": blockers,
        "packet": {
            "prediction_update_visibility_version": packet.get("prediction_update_visibility_version"),
            "operator_visible_prediction_update_visibility": packet.get("operator_visible_prediction_update_visibility"),
            "prediction_update_visibility_rendered": packet.get("prediction_update_visibility_rendered"),
            "prediction_data_generated_at_utc": packet.get("prediction_data_generated_at_utc"),
            "prediction_data_generated_at_jst": packet.get("prediction_data_generated_at_jst"),
            "refresh_heartbeat_utc": packet.get("refresh_heartbeat_utc"),
            "refresh_heartbeat_jst": packet.get("refresh_heartbeat_jst"),
            "warroom_prediction_display_auto_refresh_enabled": packet.get("warroom_prediction_display_auto_refresh_enabled"),
            "fragment_enabled": packet.get("fragment_enabled"),
            "refresh_interval_sec": packet.get("refresh_interval_sec"),
            "prediction_update_visibility_note": packet.get("prediction_update_visibility_note"),
        },
        "safety": {
            "read_only_diagnostic": True,
            "warroom_display_only": True,
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
    result = run_warroom_prediction_refresh_visibility_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
