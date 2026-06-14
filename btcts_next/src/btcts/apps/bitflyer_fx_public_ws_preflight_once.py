# path: ./btcts_next/src/btcts/apps/bitflyer_fx_public_ws_preflight_once.py
# desc: Safe SR-FX public WebSocket preflight. Diagnostic only; no data writes and no broker calls.

from __future__ import annotations

import json

from btcts.collector_vnext.fx_public_ws import preflight_fx_public_ws


def main() -> int:
    result = preflight_fx_public_ws()
    out = {"stage": "bitflyer_fx_public_ws_preflight_once", **result}
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    # Return 0 even when network/SSL is not OK: this is a diagnostic preflight, not a readiness gate.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
