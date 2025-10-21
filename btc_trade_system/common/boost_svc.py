# path: btc_trade_system/common/boost_svc.py
# desc: BOOSTモード用スナップショット（構造/環境/直近監査）を logs/boost_snapshot.json に上書き出力（10秒レート制御）

from __future__ import annotations
import os
import json
import importlib
import pkgutil
import time
import datetime as dt
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Literal

from btc_trade_system.common import paths, io_safe
from btc_trade_system.features.audit_dev import writer  # 現在の実効モード取得に使用

# --- レート制御（プロセス内） ---
_LAST_WRITE_MS: float | None = None
_RATE_MS = 10_000  # 10 秒


def _utc_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _list_modules(root_pkg: str) -> List[str]:
    """主要層までのモジュール名だけ列挙して重さを避ける"""
    mods: List[str] = []
    try:
        pkg = importlib.import_module(root_pkg)
        for m in pkgutil.walk_packages(pkg.__path__, prefix=root_pkg + "."):
            if m.name.count(".") <= 4:
                mods.append(m.name)
    except Exception:
        pass
    return mods

def _tail_levels_jsonl(path: Path, levels: Tuple[str, ...], n: int) -> List[Dict[str, Any]]:
    """
    末尾側からレベルで絞った行だけを取り出す（ERROR/CRIT 等）。
    取りこぼしを避けるため、まず多めに末尾を読み込み（既定500行）→ フィルタ → 末尾n件。
    """
    # 多めに読んでからレベルで抽出
    rows = _tail_jsonl(path, 500 if n < 500 else n)
    lvset = {lv.upper() for lv in levels}
    picked = [r for r in rows if str(r.get("level", "")).upper() in lvset]
    return picked[-n:]

def _tail_jsonl(path: Path, n: int) -> List[Dict[str, Any]]:
    """
    大容量 JSONL を想定し、末尾からチャンク逆読みで n 行だけ取り出す。
    エンコーディングは UTF-8 前提（不正バイトは ignore）。
    ・ファイル末尾に改行が無いケースも取りこぼさないよう buf も最終的に取り込む
    ・停止条件を < n にして余分なチャンク読みを避ける
    """
    if not path.exists() or n <= 0:
        return []
    try:
        chunk_size = 64 * 1024
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            buf = b""
            lines: List[str] = []
            pos = file_size
            while pos > 0 and len(lines) < n:
                read_len = chunk_size if pos >= chunk_size else pos
                pos -= read_len
                f.seek(pos, os.SEEK_SET)
                buf = f.read(read_len) + buf  # 先頭側に連結（逆読み）
                parts = buf.split(b"\n")
                # parts[0] は次ループの先頭と連結するので保持
                buf = parts[0]
                for p in parts[1:]:
                    lines.append(p.decode("utf-8", errors="ignore"))
                    if len(lines) >= n:
                        break
            # 先頭断片（ファイル先頭〜最初の改行前）が残っていれば行として加える
            if buf and len(lines) < n:
                lines.append(buf.decode("utf-8", errors="ignore"))
            # 末尾 n 行を正順で返す
            take = lines[-n:]
            out: List[Dict[str, Any]] = []
            for ln in take:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    # 途中破損行はスキップ
                    pass
            return out
    except Exception:
        return []

def _list_tree(base: Path, *, max_depth: int = 2, max_entries: int = 200) -> Dict[str, Any]:
    """
    data/ と logs/ の“薄い”ツリー。深さ/件数を厳しめに打ち切る。
    返り値は {root: str, entries: [(relpath, 'd'|'f', size_or_0)]}
    """
    entries: List[Tuple[str, str, int]] = []
    base = Path(base)
    try:
        for root, dirs, files in os.walk(base):
            rel_root = str(Path(root).relative_to(base))
            depth = 0 if rel_root == "." else rel_root.count(os.sep) + 1
            if depth > max_depth:
                # 深すぎる階層は切る
                dirs[:] = []
                continue
            # ディレクトリ
            for d in list(dirs):
                rel = str(Path(rel_root) / d) if rel_root != "." else d
                entries.append((rel.replace("\\", "/"), "d", 0))
                if len(entries) >= max_entries:
                    raise StopIteration
            # ファイル（サイズは最小限）
            for f in files:
                rel = str(Path(rel_root) / f) if rel_root != "." else f
                try:
                    sz = (Path(root) / f).stat().st_size
                except Exception:
                    sz = 0
                entries.append((rel.replace("\\", "/"), "f", int(sz)))
                if len(entries) >= max_entries:
                    raise StopIteration
    except StopIteration:
        pass
    except Exception:
        pass
    return {"root": str(base), "entries": entries}

def _try_repo_root() -> Path:
    """
    このファイルから辿って、repo ルート（btc_trade_system の親）を推定。
    失敗時はカレントを返す。
    """
    here = Path(__file__).resolve()
    for p in here.parents:
        if p.name == "btc_trade_system":
            return p.parent
    return Path.cwd()

def _file_info(p: Path) -> Dict[str, Any]:
    try:
        st = p.stat()
        return {
            "path": str(p),
            "size": int(st.st_size),
            "mtime": dt.datetime.utcfromtimestamp(st.st_mtime).replace(microsecond=0).isoformat() + "Z",
        }
    except Exception:
        return {"path": str(p), "size": 0, "mtime": None}

def _safe_sha1(p: Path, limit_bytes: int = 128 * 1024) -> Optional[str]:
    """
    大きすぎるファイルは先頭 limit_bytes のみハッシュして 'partial:' を付ける。
    """
    try:
        import hashlib
        with p.open("rb") as f:
            data = f.read(limit_bytes)
        h = hashlib.sha1(data).hexdigest()
        if p.stat().st_size > limit_bytes:
            return f"partial:{h}"
        return h
    except Exception:
        return None

def _settings_digest(repo_root: Path) -> Dict[str, Any]:
    """
    config/settings.yaml を探し、存在すればサイズ/mtime/sha1(部分)を返す。
    無ければ not_found。
    """
    cand = repo_root / "config" / "settings.yaml"
    if not cand.exists():
        return {"path": str(cand), "found": False}
    return {
        "path": str(cand),
        "found": True,
        "info": _file_info(cand),
        "sha1": _safe_sha1(cand) or None,
    }

# --- REPO_MAP: 先頭ヘッダの # path / # desc を収集 ----------------------------
def _parse_head_tags(p: Path, max_head_lines: int = 8) -> tuple[str | None, str | None]:
    """
    ファイル先頭から最大 max_head_lines を読み、 '# path:' / '# desc:' を抽出（ゆるめ一致）。
    - 例: '# path: ./tools/make_repo_map_extract.py'
          '# desc: リポジトリを走査し...'
    - コロンあり/なしや全角スペースにも寛容にする
    """
    try:
        head = p.read_text(encoding="utf-8", errors="ignore").splitlines()[:max_head_lines]
    except Exception:
        return None, None

    path_val: str | None = None
    desc_val: str | None = None
    for ln in head:
        s = ln.strip().lstrip("#").strip()
        low = s.lower()
        if low.startswith("path") or low.startswith("パス"):
            # 'path: xxx' 形式を想定（: が無くても後半を拾う）
            v = s.split(":", 1)
            path_val = v[1].strip() if len(v) > 1 else s[4:].strip()
        elif low.startswith("desc") or low.startswith("説明") or low.startswith("desc:"):
            v = s.split(":", 1)
            desc_val = v[1].strip() if len(v) > 1 else s[4:].strip()
    return path_val or None, desc_val or None


def _build_repo_map(repo_root: Path, *, max_files: int = 1000) -> list[dict[str, str]]:
    """
    リポジトリ配下を走査し、先頭タグ '# path' / '# desc' を持つファイルの一覧を返す。
    返り値: [{'path': '...', 'desc': '...'}, ...] を path 昇順で。
    """
    repo_root = Path(repo_root)
    items: list[dict[str, str]] = []
    try:
        cnt = 0
        for root, _, files in os.walk(repo_root):
            for fn in files:
                # 対象拡張子は .py を中心に、.ps1/.sh/.md も許容
                if not any(fn.endswith(ext) for ext in (".py", ".ps1", ".sh", ".md")):
                    continue
                p = Path(root) / fn
                # .venv や __pycache__、.git はスキップ
                if any(skip in p.parts for skip in (".venv", "__pycache__", ".git")):
                    continue
                rel = str(p.relative_to(repo_root)).replace("\\", "/")
                head_path, head_desc = _parse_head_tags(p)
                if head_path or head_desc:
                    items.append({"path": head_path or rel, "desc": head_desc or ""})
                    cnt += 1
                    if cnt >= max_files:
                        raise StopIteration
    except StopIteration:
        pass
    except Exception:
        pass
    # path で安定ソート
    items.sort(key=lambda x: x["path"])
    return items

def _versions_info() -> Dict[str, Any]:
    import platform
    try:
        import importlib.metadata as md  # py3.8+
    except Exception:
        md = None
    pkgs = {}
    for name in ("streamlit", "pandas", "numpy", "requests"):
        ver = None
        if md:
            try:
                ver = md.version(name)
            except Exception:
                pass
        pkgs[name] = ver
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "os": f"{platform.system()} {platform.release()}",
        "packages": pkgs,
    }

def _process_top(limit: int = 20) -> List[Dict[str, Any]]:
    """
    psutil があれば上位プロセス（CPU/WS）を返す。無ければ空。
    ・cpu_percent は2回呼びで差分を取らないと 0% が並ぶので、短いプライミングを入れる
    """
    try:
        import psutil  # type: ignore
    except Exception:
        return []
    # 1st sweep: プライミング（差分基準を作る）
    plist = []
    try:
        for p in psutil.process_iter(attrs=["pid", "name"]):
            try:
                p.cpu_percent(None)  # 基準化
                mem = p.memory_info().rss
                plist.append((p, p.info.get("name"), p.info.get("pid"), int(mem)))
            except Exception:
                pass
        # ごく短いスリープで差分期間を確保
        time.sleep(0.05)
    except Exception:
        return []
    # 2nd sweep: 実測
    procs: List[Dict[str, Any]] = []
    for p, name, pid, mem in plist:
        try:
            cpu = p.cpu_percent(None)
            procs.append({"name": name, "pid": pid, "cpu": cpu, "ws": mem})
        except Exception:
            pass
    procs.sort(key=lambda x: (x["cpu"], x["ws"]), reverse=True)
    return procs[:limit]

def make_snapshot(mode: Literal["DEBUG", "BOOST"]) -> Dict[str, Any]:
    """
    mode=DEBUG: LITE（軽量） / mode=BOOST: FULL（詳細）
    """
    data_root = paths.data_dir()
    logs_root = paths.logs_dir()
    repo_root = _try_repo_root()

    # 共通ヘッダ（軽量）
    snapshot: Dict[str, Any] = {
        "ts": _utc_iso(),
        "mode": mode,
        "roots": {"data_root": str(data_root), "logs_root": str(logs_root), "repo_root": str(repo_root)},
        "env": {
            "BTC_TS_MODE": os.getenv("BTC_TS_MODE"),
            "PYTHONPATH_contains_repo": any(
                str(p).endswith("BtcTradeSystemV1")
                for p in filter(None, os.getenv("PYTHONPATH", "").split(os.pathsep))
            ),
        },  # ← ここで env を閉じる（, も忘れずに）

        "recent": {
            # 通常の tail
            "audit_tail": _tail_jsonl(Path(logs_root) / "audit.jsonl", 20 if mode == "DEBUG" else 50),
            "dev_audit_tail": _tail_jsonl(Path(logs_root) / "dev_audit.jsonl", 20 if mode == "DEBUG" else 100),
            # 追加: エラー/クリティカルのみ抽出 tail（深堀り用）
            "audit_err_tail": _tail_levels_jsonl(
                Path(logs_root) / "audit.jsonl",
                ("ERROR", "CRIT"),
                20 if mode == "DEBUG" else 50,
            ),
            "dev_audit_err_tail": _tail_levels_jsonl(
                Path(logs_root) / "dev_audit.jsonl",
                ("ERROR", "CRIT"),
                20 if mode == "DEBUG" else 100,
            ),
        },

        "versions": _versions_info(),

        "files": {
            "logs": [
                _file_info(Path(logs_root) / "boost_snapshot.json"),
                _file_info(Path(logs_root) / "handover_gpt.txt"),
                _file_info(Path(logs_root) / "audit.jsonl"),
                _file_info(Path(logs_root) / "dev_audit.jsonl"),
            ],
        },
        "settings_digest": _settings_digest(repo_root),
    }

    if mode == "BOOST":
        # FULL: 重めの情報も同梱
        snapshot["tree"] = {
            "data": _list_tree(Path(data_root)),
            "logs": _list_tree(Path(logs_root)),
        }
        snapshot["modules"] = _list_modules("btc_trade_system")

        # REPO_MAP（BOOSTのみ・上限300件まで出力、総数は total に入れる）
        try:
            _all = _build_repo_map(repo_root, max_files=1000)
            snapshot["repo_map"] = {
                "total": len(_all),
                "items": _all[:300],  # handover/boost_snapshot の肥大化を防ぐ
            }
        except Exception:
            snapshot["repo_map"] = {"total": 0, "items": []}

        # プロセストップ（psutil がある場合のみ）
        procs = _process_top()
        if procs:
            snapshot["processes_top"] = procs
    return snapshot

def export_snapshot(
    out_path: Path | None = None,
    *,
    mode: Optional[Literal["DEBUG", "BOOST"]] = None,
    force: bool = False,
) -> str:
    """
    logs/boost_snapshot.json を生成（原子的上書き）。
    mode 未指定なら writer.get_mode() → OFF の場合は DEBUG とみなす。
    - BOOST切替直後は force=True で即出力
    - 以降は 10 秒以内の連続生成をスキップ
    """
    global _LAST_WRITE_MS
    now_ms = time.time() * 1000
    out = out_path or (Path(paths.logs_dir()) / "boost_snapshot.json")

    # レート制御
    if not force and _LAST_WRITE_MS is not None and (now_ms - _LAST_WRITE_MS) < _RATE_MS:
        return str(out)

    # 実効モードを決定
    eff = (mode or (writer.get_mode() or "DEBUG")).upper()
    if eff not in ("DEBUG", "BOOST"):
        eff = "DEBUG"

    snap = make_snapshot(eff)
    data = json.dumps(snap, ensure_ascii=False).encode("utf-8")

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        io_safe.write_atomic(out, data)
        _LAST_WRITE_MS = now_ms
    except Exception:
        try:
            tmp = out.with_suffix(out.suffix + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(out)
            _LAST_WRITE_MS = now_ms
        except Exception as e2:
            raise OSError(f"export_snapshot failed: {out}") from e2

    return str(out)

# desc: スナップショットJSONから、GPT引き継ぎ向けのテキストを生成する（DEBUG=LITE / BOOST=FULL）
def build_handover_text(snapshot: dict | None = None) -> str:
    snap = snapshot or {}
    mode = (snap.get("mode") or "DEBUG").upper()
    if mode not in ("DEBUG", "BOOST"):
        mode = "DEBUG"

    roots = snap.get("roots", {})
    recent = snap.get("recent", {})
    modules = snap.get("modules", [])
    env = snap.get("env", {})
    vers = snap.get("versions", {})
    files = snap.get("files", {})
    proc = snap.get("processes_top", [])
    settings = snap.get("settings_digest", {})

    lines: List[str] = []
    p = lines.append
    p(f"# BtcTradeSystemV1 Handover ({mode})")
    p(f"- ts: {snap.get('ts','')}")
    p("## Roots")
    p(f"- data_root: {roots.get('data_root','')}")
    p(f"- logs_root: {roots.get('logs_root','')}")
    if roots.get("repo_root"):
        p(f"- repo_root: {roots.get('repo_root','')}")
    p("## Env")
    p(f"- BTC_TS_MODE: {env.get('BTC_TS_MODE')}")
    p(f"- PYTHONPATH_contains_repo: {env.get('PYTHONPATH_contains_repo')}")

    # Versions
    if vers:
        p("### Versions")
        if vers.get("python"):
            p(f"- python: {vers.get('python')}")
        if vers.get("packages"):
            pk = vers["packages"]
            for k in ("streamlit", "pandas", "numpy", "requests"):
                if k in pk and pk[k] is not None:
                    p(f"- {k}: {pk[k]}")
        if vers.get("platform"):
            p(f"- platform: {vers.get('platform')}")
        if vers.get("os"):
            p(f"- os: {vers.get('os')}")

    # Logs files digest
    if files.get("logs"):
        p("### Files (logs)")
        for fi in files["logs"]:
            p(f"- {Path(fi['path']).name} ({fi.get('size',0)}B, mtime={fi.get('mtime')})")

    # Settings digest
    p("### config/settings.yaml (digest)")
    if settings.get("found"):
        info = settings.get("info", {})
        p(f"- size={info.get('size',0)}B, mtime={info.get('mtime')}, sha1={settings.get('sha1')}")
    else:
        p("- (not found)")

    # BOOST では読み込みモジュールと dev_audit の要約を厚めに出す
    if mode == "BOOST" and modules:
        p("## Loaded modules (top 50)")
        for m in modules[:50]:
            p(f"- {m}")

    # REPO_MAP（どのファイルが何をするかの要約）
    repo_map = snap.get("repo_map", {})
    if repo_map:
        total = repo_map.get("total", 0)
        items = repo_map.get("items") or []
        p(f"## REPO_MAP (showing {len(items)}/{total})")
        for it in items[:50 if mode == "DEBUG" else 200]:
            p(f"- {it.get('path','')} — {it.get('desc','')}")

    # Errors & Critical（直近）
    err_dev = recent.get("dev_audit_err_tail") or []
    err_aud = recent.get("audit_err_tail") or []
    if err_dev or err_aud:
        p("## Errors & Critical (recent)")
        if err_dev:
            p(f"### dev_audit (last {len(err_dev)})")
            if mode == "BOOST":
                for r in err_dev:
                    try:
                        p("- " + json.dumps(r, ensure_ascii=False))
                    except Exception:
                        p(f"- {r}")
            else:
                for r in err_dev:
                    ev = r.get("event","")
                    ts = r.get("ts","")
                    feat = r.get("feature","")
                    p(f"- [{ts}] {ev} ({feat})")
        if err_aud:
            p(f"### audit (last {len(err_aud)})")
            if mode == "BOOST":
                for r in err_aud:
                    try:
                        p("- " + json.dumps(r, ensure_ascii=False))
                    except Exception:
                        p(f"- {r}")
            else:
                for r in err_aud:
                    ev = r.get("event","")
                    ts = r.get("ts","")
                    feat = r.get("feature","")
                    p(f"- [{ts}] {ev} ({feat})")

    # Recent dev_audit tail
    p("## Recent dev_audit tail (last 20)")
    tail = (recent.get("dev_audit_tail") or [])[-20:]
    if mode == "BOOST":
        # 解決の役に立つように JSON 行をそのまま貼る
        for r in tail:
            try:
                p("- " + json.dumps(r, ensure_ascii=False))
            except Exception:
                p(f"- {r}")
    else:
        # LITE は圧縮表示
        for r in tail:
            ev = r.get("event","")
            lvl = r.get("level","")
            ts  = r.get("ts","")
            feat= r.get("feature","")
            p(f"- [{ts}] {lvl} {ev} ({feat})")

    # プロセス Top（BOOST のみ）
    if mode == "BOOST" and proc:
        p("### Processes (top)")
        for it in proc[:20]:
            p(f"- {it.get('name')} pid={it.get('pid')} cpu={it.get('cpu')} ws={it.get('ws')}")

    # Reproduce
    p("## How to reproduce (PowerShell)")
    p("```powershell")
    p("Set-Location $env:USERPROFILE\\BtcTradeSystemV1")
    p("$env:PYTHONPATH = (Get-Location).Path")
    p("if (-not $env:BTC_TS_LOGS_DIR) { $env:BTC_TS_LOGS_DIR = \"D:\\BtcTS_V1\\logs\" }")
    p("python -m streamlit run .\\btc_trade_system\\features\\dash\\dashboard.py --server.port 8501")
    p("```")
    return "\n".join(lines) + "\n"

# desc: BOOST時に handover テキストも同時出力（logs/handover_gpt.txt）
def export_handover_text(*, mode: Optional[Literal["DEBUG","BOOST"]] = None, force: bool = False) -> str:
    """
    handover_gpt.txt を logs に出力してフルパス（str）を返す。
    mode 未指定なら writer.get_mode() → OFF は DEBUG とみなす。
    """
    out = Path(paths.logs_dir()) / "handover_gpt.txt"

    eff = (mode or (writer.get_mode() or "DEBUG")).upper()
    if eff not in ("DEBUG", "BOOST"):
        eff = "DEBUG"

    snap = make_snapshot(eff)
    text = build_handover_text(snap)

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        io_safe.write_atomic(out, text.encode("utf-8"))
    except Exception:
        try:
            tmp = out.with_suffix(out.suffix + ".tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(out)
        except Exception as e2:
            raise OSError(f"export_handover_text failed: {out}") from e2

    return str(out)
