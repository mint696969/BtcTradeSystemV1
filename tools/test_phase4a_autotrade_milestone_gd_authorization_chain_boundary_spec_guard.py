# path: ./tools/test_phase4a_autotrade_milestone_gd_authorization_chain_boundary_spec_guard.py
# desc: Guard S115 authorization_request chain boundary spec is present, current, non-authorizing, and points to essential next work.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "docs/architecture/AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_CHAIN_BOUNDARY_SPEC_2026-06-18.md"
INDEX = REPO_ROOT / "docs/_INDEX.md"
SELF = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_gd_authorization_chain_boundary_spec_guard.py"
EXPECTED_SLICE_FILES = {
    "docs/architecture/AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_CHAIN_BOUNDARY_SPEC_2026-06-18.md",
    "docs/_INDEX.md",
    "tools/test_phase4a_autotrade_milestone_gd_authorization_chain_boundary_spec_guard.py",
}
REQUIRED_SPEC_FRAGMENTS = (
    "S111-S114",
    "What this chain guarantees",
    "What this chain does not permit",
    "ready_not_authorized_not_recorded_not_executed",
    "not an approval",
    "do not generate S115 as another recursive authorization_request",
    "5 cycles maximum",
    "Authorization grant design",
    "Record persistence",
    "Mode apply preview",
    "broker-free; no broker execution; no real orders",
    "no authorization grant",
    "no approval append",
    "no command ledger append",
    "no mode-change request",
)
FORBIDDEN_SPEC_FRAGMENTS = (
    "authorization granted",
    "live authorization granted",
    "send order",
    "place order",
    "broker execution permitted",
    "mode apply permitted",
)
REQUIRED_INDEX_FRAGMENT = "AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_CHAIN_BOUNDARY_SPEC_2026-06-18.md"


def _syntax(path: Path, failures: list[str]) -> dict[str, object]:
    if not path.exists():
        failures.append(f"missing syntax target: {path.relative_to(REPO_ROOT)}")
        return {"ok": False, "missing": True}
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return {"ok": True}
    except Exception as exc:
        failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
        return {"ok": False, "error": str(exc)}


def _git_boundary(failures: list[str]) -> dict[str, object]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    unexpected: list[str] = []
    for line in lines:
        rel = (line[3:] if len(line) > 3 else line).replace(chr(92), "/")
        if rel not in EXPECTED_SLICE_FILES:
            unexpected.append(line)
    failures.extend(f"unexpected dirty file during S115 spec guard: {line}" for line in unexpected)
    return {"lines": lines, "unexpected": unexpected, "expected_slice_files": sorted(EXPECTED_SLICE_FILES)}


def main() -> int:
    failures: list[str] = []
    syntax = {"self": _syntax(SELF, failures)}
    if not SPEC.exists():
        failures.append(f"missing spec: {SPEC.relative_to(REPO_ROOT)}")
        spec_text = ""
    else:
        spec_text = SPEC.read_text(encoding="utf-8")
    missing = [frag for frag in REQUIRED_SPEC_FRAGMENTS if frag not in spec_text]
    forbidden = [frag for frag in FORBIDDEN_SPEC_FRAGMENTS if frag.lower() in spec_text.lower()]
    failures.extend(f"spec missing required fragment: {frag}" for frag in missing)
    failures.extend(f"spec contains forbidden fragment: {frag}" for frag in forbidden)

    index_text = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    index_has_spec = REQUIRED_INDEX_FRAGMENT in index_text
    if not index_has_spec:
        failures.append("docs/_INDEX.md missing authorization chain boundary spec link")

    git_boundary = _git_boundary(failures)
    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gd_authorization_request_chain_boundary_spec_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "spec_present": SPEC.exists(),
            "spec_required_fragments_present": not missing,
            "spec_forbidden_fragments_absent": not forbidden,
            "index_link_present": index_has_spec,
            "syntax_checked_without_pyc": all(item.get("ok") is True for item in syntax.values()),
            "expected_git_boundary_only": not git_boundary.get("unexpected"),
            "chain_stop_policy_present": "do not generate S115 as another recursive authorization_request" in spec_text and "5 cycles maximum" in spec_text,
            "next_essential_boundaries_present": all(fragment in spec_text for fragment in ("Authorization grant design", "Record persistence", "Mode apply preview")),
        },
        "missing": missing,
        "forbidden": forbidden,
        "syntax": syntax,
        "git_boundary": git_boundary,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
