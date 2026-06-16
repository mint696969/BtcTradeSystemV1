# path: ./tools/test_phase4a_operator_ui_reload_whitening_readability_guard.py
# desc: Guard that reload whitening readability patch stays UI-only and widgetization remains frozen.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LIVE_SHELL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py"
DECISION = REPO_ROOT / "tmp/gpt_room/memory/decisions/2026-06-12_operator_ui_widgetization_freeze_and_reload_readability_decision.md"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/processing/",
    "btcts_next/src/btcts/market_engine/",
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/replay/",
)

REQUIRED_LIVE_SHELL_FRAGMENTS = [
    "B-8 reload whitening readability shield",
    "Widgetization is temporarily frozen",
    "background-color: transparent !important",
    "[data-testid=\"stSkeleton\"]",
    "[aria-busy=\"true\"]",
    "[data-testid=\"stMetric\"]",
]

REQUIRED_DECISION_FRAGMENTS = [
    "Freeze widgetization temporarily",
    "Fix only the white/fade readability problem during refresh",
    "L4/shared consumer model mutation",
    "Patch refresh readability minimally",
]


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, check=True)


def main() -> int:
    failures: list[str] = []
    live_shell_text = LIVE_SHELL.read_text(encoding="utf-8")
    decision_text = DECISION.read_text(encoding="utf-8") if DECISION.exists() else ""

    for fragment in REQUIRED_LIVE_SHELL_FRAGMENTS:
        if fragment not in live_shell_text:
            failures.append(f"live_shell missing fragment: {fragment}")

    for fragment in REQUIRED_DECISION_FRAGMENTS:
        if fragment not in decision_text:
            failures.append(f"decision missing fragment: {fragment}")

    diff_files = run(["git", "diff", "--name-only"]).stdout.splitlines()
    status_lines = run(["git", "status", "--short"]).stdout.splitlines()

    for rel in diff_files:
        if rel.startswith(PROTECTED_PREFIXES):
            failures.append(f"protected lower-layer diff detected: {rel}")

    for line in status_lines:
        rel = line[3:] if len(line) > 3 else line
        if rel.startswith(PROTECTED_PREFIXES):
            failures.append(f"protected lower-layer status detected: {line}")

    result = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_reload_whitening_readability_guard",
        "status": "closed" if not failures else "open",
        "reload_readability_contract": {
            "live_shell_reload_whitening_css_added": not failures,
            "widgetization_frozen": not failures,
            "lower_layers_untouched": not failures,
            "manual_smoke_required": True,
        },
        "diff_files": diff_files,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
