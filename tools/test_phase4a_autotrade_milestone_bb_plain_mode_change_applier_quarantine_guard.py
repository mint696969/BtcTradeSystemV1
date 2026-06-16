# path: ./tools/test_phase4a_autotrade_milestone_bb_plain_mode_change_applier_quarantine_guard.py
# desc: Guard plain mode-change applier is quarantined from apps/UI. Default runtime entry points use readiness recheck.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

APP_ROOT = REPO_ROOT / "btcts_next/src/btcts/apps"
UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
DEFAULT_CLI = REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_apply_mode_change_once.py"
RECHECKED_CLI = REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_apply_mode_change_rechecked_once.py"
RECHECKED_PREVIEW_CLI = REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_preview_mode_change_rechecked_once.py"
APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
EXEC_INIT = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/__init__.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
PLAIN_NAME = "apply_latest_mode_change_command_once"
RECHECKED_NAME = "apply_latest_mode_change_command_once_with_readiness_recheck"
RECHECKED_PREVIEW_NAME = "preview_latest_mode_change_command_apply_with_readiness_recheck"
PLAIN_ALLOWED_FILES = {
    str(APPLIER_FILE.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(EXEC_INIT.relative_to(REPO_ROOT)).replace("\\", "/"),
}
PLAIN_FUNCTION_FORBIDDEN_TOKENS = (
    "btcts.apps.operator_ui",
    "streamlit",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def imported_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
    return names


def called_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.add(func.id)
            elif isinstance(func, ast.Attribute):
                calls.add(func.attr)
    return calls


def app_py_files() -> list[Path]:
    return sorted(path for path in APP_ROOT.rglob("*.py") if path.is_file())


def main() -> int:
    failures: list[str] = []
    apps_importing_plain: list[str] = []
    apps_calling_plain: list[str] = []
    for path in app_py_files():
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        imports = imported_names(path)
        calls = called_names(path)
        if PLAIN_NAME in imports:
            apps_importing_plain.append(rel)
        if PLAIN_NAME in calls:
            apps_calling_plain.append(rel)

    default_text = DEFAULT_CLI.read_text(encoding="utf-8")
    rechecked_text = RECHECKED_CLI.read_text(encoding="utf-8")
    rechecked_preview_text = RECHECKED_PREVIEW_CLI.read_text(encoding="utf-8")
    ui_text = UI_FILE.read_text(encoding="utf-8")
    applier_text = APPLIER_FILE.read_text(encoding="utf-8")
    exec_init_text = EXEC_INIT.read_text(encoding="utf-8")
    plain_source = function_source(APPLIER_FILE, PLAIN_NAME)

    default_imports = imported_names(DEFAULT_CLI)
    default_calls = called_names(DEFAULT_CLI)
    rechecked_imports = imported_names(RECHECKED_CLI)
    rechecked_calls = called_names(RECHECKED_CLI)
    rechecked_preview_imports = imported_names(RECHECKED_PREVIEW_CLI)
    rechecked_preview_calls = called_names(RECHECKED_PREVIEW_CLI)
    ui_imports = imported_names(UI_FILE)
    ui_calls = called_names(UI_FILE)

    checks = {
        "plain_function_exists_for_compatibility": bool(plain_source),
        "plain_function_quarantined_from_apps": not apps_importing_plain and not apps_calling_plain,
        "default_cli_uses_rechecked_applier": RECHECKED_NAME in default_imports and RECHECKED_NAME in default_calls and PLAIN_NAME not in default_imports and PLAIN_NAME not in default_calls,
        "rechecked_cli_uses_rechecked_applier": RECHECKED_NAME in rechecked_imports and RECHECKED_NAME in rechecked_calls and PLAIN_NAME not in rechecked_imports and PLAIN_NAME not in rechecked_calls,
        "rechecked_preview_cli_read_only": RECHECKED_PREVIEW_NAME in rechecked_preview_imports and RECHECKED_PREVIEW_NAME in rechecked_preview_calls and PLAIN_NAME not in rechecked_preview_imports and PLAIN_NAME not in rechecked_preview_calls and RECHECKED_NAME not in rechecked_preview_imports and RECHECKED_NAME not in rechecked_preview_calls,
        "operator_ui_does_not_import_or_call_plain_apply": PLAIN_NAME not in ui_imports and PLAIN_NAME not in ui_calls and RECHECKED_NAME not in ui_imports and RECHECKED_NAME not in ui_calls,
        "operator_ui_uses_rechecked_preview_only": RECHECKED_PREVIEW_NAME in ui_imports and RECHECKED_PREVIEW_NAME in ui_calls,
        "plain_function_no_ui_no_observer_no_broker": bool(plain_source) and not any(token in plain_source for token in PLAIN_FUNCTION_FORBIDDEN_TOKENS),
        "execution_package_exports_plain_only_for_compatibility": PLAIN_NAME in exec_init_text and RECHECKED_NAME in exec_init_text,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    for rel in apps_importing_plain:
        failures.append(f"app imports plain mode-change applier: {rel}")
    for rel in apps_calling_plain:
        failures.append(f"app calls plain mode-change applier: {rel}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BB: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bb_plain_mode_change_applier_quarantine_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "plain_function_exists_for_compatibility": checks["plain_function_exists_for_compatibility"],
            "plain_function_quarantined_from_apps": checks["plain_function_quarantined_from_apps"],
            "default_cli_uses_rechecked_applier": checks["default_cli_uses_rechecked_applier"],
            "rechecked_cli_uses_rechecked_applier": checks["rechecked_cli_uses_rechecked_applier"],
            "rechecked_preview_cli_read_only": checks["rechecked_preview_cli_read_only"],
            "operator_ui_uses_rechecked_preview_only": checks["operator_ui_uses_rechecked_preview_only"],
            "plain_function_no_ui_no_observer_no_broker": checks["plain_function_no_ui_no_observer_no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "apps_importing_plain": apps_importing_plain,
        "apps_calling_plain": apps_calling_plain,
        "checked_app_file_count": len(app_py_files()),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
