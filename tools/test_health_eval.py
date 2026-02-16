# path: ./tools/test_health_eval.py
# desc: Health(read_health) の最小スモーク（monitoring.yaml + status.json を用意して読む）

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from dataclasses import asdict, is_dataclass

from btcts.health.svc import read_health

def _to_jsonable(x):
    # HealthSummary は dataclass 想定
    if is_dataclass(x):
        return asdict(x)
    # pydantic v2 互換
    if hasattr(x, "model_dump"):
        return x.model_dump()
    # pydantic v1 互換
    if hasattr(x, "dict"):
        return x.dict()
    return x

def main() -> int:
    print("[ENV] BTC_TS_CONFIG_DIR =", os.environ.get("BTC_TS_CONFIG_DIR", ""))
    print("[ENV] BTC_TS_DATA_DIR   =", os.environ.get("BTC_TS_DATA_DIR", ""))
    print("[ENV] BTC_TS_LOGS_DIR   =", os.environ.get("BTC_TS_LOGS_DIR", ""))

    h = read_health(audit_lines=50)

    print("\n[HEALTH] read_health result:")
    print(json.dumps(_to_jsonable(h), ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
