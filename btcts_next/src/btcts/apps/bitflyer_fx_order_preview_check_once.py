# path: ./btcts_next/src/btcts/apps/bitflyer_fx_order_preview_check_once.py
# desc: One-shot SR-FX manual order preview check. Preview only; never sends broker orders.

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from btcts.autotrade.execution.intents import attach_execution_market, build_order_intent_from_decision
from btcts.autotrade.execution.order_preview import build_bitflyer_fx_manual_order_preview
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


def _side() -> str:
    raw = os.getenv("BTCTS_ORDER_PREVIEW_SIDE", "buy").strip().lower()
    return "sell" if raw == "sell" else "buy"


def _size() -> float:
    raw = os.getenv("BTCTS_ORDER_PREVIEW_SIZE", "0.001").strip()
    return float(raw)


def _price() -> float:
    raw = os.getenv("BTCTS_ORDER_PREVIEW_PRICE", "1.0").strip()
    return float(raw)


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

    exe = cfg.execution_market.normalized()
    base_intent = build_order_intent_from_decision(
        decision_id="decision_manual_preview_once",
        snapshot_id="snapshot_manual_preview_once",
        forecast_id=None,
        parameter_set_id="manual_preview",
        logic_version="sr_fx_order_preview_v1",
        side=_side(),
        size=_size(),
        price=_price(),
        reason_codes=("manual_preview", "preview_only"),
        risk_gate_allowed=True,
        mode="ARMED_DRY_RUN",
    )
    intent = attach_execution_market(
        base_intent,
        exchange=exe.exchange,
        product_code=exe.product_code,
        market_type=exe.market_type,
        market_uid=exe.market_uid,
        market_role=exe.role,
    )

    preview = build_bitflyer_fx_manual_order_preview(
        intent,
        private_readiness=readiness,
        require_account_clear_for_new_auto_entry=True,
    )

    out: Dict[str, object] = {
        "ok": preview.ok,
        "stage": "bitflyer_fx_order_preview_check_once",
        "readiness_path": str(readiness_path),
        "market_identity": cfg.market_identity_summary(),
        "preview": preview.to_dict(),
    }
    _print_json(out)
    # A blocked preview is an expected safe result when existing positions/open orders are present.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
