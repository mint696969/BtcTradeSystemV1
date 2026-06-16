# path: ./tools/test_phase4a_autotrade_milestone_l_ui_command_ledger_wiring_guard.py
# desc: Guard AutoTrade UI command buttons write command-request ledger only and never broker orders.

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"

FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)

REQUIRED_TOKENS = (
    "validate_and_append_command",
    "default_command_ledger_path",
    "read_command_ledger",
    "CommandRequest",
    "CommandType.REQUEST_EMERGENCY_FLATTEN",
    "CommandType.REQUEST_HALT_AND_CANCEL",
    "CommandType.REQUEST_HALT_NEW",
    "would_send_to_broker",
    "Last command ledger record",
    "Recent command ledger",
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
    text = PAGE.read_text(encoding="utf-8")
    imports = imports_from(PAGE)

    checks = {
        "required_tokens_present": all(token in text for token in REQUIRED_TOKENS),
        "uses_command_ledger_import": "btcts.autotrade.execution" in imports,
        "request_buttons_present": "HALT_NEW request" in text and "HALT_AND_CANCEL request" in text and "EMERGENCY_FLATTEN request" in text,
        "dangerous_confirmation_present": "Confirm emergency flatten request" in text and "Confirm halt+cancel request" in text,
        "ui_marks_no_broker_send": "would_send_to_broker" in text and "False" in text,
        "no_forbidden_tokens": not any(token in text for token in FORBIDDEN_TOKENS),
        "no_broker_imports": all("broker" not in item.lower() and item not in {"requests", "httpx", "ccxt", "pybitflyer"} for item in imports),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone L: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_l_ui_command_ledger_wiring_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "ui_writes_command_request_ledger": checks["required_tokens_present"] and checks["uses_command_ledger_import"],
            "dangerous_commands_require_confirmation_surface": checks["dangerous_confirmation_present"],
            "request_buttons_present": checks["request_buttons_present"],
            "ui_never_sends_broker": checks["ui_marks_no_broker_send"] and checks["no_forbidden_tokens"] and checks["no_broker_imports"],
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
