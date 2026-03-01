# path: ./btcts_next/src/btcts/collector/main.py
# desc: collector 常駐プロセスのエントリ。settings から exchanges/endpoints/collector を読み、Scheduler を起動する。

from __future__ import annotations

import json
import os
import signal
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from btcts.core import audit, io, paths
from btcts.settings import svc as settings_svc

from .rate import RatePolicy
from .scheduler import Endpoint, Scheduler
from .providers import bitflyer
from .status import CollectorStatus, write_status
from .scheduler import EndpointSkipped


def _now() -> float:
    return time.time()


def _utc_yyyymmdd(ts: Optional[float] = None) -> str:
    dt = datetime.fromtimestamp(ts or time.time(), tz=timezone.utc)
    return dt.strftime("%Y%m%d")


def _collector_out_path(exchange: str, topic: str, ts: Optional[float] = None) -> str:
    # data_dir は paths の正準（ENV未設定でも repo 直下に落ちない）
    data_dir = str(paths.data_dir())
    ymd = _utc_yyyymmdd(ts)
    # 例: <DATA_DIR>/collector/bitflyer/orderbook/20251219.jsonl
    return os.path.join(data_dir, "collector", exchange, topic, f"{ymd}.jsonl")


def _append_jsonl(path: str, record: Dict[str, Any]) -> int:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # data への追記も audit と同様に「壊れにくさ」を優先（多重起動・同時追記の保護）
    # - file_lock: クロスプロセス排他
    # - append: 追記
    # - fsync_each=False: 収集性能を優先（必要なら True にできる）
    # io.file_lock は Path 前提
    p = Path(path)
    with io.file_lock(p, timeout_sec=10.0):
        io.append_jsonl(p, record, fsync_each=False)

    # io.append_jsonl は内部で JSON 文字列化して追記するため、ここでは概算バイト数を返す
    #（bytes は監査表示用。厳密でなくて良い）
    return len(json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) + 1


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
    """
    exchanges.yaml + monitoring.yaml から RatePolicy を生成する（schema準拠）。

    schema（exchanges_def.yaml）の正準:
      exchanges.<id>.enabled
      exchanges.<id>.rate.max_rps
      exchanges.<id>.rate.burst
    追加（将来拡張）:
      exchanges.<id>.rate.soft_ratio / hard_ratio / burst_base_sec などが来ても壊れないようにしておく
    """
    exmap = _norm_exchanges_cfg(exchanges_cfg)

    # NOTE:
    # - RatePolicy.official_max_rps は「取引所公式上限（事実値）」をそのまま保持する。
    # - safety_factor 等の運用上の安全係数は RateController（cap側）で扱う（ここで減衰させると二重になる）。
    _ = monitoring_cfg  # reserved

    out: List[Tuple[str, RatePolicy]] = []
    for ex, cfg in exmap.items():
        enabled = _as_bool(cfg.get("enabled"), True)
        if not enabled:
            continue

        # --- schema準拠: rate セクションから読む ---
        rate = cfg.get("rate") if isinstance(cfg.get("rate"), dict) else {}

        # 正準: max_rps
        base_max_rps = _as_float(rate.get("max_rps"), 0.0)
        if base_max_rps <= 0:
            # schema的には必須だが、Collector側は安全に落とす（start側でdisabledになる想定）
            # ここで無理に 1.0 を入れて走らせると事故るので、スキップ扱いにする。
            continue

        # burst（任意）
        burst_base = _as_float(rate.get("burst_base_sec"), 1.0)
        # schemaの burst は「回数」寄りの意味だが、現実装では burst_base_sec を使っているため、
        # 今は burst を直接使わず、将来RatePolicy側を拡張する。
        _ = _as_float(rate.get("burst"), 0.0)

        # soft/hard（cap倍率）。未設定は仕様書に合わせて 0.8 / 0.9 ではなく、
        # WARNは緩い抑制を守るため soft=0.9, hard=0.8 を既定にする。
        soft_ratio = _as_float(rate.get("soft_ratio"), _as_float(cfg.get("soft_ratio"), 0.9))
        hard_ratio = _as_float(rate.get("hard_ratio"), _as_float(cfg.get("hard_ratio"), 0.8))

        # 仕様: WARNはCRITより緩い抑制 → soft_ratio >= hard_ratio を維持
        if soft_ratio < hard_ratio:
            soft_ratio, hard_ratio = hard_ratio, soft_ratio

        # official_max_rps は「事実値（公式上限）」をそのまま採用（ここで安全係数を掛けない）
        official_max_rps = max(base_max_rps, 0.1)

        out.append(
            (
                ex,
                RatePolicy(
                    official_max_rps=official_max_rps,
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
        # 未対応(exchange/topic) は “動いてる風” の原因になるため、理由を必ず残す
        reason = "unsupported_exchange_or_topic"
        hint = "Unsupported exchange/topic. Implement it in _make_runner (providers) or fix endpoints.yaml."

        audit.emit(
            "collector.endpoint.skip",
            feature="collector",
            level="DEBUG",
            payload={
                "exchange": exchange,
                "topic": topic,
                "reason": reason,
                "normalized": {"exchange": ex_l, "topic": tp_l},
                "hint": hint,
            },
        )

        # 重要: skip は「成功扱い」にしない（Scheduler 側の no_data 判定を成立させる）
        raise EndpointSkipped(reason=reason, hint=hint)

    return _run


def build_scheduler() -> Scheduler:
    # settings は svc（schema defaults + current diff）を正準とする
    exchanges_cfg = settings_svc.load_effective("exchanges")
    endpoints_cfg = settings_svc.load_effective("endpoints")
    monitoring_cfg = settings_svc.load_effective("monitoring")
    collector_cfg = settings_svc.load_effective("collector")
    rate_control_cfg = settings_svc.load_effective("rate_control")

    sch = Scheduler()

    # Collector 設定のループ周期など（run_forever の引数で使う）
    sch._btcts_collector_cfg = collector_cfg  # type: ignore[attr-defined]

    # Phase1: Scheduler が util 判定や backoff/floor に使う共通ポリシー
    sch._btcts_rate_control_cfg = rate_control_cfg  # type: ignore[attr-defined]

    # RateController へ共通ポリシーを注入（rate_control.yaml を実効化）
    try:
        sch.rc.set_common_policy(rate_control_cfg)  # type: ignore[attr-defined]
    except Exception as e:
        # 設定不正でも即死させず、事実を監査に残してデフォルトで継続（安全側）
        audit.emit(
            "collector.rate_control.cfg.error",
            feature="collector",
            level="WARN",
            payload={"err": f"{type(e).__name__}: {e}"},
        )

    # policies
    for ex, pol in _build_policies(exchanges_cfg, monitoring_cfg):
        sch.set_policy(ex, pol)

    # endpoints
    # - endpoints.yaml をベースに items を列挙
    # - exchanges.yaml の enabled=false は endpoint 登録対象外（policy未設定で落ちる事故を防ぐ）
    # - collector.yaml: feeds.<exchange>.<topic> があれば enabled/priority/target_interval を上書きする
    items = _norm_endpoints_cfg(endpoints_cfg)

    # 有効な取引所（exchanges.yaml の enabled を正準とする）
    exmap = _norm_exchanges_cfg(exchanges_cfg)
    enabled_exchanges: set[str] = set()
    for exk, exv in exmap.items():
        if _as_bool((exv or {}).get("enabled"), True):
            enabled_exchanges.add(str(exk).strip().lower())

    # collector.yaml の enabled_exchanges がある場合はさらに絞る
    enabled_by_collector: Optional[set[str]] = None
    if isinstance(collector_cfg, dict):
        ex_list = collector_cfg.get("enabled_exchanges")
        if isinstance(ex_list, list) and len(ex_list) > 0:
            enabled_by_collector = {str(x).strip().lower() for x in ex_list if str(x).strip()}

    # feeds override（collector_def.yaml に定義される制御レイヤ）
    feeds_root = collector_cfg.get("feeds") if isinstance(collector_cfg, dict) else None
    feeds_map: Dict[str, Dict[str, Any]] = {}
    if isinstance(feeds_root, dict):
        for exk, exv in feeds_root.items():
            if not isinstance(exv, dict):
                continue
            ex_l = str(exk).strip().lower()
            feeds_map[ex_l] = {str(tk).strip().lower(): tv for tk, tv in exv.items() if isinstance(tv, dict)}

    def _get_feed_override(exchange: str, topic: str) -> Dict[str, Any]:
        ex_l = exchange.strip().lower()
        tp_l = topic.strip().lower()
        return feeds_map.get(ex_l, {}).get(tp_l, {})

    added = 0
    registered: List[Dict[str, Any]] = []
    for it in items:
        ex = str(it.get("exchange") or "").strip()
        topic = str(it.get("topic") or it.get("endpoint") or "").strip()
        if not ex or not topic:
            continue

        # exchanges.yaml / collector.yaml 側で無効な取引所は登録しない（policy未設定・事故防止）
        ex_l = ex.strip().lower()
        if ex_l not in enabled_exchanges:
            continue
        if enabled_by_collector is not None and ex_l not in enabled_by_collector:
            continue

        # endpoints.yaml 側 enabled（先に見る）
        if not _as_bool(it.get("enabled"), True):
            continue

        # feeds override（あればこちらが最終決定）
        fov = _get_feed_override(ex, topic)

        # RatePolicy が無い exchange は、後段で rc.acquire() が KeyError で落ちる。
        # テスト/運用ともに「設定不備」として endpoint 登録自体を止める（no_data/empty 判定へ寄せる）。
        try:
            if not sch.rc.has_policy(ex_l):  # type: ignore[attr-defined]
                audit.emit(
                    "collector.endpoint.skip",
                    feature="collector",
                    level="CRIT",
                    payload={
                        "exchange": ex,
                        "topic": topic,
                        "reason": "policy_not_set",
                        "hint": "Check exchanges.yaml: enabled=true and exchanges.<id>.rate.max_rps > 0 (and schema allows override).",
                    },
                )
                continue

        except Exception:
            # has_policy が無い/rc 未注入などの異常時は、より安全に「登録しない」
            continue

        if fov:
            # feeds.enabled が明示されて false なら停止（Phase1停止表現は enabled:false に統一）
            if "enabled" in fov and not _as_bool(fov.get("enabled"), True):
                continue

        # priority/prio（endpoints → feeds の順で上書き）
        prio = int(_as_float(it.get("priority"), _as_float(it.get("prio"), 0)))
        if fov and ("priority" in fov):
            prio = int(_as_float(fov.get("priority"), prio))

        # interval（endpoints.yaml の max_rps 由来 → feeds.target_interval で上書き）
        # NOTE: interval is a scheduler hint; actual pacing is enforced by RateController
        max_rps = _as_float(it.get("max_rps"), 0.0)
        interval = (1.0 / max(max_rps, 0.1)) if max_rps > 0 else 1.0

        if fov and ("target_interval" in fov):
            interval = float(_as_float(fov.get("target_interval"), interval))

        sch.add(
            Endpoint(
                exchange=ex,
                endpoint=topic,
                priority=prio,
                target_interval=interval,
                runner=_make_runner(sch, ex, topic, it),
            )
        )

        registered.append(
            {
                "exchange": ex,
                "topic": topic,
                "priority": prio,
                "target_interval": interval,
                "feeds_override": bool(fov),
            }
        )

        added += 1

    # endpoints が 0 件は「設定不備」なので起動失敗に寄せる（事故防止）
    # ダミー登録で“起動してる風”に見せると運用判断を誤るため禁止。
    if added == 0:
        audit.emit(
            "collector.endpoints.empty",
            feature="collector",
            level="CRIT",
            payload={
                "hint": "Add endpoint definitions to endpoints.yaml (format: items: [...] or exchange map).",
                "endpoints_format": (
                    "items"
                    if isinstance(endpoints_cfg, dict) and isinstance(endpoints_cfg.get("items"), list)
                    else "map"
                ),
            },
        )
        raise RuntimeError("no endpoints registered (endpoints config is empty)")

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
                "registered_topics_total": len(registered),
                "registered_topics": registered[:20],
            },
        )
    except Exception:
        pass

    return sch


def main() -> int:
    audit.emit("collector.main.start", feature="collector", level="INFO", payload={"pid": os.getpid()})
    sch: Optional[Scheduler] = None
    stop_reason: str = "unknown"
    stop_signal: Optional[int] = None
    stop_error: str = ""

    try:
        sch = build_scheduler()

        def _status_items() -> List[Dict[str, Any]]:
            try:
                return sch._build_status_items(_now())  # type: ignore[attr-defined]
            except Exception:
                return []

        cfg = getattr(sch, "_btcts_collector_cfg", {})  # type: ignore[attr-defined]

        tick_sec = _as_float(cfg.get("tick_sec"), 0.05) if isinstance(cfg, dict) else 0.05

        # rate_state.json は fsync + atomic replace を伴うため、既定を低頻度に寄せる（事故防止）
        # ※運用で秒間監視が必要なら collector.yaml 側で rate_state_every_sec を明示設定する
        rate_every = _as_float(cfg.get("rate_state_every_sec"), 10.0) if isinstance(cfg, dict) else 10.0

        status_every = _as_float(cfg.get("status_every_sec"), 2.0) if isinstance(cfg, dict) else 2.0

        startup_grace_sec = _as_float(cfg.get("startup_grace_sec"), 30.0) if isinstance(cfg, dict) else 30.0
        no_data_check_every_sec = (
            _as_float(cfg.get("no_data_check_every_sec"), 1.0) if isinstance(cfg, dict) else 1.0
        )

    except Exception as _e:
        stop_reason = "exception"
        stop_error = str(_e)

        audit.emit(
            "collector.main.error",
            feature="collector",
            level="CRIT",
            payload={"err": stop_error},
        )
        write_status(CollectorStatus(ts=_now(), mode="ERROR", message="collector error", last_error=stop_error))
        audit.emit(
            "collector.main.exit",
            feature="collector",
            level="INFO",
            payload={"reason": stop_reason, "signum": stop_signal, "err": stop_error},
        )
        return 2

    def _handle_sig(signum: int, _frame: Any) -> None:
        nonlocal stop_reason, stop_signal
        stop_reason = "signal"
        stop_signal = signum
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
        # 起動直後の状態は RUNNING を明示（msg未定義の事故を避ける）
        write_status(
            CollectorStatus(
                ts=_now(),
                mode="RUNNING",
                message="collector running",
                last_error="",
                items=_status_items(),
            ),
            emit_audit=False,
        )

        startup_grace_sec = _as_float(cfg.get("startup_grace_sec"), 30.0) if isinstance(cfg, dict) else 30.0
        no_data_check_every_sec = (
            _as_float(cfg.get("no_data_check_every_sec"), 1.0) if isinstance(cfg, dict) else 1.0
        )

        sch.run_forever(
            tick_sec=tick_sec,
            rate_state_every_sec=rate_every,
            status_every_sec=status_every,
            startup_grace_sec=startup_grace_sec,
            no_data_check_every_sec=no_data_check_every_sec,
        )

        if stop_reason == "unknown":
            stop_reason = "stop_requested"
        return 0

    except Exception as _e:
        stop_reason = "exception"
        stop_error = str(_e)

        audit.emit(
            "collector.main.error",
            feature="collector",
            level="CRIT",
            payload={"err": stop_error},
        )
        write_status(
            CollectorStatus(
                ts=_now(),
                mode="ERROR",
                message="collector error",
                last_error=stop_error,
                items=_status_items(),
            )
        )
        return 2

    finally:
        msg = f"collector main exit reason={stop_reason}"
        if stop_signal is not None:
            msg += f" signum={stop_signal}"
        if stop_error:
            msg += f" err={stop_error}"

        # 例外で落ちた場合、ERROR を STOPPED で上書きしない（原因追跡を容易にする）
        final_mode = "ERROR" if stop_reason == "exception" else "STOPPED"
        # sch があるなら items を付けて「空に戻す事故」を防ぐ
        items = []
        if sch is not None:
            try:
                items = sch._build_status_items(_now())  # type: ignore[attr-defined]
            except Exception:
                items = []

        write_status(
            CollectorStatus(ts=_now(), mode=final_mode, message=msg, last_error=stop_error, items=items),
            emit_audit=False,
        )

        audit.emit(
            "collector.main.exit",
            feature="collector",
            level="INFO",
            payload={"reason": stop_reason, "signum": stop_signal, "err": stop_error},
        )


if __name__ == "__main__":
    raise SystemExit(main())
