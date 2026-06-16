# path: ./btcts_next/src/btcts/health/health.py
# desc: HealthのCLI/デバッグ入口（UIは扱わない）。btcts.health.svc.read_health() を呼んで標準出力に出す。

from __future__ import annotations

import json
from typing import Any

from btcts.health.svc import read_health


def _to_jsonable(x: Any) -> Any:
    if hasattr(x, "model_dump"):
        return x.model_dump()
    if hasattr(x, "__dict__"):
        return dict(x.__dict__)
    return x


def main() -> None:
    h = read_health()
    out = _to_jsonable(h)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
