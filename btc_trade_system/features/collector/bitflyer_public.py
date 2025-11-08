# path: btc_trade_system/features/collector/bitflyer_public.py
# desc: bitFlyer 公開RESTの最小ランナー。成功時はハートビートを刻み、429時は RateLimited を投げる。

from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Optional

# dev_audit（無ければ no-op）
try:
    from btc_trade_system.features.audit_dev.writer import emit as dev_audit_emit  # type: ignore
except Exception:  # pragma: no cover
    def dev_audit_emit(**kwargs):  # type: ignore
        pass

# Scheduler 側の例外を利用（429/Retry-After）
try:
    from .collector_scheduler import RateLimited  # type: ignore
except Exception:
    class RateLimited(Exception):  # フォールバック
        def __init__(self, retry_after_sec: Optional[float] = None, message: str = "rate limited"):
            super().__init__(message)
            self.retry_after_sec = retry_after_sec

# 置換書き（Windows耐性つき）。将来は core/io_atomic を使う。
def _atomic_write_text(path: Path, text: str) -> None:
    """
    Windows の一時的ロック（WinError 32）に耐える原子的置換。
    一時ファイルは衝突しにくいユニーク名を用い、PermissionError 時は短いバックオフで数回再試行する。
    """
    import uuid
    path.parent.mkdir(parents=True, exist_ok=True)

    # ユニークな tmp（with_suffix だと置換になるので name を直接拡張）
    tmp = path.parent / f"{path.name}.{uuid.uuid4().hex}.tmp"

    # 先にフル書込み・クローズ（ディスクへ確実に押し出す）
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())

    # 置換（短いバックオフでリトライ）
    max_retry = 6
    delay = 0.02  # 20ms から開始
    for i in range(max_retry):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            if i == max_retry - 1:
                # 最終リトライでもダメならそのまま投げる
                raise
            time.sleep(delay)
            delay *= 1.8  # ~200ms まで漸増
        except Exception:
            # それ以外は即座に伝播（想定外の異常）
            raise

    # ディレクトリ fsync（best-effort）
    try:
        dir_fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except Exception:
        pass


def _data_dir() -> Path:
    return Path(os.environ.get("BTC_TS_DATA_DIR") or os.environ.get("DATA") or (Path(__file__).resolve().parents[3] / "data"))


def _heartbeat_path(exchange: str, endpoint: str) -> Path:
    return _data_dir() / "collector" / "heartbeat" / f"{exchange}_{endpoint}.json"


def _write_heartbeat(exchange: str, endpoint: str) -> None:
    payload = {"ts": int(time.time() * 1000)}
    _atomic_write_text(_heartbeat_path(exchange, endpoint), json.dumps(payload, ensure_ascii=False))


def _fetch_json(url: str, *, timeout: float = 5.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "BtcTSv1/collector"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if code == 429:
                ra = resp.headers.get("Retry-After")
                retry = float(ra) if ra and ra.isdigit() else None
                raise RateLimited(retry_after_sec=retry)
            if code >= 400:
                raise RuntimeError(f"HTTP {code}")
            data = resp.read()
            return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as e:  # type: ignore
        if e.code == 429:
            ra = e.headers.get("Retry-After")
            retry = float(ra) if ra and str(ra).isdigit() else None
            raise RateLimited(retry_after_sec=retry)
        raise


# ランナー：板（軽量化のため最初は ticker でもOK。URL は必要に応じて切替）
BITFLYER_TICKER = "https://api.bitflyer.com/v1/ticker?product_code=BTC_JPY"
BITFLYER_BOARD  = "https://api.bitflyer.com/v1/board?product_code=BTC_JPY"


def run_orderbook() -> None:
    """orderbook ランナー：成功でハートビート、失敗は例外に包んで上位へ。"""
    # まずは軽い ticker で疎通を確認。後で board に切替可。
    _ = _fetch_json(BITFLYER_TICKER)
    _write_heartbeat("bitflyer", "orderbook")
    dev_audit_emit(event="collector.heartbeat", level="INFO", feature="collector",
                   payload={"exchange": "bitflyer", "endpoint": "orderbook"})


def run_trades() -> None:
    # 将来の実装。まずは orderbook だけでもOK
    _ = _fetch_json(BITFLYER_TICKER)
    _write_heartbeat("bitflyer", "trades")
    dev_audit_emit(event="collector.heartbeat", level="INFO", feature="collector",
                   payload={"exchange": "bitflyer", "endpoint": "trades"})

