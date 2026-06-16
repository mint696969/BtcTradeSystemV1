# path: ./btcts_next/src/btcts/apps/sr_fx_service_path_contract_once.py
# desc: Print read-only SR-FX hot/cold/service path contract diagnostics. No broker calls.

from __future__ import annotations

import json

from btcts.collector_vnext.service_path_contract import build_sr_fx_service_path_contract


def main() -> int:
    contract = build_sr_fx_service_path_contract()
    out = {
        "stage": "sr_fx_service_path_contract_once",
        "ok": not bool(contract.blocked_by),
        "contract": contract.to_dict(),
        "read_only": True,
        "would_send_to_broker": False,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if out["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
