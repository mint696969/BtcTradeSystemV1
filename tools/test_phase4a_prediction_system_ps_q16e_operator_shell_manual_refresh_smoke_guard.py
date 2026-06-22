# path: ./tools/test_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke_guard.py
# desc: Focused guard for PS-Q16E operator-shell manual refresh wrapper/smoke. Uses temp root and fake export; does not write D-hot.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

import check_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke as smoke_mod  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKE = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16E_OPERATOR_SHELL_MANUAL_REFRESH_SMOKE_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16E_OPERATOR_SHELL_MANUAL_REFRESH_SMOKE_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16e_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke_guard.py",
}
REQUIRED_DOC_MARKERS = (
    "PS-Q16E provides a human-run operator-shell command",
    "operator_shell_only=true",
    "clean_tree_precheck=true",
    "python .\\tools\\check_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke.py",
    "refresh.runner_state=bounded_manual_refresh_exported_status_written",
    "source_smoke.ok=true",
    "producer_status_panel.panel_state=producer_status_panel_loaded",
    "scheduler_registered=false",
    "PS-Q16F: scheduler enablement preflight guard",
)
FORBIDDEN_SOURCE_TOKENS = (
    "import streamlit",
    "from streamlit",
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
    "approval_or_ledger_or_autotrade_or_broker=true",
    "freshness_bypass_added=true",
    "force_ready_added=true",
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
    target.write_text(json.dumps({"ok": True}, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "runner_state": "latest_payload_actual_export_runner_exported",
        "target_file_written": True,
        "target_artifact_path": str(target),
        "target_file_size_bytes": target.stat().st_size,
        "prediction_run_id": "prediction_system.ps_q16e.guard:BTC_JPY:bitFlyer:2026-06-22T10:00:00Z",
        "generated_at": "2026-06-22T10:00:00Z",
        "exported_at": "2026-06-22T10:00:01Z",
        "blocked_reasons": [],
        "warning_reasons": [],
    }


def _fake_source_smoke(*, hot_latest_root_hint: str) -> dict[str, Any]:
    return {
        "ok": True,
        "adapter_state": "latest_prediction_source_ready",
        "actual_file_read_succeeded": True,
        "payload_decode_succeeded": True,
        "review_packet_ready": True,
        "session_state_updated": True,
        "blocker_count": 0,
        "warning_count": 0,
        "source_summary": {
            "prediction_run_id": "prediction_system.ps_q16e.guard:BTC_JPY:bitFlyer:2026-06-22T10:00:00Z",
            "generated_at": "2026-06-22T10:00:00Z",
        },
    }


def main() -> int:
    failures: list[str] = []
    for path in (SMOKE, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    smoke_text = _read(SMOKE) if SMOKE.exists() else ""
    if "build_prediction_warroom_bounded_manual_refresh_runner" not in smoke_text:
        failures.append("PS-Q16E must use PS-Q16D bounded manual refresh runner")
    if "build_warroom_live_inference_smoke_payload" not in smoke_text:
        failures.append("PS-Q16E must verify WarRoom source smoke")
    if "build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet" not in smoke_text:
        failures.append("PS-Q16E must verify producer status panel visibility")
    for token in FORBIDDEN_SOURCE_TOKENS:
        if token in smoke_text:
            failures.append(f"forbidden source token: {token}")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")

    original_status = smoke_mod._git_status_short
    original_source_smoke = smoke_mod.build_warroom_live_inference_smoke_payload
    try:
        smoke_mod._git_status_short = lambda: [" M dirty.py"]
        blocked = smoke_mod.build_report(require_clean_tree=True, actual_export_runner=_fake_export)
        if blocked.get("ok") is not False or blocked.get("manual_refresh_executed") is not False:
            failures.append("dirty tree precheck must block before refresh")
        smoke_mod._git_status_short = lambda: []
        smoke_mod.build_warroom_live_inference_smoke_payload = _fake_source_smoke
        with TemporaryDirectory() as temp_dir:
            payload = smoke_mod.build_report(
                hot_root=temp_dir,
                require_clean_tree=True,
                actual_export_runner=_fake_export,
                allow_guard_test_root=True,
            )
        if payload.get("ok") is not True:
            failures.append(f"stubbed PS-Q16E report should be ok: {payload}")
        refresh = payload.get("refresh", {})
        if refresh.get("runner_state") != "bounded_manual_refresh_exported_status_written":
            failures.append("refresh state mismatch")
        if refresh.get("safe_flags", {}).get("scheduler_enabled_false") is not True:
            failures.append("scheduler safety flag missing")
        status = payload.get("producer_status_panel", {})
        if status.get("panel_state") != "producer_status_panel_loaded":
            failures.append("producer status panel should load after stubbed refresh")
    finally:
        smoke_mod._git_status_short = original_status
        smoke_mod.build_warroom_live_inference_smoke_payload = original_source_smoke

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16e_operator_shell_manual_refresh_smoke",
        "phase": "phase3_prediction_system_warroom_realtime_observation_operator_shell_smoke",
        "contract": {
            "operator_shell_only": True,
            "clean_tree_precheck": True,
            "uses_ps_q16d_runner": "build_prediction_warroom_bounded_manual_refresh_runner" in smoke_text,
            "verifies_source_smoke": "build_warroom_live_inference_smoke_payload" in smoke_text,
            "verifies_producer_status_panel": "build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet" in smoke_text,
            "scheduler_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16e_operator_shell_manual_refresh_smoke_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
