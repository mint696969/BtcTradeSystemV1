# path: ./tools/run_sr_fx_runtime_control_report_sequence_once.py
# desc: Operator-facing broker-free CLI wrapper for SR-FX runtime_control refresh/report sequence. Non-authorizing; no broker calls/no mode changes.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping

from btcts.apps.sr_fx_runtime_control_report_sequence_once import run_sr_fx_runtime_control_report_sequence

TOOL = "run_sr_fx_runtime_control_report_sequence_once"


def _set_env_if_value(name: str, value: str | None) -> None:
    text = str(value or "").strip()
    if text:
        os.environ[name] = text


def _print_json(data: Mapping[str, Any]) -> None:
    print(json.dumps(dict(data), ensure_ascii=False, indent=2, sort_keys=True, default=str))


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Broker-free SR-FX runtime_control refresh/report sequence wrapper. "
            "This command is read-only, non-authorizing, and does not send broker orders."
        )
    )
    parser.add_argument("--runtime-root", default="", help="Optional BTC_TS_AUTOTRADE_RUNTIME_ROOT override.")
    parser.add_argument("--data-root", default="", help="Optional BTC_TS_DATA_DIR / BTCTS_DATA_ROOT override.")
    parser.add_argument("--logs-root", default="", help="Optional BTC_TS_LOGS_DIR / BTCTS_LOGS_ROOT override.")
    parser.add_argument("--state-root", default="", help="Optional BTCTS_STATE_ROOT override.")
    parser.add_argument("--now", default="", help="Optional BTCTS_RUNTIME_CONTROL_NOW override, ISO timestamp.")
    parser.add_argument("--heartbeat-observed-at", default="", help="Optional BTCTS_RUNTIME_CONTROL_HEARTBEAT_OBSERVED_AT override.")
    parser.add_argument("--heartbeat-max-age-sec", default="", help="Optional BTCTS_RUNTIME_CONTROL_HEARTBEAT_MAX_AGE_SEC override.")
    parser.add_argument("--incident-open", default="", help="Optional BTCTS_RUNTIME_CONTROL_INCIDENT_OPEN override.")
    parser.add_argument("--incident-reason", default="", help="Optional BTCTS_RUNTIME_CONTROL_INCIDENT_REASON override.")
    parser.add_argument("--kill-switch-active", default="", help="Optional BTCTS_RUNTIME_CONTROL_KILL_SWITCH_ACTIVE override.")
    parser.add_argument("--kill-switch-action", default="", help="Optional BTCTS_RUNTIME_CONTROL_KILL_SWITCH_ACTION override.")
    parser.add_argument("--kill-switch-reason", default="", help="Optional BTCTS_RUNTIME_CONTROL_KILL_SWITCH_REASON override.")
    parser.add_argument("--out", default="", help="Optional path to write wrapper JSON output.")
    return parser


def _apply_args(args: argparse.Namespace) -> None:
    _set_env_if_value("BTC_TS_AUTOTRADE_RUNTIME_ROOT", args.runtime_root)
    _set_env_if_value("BTC_TS_DATA_DIR", args.data_root)
    _set_env_if_value("BTCTS_DATA_ROOT", args.data_root)
    _set_env_if_value("BTC_TS_LOGS_DIR", args.logs_root)
    _set_env_if_value("BTCTS_LOGS_ROOT", args.logs_root)
    _set_env_if_value("BTCTS_STATE_ROOT", args.state_root)
    _set_env_if_value("BTCTS_RUNTIME_CONTROL_NOW", args.now)
    _set_env_if_value("BTCTS_RUNTIME_CONTROL_HEARTBEAT_OBSERVED_AT", args.heartbeat_observed_at)
    _set_env_if_value("BTCTS_RUNTIME_CONTROL_HEARTBEAT_MAX_AGE_SEC", args.heartbeat_max_age_sec)
    _set_env_if_value("BTCTS_RUNTIME_CONTROL_INCIDENT_OPEN", args.incident_open)
    _set_env_if_value("BTCTS_RUNTIME_CONTROL_INCIDENT_REASON", args.incident_reason)
    _set_env_if_value("BTCTS_RUNTIME_CONTROL_KILL_SWITCH_ACTIVE", args.kill_switch_active)
    _set_env_if_value("BTCTS_RUNTIME_CONTROL_KILL_SWITCH_ACTION", args.kill_switch_action)
    _set_env_if_value("BTCTS_RUNTIME_CONTROL_KILL_SWITCH_REASON", args.kill_switch_reason)


def build_wrapper_payload(sequence: Mapping[str, Any]) -> dict[str, Any]:
    paths = dict(sequence.get("paths") or {}) if isinstance(sequence.get("paths"), Mapping) else {}
    runtime_control = dict(sequence.get("runtime_control") or {}) if isinstance(sequence.get("runtime_control"), Mapping) else {}
    return {
        "ok": bool(sequence.get("ok")) and bool(sequence.get("sequence_complete")),
        "tool": TOOL,
        "stage": "sr_fx_runtime_control_report_sequence_cli_wrapper",
        "sequence": dict(sequence),
        "paths": paths,
        "runtime_control": runtime_control,
        "operator_safety_lock": {
            "non_authorizing": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "final_human_review_required": True,
        },
        "summary": {
            "sequence_complete": bool(sequence.get("sequence_complete")),
            "runtime_control_refreshed_first": bool((sequence.get("summary") or {}).get("runtime_control_refreshed_first")) if isinstance(sequence.get("summary"), Mapping) else False,
            "runtime_control_state_path": paths.get("runtime_control_state"),
            "runtime_control_ok": bool(runtime_control.get("ok")),
            "runtime_control_blocked_by": list(runtime_control.get("blocked_by") or []),
            "non_authorizing": True,
        },
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
        "autotrade_resume_authorized": False,
        "final_human_review_required": True,
    }


def main() -> int:
    args = _build_arg_parser().parse_args()
    _apply_args(args)
    try:
        sequence = run_sr_fx_runtime_control_report_sequence()
        payload = build_wrapper_payload(sequence)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "stage": "sr_fx_runtime_control_report_sequence_cli_wrapper",
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["runtime_control_report_sequence_cli_wrapper_failed"],
            "operator_safety_lock": {
                "non_authorizing": True,
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
                "autotrade_resume_authorized": False,
                "final_human_review_required": True,
            },
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "final_human_review_required": True,
        }
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    _print_json(payload)
    # Pre-live blockers are expected. The wrapper fails only when invocation/safety contract fails.
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
