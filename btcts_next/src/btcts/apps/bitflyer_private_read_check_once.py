# path: ./btcts_next/src/btcts/apps/bitflyer_private_read_check_once.py
# desc: One-shot redacted bitFlyer private API read check for SR-FX.

from __future__ import annotations

import json
import os
from typing import Dict

from btcts.collector_vnext.config import ConfigValidationError, load_config
from btcts.collector_vnext.providers.bitflyer_private_rest import (
    fetch_child_orders,
    fetch_collateral,
    fetch_own_executions,
    fetch_positions,
)
from btcts.collector_vnext.rate_runtime import VNextRateRuntime
from btcts.collector_vnext.secrets import SecretLoadError, load_bitflyer_private_credential


def _print_json(data: Dict[str, object]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def _resolve_execution_product_code(cfg) -> str:
    # Backward-compatible explicit override for the current verification CLI.
    raw = os.getenv("BTCTS_BITFLYER_EXECUTION_PRODUCT_CODE", "").strip()
    if raw:
        return raw
    return str(cfg.execution_market.product_code or "").strip()


def main() -> int:
    try:
        credential = load_bitflyer_private_credential()
    except SecretLoadError as exc:
        _print_json({"ok": False, "stage": "load_credential", "error": str(exc)})
        return 2

    try:
        cfg = load_config()
    except ConfigValidationError as exc:
        _print_json({"ok": False, "stage": "load_config", "error": str(exc)})
        return 2

    rate_runtime = VNextRateRuntime.build(cfg)

    product_code = _resolve_execution_product_code(cfg)

    results: Dict[str, object] = {
        "ok": True,
        "stage": "bitflyer_private_read_check_once",
        "credential": credential.redacted(),
        "market_identity": cfg.market_identity_summary(),
        "product_code": product_code or None,
        "checks": {},
    }

    collateral = fetch_collateral(credential, rate_runtime=rate_runtime)
    results["checks"]["collateral"] = collateral.redacted()  # type: ignore[index]

    if not collateral.ok:
        results["ok"] = False
        _print_json(results)
        return 3

    if product_code:
        positions = fetch_positions(credential, product_code=product_code, rate_runtime=rate_runtime)
        child_orders = fetch_child_orders(credential, product_code=product_code, rate_runtime=rate_runtime)
        own_executions = fetch_own_executions(credential, product_code=product_code, rate_runtime=rate_runtime)
        results["checks"]["positions"] = positions.redacted()  # type: ignore[index]
        results["checks"]["child_orders"] = child_orders.redacted()  # type: ignore[index]
        results["checks"]["own_executions"] = own_executions.redacted()  # type: ignore[index]
        results["ok"] = bool(positions.ok and child_orders.ok and own_executions.ok)
    else:
        results["notes"] = [
            "execution product_code is not set; only collateral was checked.",
            "Set BTCTS_EXECUTION_PRODUCT_CODE after FX product identity is confirmed.",
        ]

    _print_json(results)
    return 0 if bool(results["ok"]) else 4


if __name__ == "__main__":
    raise SystemExit(main())
