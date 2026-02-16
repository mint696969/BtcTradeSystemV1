# path: ./tools/test_providers_health.py
# desc: Provider(例: bitflyer) の最小疎通スモーク（公開APIを叩けるか）

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.collector.providers.bitflyer import fetch_board, fetch_executions

def main():
    print("[TEST] bitflyer board/executions")
    b = fetch_board("BTC_JPY")
    assert "mid_price" in b or "bids" in b or "asks" in b
    print("[OK] board keys:", list(b.keys())[:8])

    e = fetch_executions("BTC_JPY", count=5)
    assert isinstance(e, list)
    print("[OK] executions len:", len(e))
    if e:
        print("[SAMPLE] exec keys:", list(e[0].keys())[:8])

    print("DONE")

if __name__ == "__main__":
    main()
