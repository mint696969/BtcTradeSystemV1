# path: ./tools/test_phase4a_autotrade_milestone_a_boundary_guard.py
# desc: Guard AutoTrade milestone A package skeleton, responsibility boundaries, and import direction.

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.boundary import (  # noqa: E402
    FORBIDDEN_AUTOTRADE_IMPORTS,
    FORBIDDEN_UPSTREAM_IMPORTERS,
    boundary_names,
)
from btcts.autotrade.modes import (  # noqa: E402
    AutoTradeMode,
    HumanControlMode,
    default_human_control_for_mode,
    is_transition_allowed,
    requires_human_confirmation,
)

REQUIRED_PATHS = (
    "btcts_next/src/btcts/autotrade/__init__.py",
    "btcts_next/src/btcts/autotrade/README.md",
    "btcts_next/src/btcts/autotrade/boundary.py",
    "btcts_next/src/btcts/autotrade/modes.py",
    "btcts_next/src/btcts/autotrade/config/__init__.py",
    "btcts_next/src/btcts/autotrade/read_model/__init__.py",
    "btcts_next/src/btcts/autotrade/strategy/__init__.py",
    "btcts_next/src/btcts/autotrade/risk/__init__.py",
    "btcts_next/src/btcts/autotrade/execution/__init__.py",
    "btcts_next/src/btcts/autotrade/ledger/__init__.py",
    "btcts_next/src/btcts/autotrade/replay/__init__.py",
    "btcts_next/src/btcts/autotrade/tests/__init__.py",
)

EXPECTED_BOUNDARIES = {"read_model", "strategy", "risk", "execution", "ledger"}
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def imports_from_file(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        raise
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def file_has_import(path: Path, module_prefix: str) -> bool:
    return any(name == module_prefix or name.startswith(module_prefix + ".") for name in imports_from_file(path))


def main() -> int:
    failures: list[str] = []

    missing = [rel for rel in REQUIRED_PATHS if not (REPO_ROOT / rel).exists()]
    failures.extend(f"missing required path: {rel}" for rel in missing)

    observed_boundaries = set(boundary_names())
    if observed_boundaries != EXPECTED_BOUNDARIES:
        failures.append(f"unexpected boundary names: {sorted(observed_boundaries)}")

    mode_checks = {
        "off_to_shadow_without_confirm": is_transition_allowed(AutoTradeMode.OFF, AutoTradeMode.SHADOW, human_confirmed=False),
        "armed_to_live_requires_confirm": not is_transition_allowed(AutoTradeMode.ARMED_DRY_RUN, AutoTradeMode.LIVE_MIN_SIZE, human_confirmed=False),
        "armed_to_live_with_confirm": is_transition_allowed(AutoTradeMode.ARMED_DRY_RUN, AutoTradeMode.LIVE_MIN_SIZE, human_confirmed=True),
        "halted_to_shadow_requires_confirm": not is_transition_allowed(AutoTradeMode.HALTED, AutoTradeMode.SHADOW, human_confirmed=False),
        "live_default_manual": default_human_control_for_mode(AutoTradeMode.LIVE_MIN_SIZE) == HumanControlMode.MANUAL_APPROVE,
        "shadow_default_auto": default_human_control_for_mode(AutoTradeMode.SHADOW) == HumanControlMode.AUTO_ALLOWED,
        "dangerous_mode_requires_confirmation": requires_human_confirmation(AutoTradeMode.ARMED_DRY_RUN, AutoTradeMode.LIVE_MIN_SIZE),
    }
    failures.extend(f"mode check failed: {name}" for name, ok in mode_checks.items() if not ok)

    upstream_import_hits: list[str] = []
    for prefix in FORBIDDEN_UPSTREAM_IMPORTERS:
        root = REPO_ROOT / prefix
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if file_has_import(path, "btcts.autotrade"):
                upstream_import_hits.append(str(path.relative_to(REPO_ROOT)))
    failures.extend(f"upstream layer imports autotrade: {hit}" for hit in upstream_import_hits)

    autotrade_import_hits: list[str] = []
    for folder, forbidden_module in FORBIDDEN_AUTOTRADE_IMPORTS:
        root = REPO_ROOT / "btcts_next/src/btcts/autotrade" / folder
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if file_has_import(path, forbidden_module):
                autotrade_import_hits.append(f"{path.relative_to(REPO_ROOT)} imports {forbidden_module}")
    failures.extend(f"forbidden autotrade dependency: {hit}" for hit in autotrade_import_hits)

    protected_dirty_hits: list[str] = []
    # Milestone A should not require editing lower-layer owner dirs.
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone A: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_a_boundary_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "package_skeleton_present": not missing,
            "boundary_names_present": observed_boundaries == EXPECTED_BOUNDARIES,
            "mode_state_machine_basics": all(mode_checks.values()),
            "upstream_layers_do_not_import_autotrade": not upstream_import_hits,
            "autotrade_forbidden_dependencies_absent": not autotrade_import_hits,
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "mode_checks": mode_checks,
        "missing": missing,
        "upstream_import_hits": upstream_import_hits,
        "autotrade_import_hits": autotrade_import_hits,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
