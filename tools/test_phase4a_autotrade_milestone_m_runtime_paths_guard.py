# path: ./tools/test_phase4a_autotrade_milestone_m_runtime_paths_guard.py
# desc: Guard AutoTrade hot/cold runtime path contract and command ledger routing.

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import default_command_ledger_path  # noqa: E402
from btcts.autotrade.runtime_paths import (  # noqa: E402
    ENV_AUTOTRADE_RUNTIME_ROOT,
    autotrade_runtime_path_diagnostics,
    autotrade_runtime_paths,
    command_ledger_path,
)

PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def main() -> int:
    failures: list[str] = []
    original = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(REPO_ROOT / "tmp/_autotrade_hot_guard")
        env_paths = autotrade_runtime_paths(ensure=False)
        env_diag = autotrade_runtime_path_diagnostics(expected_hot_runtime_root=REPO_ROOT / "tmp/_autotrade_hot_guard")
        env_command_path = command_ledger_path(ensure=False)

        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(REPO_ROOT / "tmp/_autotrade_cold_archive")
        cold_diag = autotrade_runtime_path_diagnostics(expected_hot_runtime_root=REPO_ROOT / "tmp/_autotrade_hot_guard")
    finally:
        if original is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original

    default_path = default_command_ledger_path(ensure=False)
    runtime_file = REPO_ROOT / "btcts_next/src/btcts/autotrade/runtime_paths.py"
    command_file = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_ledger.py"
    runtime_text = runtime_file.read_text(encoding="utf-8")
    command_text = command_file.read_text(encoding="utf-8")

    checks = {
        "env_runtime_root_respected": env_paths.runtime_root == (REPO_ROOT / "tmp/_autotrade_hot_guard").resolve(),
        "env_command_path_under_autotrade": env_command_path.name == "command_requests.jsonl" and "autotrade" in env_command_path.parts and "commands" in env_command_path.parts,
        "env_diag_json_safe": json.loads(json.dumps(env_diag.to_dict(), ensure_ascii=False))["paths"]["source"].startswith("env:"),
        "cold_archive_not_live_ready": cold_diag.live_ready is False and cold_diag.cold_runtime_detected is True,
        "default_command_ledger_uses_runtime_paths": "from btcts.autotrade.runtime_paths import command_ledger_path" in command_text,
        "runtime_contract_has_hot_default": "D:/btc_ts_hot" in runtime_text,
        "default_path_under_autotrade_commands": default_path.name == "command_requests.jsonl" and "autotrade" in default_path.parts and "commands" in default_path.parts,
        "no_broker_tokens": not any(token in runtime_text + command_text for token in ("place_order(", "send_order(", "broker_order(", "private_api", "pybitflyer", "ccxt", "requests.post", "httpx.post")),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone M: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_m_runtime_paths_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_runtime_paths_present": checks["env_runtime_root_respected"] and checks["env_command_path_under_autotrade"],
            "cold_archive_live_ready_block_present": checks["cold_archive_not_live_ready"],
            "command_ledger_routed_through_runtime_paths": checks["default_command_ledger_uses_runtime_paths"],
            "hot_default_present": checks["runtime_contract_has_hot_default"],
            "no_broker_execution_path": checks["no_broker_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "default_command_ledger_path": str(default_path),
        "env_diag": env_diag.to_dict(),
        "cold_diag": cold_diag.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
