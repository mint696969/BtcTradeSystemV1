# path: btc_trade_system/ops/collector/lock.py
# desc: コレクタ多重起動防止のファイルロック。stale/force 対応・atomic 書き込み。

from __future__ import annotations
import os
import time
import errno
from pathlib import Path
from typing import Optional

def _logs_dir() -> Path:
    root = Path(os.environ.get("BTC_TS_LOGS_DIR") or os.environ.get("LOGS") or (Path.cwd() / "logs"))
    (root / "locks").mkdir(parents=True, exist_ok=True)
    return root

class CollectorLock:
    """
    単純なPIDロック:
      - ロックファイル: logs/locks/<name>.lock
      - 内容: {"pid": <int>, "ts": <unix_time>}
      - 既存プロセスが生存中なら取得失敗
      - stale（指定秒より古い/プロセス死）なら奪取可能
      - --force 指定時は問答無用で奪取
    """
    def __init__(self, name: str):
        self.name = name
        self.path = _logs_dir() / "locks" / f"{name}.lock"
        self._mine = False

    def _read(self) -> Optional[dict]:
        if not self.path.exists():
            return None
        try:
            import json
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return None
            return data
        except Exception:
            return None

    def _write_atomic(self, payload: dict) -> None:
        import json
        tmp = Path(str(self.path) + ".tmp")
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(payload, ensure_ascii=False))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

    def _pid_alive(self, pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            # Windowsでも擬似的に: 存在チェックだけ
            os.kill(pid, 0)
        except OSError as e:
            # ESRCH: no such process
            if getattr(e, "errno", None) in (errno.ESRCH,):
                return False
            # EPERM: 権限なし → 存在はしている
            if getattr(e, "errno", None) in (errno.EPERM,):
                return True
            return False
        else:
            return True

    def acquire(self, *, stale_sec: int = 3600, force: bool = False) -> None:
        """
        ロック取得:
          - force=True: 既存を即奪取
          - 既存が生存中: 例外
          - 既存が死亡 or stale: 奪取
        """
        me = os.getpid()
        now = time.time()

        if self.path.exists():
            info = self._read() or {}
            pid = int(info.get("pid", 0))
            ts = float(info.get("ts", 0.0))

            if force:
                # 強制奪取
                self._write_atomic({"pid": me, "ts": now})
                self._mine = True
                return

            if pid and self._pid_alive(pid):
                # 生きている & ステール猶予内 → 取得失敗
                if stale_sec > 0 and (now - ts) <= stale_sec:
                    raise RuntimeError(f"collector already running (pid={pid}, lock={self.path})")
                # stale 扱い（時刻が大きく超過） → 奪取
                # 明示的に stale でも奪取する（安全側：実体が死んでいると判断）
            # ここに来たら「死んでいる or 情報不明 or stale」→ 奪取続行

        # 新規作成 / 奪取
        self._write_atomic({"pid": me, "ts": now})
        self._mine = True

    def release(self) -> None:
        if self._mine and self.path.exists():
            try:
                self.path.unlink()
            except Exception:
                # ログファイル系の競合は致命ではない
                pass
        self._mine = False

