# path: ./btcts_next/src/btcts/apps/bitflyer_fx_live_readiness_contract_check_once.py
# desc: One-shot SR-FX live readiness contract check. Read-only; no broker calls.

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from btcts.autotrade.execution.intents import attach_execution_market, build_order_intent_from_decision
from btcts.autotrade.execution.live_readiness_contract import evaluate_fx_live_readiness_contract
from btcts.autotrade.execution.order_preview import build_bitflyer_fx_manual_order_preview
from btcts.autotrade.execution.reconciliation import reconcile_fx_private_state_with_paper
from btcts.collector_vnext.config import ConfigValidationError, load_config
from btcts.collector_vnext.paths import ensure_dir


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


def _write_json(path: Path, data: Dict[str, object]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _side() -> str:
    raw = os.getenv("BTCTS_ORDER_PREVIEW_SIDE", "buy").strip().lower()
    return "sell" if raw == "sell" else "buy"


def _size() -> float:
    return float(os.getenv("BTCTS_ORDER_PREVIEW_SIZE", "0.001").strip())


def _price() -> float:
    return float(os.getenv("BTCTS_ORDER_PREVIEW_PRICE", "1.0").strip())


def _nested_public_readiness(payload: Dict[str, object]) -> Dict[str, object]:
    nested = payload.get("public_market_readiness")
    if isinstance(nested, dict):
        return nested
    return payload


def main() -> int:
    try:
        cfg = load_config()
    except ConfigValidationError as exc:
        _print_json({"ok": False, "stage": "load_config", "error": str(exc)})
        return 2

    readiness_path = cfg.roots()["state"] / "private" / "bitflyer_fx_readiness.json"
    public_market_readiness_path = cfg.roots()["state"] / "public" / "bitflyer_fx_public_market_readiness.json"
    contract_path = cfg.roots()["state"] / "private" / "bitflyer_fx_live_readiness_contract.json"
    try:
        readiness = _read_json(readiness_path)
    except Exception as exc:
        _print_json({"ok": False, "stage": "read_private_readiness", "error": str(exc), "path": str(readiness_path)})
        return 2
    try:
        public_market_readiness = _nested_public_readiness(_read_json(public_market_readiness_path))
    except Exception as exc:
        public_market_readiness = {
            "ok": False,
            "product_code": cfg.execution_market.product_code,
            "market_uid": cfg.execution_market.market_uid,
            "market_role": cfg.execution_market.role,
            "blocked_by": ["public_market_readiness_missing_or_unreadable"],
            "warnings": [str(exc)],
            "read_only": True,
            "would_send_to_broker": False,
        }

    exe = cfg.execution_market.normalized()
    base_intent = build_order_intent_from_decision(
        decision_id="decision_live_readiness_contract_once",
        snapshot_id="snapshot_live_readiness_contract_once",
        forecast_id=None,
        parameter_set_id="live_readiness_contract",
        logic_version="sr_fx_live_readiness_contract_v1",
        side=_side(),
        size=_size(),
        price=_price(),
        reason_codes=("live_readiness_contract", "read_only"),
        risk_gate_allowed=True,
        mode=os.getenv("BTCTS_LIVE_READINESS_TARGET_MODE", "LIVE_MIN_SIZE"),
    )
    intent = attach_execution_market(
        base_intent,
        exchange=exe.exchange,
        product_code=exe.product_code,
        market_type=exe.market_type,
        market_uid=exe.market_uid,
        market_role=exe.role,
    )

    reconciliation = reconcile_fx_private_state_with_paper(private_readiness=readiness, paper_orders=())
    preview = build_bitflyer_fx_manual_order_preview(intent, private_readiness=readiness)
    contract = evaluate_fx_live_readiness_contract(
        private_readiness=readiness,
        reconciliation=reconciliation,
        order_preview=preview,
        public_market_readiness=public_market_readiness,
        target_mode=os.getenv("BTCTS_LIVE_READINESS_TARGET_MODE", "LIVE_MIN_SIZE"),
        bitflyer_order_send_enabled=_env_bool("BTCTS_BITFLYER_ORDER_SEND_ENABLED", False),
        autotrade_live_order_enabled=_env_bool("BTCTS_AUTOTRADE_LIVE_ORDER_ENABLED", False),
        order_sender_implemented=False,
    )

    out: Dict[str, object] = {
        "ok": contract.ready,
        "stage": "bitflyer_fx_live_readiness_contract_check_once",
        "readiness_path": str(readiness_path),
        "public_market_readiness_path": str(public_market_readiness_path),
        "contract_path": str(contract_path),
        "market_identity": cfg.market_identity_summary(),
        "public_market_readiness": public_market_readiness,
        "reconciliation": reconciliation.to_dict(),
        "order_preview": preview.to_dict(),
        "live_readiness_contract": contract.to_dict(),
    }
    _write_json(contract_path, out)
    _print_json(out)
    # Not-ready is the expected safe result until market/private/account/flags/sender are all ready.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
