# path: ./tools/test_phase4a_prediction_system_ps_q16d_bounded_manual_refresh_runner_guard.py
# desc: Focused guard for PS-Q16D bounded manual refresh runner.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_bounded_manual_refresh_runner import (  # noqa: E402
    build_prediction_warroom_bounded_manual_refresh_runner,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_bounded_manual_refresh_runner.py"
UNIT_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_bounded_manual_refresh_runner.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16D_BOUNDED_MANUAL_REFRESH_RUNNER_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_bounded_manual_refresh_runner.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_bounded_manual_refresh_runner.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16D_BOUNDED_MANUAL_REFRESH_RUNNER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16d_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16d_bounded_manual_refresh_runner_guard.py",
}
REQUIRED_DOC_MARKERS = (
    "PS-Q16D adds a bounded manual refresh runner",
    "actual_export_runner_invoked_only_after_all_explicit_flags=true",
    "execute_manual_refresh=true",
    "allow_runtime_artifact_write=true",
    "allow_status_artifact_write=true",
    "scheduler_enabled=false",
    "scheduled_loop_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "PS-Q16E: operator-shell manual run wrapper/smoke",
)
FORBIDDEN_SOURCE_TOKENS = (
    "import streamlit",
    "from streamlit",
    "subprocess.run(",
    "schtasks",
    "TaskScheduler",
    "run_ps_q12d_export_and_smoke",
    "send_order(",
    "create_order(",
    "append_decision(",
    "append_command(",
)
FORBIDDEN_DOC_MARKERS = (
    "scheduler_registration=true",
    "scheduled_loop=true",
    "WarRoom UI trigger=true",
    "automation_enablement=true",
    "parameter_apply=true",
    "parameter_staging_write=true",
    "ledger_append_allowed=true",
    "autotrade_trigger_allowed=true",
    "broker_private_api_allowed=true",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def _fake_export(**kwargs: Any) -> dict[str, Any]:
    root = Path(str(kwargs["hot_latest_root_hint"]))
    target = root / "prediction" / "latest_prediction_system_result.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('{"ok": true}\n', encoding="utf-8")
    return {
        "runner_state": "latest_payload_actual_export_runner_exported",
        "target_file_written": True,
        "target_artifact_path": str(target),
        "target_file_size_bytes": target.stat().st_size,
        "prediction_run_id": "prediction_system.ps_q16d.guard:BTC_JPY:bitFlyer:2026-06-22T10:00:00Z",
        "generated_at": "2026-06-22T10:00:00Z",
        "exported_at": "2026-06-22T10:00:01Z",
        "blocked_reasons": [],
        "warning_reasons": [],
    }


def main() -> int:
    failures: list[str] = []
    for path in (MODULE, UNIT_TEST, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")

    module_text = _read(MODULE) if MODULE.exists() else ""
    if "build_prediction_warroom_latest_payload_actual_export_runner" not in module_text:
        failures.append("PS-Q16D runner must reference PS-Q10H actual export runner")
    for token in FORBIDDEN_SOURCE_TOKENS:
        if token in module_text:
            failures.append(f"forbidden source token in PS-Q16D runner: {token}")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")

    default_packet = build_prediction_warroom_bounded_manual_refresh_runner().to_dict()
    if default_packet.get("actual_export_runner_invoked") is not False:
        failures.append("default runner must not invoke actual export")
    for key in (
        "latest_prediction_artifact_written",
        "status_artifact_written",
        "scheduler_enabled",
        "scheduled_loop_enabled",
        "warroom_ui_trigger_enabled",
        "ui_triggered_runner_execution",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ready_for_scheduler_enablement",
        "ready_for_automation_enablement",
    ):
        if default_packet.get(key) is not False:
            failures.append(f"default unsafe flag not false: {key}={default_packet.get(key)!r}")
    with TemporaryDirectory() as temp_dir:
        packet = build_prediction_warroom_bounded_manual_refresh_runner(
            hot_latest_root_hint=temp_dir,
            operator_acknowledged=True,
            execute_manual_refresh=True,
            allow_actual_read=True,
            allow_prediction_build=True,
            allow_export_preflight=True,
            allow_latest_payload_export=True,
            allow_runtime_artifact_write=True,
            allow_status_artifact_write=True,
            execute_status_artifact_write=True,
            allow_guard_test_root=True,
            actual_export_runner=_fake_export,
        ).to_dict()
        if packet.get("runner_state") != "bounded_manual_refresh_exported_status_written":
            failures.append("explicit guard-root manual refresh should export and write status")
        if packet.get("actual_export_runner_invoked") is not True:
            failures.append("explicit manual refresh should invoke actual export runner")
        if packet.get("scheduler_enabled") is not False or packet.get("warroom_ui_trigger_enabled") is not False:
            failures.append("manual refresh must keep scheduler/UI trigger false")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q16d_bounded_manual_refresh_runner",
        "phase": "phase3_prediction_system_warroom_realtime_observation_bounded_manual_refresh",
        "contract": {
            "bounded_manual_refresh_only": True,
            "actual_export_runner_invoked_only_after_all_explicit_flags": True,
            "scheduler_enabled": False,
            "scheduled_loop_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "status_visibility_written_after_attempt": True,
            "autotrade_trigger_candidate_deferred": True,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16d_bounded_manual_refresh_runner_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
