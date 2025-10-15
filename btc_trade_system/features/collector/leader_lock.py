# path: ./btc_trade_system/features/collector/core/leader_lock.py
# desc: 収集の単一アクティブ性を担保する軽量ロック（NAS 共有前提）。昇格/心拍/降格を監査に記録。

from __future__ import annotations
import json, os, socket, time, tempfile
from pathlib import Path
from typing import Optional, Dict, Any

# optional: audit (soft dependency)
try:
    from btc_trade_system.common.audit import audit_ok, audit_err  # type: ignore
except Exception:  # pragma: no cover
    def audit_ok(event: str, *, feature: str, payload: dict | None = None) -> None:  # type: ignore
        return
    def audit_err(event: str, *, feature: str, payload: dict | None = None) -> None:  # type: ignore
        return


def _resolve_data_root(explicit: Optional[Path] = None) -> Path:
    """data ルートの解決（common.paths > ENV > ./data）。"""
    if explicit:
        return Path(explicit)
    try:
        from btc_trade_system.common.paths import data_dir  # type: ignore
        return Path(data_dir())
    except Exception:
        pass
    return Path(os.environ.get("BTC_TS_DATA_DIR", "data"))


class LeaderLock:
    """
    (data ルート)/locks/collector.leader.json を用いた軽量リーダーロック。
    - acquire(): 既存が無ければ作成。既存が stale(heartbeat 超過) なら奪取。
    - renew(): 心拍(heartbeat_ms) の更新。自分が所有者の時のみ成功。
    - release(): 自分が所有者なら解放。
    NOTE: NFS/NAS 前提のアドバイザリーロック。絶対排他は保証しないが、設計上は十分。
    """

    def __init__(self, base_dir: Path, *, stale_after_sec: int = 30):
        self.base_dir = Path(base_dir)
        # base_dir は “data ルート” 前提。二重 "data" を避ける
        self.lock_dir = self.base_dir / "locks"
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.lock_dir / "collector.leader.json"
        self.stale_after_ms = int(stale_after_sec * 1000)
        self.host = socket.gethostname()
        self.pid = os.getpid()
        self.started_ms = self._utc_ms()
        self._owned = False

    @classmethod
    def from_env(cls, *, stale_after_sec: int = 30) -> "LeaderLock":
        """ENV / common.paths から data ルートを解決して LeaderLock を生成。"""
        data_root = _resolve_data_root(None)
        return cls(base_dir=data_root, stale_after_sec=stale_after_sec)

    @staticmethod
    def _utc_ms() -> int:
        return int(time.time() * 1000)

    def _record(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "pid": self.pid,
            "started_ms": self.started_ms,
            "heartbeat_ms": self._utc_ms(),
        }

    # ---- core ops -------------------------------------------------------------
    def read(self) -> Optional[Dict[str, Any]]:
        if not self.lock_path.exists():
            return None
        try:
            with open(self.lock_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            # soft audit（存在するなら）だけ記録して握りつぶす
            try:
                audit_err("collector.leader.read.fail", feature="collector",
                          payload={"path": str(self.lock_path), "error": str(e)})
            except Exception:
                pass
            return None

    def _write_atomic(self, rec: Dict[str, Any]) -> None:
        tmp_fd, tmp_path = tempfile.mkstemp(prefix="leader_", suffix=".tmp", dir=str(self.lock_dir))
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8", newline="\n") as f:
                data = json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n"
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.lock_path)
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass

    def is_stale(self, rec: Dict[str, Any]) -> bool:
        hb = int(rec.get("heartbeat_ms", 0) or 0)
        return (self._utc_ms() - hb) > self.stale_after_ms

    def is_owned(self) -> bool:
        if not self._owned:
            return False
        rec = self.read()
        return bool(rec and rec.get("host") == self.host and int(rec.get("pid", -1)) == self.pid)

    # ---- public API -----------------------------------------------------------
    def acquire(self) -> bool:
        """自分がリーダーになる。成功すれば True。既存が生きていれば False。"""
        rec = self.read()
        if rec is None or self.is_stale(rec):
            # create or steal
            new_rec = self._record()
            self._write_atomic(new_rec)
            # verify ownership
            check = self.read()
            self._owned = bool(check and check.get("host") == self.host and int(check.get("pid", -1)) == self.pid)
            if self._owned:
                audit_ok("collector.leader.acquire", feature="collector",
                         payload={"host": self.host, "pid": self.pid})
            else:
                audit_err("collector.leader.acquire.race", feature="collector",
                          payload={"prev": rec})
            return self._owned
        else:
            return False

    def renew(self) -> bool:
        """心拍更新。自分が所有者である時のみ True。"""
        rec = self.read()
        if not rec or rec.get("host") != self.host or int(rec.get("pid", -1)) != self.pid:
            self._owned = False
            return False
        rec["heartbeat_ms"] = self._utc_ms()
        self._write_atomic(rec)
        audit_ok("collector.leader.renew", feature="collector",
                 payload={"host": self.host, "pid": self.pid})
        self._owned = True
        return True

    def release(self) -> bool:
        """自分が所有者なら解放して True。所有者でなければ何もしない。"""
        rec = self.read()
        if rec and rec.get("host") == self.host and int(rec.get("pid", -1)) == self.pid:
            try:
                os.remove(self.lock_path)
                audit_ok("collector.leader.release", feature="collector",
                         payload={"host": self.host, "pid": self.pid})
                self._owned = False
                return True
            except Exception as e:
                audit_err("collector.leader.release.fail", feature="collector",
                          payload={"error": str(e)})
                return False
        return False
