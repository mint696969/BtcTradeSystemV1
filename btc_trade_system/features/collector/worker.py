# path: ./btc_trade_system/features/collector/worker.py
# desc: 各取引所用の最小ワーカ基底。レート制御・監査・status更新・リーダーロックを提供（API実装は fetch() を差し替え）。

from __future__ import annotations
import time
import random
_monotonic = time.perf_counter  # システム時計の跳ねに影響されない
from pathlib import Path
from btc_trade_system.common.audit import audit_ok, audit_warn, audit_err
from typing import Optional, Any
from btc_trade_system.common.rate import RateRegistry, RateLimitExceeded
from btc_trade_system.features.collector.status import StatusWriter
from btc_trade_system.features.collector.leader_lock import LeaderLock
from btc_trade_system.features.collector.api_bf import BitflyerPublic
from btc_trade_system.features.collector.snapshot_sink import SnapshotSink

class CollectorWorker:
    """
    最小の収集ワーカ骨格:
      - rate_registry でエンドポイントごとの取得間隔を制御
      - fetch() の成否で StatusWriter を更新
      - 成功/失敗/例外を audit に記録
      - use_leader_lock=True の場合は単一アクティブ運用（acquire/renew/release）
    実 API は fetch() をサブクラス or ラムダで差し替える。
    """

    # --- audit helpers (追加のみ／既存処理は変更しない) -----------------------
    def _audit_fetch_success(self, exchange: str, topic: str,
                             *, latency_ms: float, rows: int | None = None) -> None:
        audit_ok("collector.fetch.success", feature="collector",
                 exchange=exchange, topic=topic,
                 latency_ms=int(latency_ms), rows=int(rows or 0))

    def _audit_fetch_retry(self, exchange: str, topic: str,
                           *, cause: str, retries: int) -> None:
        audit_warn("collector.fetch.retry", feature="collector",
                   exchange=exchange, topic=topic,
                   cause=cause, retries=int(retries))

    def _audit_fetch_fail(self, exchange: str, topic: str,
                          *, cause: str | None = None,
                          code: int | None = None,
                          endpoint: str | None = None,
                          message: str | None = None) -> None:
        payload = {}
        if code is not None: payload["code"] = int(code)
        if endpoint:         payload["endpoint"] = endpoint
        if message:          payload["message"] = message
        audit_err("collector.fetch.fail", feature="collector",
                  exchange=exchange, topic=topic, cause=cause, payload=payload)

    # 軽量なレイテンシ計測（perf_counter → ms）
    import time as _t
    def _now_ms(self) -> float:
        return self._t.perf_counter() * 1000.0

    class _Timer:
        def __init__(self, owner: "CollectorWorker"):
            self.o = owner
            self.t0 = owner._now_ms()
        def ms(self) -> float:
            return max(0.0, self.o._now_ms() - self.t0)

    def __init__(self, base_dir: Path, *, exchange: str, topic: str,
                rate_name: str, capacity: float, refill_per_sec: float,
                use_leader_lock: bool = True, stale_after_sec: int = 45, renew_every_sec: float = 2.0,
                adapter: Optional[Any] = None, product_code: str = "BTC_JPY"):
        self.exchange = exchange
        self.topic = topic
        self.rate_name = rate_name
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self.adapter = adapter
        self.product_code = product_code

        self.rate = RateRegistry()
        self.status = StatusWriter(base_dir)
        self.sink = SnapshotSink(base_dir, use_local_time=False)  # 保存はUTC運用

        self.use_leader_lock = use_leader_lock
        self._lock = LeaderLock(base_dir, stale_after_sec=stale_after_sec) if use_leader_lock else None
        self._renew_every_sec = float(renew_every_sec)
        self._last_renew_m = _monotonic()
        # 失敗時の指数バックオフ（ms）
        self._base_backoff_ms = 500
        self._max_backoff_ms = 15000
        self._backoff_ms = 0

    # ---- 差し替えポイント -----------------------------------------------------
    def fetch(self) -> Any:
        """
        実 API 呼び出し。adapter があればそれを使い、無ければ exchange/topic に応じて既定の実装。
        - bitflyer: trades -> /v1/executions を取得して先頭だけ返す（スモーク用）
        """
        if self.adapter is not None:
            return self.adapter()

        # 既定: bitflyer の trades
        if self.exchange == "bitflyer" and self.topic == "trades":
            cli = BitflyerPublic(user_agent="BtcTS-V1/collector")
            rows = cli.executions(product_code=self.product_code, count=50)
            # 何か返れば成功とみなす（詳細保存は次段）
            return {"count": len(rows), "first": rows[0].__dict__ if rows else None}

        # 既定: bitflyer の board
        if self.exchange == "bitflyer" and self.topic == "board":
            cli = BitflyerPublic(user_agent="BtcTS-V1/collector")
            doc = cli.board(product_code=self.product_code, top=5)
            # スナップショットで使いやすい薄い辞書に整形して返す
            out = {
                "mid_price": doc.get("mid_price"),
                "best_bid": doc.get("best_bid"),
                "best_ask": doc.get("best_ask"),
                "count_bids": (doc.get("raw_count") or {}).get("bids"),
                "count_asks": (doc.get("raw_count") or {}).get("asks"),
            }
            return out

        # それ以外はまだ未実装
        raise RuntimeError(f"fetch not implemented for {self.exchange}:{self.topic}")

    # ---- メインループ ---------------------------------------------------------
    def run_once(self) -> None:
        """1回分の収集（レート取得→fetch→status更新→監査）"""
        # レート取得（待機 or 例外）
        try:
            self.rate.acquire(
                self.rate_name,
                capacity=self.capacity,
                refill_per_sec=self.refill_per_sec,
                timeout_ms=2000,
            )
        except RateLimitExceeded:
            audit_err(
                "collector.rate.timeout",
                feature="collector",
                exchange=self.exchange,
                topic=self.topic,
                rate=self.rate_name,
            )
            time.sleep(0.1)
            return  # ← この周回はスキップして次へ

        # 実行
        try:
            t0_ms = self._now_ms()
            result = self.fetch()
            # 成功: status を OK に
            # 収集スナップショット（UTC日付で日別JSONLへ）
            try:
                obj = {}
                if isinstance(result, dict):
                    # trades 用（従来）
                    if "count" in result:
                        try:
                            obj["count"] = int(result.get("count", 0))
                        except Exception:
                            pass
                    first = result.get("first")
                    if isinstance(first, dict):
                        for k in ("id", "price", "size", "exec_date", "side"):
                            if k in first:
                                obj[f"first_{k}"] = first[k]
                    # board 用（mid/best の最小セットを保存）
                    if "mid_price" in result and result.get("mid_price") is not None:
                        obj["mid_price"] = float(result["mid_price"])
                    best_bid = result.get("best_bid")
                    if isinstance(best_bid, dict):
                        if "price" in best_bid: obj["best_bid_price"] = best_bid["price"]
                        if "size"  in best_bid: obj["best_bid_size"]  = best_bid["size"]
                    best_ask = result.get("best_ask")
                    if isinstance(best_ask, dict):
                        if "price" in best_ask: obj["best_ask_price"] = best_ask["price"]
                        if "size"  in best_ask: obj["best_ask_size"]  = best_ask["size"]
                    # 任意：元の raw_count を薄く保存（UIで使うなら）
                    if "count_bids" in result: obj["count_bids"] = result["count_bids"]
                    if "count_asks" in result: obj["count_asks"] = result["count_asks"]
                else:
                    obj["count"] = 1 if result is not None else 0

                self.sink.write_jsonl(exchange=self.exchange, topic=self.topic, obj=obj)
            except Exception as e:
                # スナップショット失敗は致命ではないので握りつぶしつつ監査に残す
                audit_warn(
                    "collector.file.write.fail",
                    feature="collector",
                    exchange=self.exchange,
                    topic=self.topic,
                    payload={"error": str(e)}
                )

            self.status.update(self.exchange, self.topic, ok=True, notes="ok")
            self.status.flush()

            # 収集成功の監査（レイテンシ/件数を付加）
            latency_ms = max(0, int(self._now_ms() - t0_ms))
            rows = None
            if isinstance(result, dict):
                if "count" in result:
                    rows = result.get("count")
                    try:
                        rows = int(rows) if rows is not None else None
                    except Exception:
                        rows = None
                else:
                    # board 系: count_bids / count_asks の合計で概算（0なら未表示扱い）
                    try:
                        cb = int(result.get("count_bids") or 0)
                        ca = int(result.get("count_asks") or 0)
                        rows = (cb + ca) or None
                    except Exception:
                        rows = None

            # 既存イベント名は維持（下位互換）
            audit_ok(
                "collector.fetch.ok",
                feature="collector",
                exchange=self.exchange,
                topic=self.topic,
                payload={
                    "sample": bool(result is not None),
                    "latency_ms": latency_ms,
                    **({"rows": rows} if rows is not None else {})
                },
            )

            # 成功したらバックオフ解除
            self._backoff_ms = 0

        except Exception as e:
            # 失敗: status を WARN/CRIT（とりあえず CRIT）に
            self.status.update(
                self.exchange, self.topic, ok=False, cause=type(e).__name__, notes=str(e)
            )
            try:
                self.status.flush()
            except Exception:
                pass

            audit_err(
                "collector.fetch.fail",
                feature="collector",
                exchange=self.exchange,
                topic=self.topic,
                cause=type(e).__name__,
                payload={"error": str(e)},
            )

            # 失敗したのでバックオフを指数的に延伸
            self._backoff_ms = min(
                self._max_backoff_ms,
                (self._backoff_ms * 2) if self._backoff_ms > 0 else self._base_backoff_ms
            )

    def run_forever(self, *, interval_sec: float = 1.0, stop_after: Optional[int] = None) -> None:
        """
        interval_sec ごとに run_once() を実行。stop_after 回で抜ける（Noneなら無限）。
        """
        # リーダー取得（必要なときだけ）
        if self.use_leader_lock and self._lock:
            got = self._lock.acquire()
            if not got:
                audit_err("collector.worker.leader.busy", feature="collector",
                          exchange=self.exchange, topic=self.topic)
                return

        self._last_renew_m = _monotonic()

        audit_ok(
            "collector.worker.start",
            feature="collector",
            exchange=self.exchange,
            topic=self.topic,
            payload={"interval_sec": interval_sec},
        )
        count = 0
        try:
            while True:
                self.run_once()

                # 心拍（一定間隔で renew）
                if self.use_leader_lock and self._lock:
                    now_m = _monotonic()
                    if (now_m - self._last_renew_m) >= self._renew_every_sec:
                        try:
                            self._lock.renew()
                            self._last_renew_m = now_m
                        except Exception as e:
                            audit_err(
                                "collector.worker.renew.fail",
                                feature="collector",
                                exchange=self.exchange,
                                topic=self.topic,
                                cause=type(e).__name__,
                                payload={"error": str(e)},
                            )

                count += 1
                if stop_after is not None and count >= stop_after:
                    break
                # ジッタ（±10%）＋ バックオフ（失敗時のみ増加）
                jitter = random.uniform(0.9, 1.1)
                delay = (interval_sec + (self._backoff_ms / 1000.0)) * jitter
                time.sleep(max(0.05, delay))

        finally:
            audit_ok(
                "collector.worker.stop",
                feature="collector",
                exchange=self.exchange,
                topic=self.topic,
                payload={"count": count},
            )
            # リーダー解放
            if self.use_leader_lock and self._lock:
                self._lock.release()
