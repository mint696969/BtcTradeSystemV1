# path: ./tools/test_phase4a_autotrade_milestone_g_operator_ui_tab_guard.py
# desc: Guard AutoTrade Operator UI tab is observer/control-request only and has no broker execution path.

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"

FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "broker_order(",
    "cancel_order(",
    "bitflyer_client",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)

REQUIRED_PAGE_TOKENS = (
    "def render():",
    "Critical State / Emergency",
    "Operation / Decision Visibility",
    "Settings / Parameter Set v0.1",
    "REQUEST_EMERGENCY_FLATTEN",
    "command_request_ledger",
    "execution_owner",
    "initial_parameter_set_v0_1",
    "Auto execution enabled preview",
    "Manual approval required preview",
)

PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def main() -> int:
    failures: list[str] = []
    app_text = APP.read_text(encoding="utf-8")
    page_text = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""

    checks = {
        "page_exists": PAGE.exists(),
        "app_imports_autotrade_page": "autotrade_page" in app_text,
        "app_page_defs_autotrade": '("autotrade", "AutoTrade", autotrade_page)' in app_text,
        "page_required_tokens": all(token in page_text for token in REQUIRED_PAGE_TOKENS),
        "page_no_forbidden_tokens": not any(token in page_text for token in FORBIDDEN_TOKENS),
        "page_imports_autotrade_config": "btcts.autotrade.config" in imports_from(PAGE) if PAGE.exists() else False,
        "page_imports_autotrade_modes": "btcts.autotrade.modes" in imports_from(PAGE) if PAGE.exists() else False,
        "page_does_not_import_execution": "btcts.autotrade.execution" not in imports_from(PAGE) if PAGE.exists() else False,
        "page_does_not_import_broker": all("broker" not in name.lower() for name in imports_from(PAGE)) if PAGE.exists() else False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone G: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_g_operator_ui_tab_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_page_registered": checks["page_exists"] and checks["app_imports_autotrade_page"] and checks["app_page_defs_autotrade"],
            "top_middle_lower_sections_present": checks["page_required_tokens"],
            "ui_command_preview_only": "ui_only_preview" in page_text and "accepted_by_ui" in page_text,
            "no_broker_execution_path": checks["page_no_forbidden_tokens"] and checks["page_does_not_import_execution"] and checks["page_does_not_import_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
