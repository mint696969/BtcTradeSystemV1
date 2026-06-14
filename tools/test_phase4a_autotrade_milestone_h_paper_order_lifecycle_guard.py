# path: ./tools/test_phase4a_autotrade_milestone_h_paper_order_lifecycle_guard.py
# desc: Guard AutoTrade milestone H paper/replay order lifecycle stays simulation-only and idempotent.

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import OrderType, PaperOrderStatus, build_order_intent_from_decision  # noqa: E402
from btcts.autotrade.replay import PaperExecutionEngine, is_terminal_status  # noqa: E402

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
    "btcts_next/src/btcts/autotrade/execution/intents.py",
    "btcts_next/src/btcts/autotrade/execution/order_state.py",
    "btcts_next/src/btcts/autotrade/replay/paper_engine.py",
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

    intent = build_order_intent_from_decision(
        decision_id="dec_test_001",
        snapshot_id="snap_test_001",
        forecast_id="fcst_test_001",
        parameter_set_id="params_fx_balanced_v0_1",
        logic_version="autotrade_logic_v0_1",
        side="sell",
        size=0.01,
        price=10000000.0,
        reason_codes=("forecast_aligned_sell", "entry_threshold_met"),
        risk_gate_allowed=True,
        mode="PAPER_OR_REPLAY",
        order_type=OrderType.LIMIT,
    )
    blocked_intent = build_order_intent_from_decision(
        decision_id="dec_test_blocked",
        snapshot_id="snap_test_002",
        forecast_id="fcst_test_002",
        parameter_set_id="params_fx_balanced_v0_1",
        logic_version="autotrade_logic_v0_1",
        side="buy",
        size=0.01,
        price=9999000.0,
        reason_codes=("stale_input",),
        risk_gate_allowed=False,
        mode="PAPER_OR_REPLAY",
    )

    engine = PaperExecutionEngine()
    order = engine.submit_intent(intent, ts="2026-06-12T12:00:00Z")
    duplicate = engine.submit_intent(intent, ts="2026-06-12T12:00:01Z")
    filled = engine.fill(intent.decision_id, ts="2026-06-12T12:00:02Z", fill_price=9999500.0)
    cancel_after_fill = engine.cancel(intent.decision_id, ts="2026-06-12T12:00:03Z", reason="should_not_change_filled")
    blocked = engine.submit_intent(blocked_intent, ts="2026-06-12T12:00:04Z")

    cancel_intent = build_order_intent_from_decision(
        decision_id="dec_test_cancel",
        snapshot_id="snap_test_003",
        forecast_id=None,
        parameter_set_id="params_fx_balanced_v0_1",
        logic_version="autotrade_logic_v0_1",
        side="buy",
        size=0.01,
        price=9998000.0,
        reason_codes=("watch_threshold_met",),
        risk_gate_allowed=True,
        mode="PAPER_OR_REPLAY",
    )
    cancel_order = engine.submit_intent(cancel_intent, ts="2026-06-12T12:00:05Z")
    canceled = engine.cancel(cancel_intent.decision_id, ts="2026-06-12T12:00:06Z", reason="forecast_flip")

    counts = engine.status_counts()

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
        "intent_has_decision_link": intent.decision_id == "dec_test_001" and intent.forecast_id == "fcst_test_001",
        "paper_order_accepted": order.status == PaperOrderStatus.ACCEPTED,
        "duplicate_decision_id_idempotent": duplicate.order_id == order.order_id and len(engine.orders_by_decision_id) == 3,
        "fill_transition": filled is not None and filled.status == PaperOrderStatus.FILLED and filled.filled_size == intent.size,
        "terminal_fill_not_canceled": cancel_after_fill is not None and cancel_after_fill.status == PaperOrderStatus.FILLED,
        "risk_blocked_rejected": blocked.status == PaperOrderStatus.REJECTED and blocked.reject_reason == "risk_gate_not_allowed",
        "cancel_transition": canceled is not None and canceled.status == PaperOrderStatus.CANCELED and canceled.cancel_reason == "forecast_flip",
        "terminal_status_helper": is_terminal_status(PaperOrderStatus.FILLED) and is_terminal_status(PaperOrderStatus.CANCELED),
        "status_counts": counts.get("filled") == 1 and counts.get("rejected") == 1 and counts.get("canceled") == 1,
        "json_safe_order": json.loads(json.dumps(filled.to_dict(), ensure_ascii=False))["intent"]["decision_id"] == intent.decision_id if filled else False,
        "no_forbidden_tokens": no_forbidden_tokens,
        "no_broker_imports": no_broker_imports,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone H: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_h_paper_order_lifecycle_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "order_intent_contract_present": checks["intent_has_decision_link"],
            "paper_lifecycle_present": checks["paper_order_accepted"] and checks["fill_transition"] and checks["cancel_transition"],
            "duplicate_decision_id_idempotent": checks["duplicate_decision_id_idempotent"],
            "risk_blocked_rejected": checks["risk_blocked_rejected"],
            "simulation_only_no_broker": checks["no_forbidden_tokens"] and checks["no_broker_imports"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "status_counts": counts,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
