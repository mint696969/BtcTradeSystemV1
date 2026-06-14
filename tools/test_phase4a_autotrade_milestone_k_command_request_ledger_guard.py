# path: ./tools/test_phase4a_autotrade_milestone_k_command_request_ledger_guard.py
# desc: Guard AutoTrade command request ledger persistence is validation-only and broker-free.

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import (  # noqa: E402
    CommandRequest,
    CommandType,
    default_command_ledger_path,
    read_command_ledger,
    validate_and_append_command,
)

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

CHECK_FILES = (
    "btcts_next/src/btcts/autotrade/execution/command_ledger.py",
    "btcts_next/src/btcts/autotrade/execution/command_request.py",
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
    tmp_path = REPO_ROOT / "tmp/_autotrade_guard_milestone_k/command_requests.jsonl"
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    if tmp_path.exists():
        tmp_path.unlink()

    accepted_cmd = CommandRequest(
        command_id="cmd_accept_001",
        command_type=CommandType.REQUEST_HALT_NEW,
        requested_by="operator",
        requested_at="2026-06-12T12:00:00Z",
        current_mode="SHADOW",
        target="halt_new",
        confirmation=False,
        reason_codes=("operator_request",),
    )
    blocked_cmd = CommandRequest(
        command_id="cmd_block_001",
        command_type=CommandType.REQUEST_EMERGENCY_FLATTEN,
        requested_by="operator",
        requested_at="2026-06-12T12:00:01Z",
        current_mode="ARMED_DRY_RUN",
        target="flatten",
        confirmation=False,
        reason_codes=("operator_request",),
    )
    confirmed_cmd = CommandRequest(
        command_id="cmd_confirm_001",
        command_type=CommandType.REQUEST_EMERGENCY_FLATTEN,
        requested_by="operator",
        requested_at="2026-06-12T12:00:02Z",
        current_mode="ARMED_DRY_RUN",
        target="flatten",
        confirmation=True,
        reason_codes=("operator_request",),
    )

    r1 = validate_and_append_command(tmp_path, accepted_cmd)
    r2 = validate_and_append_command(tmp_path, blocked_cmd)
    r3 = validate_and_append_command(tmp_path, confirmed_cmd)
    rows = [json.loads(line) for line in tmp_path.read_text(encoding="utf-8").splitlines()]
    loaded = read_command_ledger(tmp_path)
    default_path = default_command_ledger_path(ensure=False)

    no_forbidden_tokens = True
    no_broker_imports = True
    for rel in CHECK_FILES:
        path = REPO_ROOT / rel
        text = path.read_text(encoding="utf-8")
        if any(token in text for token in FORBIDDEN_TOKENS):
            no_forbidden_tokens = False
        imports = imports_from(path)
        if any("broker" in item.lower() or item in {"requests", "httpx", "ccxt", "pybitflyer"} for item in imports):
            no_broker_imports = False

    checks = {
        "accepted_command_recorded": r1.accepted is True and rows[0]["accepted"] is True,
        "dangerous_unconfirmed_rejected": r2.accepted is False and "confirmation_required" in r2.blocked_by,
        "dangerous_confirmed_accepted": r3.accepted is True,
        "jsonl_three_lines": len(rows) == 3,
        "ledger_event_present": all(row.get("ledger_event") == "autotrade.command_request_validated" for row in rows),
        "command_id_preserved": rows[1]["command"]["command_id"] == "cmd_block_001",
        "loaded_roundtrip": len(loaded) == 3 and loaded[2].command.command_id == "cmd_confirm_001",
        "default_path_under_autotrade_commands": "autotrade" in default_path.parts and "commands" in default_path.parts and default_path.name == "command_requests.jsonl",
        "no_forbidden_tokens": no_forbidden_tokens,
        "no_broker_imports": no_broker_imports,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    import shutil
    shutil.rmtree(tmp_path.parent, ignore_errors=True)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone K: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_k_command_request_ledger_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "command_request_ledger_persistence_present": checks["jsonl_three_lines"] and checks["ledger_event_present"],
            "dangerous_command_confirmation_enforced": checks["dangerous_unconfirmed_rejected"] and checks["dangerous_confirmed_accepted"],
            "command_roundtrip_present": checks["loaded_roundtrip"],
            "default_path_under_autotrade_runtime": checks["default_path_under_autotrade_commands"],
            "validation_only_no_broker": checks["no_forbidden_tokens"] and checks["no_broker_imports"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "default_path": str(default_path),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
