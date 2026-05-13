# path: ./tools/test_phase4a_phasec_close_bundle.py
# desc: Phase 4-A Phase C close verification bundle for L2 canonical owner / collector adapter boundary.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]


CRITICAL_COMPILE_TARGETS = [
    "btcts_next/src/btcts/ingestion/l2_canonical/__init__.py",
    "btcts_next/src/btcts/ingestion/l2_canonical/orderbook/__init__.py",
    "btcts_next/src/btcts/ingestion/l2_canonical/orderbook/payload.py",
    "btcts_next/src/btcts/ingestion/l2_canonical/tradeflow/__init__.py",
    "btcts_next/src/btcts/ingestion/l2_canonical/tradeflow/payload.py",
    "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py",
    "btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py",
    "btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py",
    "btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py",
    "btcts_next/src/btcts/collector_vnext/transforms/board_structural_hints.py",
    "btcts_next/src/btcts/collector_vnext/transforms/trade_structural_hints.py",
    "btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py",
    "btcts_next/src/btcts/collector_vnext/emit_rest.py",
    "btcts_next/src/btcts/collector_vnext/emit_ws.py",
    "tools/test_collector_vnext_boundary_cleanup.py",
    "tools/test_collector_vnext_canonical_rebuild_audit.py",
]


def _read_text(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _assert(cond: bool, message: str, failures: List[str]) -> None:
    if not cond:
        failures.append(message)


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []

    for rel_path in CRITICAL_COMPILE_TARGETS:
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


def _run_json_script(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"script missing: {rel_path}")
        return {
            "returncode": None,
            "json": None,
            "stdout_tail": "",
            "stderr_tail": "",
        }

    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=300,
    )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    parsed = None

    try:
        parsed = json.loads(stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit valid JSON: {exc}")

    if proc.returncode != 0:
        failures.append(f"{rel_path} failed with returncode={proc.returncode}")

    return {
        "returncode": proc.returncode,
        "json": parsed,
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-2000:],
    }


def _check_l2_public_boundary(failures: List[str]) -> Dict[str, Any]:
    rel_path = "btcts_next/src/btcts/ingestion/l2_canonical/__init__.py"
    path = REPO_ROOT / rel_path
    _assert(path.exists(), "L2 canonical public boundary __init__.py must exist", failures)

    text = path.read_text(encoding="utf-8") if path.exists() else ""
    required_exports = [
        "OrderBookRebuilder",
        "OrderBookState",
        "TradeAggregator",
        "make_orderbook_event_payload",
        "make_orderbook_snapshot_payload",
        "make_trade_event_payload",
        "normalize_orderbook_levels",
    ]

    missing = [name for name in required_exports if name not in text]
    for name in missing:
        failures.append(f"L2 canonical public boundary missing export: {name}")

    _assert("collector_vnext" not in text, "L2 canonical public boundary must not depend on collector_vnext", failures)

    return {
        "path": rel_path,
        "missing_exports": missing,
    }


def _check_private_import_ban(failures: List[str]) -> Dict[str, Any]:
    forbidden_fragments = [
        "btcts.ingestion.l2_canonical.orderbook.payload",
        "btcts.ingestion.l2_canonical.tradeflow.payload",
    ]
    hits: List[Dict[str, str]] = []

    src_root = REPO_ROOT / "btcts_next" / "src"
    for path in src_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for fragment in forbidden_fragments:
            if fragment in text:
                hits.append({"path": rel, "fragment": fragment})
                failures.append(f"forbidden L2 private payload import: {rel}: {fragment}")

    return {
        "forbidden_hit_count": len(hits),
        "hits": hits,
    }


def _check_l2_reverse_dependency_ban(failures: List[str]) -> Dict[str, Any]:
    hits: List[Dict[str, str]] = []

    l2_root = REPO_ROOT / "btcts_next" / "src" / "btcts" / "ingestion" / "l2_canonical"
    _assert(l2_root.exists(), "L2 canonical root must exist", failures)

    if not l2_root.exists():
        return {"hit_count": 0, "hits": hits}

    for path in l2_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for fragment in ["collector_vnext", "btcts.collector_vnext"]:
            if fragment in text:
                hits.append({"path": rel, "fragment": fragment})
                failures.append(f"L2 canonical must not depend on collector_vnext: {rel}: {fragment}")

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def _check_docs_and_room_sync(failures: List[str]) -> Dict[str, Any]:
    checks = [
        {
            "path": "tmp/docs/architecture/05_L2_CANONICAL_OWNER_AND_COLLECTOR_RUNTIME_ADAPTER_BOUNDARY_SPEC_2026-04-22.md",
            "required": [
                "2026-05-07 Phase C implementation update",
                "L2 public boundary",
                "canonical payload shape owner = ingestion/l2_canonical/*/payload.py",
                "collector transforms = runtime adapter using L2 public boundary",
                "structural hints = collector runtime adapter metadata helpers",
            ],
        },
        {
            "path": "tmp/gpt_room/08_STATUS.md",
            "required": [
                "Phase C",
                "close 済み",
                "btcts.ingestion.l2_canonical",
                "collector transforms は L2 public boundary 経由",
            ],
        },

        {
            "path": "tmp/gpt_room/memory/handoffs/CURRENT_HANDOFF_PHASE4A_PHASEC_COLLECTOR_BOUNDARY_REENTRY_2026-05-03.md",
            "required": [
                "Phase C: L2 canonical owner / collector adapter boundary cleanup close 済み",
                "canonical payload shape owner = ingestion/l2_canonical/*/payload.py",
                "L2 public boundary = btcts.ingestion.l2_canonical",
                "collector transforms = runtime adapter using L2 public boundary",
                "structural hints = collector runtime adapter metadata helpers",
            ],
        },
    ]

    missing: List[Dict[str, str]] = []

    for check in checks:
        path = REPO_ROOT / check["path"]
        if not path.exists():
            failures.append(f"sync file missing: {check['path']}")
            missing.append({"path": check["path"], "fragment": "<file missing>"})
            continue

        text = path.read_text(encoding="utf-8")
        for fragment in check["required"]:
            if fragment not in text:
                failures.append(f"sync file missing fragment: {check['path']}: {fragment}")
                missing.append({"path": check["path"], "fragment": fragment})

    return {
        "missing_count": len(missing),
        "missing": missing,
    }


def _check_boundary_cleanup_result(result: Dict[str, Any], failures: List[str]) -> Dict[str, Any]:
    data = result.get("json")
    if not isinstance(data, dict):
        failures.append("boundary cleanup result JSON missing")
        return {"ok": False, "failures": ["json missing"]}

    script_failures = data.get("failures")
    ok = data.get("ok") is True and script_failures == []

    if not ok:
        failures.append("boundary cleanup result must be ok:true with failures:[]")

    return {
        "ok": bool(ok),
        "canonical_record_count": data.get("canonical_record_count"),
        "failures": script_failures,
    }


def _check_rebuild_audit_result(result: Dict[str, Any], failures: List[str]) -> Dict[str, Any]:
    data = result.get("json")
    if not isinstance(data, dict):
        failures.append("canonical rebuild audit result JSON missing")
        return {"ok": False, "summaries": []}

    summaries: List[Dict[str, Any]] = []
    ok = True

    for group in data.get("results", []):
        summary = group.get("summary", {}) if isinstance(group, dict) else {}
        item = {
            "exchange": group.get("exchange") if isinstance(group, dict) else None,
            "symbol": group.get("symbol") if isinstance(group, dict) else None,
            "date": group.get("date") if isinstance(group, dict) else None,
            "board_ws_session_count": summary.get("board_ws_session_count"),
            "board_ws_issue_session_count": summary.get("board_ws_issue_session_count"),
        }
        summaries.append(item)

        if summary.get("board_ws_issue_session_count") != 0:
            ok = False
            failures.append(
                "canonical rebuild audit board_ws_issue_session_count must be 0: "
                f"{item['exchange']} {item['symbol']} {item['date']}"
            )

    if not summaries:
        ok = False
        failures.append("canonical rebuild audit returned no summaries")

    return {
        "ok": bool(ok),
        "summaries": summaries,
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    l2_public_boundary = _check_l2_public_boundary(failures)
    private_import_ban = _check_private_import_ban(failures)
    l2_reverse_dependency_ban = _check_l2_reverse_dependency_ban(failures)
    docs_and_room_sync = _check_docs_and_room_sync(failures)

    boundary_cleanup_raw = _run_json_script("tools/test_collector_vnext_boundary_cleanup.py", failures)
    rebuild_audit_raw = _run_json_script("tools/test_collector_vnext_canonical_rebuild_audit.py", failures)

    boundary_cleanup = _check_boundary_cleanup_result(boundary_cleanup_raw, failures)
    rebuild_audit = _check_rebuild_audit_result(rebuild_audit_raw, failures)

    summary = {
        "phase": "phase4a_phasec_l2_canonical_owner_collector_adapter_boundary_cleanup",
        "close_status": "closed",
        "checks": {
            "compile": compile_result,
            "l2_public_boundary": l2_public_boundary,
            "private_import_ban": private_import_ban,
            "l2_reverse_dependency_ban": l2_reverse_dependency_ban,
            "docs_and_room_sync": docs_and_room_sync,
            "boundary_cleanup": boundary_cleanup,
            "canonical_rebuild_audit": rebuild_audit,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())