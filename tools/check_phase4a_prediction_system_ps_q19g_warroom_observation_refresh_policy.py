# path: ./tools/check_phase4a_prediction_system_ps_q19g_warroom_observation_refresh_policy.py
# desc: PS-Q19G read-only observation close / refresh policy decision helper. Verifies PS-Q19F live smoke, records D-hot observation readiness, and declares manual-refresh-first policy; does not execute refresh, scheduler, AutoTrade, broker, parameter, ledger, or artifact writes.

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

from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import (  # noqa: E402
    DEFAULT_HOT_LATEST_ROOT_HINT,
)
from tools.check_phase4a_prediction_system_ps_q19f_warroom_live_smoke import (  # noqa: E402
    build_ps_q19f_warroom_live_smoke_packet,
)
from tools.run_prediction_warroom_bounded_manual_refresh_ps_q19e import (  # noqa: E402
    PS_Q19E_MANUAL_REFRESH_ACK,
)

PS_Q19G_REFRESH_POLICY_VERSION = "prediction_warroom.ps_q19g_observation_close_and_refresh_policy_decision.v1"
NEXT_OPERATIONAL_STEP = "PS-Q19H_OPERATOR_ACK_BOUNDED_MANUAL_REFRESH_AND_WARROOM_VISUAL_RESMOKE"


def _norm_path(value: Any) -> str:
    return str(value or "").replace("\\", "/")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _manual_refresh_command(root: str) -> list[str]:
    return [
        "python",
        ".\\tools\\run_prediction_warroom_bounded_manual_refresh_ps_q19e.py",
        "--root",
        str(root),
        "--execute-manual-refresh",
        "--ack",
        PS_Q19E_MANUAL_REFRESH_ACK,
    ]


def _resmoke_command(root: str) -> list[str]:
    return [
        "python",
        ".\\tools\\check_phase4a_prediction_system_ps_q19f_warroom_live_smoke.py",
        "--root",
        str(root),
        "--manual-visual-confirmation",
        "--observed-panel-visible",
        "--observed-prediction-rows",
        "--observed-market-snapshot",
        "--observed-safety-flags",
    ]


def build_ps_q19g_warroom_observation_refresh_policy_packet(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    supplied_smoke_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return PS-Q19G observation close / refresh policy decision packet.

    This helper is read-only. It does not run manual refresh and does not enable a
    scheduler. It decides whether the current WarRoom observation lane is wired to
    D-hot and what the next safe refresh action should be.
    """
    smoke = dict(supplied_smoke_packet or build_ps_q19f_warroom_live_smoke_packet(hot_latest_root_hint=str(hot_latest_root_hint)))
    read_model = _as_mapping(smoke.get("read_model"))
    display = _as_mapping(smoke.get("display_packet"))
    source_path = _norm_path(read_model.get("source_artifact_path"))
    root = _norm_path(hot_latest_root_hint).rstrip("/")
    expected_suffix = f"{root}/prediction/latest_prediction_system_result.json"
    source_is_hot_root = source_path.endswith(expected_suffix)
    prediction_row_count = int(display.get("prediction_row_count") or 0)
    freshness_state = str(read_model.get("freshness_state") or display.get("freshness_state") or "unknown")
    smoke_ok = smoke.get("ok") is True
    display_ok = display.get("ok") is True
    read_model_ok = read_model.get("ok") is True
    observation_path_ready = bool(smoke_ok and display_ok and read_model_ok and source_is_hot_root and prediction_row_count > 0)
    stale_or_unknown = freshness_state in {"stale", "unknown", "delayed"}

    failures: list[str] = []
    if not smoke_ok:
        failures.append("ps_q19f_smoke_not_ok")
    if not source_is_hot_root:
        failures.append("read_model_source_not_hot_latest_root")
    if not display_ok:
        failures.append("ps_q19d_display_packet_not_ok")
    if prediction_row_count <= 0:
        failures.append("prediction_display_rows_missing")
    for key in (
        "scheduler_enabled",
        "producer_enabled",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_send_to_broker",
    ):
        if smoke.get(key) is not False:
            failures.append(f"smoke_safety_boundary_not_false:{key}")

    ok = bool(not failures)
    return {
        "ok": ok,
        "ps_q19g_version": PS_Q19G_REFRESH_POLICY_VERSION,
        "phase": "ps_q19g_warroom_observation_close_and_refresh_policy_decision",
        "hot_latest_root_hint": str(hot_latest_root_hint),
        "observation_path_ready": observation_path_ready,
        "read_model_source_is_hot_latest_root": source_is_hot_root,
        "source_artifact_path": read_model.get("source_artifact_path"),
        "prediction_row_count": prediction_row_count,
        "freshness_state": freshness_state,
        "generated_at": read_model.get("generated_at"),
        "age_sec": read_model.get("age_sec"),
        "manual_refresh_recommended_now": bool(stale_or_unknown and observation_path_ready),
        "manual_refresh_reason": "latest_prediction_artifact_stale_or_unknown" if stale_or_unknown else "latest_prediction_artifact_fresh_enough",
        "manual_refresh_tool": "tools/run_prediction_warroom_bounded_manual_refresh_ps_q19e.py",
        "manual_refresh_ack_required": True,
        "manual_refresh_ack": PS_Q19E_MANUAL_REFRESH_ACK,
        "manual_refresh_command": _manual_refresh_command(str(hot_latest_root_hint)),
        "post_refresh_resmoke_command": _resmoke_command(str(hot_latest_root_hint)),
        "refresh_policy_decision": "manual_refresh_first_scheduler_deferred",
        "scheduler_policy_decision": "do_not_enable_scheduler_until_after_manual_refresh_visual_confirmation",
        "scheduled_loop_enabled": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "next_operational_step": NEXT_OPERATIONAL_STEP,
        "failures": failures,
        "runtime_artifact_write_performed_by_policy_helper": False,
        "status_artifact_write_performed_by_policy_helper": False,
        "manual_refresh_executed_by_policy_helper": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19G WarRoom observation close / refresh policy decision")
    parser.add_argument("--root", default=DEFAULT_HOT_LATEST_ROOT_HINT, help="Hot latest root. Default: D:/btc_ts_hot")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    packet = build_ps_q19g_warroom_observation_refresh_policy_packet(hot_latest_root_hint=str(args.root))
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
