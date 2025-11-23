# path: btc_trade_system/features/collector/collector_main.py
# desc: Collector 起動エントリ。scheduler＋endpoint 登録＋無限ループ。

from __future__ import annotations
import time
from pathlib import Path

from .collector_scheduler import Scheduler
from .collector_rate import RateController
from btc_trade_system.features.settings import set_exchanges
from btc_trade_system.features.settings.settings_svc import load_yaml

# 各 endpoint runner（仮）
from btc_trade_system.features.collector import bitflyer_public

def build_scheduler():

    rc = RateController()
    sch = Scheduler(rc)

    # 1) 取引所ごとのレート設定を投入
    ex_cfg = set_exchanges.load_exchanges().get("exchanges", {})
    for ex, cfg in ex_cfg.items():
        if not cfg.get("enabled", False):
            continue
        max_rps  = float(cfg.get("official_max_rps", 0.0))
        safety   = 0.8 if ex == "bitflyer" else 0.9   # 現状の固定値
        eff_rps  = max_rps * safety
        burst    = int(max_rps * cfg.get("burst_base_sec", 1))
        rc.set_exchange_policy(ex, max_rps=eff_rps, burst=burst)

    # 2) endpoint の登録（最低限のデモ）
    sch.register_endpoint(
        "bitflyer", "orderbook",
        priority=0, target_interval=0.2,
        runner=bitflyer_public.run_orderbook,
    )

    sch.register_endpoint(
        "bitflyer", "trades",
        priority=1, target_interval=0.4,
        runner=bitflyer_public.run_trades,
    )

    return sch


def main():
    sch = build_scheduler()
    sch.run_forever()


if __name__ == "__main__":
    main()
