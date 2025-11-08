# path: ./btc_trade_system/ops/collector/entry.py
# desc: collector 運転サブコマンド（start/status/demo）公式入口。設定YAML(endpoints_def.yaml)でエンドポイントを登録。

from __future__ import annotations

import argparse
import os
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from .lock import CollectorLock

# YAML 読み込み（PyYAML 必須）
try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError("PyYAML is required. Install via: pip install pyyaml") from e


# == 環境整備 ==

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]

def _ensure_env() -> None:
    """DATA 環境などを整える（開発フォールバック）。"""
    if not os.environ.get("BTC_TS_DATA_DIR") and not os.environ.get("DATA"):
        os.environ["BTC_TS_DATA_DIR"] = str(_repo_root() / "data")
    # PYTHONPATH は通常不要だが、明示しても害はない
    os.environ.setdefault("PYTHONPATH", str(_repo_root()))


# == エンドポイント定義YAML ==

def _default_endpoints_yaml_path() -> Path:
    """
    唯一の正を features 側に置く。
    互換のため、存在しない場合のみ ops 側をフォールバックで探す。
    """
    here = Path(__file__).resolve()
    # 1st: features 側（正）
    feat = here.parents[3] / "btc_trade_system" / "features" / "collector" / "config" / "endpoints_def.yaml"
    if feat.exists():
        return feat
    # 2nd: 旧/互換（ops 側）
    ops = here.parent / "config" / "endpoints_def.yaml"
    return ops


def _load_endpoints(def_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """YAML から [{exchange, endpoint, priority, target_interval, runner}] を平坦化して返す。
    runner は 'module.path:func' 形式。
    """
    path = def_path or _default_endpoints_yaml_path()
    if not path.exists():
        raise FileNotFoundError(f"endpoints_def.yaml not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: List[Dict[str, Any]] = []

    for ex in data.get("exchanges", []):
        ex_name = ex.get("name")
        for ep in ex.get("endpoints", []):
            key = ep.get("key")
            priority = int(ep.get("priority", 0))
            target = float(ep.get("target_interval", 1.0))
            runner_spec = ep.get("runner")

            if not ex_name or not key:
                raise ValueError(f"invalid endpoint row: exchange={ex_name}, key={key}")
            if not runner_spec:
                raise ValueError(f"runner missing for {ex_name}/{key}")
            if ":" not in runner_spec:
                raise ValueError(f"runner must be 'module.path:func' format: {runner_spec}")

            mod_name, func_name = runner_spec.split(":", 1)
            mod = importlib.import_module(mod_name)
            runner = getattr(mod, func_name)

            out.append(dict(
                exchange=ex_name,
                endpoint=key,
                priority=priority,
                target_interval=target,
                runner=runner,
            ))
    return out

def _load_exchange_rates(def_path: Optional[Path] = None) -> Dict[str, Dict[str, float]]:
    """YAML から {exchange: {max_rps, burst}} を返す。無ければ空。"""
    path = def_path or _default_endpoints_yaml_path()
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: Dict[str, Dict[str, float]] = {}
    for ex in data.get("exchanges", []):
        name = ex.get("name")
        rate = ex.get("rate") or {}
        if not name:
            continue
        max_rps = float(rate.get("max_rps", 0.0))
        burst = int(rate.get("burst", 1))
        out[name] = {"max_rps": max_rps, "burst": burst}
    return out

# == サブコマンド ==

def cmd_start(args) -> None:
    """設定YAMLを読み、Scheduler に登録して常駐実行"""
    from btc_trade_system.features.collector.collector_scheduler import Scheduler

    _ensure_env()
    def_path = Path(args.def_path).resolve() if getattr(args, "def_path", None) else None

    # === ここから追記：多重起動ロック ===
    lock = CollectorLock("collector")
    lock.acquire(stale_sec=3600, force=getattr(args, "force", False))
    try:
        # 1) exchange 単位のレート（max_rps / burst）
        rates = _load_exchange_rates(def_path)

        # 2) endpoint 群
        ep_list = _load_endpoints(def_path)

        sch = Scheduler()

        # 1) まず exchange レベルのポリシーを投入
        for ex, r in rates.items():
            sch.set_exchange_policy(ex, max_rps=r.get("max_rps", 0.0), burst=int(r.get("burst", 1)))

        # 2) 次に endpoint の SLA を投入
        for ep in ep_list:
            sch.register_endpoint(
                ep["exchange"], ep["endpoint"],
                priority=ep["priority"],
                target_interval=ep["target_interval"],
                runner=ep["runner"],
            )

        sch.run_forever()
    finally:
        lock.release()


def cmd_status(args) -> None:
    """status writer（常駐/単発）。"""
    from btc_trade_system.features.collector.collector_status import update_loop

    _ensure_env()
    update_loop(interval=float(args.interval), once=bool(args.once))


def cmd_demo(args) -> None:
    """開発用デモ：ダミー runner を回す。"""
    from btc_trade_system.features.collector.collector_scheduler import Scheduler, RateLimited
    import random

    _ensure_env()
    sch = Scheduler()

    def dummy():
        r = random.random()
        if r < 0.08:
            raise RateLimited(retry_after_sec=1.2)
        elif r < 0.10:
            raise RuntimeError("net glitch")

    sch.register_endpoint("bitflyer", "orderbook", priority=0, target_interval=0.3, runner=dummy)
    sch.register_endpoint("bitflyer", "trades",   priority=1, target_interval=0.6, runner=dummy)
    sch.run_forever()


# == CLI ==

def main() -> None:
    p = argparse.ArgumentParser(prog="btc_ts.collector", description="BtcTS Collector Ops")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("start", help="Run scheduler + endpoints (collector)")
    sp.add_argument("--def", dest="def_path", default=None, help="path to endpoints_def.yaml")
    sp.set_defaults(func=cmd_start)
    sp.add_argument("--force", action="store_true", help="stale/unknown lock を強制破棄して起動")

    sp = sub.add_parser("status", help="Run status writer")
    sp.add_argument("--interval", type=float, default=2.0, help="status update interval sec")
    sp.add_argument("--once", action="store_true", help="write once and exit")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("demo", help="Run demo scheduler")
    sp.set_defaults(func=cmd_demo)

    args = p.parse_args()
    args.func(args)

