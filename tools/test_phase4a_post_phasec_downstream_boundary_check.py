# path: ./tools/test_phase4a_post_phasec_downstream_boundary_check.py
# desc: Post Phase C downstream boundary check for L2 canonical public boundary usage.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]

COMPILE_TARGETS = [
    "btcts_next/src/btcts/replay/replay_pipeline.py",
    "btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_pipeline.py",
    "btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_signals.py",
    "btcts_next/src/btcts/processing/features/orderbook/book_features.py",
    "btcts_next/src/btcts/market_engine/onboarding/bitflyer_rebuild_review.py",
    "btcts_next/src/btcts/market_engine/market_state/live_orderbook_semantics.py",
    "btcts_next/src/btcts/collector_vnext/emit_rest.py",
    "btcts_next/src/btcts/collector_vnext/emit_ws.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py",
    "btcts_next/src/btcts/collector_vnext/transforms/board_structural_hints.py",
    "btcts_next/src/btcts/collector_vnext/transforms/trade_structural_hints.py",
]

DOWNSTREAM_ROOTS = [
    "btcts_next/src/btcts/replay",
    "btcts_next/src/btcts/processing",
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/apps",
]

ALLOWED_STRUCTURAL_HINT_HELPERS = {
    "btcts_next/src/btcts/collector_vnext/transforms/board_structural_hints.py",
    "btcts_next/src/btcts/collector_vnext/transforms/trade_structural_hints.py",
}


def _assert(cond: bool, message: str, failures: List[str]) -> None:
    if not cond:
        failures.append(message)


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []

    for rel_path in COMPILE_TARGETS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            failed.append({"path": rel_path, "error": "missing"})
            failures.append(f"compile target missing: {rel_path}")
            continue

        try:
            py_compile.compile(str(path), doraise=True)
            passed.append(rel_path)
        except Exception as exc:
            failed.append({"path": rel_path, "error": str(exc)})
            failures.append(f"py_compile failed: {rel_path}: {exc}")

    return {
        "passed_count": len(passed),
        "failed": failed,
    }


def _check_downstream_l2_public_boundary_imports(failures: List[str]) -> Dict[str, Any]:
    forbidden_fragments = [
        "btcts.ingestion.l2_canonical.orderbook.book_state",
        "btcts.ingestion.l2_canonical.orderbook.book_rebuilder",
        "btcts.ingestion.l2_canonical.orderbook.payload",
        "btcts.ingestion.l2_canonical.tradeflow.payload",
    ]

    hits: List[Dict[str, str]] = []

    for root_rel in DOWNSTREAM_ROOTS:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")

            for fragment in forbidden_fragments:
                if fragment in text:
                    hits.append({"path": rel, "fragment": fragment})
                    failures.append(
                        f"downstream must use btcts.ingestion.l2_canonical public boundary: {rel}: {fragment}"
                    )

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def _check_structural_hints_not_consumed_as_market_meaning(failures: List[str]) -> Dict[str, Any]:
    hint_fragments = [
        "integration_hint",
        "dedupe_hint",
        "completeness_hint",
        "origin_hint",
    ]

    hits: List[Dict[str, str]] = []

    src_root = REPO_ROOT / "btcts_next" / "src"
    for path in src_root.rglob("*.py"):
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        if rel in ALLOWED_STRUCTURAL_HINT_HELPERS:
            continue

        text = path.read_text(encoding="utf-8")
        for fragment in hint_fragments:
            if fragment in text:
                hits.append({"path": rel, "fragment": fragment})
                failures.append(
                    f"structural hint must not be consumed as downstream market meaning: {rel}: {fragment}"
                )

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def _check_collector_canonical_shape_drift(failures: List[str]) -> Dict[str, Any]:
    """Detect collector-side re-ownership of canonical payload shape.

    Do not ban generic status/audit keys such as "event_type" or "trade_id"
    everywhere. Those names can appear in audit/status/smoke payloads.
    This guard only bans canonical shape dict construction in collector
    adapter files where it would bypass L2 public boundary builders.
    """

    targets = {
        "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py": [
            '"event_type":',
            "'event_type':",
            '"snapshot_id":',
            "'snapshot_id':",
            '"base_snapshot_id":',
            "'base_snapshot_id':",
        ],
        "btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py": [
            '"event_type":',
            "'event_type':",
            '"snapshot_id":',
            "'snapshot_id':",
            '"base_snapshot_id":',
            "'base_snapshot_id':",
        ],
        "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py": [
            '"trade_id":',
            "'trade_id':",
            '"notional":',
            "'notional':",
            '"liquidity_role":',
            "'liquidity_role':",
        ],
        "btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py": [
            '"trade_id":',
            "'trade_id':",
            '"notional":',
            "'notional':",
            '"liquidity_role":',
            "'liquidity_role':",
        ],
    }

    hits: List[Dict[str, str]] = []

    for rel_path, forbidden_fragments in targets.items():
        path = REPO_ROOT / rel_path
        if not path.exists():
            failures.append(f"collector transform missing for drift guard: {rel_path}")
            hits.append({"path": rel_path, "fragment": "<file missing>"})
            continue

        text = path.read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            if fragment in text:
                hits.append({"path": rel_path, "fragment": fragment})
                failures.append(
                    f"collector transform must delegate canonical payload shape to L2 public boundary: {rel_path}: {fragment}"
                )

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def _check_collector_structural_hint_helper_usage(failures: List[str]) -> Dict[str, Any]:
    required_any = {
        "btcts_next/src/btcts/collector_vnext/emit_rest.py": [
            ["from .transforms.board_structural_hints import apply_board_structural_hints", "from .transforms.facade import ("],
            ["from .transforms.trade_structural_hints import apply_trade_structural_hints", "from .transforms.facade import ("],
            ["apply_board_structural_hints("],
            ["apply_trade_structural_hints("],
        ],
        "btcts_next/src/btcts/collector_vnext/emit_ws.py": [
            ["from .transforms.board_structural_hints import apply_board_structural_hints", "from .transforms.facade import ("],
            ["from .transforms.trade_structural_hints import apply_trade_structural_hints", "from .transforms.facade import ("],
            ["apply_board_structural_hints("],
            ["apply_trade_structural_hints("],
        ],
        "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py": [
            ["from .transforms.board_structural_hints import apply_board_structural_hints"],
            ["apply_board_structural_hints("],
        ],
        "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py": [
            ["from .transforms.trade_structural_hints import apply_trade_structural_hints"],
            ["apply_trade_structural_hints("],
        ],
    }

    missing: List[Dict[str, str]] = []

    for rel_path, fragment_groups in required_any.items():
        path = REPO_ROOT / rel_path
        if not path.exists():
            failures.append(f"collector structural hint consumer missing: {rel_path}")
            missing.append({"path": rel_path, "fragment": "<file missing>"})
            continue

        text = path.read_text(encoding="utf-8")
        for fragments in fragment_groups:
            if not any(fragment in text for fragment in fragments):
                label = " OR ".join(fragments)
                failures.append(f"collector structural hint helper usage missing: {rel_path}: {label}")
                missing.append({"path": rel_path, "fragment": label})

    return {
        "missing_count": len(missing),
        "missing": missing,
    }


def _check_public_import_presence(failures: List[str]) -> Dict[str, Any]:
    required = {
        "btcts_next/src/btcts/replay/replay_pipeline.py": [
            "from btcts.ingestion.l2_canonical import OrderBookRebuilder",
        ],
        "btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_pipeline.py": [
            "from btcts.ingestion.l2_canonical import OrderBookRebuilder, OrderBookState",
        ],
        "btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_signals.py": [
            "from btcts.ingestion.l2_canonical import OrderBookState",
        ],
        "btcts_next/src/btcts/processing/features/orderbook/book_features.py": [
            "from btcts.ingestion.l2_canonical import OrderBookState",
        ],
        "btcts_next/src/btcts/market_engine/onboarding/bitflyer_rebuild_review.py": [
            "from btcts.ingestion.l2_canonical import OrderBookRebuilder",
        ],
        "btcts_next/src/btcts/market_engine/market_state/live_orderbook_semantics.py": [
            "from btcts.ingestion.l2_canonical import OrderBookState",
        ],
    }

    missing: List[Dict[str, str]] = []

    for rel_path, fragments in required.items():
        path = REPO_ROOT / rel_path
        if not path.exists():
            failures.append(f"required downstream file missing: {rel_path}")
            missing.append({"path": rel_path, "fragment": "<file missing>"})
            continue

        text = path.read_text(encoding="utf-8")
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"downstream file missing public boundary import: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    return {
        "missing_count": len(missing),
        "missing": missing,
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    public_import_presence = _check_public_import_presence(failures)
    downstream_l2_imports = _check_downstream_l2_public_boundary_imports(failures)
    structural_hint_usage = _check_structural_hints_not_consumed_as_market_meaning(failures)
    collector_shape_drift = _check_collector_canonical_shape_drift(failures)
    collector_structural_hint_helper_usage = _check_collector_structural_hint_helper_usage(failures)

    summary = {
        "phase": "phase4a_post_phasec_downstream_boundary_check",
        "checks": {
            "compile": compile_result,
            "public_import_presence": public_import_presence,
            "downstream_l2_public_boundary_imports": downstream_l2_imports,
            "structural_hint_usage": structural_hint_usage,
            "collector_shape_drift": collector_shape_drift,
            "collector_structural_hint_helper_usage": collector_structural_hint_helper_usage,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())