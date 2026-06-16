# path: ./btcts_next/src/btcts/apps/bitflyer_fx_public_ws_plan_check_once.py
# desc: Network-free SR-FX public WebSocket identity/channel plan check.

from __future__ import annotations

import json

from btcts.collector_vnext.fx_public_ws import fx_ws_channel_plan


def main() -> int:
    plan = fx_ws_channel_plan()
    print(json.dumps({"stage": "bitflyer_fx_public_ws_plan_check_once", **plan}, ensure_ascii=False, indent=2, sort_keys=True))
    guard = plan.get("path_guard", {}) if isinstance(plan.get("path_guard"), dict) else {}
    return 0 if plan.get("ok") and guard.get("all_channels_are_fx_symbol") and guard.get("no_channel_is_spot_symbol") else 4


if __name__ == "__main__":
    raise SystemExit(main())
