# path: ./tools/test_phase4a_autotrade_milestone_ge_authorization_grant_design_spec_guard.py
# desc: Guard S116 authorization grant design spec is spec-only, non-executing, and points to grant status dry-run rather than append/mode/broker execution.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "docs/architecture/AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_DESIGN_SPEC_2026-06-18.md"
INDEX = REPO_ROOT / "docs/_INDEX.md"
SELF = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_ge_authorization_grant_design_spec_guard.py"
CHAIN_SPEC = REPO_ROOT / "docs/architecture/AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_CHAIN_BOUNDARY_SPEC_2026-06-18.md"
EXPECTED_SLICE_FILES = {
    "docs/architecture/AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_DESIGN_SPEC_2026-06-18.md",
    "docs/_INDEX.md",
    "tools/test_phase4a_autotrade_milestone_ge_authorization_grant_design_spec_guard.py",
}
REQUIRED_SPEC_FRAGMENTS = (
    "Specification-only boundary after S115",
    "no implementation grant yet",
    "S114: authorization request/status packet chain stop",
    "S115: authorization_request chain boundary spec",
    "Ready is not approval",
    "A status packet becoming ready must never create a grant by itself",
    "source_authorization_request_status_path",
    "confirm_ready_status_is_not_itself_approval",
    "confirm_grant_is_explicit_human_decision",
    "confirm_grant_does_not_send_orders",
    "confirm_grant_does_not_apply_mode",
    "confirm_record_persistence_or_mode_apply_requires_separate_slice",
    "Explicit non-permissions",
    "authorization_grant_granted=False",
    "authorization_grant_executed=False",
    "authorization_grant_recorded=False",
    "approval_ledger_appended=False",
    "command_ledger_appended=False",
    "mode_change_requested=False",
    "would_send_to_broker=False",
    "pre_armed_dry_run_authorized=False",
    "live_authorized=False",
    "Relationship to record persistence",
    "Relationship to mode apply preview",
    "S117: authorization grant status dry-run packet",
)
FORBIDDEN_SPEC_FRAGMENTS = (
    "grant is approved",
    "grant has been approved",
    "broker execution permitted",
    "orders may be sent",
    "mode apply is permitted",
    "append execution is permitted",
    "UI command button enabled",
)
REQUIRED_INDEX_FRAGMENT = "AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_DESIGN_SPEC_2026-06-18.md"


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
    failures.extend(f"unexpected dirty file during S116 grant design spec guard: {line}" for line in unexpected)
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
        failures.append("docs/_INDEX.md missing authorization grant design spec link")
    chain_spec_present = CHAIN_SPEC.exists()
    if not chain_spec_present:
        failures.append("missing S115 chain boundary spec anchor")

    spec_only_no_append_no_mode_no_broker = all(fragment in spec_text for fragment in (
        "no implementation grant yet",
        "no grant append",
        "no record persistence",
        "no mode apply",
        "no broker execution",
        "no UI command buttons",
    ))
    if not spec_only_no_append_no_mode_no_broker:
        failures.append("spec-only no-append/no-mode/no-broker contract must be explicit")

    git_boundary = _git_boundary(failures)
    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ge_authorization_grant_design_spec_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "spec_present": SPEC.exists(),
            "s115_chain_spec_anchor_present": chain_spec_present,
            "spec_required_fragments_present": not missing,
            "spec_forbidden_fragments_absent": not forbidden,
            "index_link_present": index_has_spec,
            "syntax_checked_without_pyc": all(item.get("ok") is True for item in syntax.values()),
            "expected_git_boundary_only": not git_boundary.get("unexpected"),
            "spec_only_no_append_no_mode_no_broker": spec_only_no_append_no_mode_no_broker,
            "next_slice_is_grant_status_dry_run": "S117: authorization grant status dry-run packet" in spec_text,
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
