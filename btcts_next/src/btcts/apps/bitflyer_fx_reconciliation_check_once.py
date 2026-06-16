# path: ./btcts_next/src/btcts/apps/bitflyer_fx_reconciliation_check_once.py
# desc: One-shot SR-FX read-only reconciliation check from private readiness. No broker calls.

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from btcts.autotrade.execution.reconciliation import reconcile_fx_private_state_with_paper
from btcts.collector_vnext.config import ConfigValidationError, load_config


def _print_json(data: Dict[str, object]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def _read_json(path: Path) -> Dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise RuntimeError(f"could not read JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return data


def main() -> int:
    try:
        cfg = load_config()
    except ConfigValidationError as exc:
        _print_json({"ok": False, "stage": "load_config", "error": str(exc)})
        return 2

    readiness_path = cfg.roots()["state"] / "private" / "bitflyer_fx_readiness.json"
    try:
        readiness = _read_json(readiness_path)
    except Exception as exc:
        _print_json({"ok": False, "stage": "read_private_readiness", "error": str(exc), "path": str(readiness_path)})
        return 2

    result = reconcile_fx_private_state_with_paper(private_readiness=readiness, paper_orders=())
    out: Dict[str, object] = {
        "ok": result.ok,
        "stage": "bitflyer_fx_reconciliation_check_once",
        "readiness_path": str(readiness_path),
        "market_identity": cfg.market_identity_summary(),
        "reconciliation": result.to_dict(),
    }
    _print_json(out)
    # A blocked reconciliation is expected while existing exchange state is not adopted/cleared.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
