# path: ./tools/test_phase4a_prediction_system_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record_guard.py
# desc: Focused guard for PS-Q18AW manual UI smoke execution record.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record import (  # noqa: E402
    FALSE_BOUNDARIES,
    PASS_CHECKS,
    build_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AW_WARROOM_OBSERVATION_QUICK_STATUS_MANUAL_UI_SMOKE_EXECUTION_RECORD_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record.py"
UICHECK = REPO_ROOT / "tmp/uicheck/uicheck_20260624_202405_369594_warroom.json"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AW_WARROOM_OBSERVATION_QUICK_STATUS_MANUAL_UI_SMOKE_EXECUTION_RECORD_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18aw_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record.py",
    "tools/test_phase4a_prediction_system_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def _load_uicheck() -> dict:
    return json.loads(_read(UICHECK)) if UICHECK.exists() else {}


def main_guard() -> int:
    failures: list[str] = []
    for path in (UNIT,):
        try:
            ast.parse(_read(path), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    packet = build_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record()
    if packet.get("manual_ui_smoke_result") != "pass":
        failures.append("manual UI smoke result must be pass")
    if packet.get("pass_check_count") != len(PASS_CHECKS):
        failures.append("pass check count mismatch")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    uicheck = _load_uicheck()
    if not uicheck:
        failures.append("uicheck evidence file missing")
    else:
        if uicheck.get("page", {}).get("selected_page_key") != "warroom":
            failures.append("uicheck page must be warroom")
        if uicheck.get("repo", {}).get("head") != "625de736":
            failures.append("uicheck repo head mismatch")
        if uicheck.get("repo", {}).get("status_short") != []:
            failures.append("uicheck repo status must be clean")
        ui_state = uicheck.get("ui_state", {})
        refresh_plan = ui_state.get("refresh_plan", {}) if isinstance(ui_state.get("refresh_plan"), dict) else {}
        if ui_state.get("ui_auto_refresh") is not True:
            failures.append("uicheck ui_auto_refresh must be true")
        if refresh_plan.get("fragment_refresh_enabled") is not True:
            failures.append("uicheck fragment_refresh_enabled must be true")
        if refresh_plan.get("page_reload_enabled") is not False:
            failures.append("uicheck page_reload_enabled must be false")
        quick = (
            uicheck.get("session_state_safe", {})
            .get("selected_safe_values", {})
            .get("warroom_latest_prediction_observation_cleanup_summary", {})
        )
        if quick.get("observation_cleanup_state") != "operator_quick_status_visible_display_only":
            failures.append("quick status state mismatch")
        if quick.get("latest_prediction_observation_status") != "ready_for_operator_review":
            failures.append("quick status observation status mismatch")
        if quick.get("implementation_gate_review_result") != "blocked_not_ready_to_enable":
            failures.append("implementation gate result mismatch")
        if quick.get("real_rendering_enabled") is not False:
            failures.append("quick real_rendering_enabled must be false")
        if quick.get("component_runtime_binding_allowed") is not False:
            failures.append("quick component runtime binding must be false")
        if quick.get("autotrade_trigger_allowed") is not False:
            failures.append("quick autotrade must be false")
        if quick.get("would_send_to_broker") is not False:
            failures.append("quick would_send_to_broker must be false")
        text = str(quick.get("operator_plain_text") or "")
        for marker in ("PS_Q18AU_OBSERVATION_QUICK_STATUS", "latest_prediction_observation_status=ready_for_operator_review", "freshness_state=stale", "safe_fallback_reason_codes=source_generated_at_stale", "implementation_gate=blocked_not_ready_to_enable", "real_render=false", "component_runtime_binding=false", "autotrade=false", "broker=false"):
            if marker not in text:
                failures.append(f"missing uicheck plain text marker: {marker}")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18AW",
        "manual_ui_smoke_result=pass",
        "operator_report=ALL OK",
        "uicheck_20260624_202405_369594_warroom.json",
        "refresh_heartbeat_utc_advances_after_wait=true",
        "broker_private_api_allowed=false",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "manual_ui_smoke_result": packet.get("manual_ui_smoke_result"),
        "pass_check_count": packet.get("pass_check_count"),
        "uicheck_path": str(UICHECK.relative_to(REPO_ROOT)).replace(chr(92), "/"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
