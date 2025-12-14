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
    """RateController で許可されたタイミングで runner を実行する最小スケジューラ。"""

    def __init__(self, rc: Optional[RateController] = None):
        self.rc = rc or RateController()
        self.table: Dict[Tuple[str, str], Endpoint] = {}
        self._keys: list[Tuple[str, str]] = []

    def set_exchange_policy(self, exchange: str, *, max_rps: float, burst: int = 1) -> None:
        """取引所レベルのレート（トークンバケット）を設定。"""
        self.rc.set_exchange_policy(exchange, max_rps=max_rps, burst=burst)

    def register_endpoint(
        self,
        exchange: str,
        endpoint: str,
        *,
        priority: int,
        target_interval: float,
        runner: Runner,
    ) -> None:
        key = (exchange, endpoint)
        self.table[key] = Endpoint(exchange, endpoint, priority, target_interval, runner)
        self.rc.set_policy(exchange, endpoint, priority=priority, target_interval=target_interval)
        # 優先度の昇順（0=最優先）で巡回するようソート済みキーを持つ
        self._keys = sorted(self.table.keys(), key=lambda k: self.table[k].priority)

    def run_forever(self, tick_sleep: float = 0.05, *, rate_state_interval_s: float = 0.5) -> None:
        """
        全 endpoint を優先度順に巡回し、許可されたものだけ実行。

        改善点:
        - request_permit() が返す wait_ms を利用し、次の permit までの最短待ちを sleep する（無駄な busy loop を抑制）
        - rate_state.json の書き出しは一定間隔に間引く（観測用I/Oを抑え、runner実行を優先）
        """
        last_rate_state_ts = 0.0

        while True:
            keys = self._keys or sorted(self.table.keys(), key=lambda k: self.table[k].priority)

            any_run = False
            min_wait_ms: Optional[float] = None

            for key in keys:
                ep = self.table[key]
                allowed, wait_ms = self.rc.request_permit(ep.exchange, ep.endpoint)

                if not allowed:
                    # 次にpermitが降りそうな最短待ちを集める（CPUを回しすぎない）
                    if wait_ms is not None:
                        if min_wait_ms is None:
                            min_wait_ms = float(wait_ms)
                        else:
                            min_wait_ms = min(min_wait_ms, float(wait_ms))
                    continue

                any_run = True
                t0 = time.perf_counter()
                try:
                    dev_audit_emit(
                        event="collector.endpoint.run",
                        level="INFO",
                        feature="collector",
                        payload={"exchange": ep.exchange, "endpoint": ep.endpoint},
                    )
                    ep.runner()
                    self.rc.on_success(ep.exchange)

                except RateLimited as rl:
                    self.rc.on_rate_limited(ep.exchange, retry_after_sec=rl.retry_after_sec)
                    dev_audit_emit(
                        event="collector.rate.limit",
                        level="WARN",
                        feature="collector",
                        payload={
                            "exchange": ep.exchange,
                            "endpoint": ep.endpoint,
                            "retry_after_sec": rl.retry_after_sec,
                        },
                    )

                except Exception as e:
                    dev_audit_emit(
                        event="collector.endpoint.error",
                        level="ERROR",
                        feature="collector",
                        payload={"exchange": ep.exchange, "endpoint": ep.endpoint, "error": str(e)},
                    )
                    logger.exception("runner error on %s/%s", ep.exchange, ep.endpoint)

                finally:
                    elapsed = (time.perf_counter() - t0) * 1000.0
                    dev_audit_emit(
                        event="collector.endpoint.elapsed",
                        level="DEBUG",
                        feature="collector",
                        payload={"exchange": ep.exchange, "endpoint": ep.endpoint, "elapsed_ms": round(elapsed, 3)},
                    )

            # rate_state.json は観測用。一定間隔で十分なので間引く（I/O削減）
            now = time.monotonic()
            if (now - last_rate_state_ts) >= float(rate_state_interval_s):
                _write_rate_state(self.rc, {ep.exchange for ep in self.table.values()})
                last_rate_state_ts = now

            # 待機戦略：
            # - 何も走らなかった場合は tick_sleep（最低限のスリープ）
            # - 何か走った場合でも、次のpermitまでの最短待ちが分かるならそれだけ待つ（無駄なループを抑制）
            if not any_run:
                time.sleep(tick_sleep)
            else:
                if min_wait_ms is not None and min_wait_ms > 0:
                    time.sleep(min_wait_ms / 1000.0)

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

