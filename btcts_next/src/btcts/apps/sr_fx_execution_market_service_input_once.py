# path: ./btcts_next/src/btcts/apps/sr_fx_execution_market_service_input_once.py
# desc: Print read-only SR-FX L4 execution-market service input for upper consumers. No broker calls.

from __future__ import annotations

import json
from typing import Any

from btcts.apps.operator_ui.components.market_state_bridge import (
    execution_market_context,
    load_execution_market_summary_bundle,
)
from btcts.processing.l4_consumer_models.shared import build_execution_market_service_input


def build_sr_fx_execution_market_service_input_payload() -> dict[str, Any]:
    context = execution_market_context()
    summary = load_execution_market_summary_bundle()
    contract = build_execution_market_service_input(
        summary,
        diagnostics={
            "entrypoint": "sr_fx_execution_market_service_input_once",
            "execution_market_context": context,
        },
    )
    return {
        "stage": "sr_fx_execution_market_service_input_once",
        "ok": not bool(contract.blocked_by),
        "context": context,
        "contract": contract.to_dict(),
        "read_only": True,
        "would_send_to_broker": False,
    }


def main() -> int:
    payload = build_sr_fx_execution_market_service_input_payload()
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
