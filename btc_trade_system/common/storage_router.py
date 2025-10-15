# path: ./btc_trade_system/common/storage_router.py
# desc: ストレージの書き込み先を primary(ENV)→secondary(ローカル) に自動切替する最小ルータ。JSONL追記とCSV原子的置換を提供。

from __future__ import annotations
import csv, json, os, tempfile, time
from pathlib import Path
from typing import Literal, Optional
from btc_trade_system.common import paths

Domain = Literal["logs", "data"]


class StorageRouter:
    """
    - primary: ENV 優先（BTC_TS_LOGS_DIR / BTC_TS_DATA_DIR）
    - secondary: リポ直下の ./local/{logs|data}
    - is_primary_available() は tmp 書込で軽診断し、状態変化時に監査を切る
    - 提供 I/F:
        append_jsonl(domain, relpath, obj)
        write_atomic_csv(domain, relpath, rows)
    """

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self._secondary_root = self.base_dir / "local"
        (self._secondary_root / "logs").mkdir(parents=True, exist_ok=True)
        (self._secondary_root / "data").mkdir(parents=True, exist_ok=True)

        self._last_primary_ok: Optional[bool] = None  # 直前の可用性（監査用）

    # ---- primary/secondary の解決 --------------------------------------------
    def _primary_root(self, domain: Domain) -> Path:
        return paths.logs_dir() if domain == "logs" else paths.data_dir()

    def _secondary_root_for(self, domain: Domain) -> Path:
        return (self._secondary_root / domain)

    def is_primary_available(self, domain: Domain = "logs") -> bool:
        """tmp 書込で軽診断。不可なら False。"""
        root = self._primary_root(domain)
        try:
            root.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(prefix="probe_", suffix=".tmp", dir=str(root))
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(str(time.time()))
                    f.flush()
                    os.fsync(f.fileno())
                os.remove(tmp)
            except Exception:
                try:
                    os.remove(tmp)
                except Exception:
                    pass
                raise
            ok = True
        except Exception:
            ok = False

        # 状態変化の記録は上位（呼び出し側）で実施して循環importを回避
        if self._last_primary_ok is None:
            self._last_primary_ok = ok
        elif self._last_primary_ok != ok:
            # ここではフラグだけ更新
            self._last_primary_ok = ok
            
        return ok

    def _resolve_base(self, domain: Domain) -> Path:
        return self._primary_root(domain) if self.is_primary_available(domain) \
               else self._secondary_root_for(domain)

    def _safe_join(self, base: Path, relpath: str) -> Path:
        """
        base 配下への相対パスのみ許容。絶対/脱出を検知して拒否。
        """
        base_res = base.resolve()
        target = (base / relpath).resolve()
        # Windows/UNIX 両対応のため commonpath で配下判定
        import os as _os
        if _os.path.commonpath([str(target), str(base_res)]) != str(base_res):
            raise ValueError(f"relpath escapes base: {relpath!r}")
        return target

    # ---- JSONL append（冪等1行追記） ----------------------------------------
    def append_jsonl(self, domain: Domain, relpath: str, obj: dict) -> Path:
        base = self._resolve_base(domain)
        path = self._safe_join(base, relpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(obj, ensure_ascii=False)
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        return path

    # ---- CSV atomic write（置換型） ------------------------------------------
    def write_atomic_csv(self, domain: Domain, relpath: str, rows: list[list[str]]) -> Path:
        base = self._resolve_base(domain)
        path = self._safe_join(base, relpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(prefix="csv_", suffix=".tmp", dir=str(path.parent))
        try:
            # newline=\"\\n\" + lineterminator='\\n' で OS に依存しないLF固定（diffが安定）
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                writer = csv.writer(f, lineterminator="\n")
                for r in rows:
                    writer.writerow(r)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, path)
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
        return path

    # --- introspection ---------------------------------------------------------
    def current_root(self, domain: Domain) -> Path:
        """現在の書き込み先ベース（probe結果）を返す。"""
        return self._resolve_base(domain)
