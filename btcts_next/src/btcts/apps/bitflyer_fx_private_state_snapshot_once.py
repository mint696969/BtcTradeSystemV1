# path: ./btcts_next/src/btcts/apps/bitflyer_fx_private_state_snapshot_once.py
# desc: One-shot FX private state snapshot/readiness writer for SR-FX.

from __future__ import annotations

import json
from typing import Dict

from btcts.collector_vnext.config import ConfigValidationError, load_config
from btcts.collector_vnext.private_state import (
    build_private_state_snapshot,
    build_readiness,
    endpoint_snapshot,
    write_private_state_files,
)
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


def main() -> int:
    try:
        cfg = load_config()
    except ConfigValidationError as exc:
        _print_json({"ok": False, "stage": "load_config", "error": str(exc)})
        return 2

    try:
        credential = load_bitflyer_private_credential()
    except SecretLoadError as exc:
        _print_json({"ok": False, "stage": "load_credential", "error": str(exc)})
        return 2

    exe = cfg.execution_market.normalized()
    rate_runtime = VNextRateRuntime.build(cfg)

    results = {
        "collateral": fetch_collateral(credential, rate_runtime=rate_runtime),
        "positions": fetch_positions(credential, product_code=exe.product_code, rate_runtime=rate_runtime),
        "child_orders": fetch_child_orders(credential, product_code=exe.product_code, rate_runtime=rate_runtime),
        "own_executions": fetch_own_executions(credential, product_code=exe.product_code, rate_runtime=rate_runtime),
    }

    endpoints = {name: endpoint_snapshot(name, result) for name, result in results.items()}
    readiness = build_readiness(
        endpoints,
        product_code=exe.product_code,
        market_uid=exe.market_uid,
    )
    credential_diag = credential.redacted()
    # build_private_state_snapshot converts runtime redacted diagnostics into persisted state-safe names.
    credential_diag.pop("source_path", None)

    snapshot = build_private_state_snapshot(
        cfg=cfg,
        execution_market=exe,
        endpoints=endpoints,
        credential_diagnostics=credential_diag,
        readiness=readiness,
    )
    paths = write_private_state_files(cfg, snapshot=snapshot, readiness=readiness)

    output: Dict[str, object] = {
        "ok": bool(readiness.get("private_state_ok")),
        "stage": "bitflyer_fx_private_state_snapshot_once",
        "market_identity": cfg.market_identity_summary(),
        "credential": credential.redacted(),
        "readiness": readiness,
        "paths": paths,
        "endpoint_status": {
            name: {
                "ok": snap.ok,
                "status_code": snap.status_code,
                "request_class": snap.request_class,
                "received_ts": snap.received_ts,
                "payload_summary": snap.payload_summary,
            }
            for name, snap in endpoints.items()
        },
    }
    _print_json(output)
    return 0 if bool(output["ok"]) else 4


if __name__ == "__main__":
    raise SystemExit(main())
