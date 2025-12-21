# path: ./btcts_next/src/btcts/collector/main.py
# desc: collector 常駐プロセスのエントリ。settings から exchanges/endpoints/collector を読み、Scheduler を起動する。

from __future__ import annotations

import json
import os
import signal
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from btcts.core import audit
from btcts.settings import load_yaml

from .rate import RatePolicy
from .scheduler import Endpoint, Scheduler
from .providers import bitflyer
from .status import CollectorStatus, write_status


def _now() -> float:
    return time.time()


def _utc_yyyymmdd(ts: Optional[float] = None) -> str:
    dt = datetime.fromtimestamp(ts or time.time(), tz=timezone.utc)
    return dt.strftime("%Y%m%d")


def _collector_out_path(exchange: str, topic: str, ts: Optional[float] = None) -> str:
    data_dir = os.environ.get("BTC_TS_DATA_DIR", "") or os.getcwd()
    ymd = _utc_yyyymmdd(ts)
    # 例: <DATA_DIR>/collector/bitflyer/orderbook/20251219.jsonl
    return os.path.join(data_dir, "collector", exchange, topic, f"{ymd}.jsonl")


def _append_jsonl(path: str, record: Dict[str, Any]) -> int:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
    return len(line.encode("utf-8"))


def _as_bool(v: Any, default: bool = False) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("1", "true", "yes", "y", "on"):
            return True
        if s in ("0", "false", "no", "n", "off"):
            return False
    return default


def _as_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _norm_exchanges_cfg(raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """exchanges 設定を {exchange: {...}} に正規化する。"""
    if not isinstance(raw, dict):
        return {}

    # 1) {exchanges: {bitflyer: {...}}}
    ex = raw.get("exchanges")
    if isinstance(ex, dict):
        return {str(k): (v if isinstance(v, dict) else {}) for k, v in ex.items()}

    # 2) 直下が exchange マップ
    return {str(k): (v if isinstance(v, dict) else {}) for k, v in raw.items()}


def _build_policies(exchanges_cfg: Dict[str, Any], monitoring_cfg: Dict[str, Any]) -> List[Tuple[str, RatePolicy]]:
    exmap = _norm_exchanges_cfg(exchanges_cfg)

    # safety_factor は monitoring 由来（将来統合のためここで受ける）
    # 未設定なら 0.9、bitflyer は 0.8 を既定（あなたの引継ぎ通り）
    sf_map: Dict[str, float] = {}
    sf = monitoring_cfg.get("safety_factor") if isinstance(monitoring_cfg, dict) else None
    if isinstance(sf, dict):
        for k, v in sf.items():
            sf_map[str(k)] = _as_float(v, 0.9)

    out: List[Tuple[str, RatePolicy]] = []
    for ex, cfg in exmap.items():
        enabled = _as_bool(cfg.get("enabled"), True)
        if not enabled:
            continue

        official = _as_float(cfg.get("official_max_rps"), 0.0)
        if official <= 0:
            # 設定が無い場合はとりあえず 1 rps（後で schema を厳格化）
            official = 1.0

        burst_base = _as_float(cfg.get("burst_base_sec"), 1.0)

        # soft/hard: WARN=soft, CRIT=hard（未設定は 0.8 / 0.9）
        soft_ratio = _as_float(cfg.get("soft_ratio"), 0.8)
        hard_ratio = _as_float(cfg.get("hard_ratio"), 0.9)

        # もし設定が逆（hard < soft）なら入れ替えて保護する
        if hard_ratio < soft_ratio:
            soft_ratio, hard_ratio = hard_ratio, soft_ratio

        # safety_factor があるなら official に掛ける（「制限を食らわない」設計）
        sfv = sf_map.get(ex)
        if sfv is None:
            sfv = 0.8 if ex.lower() == "bitflyer" else 0.9
        official_eff = max(official * sfv, 0.1)

        out.append(
            (
                ex,
                RatePolicy(
                    official_max_rps=official_eff,
                    soft_ratio=soft_ratio,
                    hard_ratio=hard_ratio,
                    burst_base_sec=burst_base,
                ),
            )
        )

    return out


def _norm_endpoints_cfg(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    endpoints 設定を items(list[dict]) に正規化する。

    対応形式:
    A) {items: [{exchange, topic, url, method, max_rps, burst, priority/prio, enabled}, ...]}
    B) {bitflyer: {orderbook: {...}, trades: {...}}, binance: {...}}  ← 現在の endpoints.yaml
       ※ B は (exchange -> endpoint_name -> cfg) を items へ展開する
    """
    if not isinstance(raw, dict):
        return []

    # A) {items:[...]}
    items = raw.get("items")
    if isinstance(items, list):
        return [x for x in items if isinstance(x, dict)]

    # B) {exchange: {endpoint_name: {...}}}
    out: List[Dict[str, Any]] = []
    for ex, mp in raw.items():
        if not isinstance(mp, dict):
            continue
        for name, cfg in mp.items():
            if not isinstance(cfg, dict):
                continue
            it: Dict[str, Any] = dict(cfg)  # shallow copy
            it.setdefault("exchange", str(ex))
            # topic/endpoint 名の扱いを統一（UI/health と揃える）
            it.setdefault("topic", str(cfg.get("topic") or name))
            # enabled が無ければ True
            it.setdefault("enabled", True)
            out.append(it)

    return out


def _make_runner(sch: Scheduler, exchange: str, topic: str, cfg: Dict[str, Any]) -> Any:
    """
    endpoint runner を生成する。
    - 成功: compact して jsonl へ保存
    - 429: Retry-After を rc に反映して例外化（last_ok を更新させない）
    """

    ex_l = exchange.strip().lower()
    tp_l = topic.strip().lower()

    # endpoints.yaml から任意パラメータを拾えるようにしておく（無ければ既定）
    product_code = str(cfg.get("product_code") or "BTC_JPY")
    count = int(_as_float(cfg.get("count"), 50))
    depth = int(_as_float(cfg.get("depth"), 10))
    limit = int(_as_float(cfg.get("limit"), 50))
    timeout_sec = float(_as_float(cfg.get("timeout_sec"), 10.0))

    def _handle_http_result(res: bitflyer.HttpResult) -> Dict[str, Any]:
        """
        provider の戻りを「dict」に正規化して返す。
        - ok かつ dict: そのまま返す
        - ok かつ list: {"items": list} に包む（trades系で起きがち）
        - 429: RateController へ反映し例外
        - その他: 例外
        """
        if res.ok:
            if isinstance(res.payload, dict):
                return res.payload
            if isinstance(res.payload, list):
                return {"items": res.payload}

            # ok だが想定外型
            audit.emit(
                "collector.http.unexpected_payload",
                feature="collector",
                level="WARN",
                payload={
                    "exchange": exchange,
                    "topic": topic,
                    "payload_type": type(res.payload).__name__,
                },
            )
            raise RuntimeError(
                f"unexpected payload type exchange={exchange} topic={topic} type={type(res.payload).__name__}"
            )

        # 429 → rc へ反映
        if res.status_code == 429:
            try:
                sch.rc.on_429(exchange, res.retry_after_sec)  # type: ignore[attr-defined]
            except Exception:
                pass

            audit.emit(
                "collector.http.429",
                feature="collector",
                level="CRIT",
                payload={
                    "exchange": exchange,
                    "topic": topic,
                    "retry_after_sec": res.retry_after_sec,
                    "err": res.err,
                },
            )
            raise RuntimeError(
                f"429 rate limited exchange={exchange} topic={topic} retry_after={res.retry_after_sec}"
            )

        audit.emit(
            "collector.http.fail",
            feature="collector",
            level="WARN",
            payload={
                "exchange": exchange,
                "topic": topic,
                "status_code": res.status_code,
                "err": res.err,
            },
        )
        raise RuntimeError(f"http fail exchange={exchange} topic={topic} code={res.status_code} err={res.err}")

    def _run() -> None:
        t0 = time.time()

        # --- bitflyer public ---
        if ex_l == "bitflyer" and tp_l in ("orderbook", "board"):
            res = bitflyer.fetch_board(product_code=product_code)
            raw = _handle_http_result(res)
            rec = bitflyer.compact_board(raw, depth=depth)
            outp = _collector_out_path("bitflyer", "orderbook", ts=t0)
            nbytes = _append_jsonl(outp, rec)

            audit.emit(
                "collector.endpoint.ok",
                feature="collector",
                level="INFO",
                payload={
                    "exchange": exchange,
                    "topic": "orderbook",
                    "bytes": nbytes,
                    "elapsed_ms": int((time.time() - t0) * 1000),
                },
            )
            return

        if ex_l == "bitflyer" and tp_l in ("trades", "executions"):
            res = bitflyer.fetch_executions(product_code=product_code, count=count)
            raw = _handle_http_result(res)
            rec = bitflyer.compact_executions(raw, limit=limit)
            outp = _collector_out_path("bitflyer", "trades", ts=t0)
            nbytes = _append_jsonl(outp, rec)

            audit.emit(
                "collector.endpoint.ok",
                feature="collector",
                level="INFO",
                payload={
                    "exchange": exchange,
                    "topic": "trades",
                    "bytes": nbytes,
                    "elapsed_ms": int((time.time() - t0) * 1000),
                },
            )
            return

        # --- fallback ---
        audit.emit(
            "collector.endpoint.skip",
            feature="collector",
            level="DEBUG",
            payload={"exchange": exchange, "topic": topic},
        )

    return _run


def build_scheduler() -> Scheduler:
    exchanges_cfg = load_yaml("exchanges")
    endpoints_cfg = load_yaml("endpoints")
    monitoring_cfg = load_yaml("monitoring")
    collector_cfg = load_yaml("collector")

    sch = Scheduler()

    # policies
    for ex, pol in _build_policies(exchanges_cfg, monitoring_cfg):
        sch.set_policy(ex, pol)

    # endpoints
    items = _norm_endpoints_cfg(endpoints_cfg)
    added = 0
    for it in items:
        ex = str(it.get("exchange") or "").strip()
        topic = str(it.get("topic") or it.get("endpoint") or "").strip()
        if not ex or not topic:
            continue

        if not _as_bool(it.get("enabled"), True):
            continue

        # priority/prio の両対応
        prio = int(_as_float(it.get("priority"), _as_float(it.get("prio"), 0)))

        # interval:
        # - max_rps が設定されていればそれに従う（endpoint 単位）
        # - 無ければ 1秒
        max_rps = _as_float(it.get("max_rps"), 0.0)
        interval = (1.0 / max(max_rps, 0.1)) if max_rps > 0 else 1.0

        sch.add(
            Endpoint(
                exchange=ex,
                endpoint=topic,
                priority=prio,
                target_interval=interval,
                runner=_make_runner(sch, ex, topic, it),
            )
        )

        added += 1

    # endpoints が無い場合は、enabled exchange ごとにダミーを1本ずつ作る
    if added == 0:
        exmap = _norm_exchanges_cfg(exchanges_cfg)
        for ex, cfg in exmap.items():
            if not _as_bool(cfg.get("enabled"), True):
                continue
            sch.add(
                Endpoint(
                    exchange=ex,
                    endpoint="dummy",
                    priority=0,
                    target_interval=1.0,
                    runner=_make_runner(sch, ex, "dummy", {}),
                )
            )

    # collector 設定のループ周期（あれば反映）
    # ※現時点では Scheduler.run_forever の引数で使うので main 側で保持
    sch._btcts_collector_cfg = collector_cfg  # type: ignore[attr-defined]

    # debug: 何を読んで、何本 endpoints を登録したか（移植中の配置ミス検出用）
    try:
        endpoints_format = (
            "items"
            if isinstance(endpoints_cfg, dict) and isinstance(endpoints_cfg.get("items"), list)
            else "map"
        )
        audit.emit(
            "collector.scheduler.built",
            feature="collector",
            level="INFO",
            payload={
                "endpoints_added": added,
                "endpoints_format": endpoints_format,
                "exchanges_keys": list(_norm_exchanges_cfg(exchanges_cfg).keys())[:50],
            },
        )
    except Exception:
        pass

    return sch


def main() -> int:
    audit.emit("collector.main.start", feature="collector", level="INFO", payload={"pid": os.getpid()})

    sch = build_scheduler()
    cfg = getattr(sch, "_btcts_collector_cfg", {})  # type: ignore[attr-defined]

    tick_sec = _as_float(cfg.get("tick_sec"), 0.05) if isinstance(cfg, dict) else 0.05
    rate_every = _as_float(cfg.get("rate_state_every_sec"), 1.0) if isinstance(cfg, dict) else 1.0
    status_every = _as_float(cfg.get("status_every_sec"), 2.0) if isinstance(cfg, dict) else 2.0

    def _handle_sig(signum: int, _frame: Any) -> None:
        audit.emit(
            "collector.signal",
            feature="collector",
            level="INFO",
            payload={"signum": signum},
        )
        sch.stop()

    signal.signal(signal.SIGINT, _handle_sig)
    signal.signal(signal.SIGTERM, _handle_sig)

    try:
        write_status(CollectorStatus(ts=_now(), mode="RUNNING", message="collector main running"))
        sch.run_forever(tick_sec=tick_sec, rate_state_every_sec=rate_every, status_every_sec=status_every)
        return 0
    except Exception as e:
        audit.emit(
            "collector.main.error",
            feature="collector",
            level="CRIT",
            payload={"err": str(e)},
        )
        write_status(CollectorStatus(ts=_now(), mode="ERROR", message="collector error", last_error=str(e)))
        return 2
    finally:
        write_status(CollectorStatus(ts=_now(), mode="STOPPED", message="collector main exit"), emit_audit=False)
        audit.emit("collector.main.exit", feature="collector", level="INFO", payload={})


if __name__ == "__main__":
    raise SystemExit(main())
