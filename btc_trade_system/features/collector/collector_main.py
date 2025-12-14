# path: btc_trade_system/features/collector/collector_main.py
# desc: Collector 起動エントリ。scheduler＋endpoint 登録＋無限ループ。

from __future__ import annotations
import time
from .collector_scheduler import Scheduler
from .collector_rate import RateController
from btc_trade_system.features.settings import set_exchanges

# 各 endpoint runner（仮）
from btc_trade_system.features.collector import bitflyer_public

def build_scheduler():

    rc = RateController()
    sch = Scheduler(rc)

    # 1) 取引所ごとのレート設定を投入
    ex_cfg = set_exchanges.load_exchanges().get("exchanges", {})
    for ex, cfg in ex_cfg.items():
        # 無効な取引所はスキップ
        if not cfg.get("enabled", False):
            continue

        # 既定の安全係数（bitflyer は 0.8、それ以外は 0.9）
        default_safety = 0.8 if ex == "bitflyer" else 0.9

        # exchanges.yaml ＋ health 側の safety 設定をマージした実効ポリシー
        policy = set_exchanges.get_exchange_policy(ex, default_safety)
        if not policy:
            # 定義不足などの場合はいったんスキップ（将来 dev_audit で警告しても良い）
            continue

        rc.set_exchange_policy(
            ex,
            max_rps=policy["effective_max_rps"],
            burst=int(policy["burst"]),
        )

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
