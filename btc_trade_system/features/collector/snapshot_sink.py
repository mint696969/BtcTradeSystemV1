# path: ./btc_trade_system/features/collector/snapshot_sink.py
# desc: 収集結果のスナップショットを data/collector/<exchange>/<topic>/YYYYMMDD.jsonl へ保存（StorageRouterで自動切替）。

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json
import os
import tempfile
import time

from btc_trade_system.common.storage_router import StorageRouter

class SnapshotSink:
    """
    収集ループの結果（軽量サマリでもOK）を日別JSONLに追記する薄い層。
    - primary(ENV) → secondary(./local) に自動フォールバック
    - 1行=1 JSON（時刻やメタを付与）
    """
    def __init__(self, base_dir: Path, *, use_local_time: bool = False):
        self.base_dir = Path(base_dir)
        self.router = StorageRouter(self.base_dir)
        self.use_local_time = bool(use_local_time)

    def _yyyymmdd(self, ts: float) -> str:
        # Trueならローカル時刻（JSTなど）で日付を切る。FalseはUTC。
        tt = time.localtime(ts) if self.use_local_time else time.gmtime(ts)
        return time.strftime("%Y%m%d", tt)

    def write_jsonl(self, *, exchange: str, topic: str, obj: Dict[str, Any]) -> Path:
        """
        任意の dict を 収集日ファイルへ追記。obj には必要なら 'count' や 'first' 等を入れてOK。
        """
        now = time.time()
        date = self._yyyymmdd(now)
        rel = f"collector/{exchange}/{topic}/{date}.jsonl"

        # 監査で追跡しやすい最低限のメタを付与
        line = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)),
            "exchange": exchange,
            "topic": topic,
            **obj,
        }
        # StorageRouter に任せて追記
        return self.router.append_jsonl("data", rel, line)
