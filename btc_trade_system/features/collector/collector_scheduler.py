# path: btc_trade_system/features/collector/collector_scheduler.py
# desc: RateController に基づいて各 endpoint runner を呼び出す薄いスケジューラ。429/Retry-After を扱い、監査に記録。

from __future__ import annotations

import time
import logging
import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Dict, Tuple, Optional, Iterable, Any

from .collector_rate import RateController

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")

# dev_audit（無ければ no-op）
try:
    from btc_trade_system.features.audit_dev.writer import emit as dev_audit_emit  # type: ignore
except Exception:  # pragma: no cover
    def dev_audit_emit(**kwargs):  # type: ignore
        logger.debug("audit_dev.emit(no-op): %s", kwargs)

# ランナーが 429/Retry-After を通知するための軽量例外
class RateLimited(Exception):
    def __init__(self, retry_after_sec: Optional[float] = None, message: str = "rate limited"):
        super().__init__(message)
        self.retry_after_sec = retry_after_sec

Runner = Callable[[], None]

def _rate_state_path() -> Path:
    """
    RateController の状態スナップショットを書き出す rate_state.json のパスを返す。
    data/collector/rate_state.json を基本とし、環境変数で上書き可能。
    """
    data_dir = os.environ.get("BTC_TS_DATA_DIR") or os.environ.get("DATA")
    if not data_dir:
        # リポ直下/data をフォールバック
        data_dir = str(Path(__file__).resolve().parents[3] / "data")
    return Path(data_dir) / "collector" / "rate_state.json"


def _write_rate_state(rc: RateController, exchanges: Iterable[str]) -> None:
    """
    各 exchange について RateController.get_exchange_state() から状態を取得し、
    rate_state.json として書き出す。

    - soft_limit: RateController 側の判定をそのまま利用
    - hard_limit: penalty > 0 の間 true（429 由来のペナルティが残っている状態）
    """
    snapshot: Dict[str, Any] = {}
    for ex in exchanges:
        state = dict(rc.get_exchange_state(ex))
        # 429/Retry-After で penalty が立っている間は「hard_limit」とみなす
        state["hard_limit"] = bool(state.get("penalty", 0) > 0)
        snapshot[ex] = state

    try:
        p = _rate_state_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        tmp.replace(p)
    except Exception as e:
        # health / dashboard 側の観測用なので、失敗しても collector 本体は止めない
        logger.debug("rate_state write err: %s", e)

@dataclass
class Endpoint:
    exchange: str
    endpoint: str
    priority: int
    target_interval: float
    runner: Runner

class Scheduler:

    def set_exchange_policy(self, exchange: str, *, max_rps: float, burst: int = 1) -> None:
        """取引所レベルのレート（トークンバケット）を設定。"""
        self.rc.set_exchange_policy(exchange, max_rps=max_rps, burst=burst)

    """RateController で許可されたタイミングで runner を実行する最小スケジューラ。"""

    def __init__(self, rc: Optional[RateController] = None):
        self.rc = rc or RateController()
        self.table: Dict[Tuple[str, str], Endpoint] = {}

    def register_endpoint(self, exchange: str, endpoint: str, *, priority: int, target_interval: float, runner: Runner) -> None:
        key = (exchange, endpoint)
        self.table[key] = Endpoint(exchange, endpoint, priority, target_interval, runner)
        self.rc.set_policy(exchange, endpoint, priority=priority, target_interval=target_interval)
        # 優先度の昇順（0=最優先）で巡回するようソート済みキーを持つ
        self._keys = sorted(self.table.keys(), key=lambda k: self.table[k].priority)

    def run_forever(self, tick_sleep: float = 0.05) -> None:
        """非常に単純なラウンド：全 endpoint を優先度順に巡回し、許可されたものだけ実行。"""
        keys = getattr(self, "_keys", sorted(self.table.keys(), key=lambda k: self.table[k].priority))
        while True:
            any_run = False
            for key in keys:
                ep = self.table[key]
                allowed, wait_ms = self.rc.request_permit(ep.exchange, ep.endpoint)
                if not allowed:
                    continue
                any_run = True
                t0 = time.perf_counter()
                try:
                    dev_audit_emit(event="collector.endpoint.run", level="INFO", feature="collector",
                                   payload={"exchange": ep.exchange, "endpoint": ep.endpoint})
                    ep.runner()
                    self.rc.on_success(ep.exchange)
                except RateLimited as rl:
                    self.rc.on_rate_limited(ep.exchange, retry_after_sec=rl.retry_after_sec)
                    dev_audit_emit(event="collector.rate.limit", level="WARN", feature="collector",
                                   payload={"exchange": ep.exchange, "endpoint": ep.endpoint, "retry_after_sec": rl.retry_after_sec})
                except Exception as e:
                    # ランナー内部の例外（ネット障害など）：監査しつつ継続
                    dev_audit_emit(event="collector.endpoint.error", level="ERROR", feature="collector",
                                   payload={"exchange": ep.exchange, "endpoint": ep.endpoint, "error": str(e)})
                    logger.exception("runner error on %s/%s", ep.exchange, ep.endpoint)
                finally:
                    elapsed = (time.perf_counter() - t0) * 1000.0
                    dev_audit_emit(event="collector.endpoint.elapsed", level="DEBUG", feature="collector",
                                   payload={"exchange": ep.exchange, "endpoint": ep.endpoint, "elapsed_ms": round(elapsed, 3)})

            # ループ 1 周ごとに、登録済み exchange について rate_state.json を更新する
            _write_rate_state(self.rc, {ep.exchange for ep in self.table.values()})

            if not any_run:
                time.sleep(tick_sleep)

# 簡易デモ（ダミー runner）
if __name__ == "__main__":
    sch = Scheduler()

    import random
    def dummy_ob():
        r = random.random()
        if r < 0.1:
            raise RateLimited(retry_after_sec=1.0)
        elif r < 0.12:
            raise RuntimeError("net glitch")
        # 成功は何もしない（本実装はファイルへ書く等）

    sch.register_endpoint("bitflyer", "orderbook", priority=0, target_interval=0.2, runner=dummy_ob)
    sch.register_endpoint("bitflyer", "trades",   priority=1, target_interval=0.5, runner=dummy_ob)

    sch.run_forever()

