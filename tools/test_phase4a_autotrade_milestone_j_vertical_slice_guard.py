# path: ./tools/test_phase4a_autotrade_milestone_j_vertical_slice_guard.py
# desc: Guard AutoTrade end-to-end shadow/paper/armed-dry-run vertical slice remains broker-free.

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.config import initial_parameter_set_v0_1  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.pipeline import run_shadow_paper_dry_run_vertical_slice  # noqa: E402
from btcts.autotrade.read_model import build_snapshot_id  # noqa: E402
from btcts.autotrade.read_model.models import (  # noqa: E402
    AutoTradeSnapshot,
    Confidence,
    CurrentMarketInputs,
    GroundDirection,
    GroundState,
    SnapshotUsability,
    TemporalFlowFeatures,
)
from btcts.autotrade.replay import PaperExecutionEngine  # noqa: E402
from btcts.autotrade.risk import KillSwitchState, RuntimeHealthState  # noqa: E402

FORBIDDEN_TOKENS = (
    "place_order(", "send_order(", "broker_order(", "private_api", "pybitflyer", "ccxt", "requests.post", "httpx.post",
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


def snapshot(*, fresh: bool = True) -> AutoTradeSnapshot:
    ps = initial_parameter_set_v0_1()
    created_at = "2026-06-12T12:00:00Z"
    sid = build_snapshot_id(market_uid="bitflyer:BTC_JPY_FX", created_at=created_at, parameter_set_id=ps.parameter_set_id, effective_event_ts="2026-06-12T11:59:59Z")
    return AutoTradeSnapshot(
        snapshot_id=sid,
        created_at=created_at,
        market_uid="bitflyer:BTC_JPY_FX",
        parameter_set_id=ps.parameter_set_id,
        logic_version=ps.logic_version,
        effective_event_ts="2026-06-12T11:59:59Z",
        ground=GroundState(direction=GroundDirection.SELL_LEANING, confidence=Confidence.MEDIUM),
        usability=SnapshotUsability(regime=True, liquidity=True, trade=fresh, l4=True, temporal=fresh),
        inputs=CurrentMarketInputs(spread=4500.0, trade_delta=-2.0, mid_price=10000000.0),
        temporal_flow=TemporalFlowFeatures(
            windows_sec=ps.temporal_flow.windows_sec,
            generated_at=created_at,
            usable=fresh,
            temporal_pressure_flow={"pressure_acceleration": "sell"},
            temporal_price_flow={"mid_return_300s": -0.001},
            temporal_pattern_flags={"liquidity_vacuum_candidate": False},
        ),
        stale_reasons=() if fresh else ("trade_stale",),
    )


def main() -> int:
    failures: list[str] = []
    ps = initial_parameter_set_v0_1()
    fresh = snapshot(fresh=True)
    stale = snapshot(fresh=False)
    engine = PaperExecutionEngine()
    runtime_clean = RuntimeHealthState(True, True, True, True, True, True, broker_reachable=False, reconciliation_clean=True)
    kill_clear = KillSwitchState(active=False, source="guard")

    shadow = run_shadow_paper_dry_run_vertical_slice(snapshot=fresh, parameter_set=ps, mode=AutoTradeMode.SHADOW)
    paper = run_shadow_paper_dry_run_vertical_slice(snapshot=fresh, parameter_set=ps, mode=AutoTradeMode.PAPER_OR_REPLAY, paper_engine=engine)
    paper_duplicate = run_shadow_paper_dry_run_vertical_slice(snapshot=fresh, parameter_set=ps, mode=AutoTradeMode.PAPER_OR_REPLAY, paper_engine=engine)
    dry = run_shadow_paper_dry_run_vertical_slice(snapshot=fresh, parameter_set=ps, mode=AutoTradeMode.ARMED_DRY_RUN, runtime=runtime_clean, kill_switch=kill_clear)
    stale_shadow = run_shadow_paper_dry_run_vertical_slice(snapshot=stale, parameter_set=ps, mode=AutoTradeMode.SHADOW)

    pipeline_path = REPO_ROOT / "btcts_next/src/btcts/autotrade/pipeline.py"
    pipeline_text = pipeline_path.read_text(encoding="utf-8")
    imports = imports_from(pipeline_path)

    checks = {
        "shadow_has_decision": shadow.shadow_decision_id.startswith("dec_") and shadow.forecast_id.startswith("fcst_"),
        "shadow_no_broker_send": shadow.would_send_to_broker is False and shadow.paper_order_status is None,
        "paper_creates_order": paper.paper_order_status == "accepted" and len(engine.orders_by_decision_id) == 1,
        "paper_duplicate_idempotent": paper_duplicate.paper_order_status == "accepted" and len(engine.orders_by_decision_id) == 1,
        "dry_run_accepts_but_never_sends": dry.dry_run_accepted is True and dry.would_send_to_broker is False,
        "stale_blocks_to_abstention": stale_shadow.abstention_class == "safety_blocked" and stale_shadow.order_intent is None,
        "entry_candidate_present": paper.candidate_action == "ENTRY_SELL",
        "order_intent_has_links": paper.order_intent is not None and paper.order_intent.decision_id == paper.shadow_decision_id and paper.order_intent.forecast_id == paper.forecast_id,
        "json_safe": json.loads(json.dumps(paper.to_dict(), ensure_ascii=False))["would_send_to_broker"] is False,
        "no_forbidden_tokens": not any(token in pipeline_text for token in FORBIDDEN_TOKENS),
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
    failures.extend(f"protected lower-layer dirty during milestone J: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_j_vertical_slice_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "shadow_vertical_slice_present": checks["shadow_has_decision"],
            "paper_vertical_slice_present": checks["paper_creates_order"] and checks["paper_duplicate_idempotent"],
            "armed_dry_run_vertical_slice_present": checks["dry_run_accepts_but_never_sends"],
            "stale_fail_closed_present": checks["stale_blocks_to_abstention"],
            "no_broker_execution_path": checks["no_forbidden_tokens"] and checks["no_broker_imports"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "shadow": shadow.to_dict(),
        "paper": paper.to_dict(),
        "dry": dry.to_dict(),
        "stale_shadow": stale_shadow.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
