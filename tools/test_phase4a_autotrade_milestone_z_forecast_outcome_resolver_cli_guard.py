# path: ./tools/test_phase4a_autotrade_milestone_z_forecast_outcome_resolver_cli_guard.py
# desc: Guard forecast outcome resolver one-shot CLI resolves due forecasts and never brokers.

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.ledger import read_forecast_outcome_links  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402
from btcts.core.env import ENV_DATA_DIR  # noqa: E402

CLI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_resolve_forecast_outcomes_once.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "btcts.apps.operator_ui",
    "streamlit",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "run_latest_market_state_shadow_decision",
    "run_shadow_decision_from_snapshot",
    "append_decision_jsonl",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
    "while True",
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


def actual_row(ts: datetime, *, reason: str, mid: int) -> dict:
    text = ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "collector_ts": text,
        "exchange_ts": text,
        "exchange": "bitflyer",
        "symbol_raw": "BTC_JPY",
        "market_uid": "bitflyer.spot.BTC_JPY",
        "mid_price": mid,
        "imbalance": -0.3 if "sell" in reason else 0.3,
        "wall_ratio": -0.5 if "sell" in reason else 0.5,
        "spread": 4200,
        "trade_delta": -1.2 if "sell" in reason else 1.2,
        "trust_state": "trusted",
        "continuity_state": "continuous",
        "interpretation_bucket": "allow_structural_use",
        "interpretation_reason": reason,
    }


def write_market_state_file(data_root: Path, rows: list[dict]) -> Path:
    latest_ts = datetime.fromisoformat(rows[-1]["collector_ts"].replace("Z", "+00:00"))
    date_dir = data_root / "market_state/exchange=bitflyer/symbol=BTC_JPY/type=market.overview" / f"date={latest_ts.date().isoformat()}"
    date_dir.mkdir(parents=True, exist_ok=True)
    part = date_dir / "part-0000.jsonl"
    part.write_text(chr(10).join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + chr(10), encoding="utf-8")
    return part


def shadow_row(decision_id: str, *, target_ts: str, direction: str = "down") -> dict:
    return {
        "decision_id": decision_id,
        "mode": "SHADOW",
        "snapshot_id": f"snap_{decision_id}",
        "forecast_id": f"fcst_{decision_id}",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {
            "forecast_id": f"fcst_{decision_id}",
            "created_at": "2026-06-13T00:00:00Z",
            "target_ts": target_ts,
            "source_snapshot_id": f"snap_{decision_id}",
            "parameter_set_id": "params_fx_balanced_v0_1",
            "logic_version": "autotrade_logic_v0_1",
            "forecast_direction": direction,
            "expected_change": "strengthen_sell",
            "confidence": "medium",
            "drivers": ["sell_pressure_or_ground"],
            "blocked_by": [],
        },
        "candidate": {"action": "ENTRY_SELL", "entry_quality": 100},
        "risk_gate": {"allowed": True, "executable": False, "blocked_by": []},
        "final_action": "ENTRY_SELL",
        "reason_codes": ["forecast_aligned_sell"],
        "blocked_by": [],
        "would_order": None,
    }


def parse_cli_json(stdout: str) -> dict:
    return json.loads(stdout)


def main() -> int:
    failures: list[str] = []
    original_data = os.environ.get(ENV_DATA_DIR)
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    data_root = REPO_ROOT / "tmp/_autotrade_z_data"
    hot_root = REPO_ROOT / "tmp/_autotrade_hot_z_guard"
    shadow_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
    outcome_path = hot_root / "autotrade/decisions/forecast_outcomes.jsonl"
    try:
        os.environ[ENV_DATA_DIR] = str(data_root)
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        if outcome_path.exists():
            outcome_path.unlink()
        base = datetime.now(timezone.utc).replace(microsecond=0)
        target = base - timedelta(seconds=90)
        rows = [
            actual_row(target - timedelta(seconds=30), reason="ask_pressure sell", mid=9990000),
            actual_row(target + timedelta(seconds=5), reason="ask_pressure sell", mid=9989000),
            actual_row(base, reason="bid_pressure buy", mid=10020000),
        ]
        part = write_market_state_file(data_root, rows)
        shadow_path.parent.mkdir(parents=True, exist_ok=True)
        target_text = target.isoformat().replace("+00:00", "Z")
        future_target = (base + timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
        shadow_path.write_text(
            chr(10).join(
                json.dumps(row, ensure_ascii=False, sort_keys=True)
                for row in (
                    shadow_row("cli_due_hit", target_ts=target_text, direction="down"),
                    shadow_row("cli_future_skip", target_ts=future_target, direction="down"),
                )
            ) + chr(10),
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        cmd = [
            sys.executable,
            "-m",
            "btcts.apps.autotrade_resolve_forecast_outcomes_once",
            "--max-actual-match-age-sec",
            "45",
        ]
        proc1 = subprocess.run(cmd, cwd=REPO_ROOT, env=env, text=True, capture_output=True)
        payload1 = parse_cli_json(proc1.stdout) if proc1.stdout.strip() else {}
        links1 = read_forecast_outcome_links()
        proc2 = subprocess.run(cmd, cwd=REPO_ROOT, env=env, text=True, capture_output=True)
        payload2 = parse_cli_json(proc2.stdout) if proc2.stdout.strip() else {}
        links2 = read_forecast_outcome_links()
        no_persist_cmd = cmd + ["--no-persist"]
        proc3 = subprocess.run(no_persist_cmd, cwd=REPO_ROOT, env=env, text=True, capture_output=True)
        payload3 = parse_cli_json(proc3.stdout) if proc3.stdout.strip() else {}
        links3 = read_forecast_outcome_links()
    finally:
        if original_data is None:
            os.environ.pop(ENV_DATA_DIR, None)
        else:
            os.environ[ENV_DATA_DIR] = original_data
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = CLI_FILE.read_text(encoding="utf-8")
    imports = imports_from(CLI_FILE)
    checks = {
        "market_state_part_written": part.exists() and "market_state" in part.parts,
        "cli_exit_zero": proc1.returncode == 0 and proc2.returncode == 0 and proc3.returncode == 0,
        "cli_appended_due_once": payload1.get("due_count") == 1 and payload1.get("appended_count") == 1 and len(links1) == 1,
        "cli_dedupes_second_run": payload2.get("appended_count") == 0 and payload2.get("duplicate_skipped_count") == 1 and len(links2) == 1,
        "cli_no_persist_does_not_append": payload3.get("appended_count") == 0 and len(links3) == 1,
        "cli_uses_target_time_actual": links1 and links1[0].result == "hit" and links1[0].forecast_id == "fcst_cli_due_hit",
        "cli_no_loop_no_broker": payload1.get("would_send_to_broker") is False and payload1.get("read_only_inputs") is True,
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in imports) and "streamlit" not in imports,
        "no_forbidden_tokens": not any(token in text for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if proc1.returncode != 0:
        failures.append(f"proc1 stderr: {proc1.stderr}")
    if proc2.returncode != 0:
        failures.append(f"proc2 stderr: {proc2.stderr}")
    if proc3.returncode != 0:
        failures.append(f"proc3 stderr: {proc3.stderr}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone Z: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_z_forecast_outcome_resolver_cli_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "forecast_outcome_resolver_cli_present": checks["cli_exit_zero"] and checks["cli_appended_due_once"],
            "target_time_actual_matching_preserved": checks["cli_uses_target_time_actual"],
            "duplicate_resolution_suppressed": checks["cli_dedupes_second_run"],
            "no_persist_supported": checks["cli_no_persist_does_not_append"],
            "one_shot_no_loop_no_broker": checks["cli_no_loop_no_broker"],
            "read_only_no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "part": str(part),
        "outcome_path": str(outcome_path),
        "first": payload1,
        "second": payload2,
        "no_persist": payload3,
        "links": [link.to_dict() for link in links3],
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
