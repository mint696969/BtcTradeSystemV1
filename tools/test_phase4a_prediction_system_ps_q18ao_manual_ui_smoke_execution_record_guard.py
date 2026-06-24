# path: ./tools/test_phase4a_prediction_system_ps_q18ao_manual_ui_smoke_execution_record_guard.py
# desc: Focused guard for PS-Q18AO manual UI smoke execution record.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18ao_manual_ui_smoke_execution_record import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18ao_manual_ui_smoke_execution_record_packet,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AO_WARROOM_LATEST_PREDICTION_MANUAL_UI_SMOKE_EXECUTION_RECORD_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18ao_manual_ui_smoke_execution_record.py"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AO_WARROOM_LATEST_PREDICTION_MANUAL_UI_SMOKE_EXECUTION_RECORD_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ao_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ao_manual_ui_smoke_execution_record.py",
    "tools/test_phase4a_prediction_system_ps_q18ao_manual_ui_smoke_execution_record_guard.py",
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
    packet = build_ps_q18ao_manual_ui_smoke_execution_record_packet()
    if packet.get("manual_ui_smoke_result") != "observed_with_ux_gaps_not_full_pass":
        failures.append("manual smoke must be recorded as observed_with_ux_gaps_not_full_pass")
    for key in ("latest_prediction_auto_refresh_panel_visible", "latest_prediction_freshness_fallback_panel_visible", "q18aj_auto_refresh_enabled", "q18aj_fragment_refresh_enabled", "operator_searchability_gap_present", "operator_refresh_visibility_gap_present"):
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    if packet.get("q18aj_page_reload_enabled") is not False:
        failures.append("page reload must remain false")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AO", "observed_with_ux_gaps_not_full_pass", "browser_find_freshness_state=false", "auto_refresh_visibly_obvious=false", "PS-Q18AP UI visibility polish", "broker_private_api_allowed=false"):
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
        "guard": "ps_q18ao_manual_ui_smoke_execution_record_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "manual_ui_smoke_result": packet.get("manual_ui_smoke_result"),
        "next_safe_slice": packet.get("next_safe_slice"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ao_manual_ui_smoke_execution_record_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
