# path: ./tools/audit_phase4a_phase_f_collector_transform_usage.py
# desc: Read-only Phase F usage audit for collector transform migration prep.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "tmp" / "work" / "phase4a_phase_f_collector_transform_migration_prep" / "outputs" / "collector_transform_usage_audit_v1.json"

TRANSFORM_TARGETS = {
    "canonical_board_snapshot": {
        "definition": "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py",
        "category": "rest_board_runtime_adapter",
        "expected_callers": ["btcts_next/src/btcts/collector_vnext/emit_rest.py"],
        "l2_builder": "make_orderbook_snapshot_payload",
    },
    "canonical_board_event": {
        "definition": "btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py",
        "category": "ws_board_runtime_adapter",
        "expected_callers": [
            "btcts_next/src/btcts/collector_vnext/emit_ws.py",
            "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
        ],
        "l2_builder": "make_orderbook_event_payload",
    },
    "canonical_trades": {
        "definition": "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py",
        "category": "rest_trade_runtime_adapter",
        "expected_callers": ["btcts_next/src/btcts/collector_vnext/emit_rest.py"],
        "l2_builder": "make_trade_event_payload",
    },
    "canonical_ws_trade": {
        "definition": "btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py",
        "category": "ws_trade_runtime_adapter",
        "expected_callers": [
            "btcts_next/src/btcts/collector_vnext/emit_ws.py",
            "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py",
        ],
        "l2_builder": "make_trade_event_payload",
    },
    "apply_board_structural_hints": {
        "definition": "btcts_next/src/btcts/collector_vnext/transforms/board_structural_hints.py",
        "category": "board_structural_hint_runtime_adapter_metadata",
        "expected_callers": [
            "btcts_next/src/btcts/collector_vnext/emit_rest.py",
            "btcts_next/src/btcts/collector_vnext/emit_ws.py",
            "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
        ],
        "l2_builder": None,
    },
    "apply_trade_structural_hints": {
        "definition": "btcts_next/src/btcts/collector_vnext/transforms/trade_structural_hints.py",
        "category": "trade_structural_hint_runtime_adapter_metadata",
        "expected_callers": [
            "btcts_next/src/btcts/collector_vnext/emit_rest.py",
            "btcts_next/src/btcts/collector_vnext/emit_ws.py",
            "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py",
        ],
        "l2_builder": None,
    },
}

RUNTIME_FILES = [
    "btcts_next/src/btcts/collector_vnext/emit_rest.py",
    "btcts_next/src/btcts/collector_vnext/emit_ws.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py",
]

FORBIDDEN_RUNTIME_MIGRATION_PATHS = [
    "btcts_next/src/btcts/collector_vnext/canonical_facade.py",
    "btcts_next/src/btcts/collector_vnext/transform_facade.py",
    "btcts_next/src/btcts/collector_vnext/transforms/facade.py",
    "btcts_next/src/btcts/collector_vnext/transforms/runtime_bridge.py",
]

FORBIDDEN_DIRECT_PAYLOAD_IMPORTS_OUTSIDE_TRANSFORMS = [
    "btcts.ingestion.l2_canonical.orderbook.payload",
    "btcts.ingestion.l2_canonical.tradeflow.payload",
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _scan_symbol(symbol: str) -> list[dict[str, Any]]:
    pattern = re.compile(rf"\b{re.escape(symbol)}\b")
    hits: list[dict[str, Any]] = []
    for root_rel in ["btcts_next/src/btcts/collector_vnext"]:
        root = REPO_ROOT / root_rel
        for path in root.rglob("*.py"):
            rel = path.relative_to(REPO_ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    hits.append({"path": rel, "line": line_no, "text": line.strip()})
    return hits


def _caller_paths_for(symbol: str, definition: str) -> list[str]:
    callers: list[str] = []
    for hit in _scan_symbol(symbol):
        path = str(hit["path"])
        text = str(hit["text"])
        if path == definition:
            continue
        if text.startswith("from ") or text.startswith("import ") or f"{symbol}(" in text:
            if path not in callers:
                callers.append(path)
    return callers


def _check_direct_payload_imports() -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for rel_path in RUNTIME_FILES:
        text = _read(rel_path)
        for fragment in FORBIDDEN_DIRECT_PAYLOAD_IMPORTS_OUTSIDE_TRANSFORMS:
            if fragment in text:
                hits.append({"path": rel_path, "fragment": fragment})
    return hits


def _usage_items() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for symbol, meta in TRANSFORM_TARGETS.items():
        definition = str(meta["definition"])
        callers = _caller_paths_for(symbol, definition)
        expected_callers = list(meta["expected_callers"])
        definition_text = _read(definition)
        l2_builder = meta.get("l2_builder")
        items.append({
            "symbol": symbol,
            "category": meta["category"],
            "definition": definition,
            "callers": callers,
            "expected_callers": expected_callers,
            "missing_expected_callers": [path for path in expected_callers if path not in callers],
            "unexpected_callers": [path for path in callers if path not in expected_callers],
            "l2_public_boundary_builder": l2_builder,
            "definition_uses_l2_public_boundary_builder": bool(l2_builder and l2_builder in definition_text),
            "future_facade_candidate": True,
            "migration_allowed_now": False,
        })
    return items


def build_audit_payload() -> dict[str, Any]:
    usage_items = _usage_items()
    payload = {
        "phase": "phase4a_phase_f_collector_transform_usage_audit",
        "read_only": True,
        "output_path": OUTPUT_PATH.relative_to(REPO_ROOT).as_posix(),
        "owner_model": {
            "l2_canonical_owner": "btcts_next/src/btcts/ingestion/l2_canonical",
            "collector_transforms_role": "runtime adapter / runtime-local bridge",
        },
        "closed_boundaries": {
            "runtime_import_migration": True,
            "collector_capture_behavior_changes": True,
            "collector_writer_backfill_changes": True,
            "facade_bridge_implementation": True,
            "market_engine_integration": True,
            "broker_order_execution": True,
            "inference_training": True,
        },
        "usage_items": usage_items,
        "usage_item_count": len(usage_items),
        "runtime_files": RUNTIME_FILES,
        "forbidden_runtime_migration_paths_existing": [
            rel for rel in FORBIDDEN_RUNTIME_MIGRATION_PATHS if (REPO_ROOT / rel).exists()
        ],
        "direct_payload_imports_outside_transforms": _check_direct_payload_imports(),
        "recommended_next": "phase4a_phase_f_collector_transform_facade_decision_entry_criteria_or_noop",
    }
    payload["ok"] = (
        payload["forbidden_runtime_migration_paths_existing"] == []
        and payload["direct_payload_imports_outside_transforms"] == []
        and all(item["missing_expected_callers"] == [] for item in usage_items)
        and all(item["unexpected_callers"] == [] for item in usage_items)
        and all(
            item["definition_uses_l2_public_boundary_builder"] is True
            for item in usage_items
            if item["l2_public_boundary_builder"] is not None
        )
    )
    payload["failures"] = [] if payload["ok"] else ["collector transform usage audit invariants failed"]
    return payload


def main() -> int:
    payload = build_audit_payload()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
