# path: ./btcts_next/src/btcts/apps/bitflyer_fx_public_ws_tls_diagnostics_once.py
# desc: SR-FX public WS TLS diagnostics. Read-only; no market data writes and no broker calls.

from __future__ import annotations

import json

from btcts.collector_vnext.fx_public_ws import diagnose_fx_ws_tls_environment, preflight_fx_public_ws


def main() -> int:
    preflight = preflight_fx_public_ws()
    diagnostics = diagnose_fx_ws_tls_environment(preflight=preflight)
    out = {
        "stage": "bitflyer_fx_public_ws_tls_diagnostics_once",
        "preflight": preflight,
        "tls_diagnostics": diagnostics,
        "ok": bool(preflight.get("ok")) and bool(diagnostics.get("ok")),
        "read_only": True,
        "would_send_to_broker": False,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    # Diagnostic command returns 0 even when TLS is not OK.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
