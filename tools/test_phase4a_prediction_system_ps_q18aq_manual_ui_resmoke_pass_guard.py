# path: ./tools/test_phase4a_prediction_system_ps_q18aq_manual_ui_resmoke_pass_guard.py
# desc: Focused guard for PS-Q18AQ manual UI re-smoke pass record.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18aq_manual_ui_resmoke_pass import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18aq_manual_ui_resmoke_pass_packet,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AQ_WARROOM_LATEST_PREDICTION_MANUAL_UI_RESMOKE_PASS_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18aq_manual_ui_resmoke_pass.py"
UICHECK = REPO_ROOT / "tmp/uicheck/uicheck_20260624_160417_810705_warroom.json"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AQ_WARROOM_LATEST_PREDICTION_MANUAL_UI_RESMOKE_PASS_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18aq_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18aq_manual_ui_resmoke_pass.py",
    "tools/test_phase4a_prediction_system_ps_q18aq_manual_ui_resmoke_pass_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    for path in (DOC, UNIT):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    if not UICHECK.exists():
        failures.append(f"missing uicheck evidence: {UICHECK.relative_to(REPO_ROOT)}")
    else:
        text = _read(UICHECK)
        for marker in ("\"head\": \"5ee19bbe\"", "\"status_short\": []", "\"page_reload_enabled\": false", "\"fragment_refresh_enabled\": true", "\"refresh_heartbeat_utc\"", "\"freshness_state\": \"stale\"", "\"source_generated_at_stale\""):
            if marker not in text:
                failures.append(f"uicheck marker missing: {marker}")
    packet = build_ps_q18aq_manual_ui_resmoke_pass_packet()
    if packet.get("manual_ui_resmoke_result") != "pass":
        failures.append("manual UI re-smoke must be pass")
    for key in ("browser_find_freshness_state", "browser_find_safe_fallback_reason_codes", "browser_find_refresh_heartbeat_utc", "searchable_plain_text_visible", "refresh_heartbeat_utc_changes_across_screenshots", "ps_q18ao_searchability_gap_closed", "ps_q18ao_refresh_visibility_gap_closed"):
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    if packet.get("q18aj_page_reload_enabled") is not False:
        failures.append("page reload must remain false")
    if packet.get("uicheck_repo_status_short") != []:
        failures.append("uicheck repo status must be clean")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AQ", "manual_ui_resmoke_result=pass", "browser_find_freshness_state=true", "browser_find_safe_fallback_reason_codes=true", "browser_find_refresh_heartbeat_utc=true", "refresh_heartbeat_utc_changes_across_screenshots=true", "broker_private_api_allowed=false"):
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
        "guard": "ps_q18aq_manual_ui_resmoke_pass_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "manual_ui_resmoke_result": packet.get("manual_ui_resmoke_result"),
        "next_safe_slice": packet.get("next_safe_slice"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18aq_manual_ui_resmoke_pass_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
