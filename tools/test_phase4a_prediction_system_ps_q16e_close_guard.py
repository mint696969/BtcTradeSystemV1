# path: ./tools/test_phase4a_prediction_system_ps_q16e_close_guard.py
# desc: Close guard for PS-Q16E operator-shell manual refresh wrapper/smoke. Uses temp root and fake export only; does not write D-hot.

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

import check_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke as smoke_mod  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16E_OPERATOR_SHELL_MANUAL_REFRESH_SMOKE_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16e_close_guard.py",
}
REQUIRED_FILES = tuple(EXPECTED_DIRTY)
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke_guard.py"


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
        "prediction_run_id": "prediction_system.ps_q16e.close:BTC_JPY:bitFlyer:2026-06-22T10:00:00Z",
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
            "prediction_run_id": "prediction_system.ps_q16e.close:BTC_JPY:bitFlyer:2026-06-22T10:00:00Z",
            "generated_at": "2026-06-22T10:00:00Z",
        },
    }


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (REPO_ROOT / rel).exists():
            failures.append(f"missing required file: {rel}")
    smoke_text = (REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke.py").read_text(encoding="utf-8-sig")
    for marker in (
        "CHECKER = \"ps_q16e_operator_shell_manual_refresh_smoke\"",
        "require_clean_tree",
        "build_prediction_warroom_bounded_manual_refresh_runner",
        "build_warroom_live_inference_smoke_payload",
        "build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet",
        "scheduler_registered\": False",
        "warroom_ui_trigger_enabled\": False",
        "parameter_apply_or_staging\": False",
    ):
        if marker not in smoke_text:
            failures.append(f"missing smoke marker: {marker}")

    original_status = smoke_mod._git_status_short
    original_source_smoke = smoke_mod.build_warroom_live_inference_smoke_payload
    try:
        smoke_mod._git_status_short = lambda: [" M dirty.py"]
        blocked = smoke_mod.build_report(require_clean_tree=True, actual_export_runner=_fake_export)
        if blocked.get("manual_refresh_executed") is not False:
            failures.append("dirty precheck must not execute manual refresh")
        if "working_tree_not_clean" not in blocked.get("blocked_reasons", []):
            failures.append("dirty precheck blocker missing")
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
            failures.append(f"stubbed close report should be ok: {payload}")
        refresh = payload.get("refresh", {})
        if refresh.get("runner_state") != "bounded_manual_refresh_exported_status_written":
            failures.append("refresh state mismatch")
        safe = refresh.get("safe_flags", {})
        for key in (
            "scheduler_enabled_false",
            "scheduled_loop_enabled_false",
            "warroom_ui_trigger_enabled_false",
            "parameter_apply_allowed_false",
            "parameter_staging_write_allowed_false",
            "autotrade_trigger_allowed_false",
            "broker_private_api_allowed_false",
        ):
            if safe.get(key) is not True:
                failures.append(f"missing safe flag: {key}")
        source = payload.get("source_smoke", {})
        if source.get("ok") is not True or source.get("adapter_state") != "latest_prediction_source_ready":
            failures.append("source smoke summary must be ready in stubbed close report")
        status = payload.get("producer_status_panel", {})
        if status.get("panel_state") != "producer_status_panel_loaded":
            failures.append("producer status panel must load in stubbed close report")
        safety = payload.get("safety", {})
        if safety.get("scheduler_registered") is not False or safety.get("warroom_ui_trigger_enabled") is not False:
            failures.append("scheduler/UI trigger safety must remain false")
    finally:
        smoke_mod._git_status_short = original_status
        smoke_mod.build_warroom_live_inference_smoke_payload = original_source_smoke

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16e_close_guard",
        "phase": "phase3_prediction_system_warroom_realtime_observation_operator_shell_smoke_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16e_closed": not failures,
            "next_slice": "Run PS-Q16E operator-shell manual refresh smoke after commit, then PS-Q16F scheduler enablement preflight guard/human checkpoint",
            "operator_shell_only": True,
            "clean_tree_precheck": True,
            "d_hot_write_only_when_human_runs_command_after_commit": True,
            "scheduler_enabled": False,
            "scheduled_loop_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16e_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
