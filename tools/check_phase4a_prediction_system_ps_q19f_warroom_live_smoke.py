# path: ./tools/check_phase4a_prediction_system_ps_q19f_warroom_live_smoke.py
# desc: PS-Q19F live smoke helper for WarRoom prediction display. Read-only by default; verifies PS-Q19E dry-run, PS-Q19C read model, and PS-Q19D display packet safety. Optional visual-confirmation flags record operator observation only.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    build_latest_prediction_warroom_display_panel_packet,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    load_latest_prediction_warroom_read_model,
)
from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import (  # noqa: E402
    DEFAULT_HOT_LATEST_ROOT_HINT,
)
from tools.run_prediction_warroom_bounded_manual_refresh_ps_q19e import (  # noqa: E402
    build_ps_q19e_non_ui_refresh_request_packet,
)

PS_Q19F_LIVE_SMOKE_VERSION = "prediction_warroom.ps_q19f_warroom_live_smoke_and_operator_visual_confirmation.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _count_prediction_rows(display_packet: Mapping[str, Any]) -> int:
    rows = display_packet.get("prediction_rows")
    return len(rows) if isinstance(rows, list) else 0


def _safety_ok(packet: Mapping[str, Any]) -> bool:
    return all(
        packet.get(key) is False
        for key in (
            "scheduler_enabled",
            "producer_enabled",
            "warroom_ui_trigger_enabled",
            "ui_triggered_runner_execution",
            "approval_or_authorization_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "would_send_to_broker",
        )
    )


def build_ps_q19f_warroom_live_smoke_packet(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    supplied_read_model: Mapping[str, Any] | None = None,
    manual_visual_confirmation: bool = False,
    observed_panel_visible: bool = False,
    observed_prediction_rows: bool = False,
    observed_market_snapshot: bool = False,
    observed_safety_flags: bool = False,
) -> dict[str, Any]:
    """Return PS-Q19F live-smoke packet.

    This is read-only by default. It does not execute a manual refresh; it only
    checks the PS-Q19E dry-run/no-write path and verifies that the PS-Q19C read
    model can be rendered through the PS-Q19D display packet contract.
    """
    dry_run = build_ps_q19e_non_ui_refresh_request_packet(
        hot_latest_root_hint=str(hot_latest_root_hint),
        execute_manual_refresh=False,
        ack="",
        request_scheduled_refresh=False,
    )
    read_model = dict(
        supplied_read_model
        or load_latest_prediction_warroom_read_model(hot_latest_root_hint=str(hot_latest_root_hint))
    )
    display_packet = build_latest_prediction_warroom_display_panel_packet(
        read_model=read_model,
        fragment_enabled=False,
    )
    prediction_row_count = _count_prediction_rows(display_packet)
    visual_confirmation_complete = bool(
        manual_visual_confirmation
        and observed_panel_visible
        and observed_prediction_rows
        and observed_market_snapshot
        and observed_safety_flags
    )
    failures: list[str] = []
    if dry_run.get("request_state") != "dry_run_no_write":
        failures.append("ps_q19e_dry_run_not_no_write")
    if dry_run.get("latest_prediction_artifact_written") is not False:
        failures.append("ps_q19e_dry_run_wrote_latest_prediction_artifact")
    if dry_run.get("status_artifact_written") is not False:
        failures.append("ps_q19e_dry_run_wrote_status_artifact")
    if read_model.get("ok") is not True:
        failures.append("ps_q19c_read_model_not_ready")
    if prediction_row_count <= 0:
        failures.append("ps_q19d_prediction_rows_missing")
    if display_packet.get("display_panel_version") != "prediction_warroom.latest_prediction_warroom_display_panel.ps_q19d.v1":
        failures.append("ps_q19d_display_panel_version_mismatch")
    if display_packet.get("view_artifact_write_allowed") is not False:
        failures.append("view_artifact_write_allowed_not_false")
    if display_packet.get("autotrade_trigger_allowed") is not False:
        failures.append("autotrade_trigger_allowed_not_false")
    if display_packet.get("broker_private_api_allowed") is not False:
        failures.append("broker_private_api_allowed_not_false")
    if not _safety_ok(dry_run):
        failures.append("ps_q19e_dry_run_safety_boundary_not_closed")
    ok = not failures
    packet: dict[str, Any] = {
        "ok": ok,
        "ps_q19f_version": PS_Q19F_LIVE_SMOKE_VERSION,
        "phase": "ps_q19f_warroom_live_smoke_and_operator_visual_confirmation",
        "hot_latest_root_hint": str(hot_latest_root_hint),
        "ps_q19e_dry_run": {
            "ok": dry_run.get("ok") is True,
            "request_state": dry_run.get("request_state"),
            "latest_prediction_artifact_written": dry_run.get("latest_prediction_artifact_written"),
            "status_artifact_written": dry_run.get("status_artifact_written"),
            "scheduler_enabled": dry_run.get("scheduler_enabled"),
            "producer_enabled": dry_run.get("producer_enabled"),
            "autotrade_trigger_allowed": dry_run.get("autotrade_trigger_allowed"),
            "broker_private_api_allowed": dry_run.get("broker_private_api_allowed"),
            "would_send_to_broker": dry_run.get("would_send_to_broker"),
        },
        "read_model": {
            "ok": read_model.get("ok") is True,
            "version": read_model.get("read_model_version"),
            "source_artifact_path": read_model.get("source_artifact_path"),
            "generated_at": read_model.get("generated_at"),
            "age_sec": read_model.get("age_sec"),
            "freshness_state": read_model.get("freshness_state"),
            "warning_reason_codes": list(read_model.get("warning_reason_codes") or []),
            "blocker_reason_codes": list(read_model.get("blocker_reason_codes") or []),
            "record_count": read_model.get("record_count"),
            "artifact_size_bytes": read_model.get("artifact_size_bytes"),
            "artifact_max_bytes": read_model.get("artifact_max_bytes"),
            "payload_load_ok": read_model.get("payload_load_ok"),
            "payload_load_blocked_reason": read_model.get("payload_load_blocked_reason"),
        },
        "display_packet": {
            "ok": display_packet.get("ok") is True,
            "version": display_packet.get("display_panel_version"),
            "state": display_packet.get("display_panel_state"),
            "prediction_row_count": prediction_row_count,
            "freshness_state": display_packet.get("freshness_state"),
            "warning_reason_codes": list(display_packet.get("warning_reason_codes") or []),
            "blocker_reason_codes": list(display_packet.get("blocker_reason_codes") or []),
            "view_artifact_write_allowed": display_packet.get("view_artifact_write_allowed"),
            "autotrade_trigger_allowed": display_packet.get("autotrade_trigger_allowed"),
            "broker_private_api_allowed": display_packet.get("broker_private_api_allowed"),
            "would_send_to_broker": display_packet.get("would_send_to_broker"),
        },
        "operator_visual_confirmation": {
            "manual_visual_confirmation_requested": bool(manual_visual_confirmation),
            "observed_panel_visible": bool(observed_panel_visible),
            "observed_prediction_rows": bool(observed_prediction_rows),
            "observed_market_snapshot": bool(observed_market_snapshot),
            "observed_safety_flags": bool(observed_safety_flags),
            "visual_confirmation_complete": visual_confirmation_complete,
        },
        "failures": failures,
        "runtime_artifact_write_performed_by_smoke": False,
        "status_artifact_write_performed_by_smoke": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "ui_triggered_runner_execution": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }
    return packet


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19F WarRoom live smoke / visual confirmation helper")
    parser.add_argument("--root", default=DEFAULT_HOT_LATEST_ROOT_HINT, help="Hot latest root. Default: D:/btc_ts_hot")
    parser.add_argument("--manual-visual-confirmation", action="store_true", help="Record operator visual confirmation fields.")
    parser.add_argument("--observed-panel-visible", action="store_true")
    parser.add_argument("--observed-prediction-rows", action="store_true")
    parser.add_argument("--observed-market-snapshot", action="store_true")
    parser.add_argument("--observed-safety-flags", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    packet = build_ps_q19f_warroom_live_smoke_packet(
        hot_latest_root_hint=str(args.root),
        manual_visual_confirmation=bool(args.manual_visual_confirmation),
        observed_panel_visible=bool(args.observed_panel_visible),
        observed_prediction_rows=bool(args.observed_prediction_rows),
        observed_market_snapshot=bool(args.observed_market_snapshot),
        observed_safety_flags=bool(args.observed_safety_flags),
    )
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
