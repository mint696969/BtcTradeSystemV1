# path: ./btcts_next/src/btcts/apps/sr_fx_runtime_control_report_sequence_once.py
# desc: One-shot broker-free SR-FX runtime_control refresh -> safety/pre-live/final-review/handoff sequence. No mode changes and no broker calls.

from __future__ import annotations

import contextlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from btcts.apps import sr_fx_data_ui_gate_handoff_once as handoff_app
from btcts.apps import sr_fx_execution_safety_harness_once as safety_app
from btcts.apps import sr_fx_final_review_package_once as final_review_app
from btcts.apps import sr_fx_pre_live_blocker_report_once as pre_live_app
from btcts.apps import sr_fx_runtime_control_snapshot_once as runtime_control_app
from btcts.autotrade.execution.runtime_control import runtime_control_state_path
from btcts.collector_vnext.config import ConfigValidationError, load_config

STAGE = "sr_fx_runtime_control_report_sequence_once"
SEQUENCE_VERSION = "sr_fx_runtime_control_report_sequence.v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _print_json(data: Mapping[str, Any]) -> None:
    print(json.dumps(dict(data), ensure_ascii=False, indent=2, sort_keys=True, default=str))


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return data


def _safe_load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _read_json(path)


def _capture_main(func: Callable[[], int]) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        rc = int(func())
    return rc, buffer.getvalue()


def _state_paths() -> dict[str, Path]:
    roots = load_config().roots()
    state = roots["state"]
    return {
        "runtime_control_state": runtime_control_state_path(ensure=True),
        "execution_safety_harness": state / "autotrade" / "sr_fx_execution_safety_harness.json",
        "pre_live_blocker_report": state / "autotrade" / "sr_fx_pre_live_blocker_report.json",
        "final_review_package": state / "operator_ui" / "sr_fx_final_review_package.json",
        "data_ui_gate_handoff": state / "operator_ui" / "sr_fx_data_ui_gate_handoff.json",
    }


def run_sr_fx_runtime_control_report_sequence() -> dict[str, Any]:
    paths = _state_paths()
    steps: list[dict[str, Any]] = []

    runtime_out = runtime_control_app.write_snapshot_from_environment(path=paths["runtime_control_state"])
    steps.append(
        {
            "name": "runtime_control_snapshot_refresh",
            "ok": True,
            "output_ok": bool(runtime_out.get("ok")),
            "path": str(paths["runtime_control_state"]),
            "blocked_by": list((runtime_out.get("runtime_control") or {}).get("blocked_by") or []),
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
        }
    )

    safety_rc, safety_stdout = _capture_main(safety_app.main)
    safety_payload = _safe_load_json(paths["execution_safety_harness"])
    steps.append(
        {
            "name": "execution_safety_harness_report",
            "ok": safety_rc == 0 and safety_payload is not None,
            "output_ok": bool((safety_payload or {}).get("ok")),
            "path": str(paths["execution_safety_harness"]),
            "stdout_tail": safety_stdout[-1200:],
            "read_only": bool((safety_payload or {}).get("read_only", True)),
            "would_send_to_broker": bool((safety_payload or {}).get("would_send_to_broker", False)),
            "mode_changed": bool((safety_payload or {}).get("mode_changed", False)),
        }
    )

    pre_live_rc, pre_live_stdout = _capture_main(pre_live_app.main)
    pre_live_payload = _safe_load_json(paths["pre_live_blocker_report"])
    steps.append(
        {
            "name": "pre_live_blocker_report",
            "ok": pre_live_rc == 0 and pre_live_payload is not None,
            "output_ok": bool((pre_live_payload or {}).get("ok")),
            "path": str(paths["pre_live_blocker_report"]),
            "stdout_tail": pre_live_stdout[-1200:],
            "read_only": bool((pre_live_payload or {}).get("read_only", True)),
            "would_send_to_broker": bool((pre_live_payload or {}).get("would_send_to_broker", False)),
            "mode_changed": bool((pre_live_payload or {}).get("mode_changed", False)),
        }
    )

    final_payload = final_review_app.build_from_state()
    steps.append(
        {
            "name": "final_review_package",
            "ok": bool(final_payload),
            "output_ok": bool(final_payload.get("ok")),
            "path": str(paths["final_review_package"]),
            "runtime_control_present": bool((final_payload.get("runtime_control") or {}).get("present")),
            "runtime_control_clear": bool((final_payload.get("runtime_control") or {}).get("clear")),
            "read_only": bool(final_payload.get("read_only", True)),
            "would_send_to_broker": bool(final_payload.get("would_send_to_broker", False)),
            "mode_changed": bool(final_payload.get("mode_changed", False)),
        }
    )

    handoff_payload = handoff_app.build_from_state()
    handoff_runtime = ((handoff_payload.get("execution_boundary") or {}).get("runtime_control") or {}) if isinstance(handoff_payload.get("execution_boundary"), Mapping) else {}
    steps.append(
        {
            "name": "data_ui_gate_handoff",
            "ok": bool(handoff_payload),
            "output_ok": bool(handoff_payload.get("ok")),
            "path": str(paths["data_ui_gate_handoff"]),
            "runtime_control_present": bool(handoff_runtime.get("present")),
            "runtime_control_clear": bool(handoff_runtime.get("clear")),
            "read_only": bool(handoff_payload.get("read_only", True)),
            "would_send_to_broker": bool(handoff_payload.get("would_send_to_broker", False)),
            "mode_changed": bool(handoff_payload.get("mode_changed", False)),
        }
    )

    unexpected_send = [step["name"] for step in steps if step.get("would_send_to_broker")]
    unexpected_mode_change = [step["name"] for step in steps if step.get("mode_changed")]
    not_read_only = [step["name"] for step in steps if not step.get("read_only", True)]
    blocked_by = []
    if unexpected_send:
        blocked_by.append("unexpected_would_send_to_broker_flag")
    if unexpected_mode_change:
        blocked_by.append("unexpected_mode_change_flag")
    if not_read_only:
        blocked_by.append("unexpected_not_read_only_flag")

    sequence_ok = all(bool(step.get("ok")) for step in steps) and not blocked_by
    return {
        "ok": sequence_ok,
        "stage": STAGE,
        "sequence_version": SEQUENCE_VERSION,
        "generated_at": _utc_now_iso(),
        "sequence_complete": sequence_ok,
        "steps": steps,
        "paths": {key: str(value) for key, value in paths.items()},
        "runtime_control": runtime_out.get("runtime_control"),
        "summary": {
            "runtime_control_refreshed_first": steps[0]["name"] == "runtime_control_snapshot_refresh",
            "runtime_control_snapshot_ok": bool(runtime_out.get("ok")),
            "execution_safety_harness_ok": bool((safety_payload or {}).get("ok")),
            "pre_live_blocker_report_ok": bool((pre_live_payload or {}).get("ok")),
            "final_review_package_ok": bool(final_payload.get("ok")),
            "handoff_ok": bool(handoff_payload.get("ok")),
            "final_review_runtime_control_present": bool((final_payload.get("runtime_control") or {}).get("present")),
            "handoff_runtime_control_present": bool(handoff_runtime.get("present")),
        },
        "blocked_by": blocked_by,
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
    }


def main() -> int:
    try:
        out = run_sr_fx_runtime_control_report_sequence()
    except ConfigValidationError as exc:
        out = {
            "ok": False,
            "stage": STAGE,
            "sequence_version": SEQUENCE_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["load_config_failed"],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
        }
    except Exception as exc:
        out = {
            "ok": False,
            "stage": STAGE,
            "sequence_version": SEQUENCE_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["runtime_control_report_sequence_failed"],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
        }
    _print_json(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
