# path: btc_trade_system/features/collector/collector_status.py
# desc: Collector 全体の稼働情報を最終形 status.json に 1–3 秒周期で“原子的置換”で書き出すモジュール

from __future__ import annotations

import json
import os
import time
import tempfile
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from datetime import datetime, timezone, timedelta

# ──────────────────────────────────────────────────────────────────────────────
# 設定ロード（def.yaml のみ。current は後続で settings_svc へ差替予定）

_DEF_REL_PATH = Path(__file__).resolve().parent / "config" / "collector_def.yaml"

def _expand_env(s: str) -> str:
    if not isinstance(s, str):
        return s
    out = s
    for k, v in os.environ.items():
        out = out.replace(f"${{{k}}}", v)
    return out

def load_collector_config() -> Dict[str, Any]:
    """最小の設定ローダ。存在しない場合は既定値を返す。"""
    cfg = {
        "status": {
            "path": "${BTC_TS_DATA_DIR}/collector/status.json",
            "update_interval": DEFAULT_UPDATE_INTERVAL,
        }
    }
    try:
        import yaml  # type: ignore
        if _DEF_REL_PATH.exists():
            with _DEF_REL_PATH.open("r", encoding="utf-8") as f:
                doc = yaml.safe_load(f) or {}
                if isinstance(doc, dict):
                    cfg = {**cfg, **doc}
    except Exception as e:
        logger.debug("config load skipped/failed: %s", e)
    # 環境変数展開
    p = cfg.get("status", {}).get("path")
    if p:
        cfg["status"]["path"] = _expand_env(p)
    return cfg

# ──────────────────────────────────────────────────────────────────────────────
# ログ設定（開発中は INFO、将来 settings_svc から注入）
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")

# ──────────────────────────────────────────────────────────────────────────────
# audit_dev への発火（存在しない環境でも安全に no-op）
try:
    from btc_trade_system.features.audit_dev.writer import emit as dev_audit_emit  # type: ignore
except Exception:  # pragma: no cover - dev 環境の互換
    def dev_audit_emit(**kwargs):  # type: ignore
        logger.debug("audit_dev.emit(no-op): %s", kwargs)

# ──────────────────────────────────────────────────────────────────────────────
# 原子的ファイル置換（core.io_atomic が未実装でも単体で動くよう内包）

def atomic_replace_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """同一ボリューム上で .tmp → fsync → replace の順に原子的置換。
    NOTE: Windows でも Path.replace は同一ボリュームなら原子的。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmpname = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="\n") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        # 置換も fsync（ディレクトリ）
        os.replace(tmpname, path)
        try:
            dir_fd = os.open(path.parent, os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except Exception:
            # 一部 OS では不要/未対応
            pass
    finally:
        # 例外時に tmp が残れば掃除
        try:
            if os.path.exists(tmpname):
                os.remove(tmpname)
        except Exception:
            pass

# ──────────────────────────────────────────────────────────────────────────────
# status.json スキーマ（最終形の雛形）と型

@dataclass
class SyncInfo:
    pending: bool = False
    last: Dict[str, Any] = None  # { at: str|null, items: int, bytes: int, ok: bool }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pending": self.pending,
            "last": self.last or {"at": None, "items": 0, "bytes": 0, "ok": True},
        }

@dataclass
class LeaderInfo:
    host: str = "local"
    since: str = None  # ISO8601Z
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {"host": self.host, "since": self.since or iso_now(), "active": self.active}

@dataclass
class StorageInfo:
    primary: str = "up"  # up/down/unknown
    secondary: str = "idle"  # idle/up/down
    secondary_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "secondary_path": self.secondary_path,
        }

@dataclass
class Item:
    exchange: str = "bitflyer"
    topic: str = "orderbook"  # orderbook/trades/...
    last_ok: Optional[str] = None  # ISO8601Z or None
    age_sec: float = 0.0
    cause: Optional[str] = None  # RATE_LIMIT/NET_BLOCK/AUTH_FAIL/SRC_DOWN/INTERNAL_ERR/WRITE_ERR
    retries: int = 0
    notes: str = "ok"
    source: str = "runtime"  # runtime/history

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exchange": self.exchange,
            "topic": self.topic,
            "last_ok": self.last_ok,
            "age_sec": round(float(self.age_sec), 6),
            "cause": self.cause,
            "retries": int(self.retries),
            "notes": self.notes,
            "source": self.source,
        }

# ──────────────────────────────────────────────────────────────────────────────
# 公開 I/F

DEFAULT_UPDATE_INTERVAL = 2.0  # seconds（def.yaml が無い環境でも動く既定）
HISTORY_INTERVAL = 10.0  # health_history.jsonl へのサンプリング間隔（秒）
HISTORY_MAX_DAYS = 10    # 最大保持日数
_last_history_ts: float = 0.0  # 直近で履歴を書いた時刻（epoch秒）


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"


def default_status_template() -> Dict[str, Any]:
    return {
        "updated_at": iso_now(),
        "leader": LeaderInfo().to_dict(),
        "storage": StorageInfo().to_dict(),
        "sync": SyncInfo().to_dict(),
        "items": [],
        # 取引所ごとのレート制御状態（あれば後段で上書き）
        # 例:
        #   "rate": {
        #       "bitflyer": {
        #           "soft_limit": true,
        #           "hard_limit": false,
        #           "penalty": 2,
        #           "cooldown_until": "...",
        #           "last_rate_limited_at": "...",
        #           "tokens": 0.0,
        #           "burst": 2
        #       },
        #       ...
        #   }
        "rate": {},
    }


def resolve_status_path() -> Path:
    cfg = load_collector_config()
    status_path = cfg.get("status", {}).get("path")
    if status_path:
        p = Path(status_path)
        if p.is_absolute():
            return p
    # 相対 or 未設定時は data_dir へ
    data_dir = os.environ.get("BTC_TS_DATA_DIR") or os.environ.get("DATA")
    if not data_dir:
        data_dir = str(Path(__file__).resolve().parents[3] / "data")
    return Path(data_dir) / "collector" / "status.json"


def validate_status_schema(status: Dict[str, Any]) -> None:
    # 最低限の検査（Health 側の堅牢化を阻害しない程度に）
    if not isinstance(status, dict):
        raise ValueError("status must be dict")
    for key in ("updated_at", "leader", "storage", "sync", "items"):
        if key not in status:
            raise ValueError(f"status missing key: {key}")
    if not isinstance(status["items"], list):
        raise ValueError("status.items must be list")

# 追記: ハートビートを読むユーティリティ
def _hb_path(exchange: str, endpoint: str) -> Path:
    data_dir = os.environ.get("BTC_TS_DATA_DIR") or os.environ.get("DATA")
    if not data_dir:
        data_dir = str(Path(__file__).resolve().parents[3] / "data")
    return Path(data_dir) / "collector" / "heartbeat" / f"{exchange}_{endpoint}.json"

def _read_heartbeat(exchange: str, endpoint: str) -> Optional[float]:
    """ミリ秒エポックの ts を秒(float)で返す。無ければ None。"""
    p = _hb_path(exchange, endpoint)
    try:
        with p.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        ts_ms = obj.get("ts")
        if isinstance(ts_ms, (int, float)):
            return float(ts_ms) / 1000.0
    except FileNotFoundError:
        return None
    except Exception as e:
        logger.debug("heartbeat read err on %s/%s: %s", exchange, endpoint, e)
    return None

# RateController 側が書き出す rate_state.json の読み取り
def _rate_state_path() -> Path:
    data_dir = os.environ.get("BTC_TS_DATA_DIR") or os.environ.get("DATA")
    if not data_dir:
        data_dir = str(Path(__file__).resolve().parents[3] / "data")
    return Path(data_dir) / "collector" / "rate_state.json"


def _read_rate_state() -> Optional[Dict[str, Any]]:
    """
    RateController からのレート制御状態スナップショットを読む。
    フォーマットは以下のような dict を想定（キーは取引所）:

      {
        "bitflyer": {
          "soft_limit": true,
          "hard_limit": false,
          "penalty": 2,
          "cooldown_until": "...",
          "last_rate_limited_at": "...",
          "tokens": 0.0,
          "burst": 2
        },
        ...
      }

    形式チェックは最小限に留め、読み取れなければ None を返す。
    """
    p = _rate_state_path()
    try:
        with p.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, dict):
            return obj
    except FileNotFoundError:
        return None
    except Exception as e:
        logger.debug("rate_state read err: %s", e)
    return None

def _health_history_path() -> Path:
    """
    health タイムライン用の履歴ファイルパスを返す。
    status.json と同じ data/collector ディレクトリ配下に health_history.jsonl を置く。
    """
    # status.json と同じルート（DATA/BTC_TS_DATA_DIR）を流用
    status_path = resolve_status_path()
    return status_path.with_name("health_history.jsonl")


def _append_health_history(status: Dict[str, Any]) -> None:
    """
    status スナップショットから 10秒粒度で health_history.jsonl へ追記する。

    - HISTORY_INTERVAL 未満の間隔では何もしない（高頻度ループから負荷を切り離す）
    - 1日1回程度（UTC 00:00）で 10日より古い行を削除する
    """
    global _last_history_ts

    now = time.time()
    if (now - _last_history_ts) < HISTORY_INTERVAL:
        return
    _last_history_ts = now

    path = _health_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    # 1行 = {ts, items, rate}
    try:
        row = {
            "ts": status.get("updated_at") or iso_now(),
            "items": status.get("items", []),
            "rate": status.get("rate", {}),
        }
        line = json.dumps(row, ensure_ascii=False) + "\n"
        with path.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        logger.debug("health_history append skipped: %s", e)
        return

    # ---- 保持期間のローテーション（1日1回程度）----
    try:
        # UTCの現在日時から cutoff を計算
        now_utc = datetime.now(timezone.utc)
        # 毎日 00:05 頃にだけローテーションを試みるイメージ（負荷を抑える）
        if not (now_utc.hour == 0 and now_utc.minute < 10):
            return

        cutoff = now_utc - timedelta(days=HISTORY_MAX_DAYS)
        cutoff_iso = cutoff.replace(microsecond=0).isoformat().replace("+00:00", "Z")

        # 既存ファイルを読み込み、cutoff 以降の行だけ残す
        try:
            with path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return

        kept: List[str] = []
        for ln in lines:
            try:
                obj = json.loads(ln)
                ts = obj.get("ts")
                if not isinstance(ts, str):
                    continue
                # 文字列比較でも ISO8601Z なら時間順に並ぶので十分
                if ts >= cutoff_iso:
                    kept.append(ln)
            except Exception:
                # 壊れた行は破棄
                continue

        # ローテーション結果を書き戻し
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            f.writelines(kept)
        os.replace(tmp, path)
    except Exception as e:
        logger.debug("health_history rotate skipped: %s", e)

def build_status_snapshot(prev: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    ハートビートから実際の last_ok / age_sec / cause を作る。
    まずは bitflyer の orderbook / trades の2点のみ。
    """
    now_iso = iso_now()
    now_sec = time.time()

    # 既定テンプレート
    base = default_status_template()
    base["updated_at"] = now_iso

    # RateController からのレート制御状態（あれば上書き）
    rate_state = _read_rate_state()
    if isinstance(rate_state, dict):
        base["rate"] = rate_state

    # 閾値（def.yaml から取得）
    cfg = load_collector_config()
    stale_warn = float(cfg.get("status", {}).get("stale_warn_sec", 3.0))
    stale_crit = float(cfg.get("status", {}).get("stale_crit_sec", 10.0))

    endpoints = [
        ("bitflyer", "orderbook"),
        ("bitflyer", "trades"),
    ]

    items = []
    for ex, ep in endpoints:
        hb_sec = _read_heartbeat(ex, ep)  # 秒（float） or None
        if hb_sec is None:
            last_ok_iso = None
            age = stale_crit
            cause = "SRC_DOWN"  # まだ一度も来ていない or 消失
            notes = "no heartbeat"
        else:
            age = max(0.0, now_sec - hb_sec)
            # ISO表記
            last_ok_iso = datetime.fromtimestamp(hb_sec, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"
            if age >= stale_crit:
                cause, notes = "SRC_DOWN", "stale(crit)"
            elif age >= stale_warn:
                cause, notes = None, "stale(warn)"  # 判定はHealth側の色分けに任せる
            else:
                cause, notes = None, "ok"

        items.append(Item(
            exchange=ex,
            topic=ep,
            last_ok=last_ok_iso,
            age_sec=age,
            cause=cause,
            retries=0,
            notes=notes,
            source="runtime"
        ).to_dict())

    base["items"] = items
    return base


def write_status_file(status: Dict[str, Any], path: Path) -> None:
    validate_status_schema(status)
    text = json.dumps(status, ensure_ascii=False, indent=2) + "\n"
    atomic_replace_text(path, text)

    dev_audit_emit(
        event="collector.status.write",
        level="INFO",
        feature="collector",
        payload={"path": str(path), "bytes": len(text)},
    )


def load_status_safe(path: Path) -> Optional[Dict[str, Any]]:
    """status.json を安全に読む。BOM 付きや破損を許容し、読めなければ None。"""
    try:
        # まずは通常の UTF-8
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        # BOM 付き（utf-8-sig）を再試行
        try:
            with path.open("r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("status.json broken: %s", e)
            # 破損ファイルは .bad へ退避（原本は次回書き換えで復旧）
            try:
                bad = path.with_suffix(path.suffix + ".bad")
                path.rename(bad)
                logger.warning("status.json moved to: %s", bad)
            except Exception:
                pass
            return None


# ──────────────────────────────────────────────────────────────────────────────
# 周期更新ループ（サービス化は後続：collector_entry / scheduler で担当）

def update_loop(interval: float = DEFAULT_UPDATE_INTERVAL, *, once: bool = False) -> None:
    # 設定から interval/path を反映
    cfg = load_collector_config()
    interval = float(cfg.get("status", {}).get("update_interval", interval))
    path = resolve_status_path()
    logger.info("status path = %s (interval=%.3fs)", path, interval)

    while True:
        start = time.perf_counter()
        prev = load_status_safe(path)
        status = build_status_snapshot(prev)
        try:
            write_status_file(status, path)
            # health タイムライン用の履歴を 10秒粒度で追記
            _append_health_history(status)
        except Exception as e:
            logger.exception("failed to write status.json: %s", e)
            # WRITE_ERR を self-status にも刻む（次周回で可視化）
            if status["items"]:
                status["items"][0]["cause"] = "WRITE_ERR"
            try:
                text = json.dumps(status, ensure_ascii=False, indent=2) + "\n"
                atomic_replace_text(path, text)
            except Exception:
                pass
        elapsed = time.perf_counter() - start
        if once:
            break
        time.sleep(max(0.0, interval - elapsed))


# ──────────────────────────────────────────────────────────────────────────────
# CLI 実行
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Write collector status.json atomically.")
    parser.add_argument("--interval", type=float, default=DEFAULT_UPDATE_INTERVAL, help="update interval seconds")
    parser.add_argument("--once", action="store_true", help="write once and exit")
    args = parser.parse_args()

    update_loop(args.interval, once=args.once)

