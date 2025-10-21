# path: ./btc_trade_system/features/dash/audit_ui.py
# desc: AuditタブのUI（開発監査表示専用）。BOOST切替時スナップショット生成対応・lint誤検出回避。ボタン色: OFF=白, DEBUG=黄, BOOST=赤。

from __future__ import annotations

import streamlit as st
import json, time
from pathlib import Path
import os, sys, datetime as _dt
import platform, hashlib, subprocess
import shutil

from ...common import paths
from btc_trade_system.features.dash.audit_svc import get_audit_rows as svc_get_audit_rows
from btc_trade_system.features.audit_dev.writer import get_mode as _dev_get_mode, set_mode as _dev_set_mode

from btc_trade_system.common.boost_svc import (
    export_snapshot as boost_export_snapshot,
    build_handover_text as boost_build_handover_text,
)

from btc_trade_system.features.audit_dev.snapshot_ui import (
    render_snapshot_code,   # CSS 注入は内部で一度だけ行う
    repo_map_excerpt,
)

def _log_file() -> Path:
    return paths.logs_dir() / "dev_audit.jsonl"

def _mode_next(m: str) -> str:
    chain = ["OFF", "DEBUG", "BOOST"]
    m = (m or "OFF").upper()
    return chain[(chain.index(m) + 1) % len(chain)] if m in chain else "OFF"

def _mask_env_items(env: dict) -> list[tuple[str, str]]:
    """環境変数をキー名でマスク。KEY/SECRET/TOKEN/PASS/PWD を含むものは伏字。"""
    def _mask(k: str, v: str) -> str:
        key = k.upper()
        if any(p in key for p in ("KEY", "SECRET", "TOKEN", "PASS", "PWD")):
            return "***"
        return v
    items = [(k, _mask(k, v)) for k, v in env.items()]
    return sorted(items, key=lambda kv: kv[0])

def _collect_versions() -> list[str]:
    """Python / Streamlit / 主要ライブラリ / OS の簡易バージョン列挙。"""
    out: list[str] = []
    out.append(f"- python: {sys.version.split()[0]}")
    try:
        import streamlit as _st
        out.append(f"- streamlit: {getattr(_st, '__version__', 'unknown')}")
    except Exception:
        out.append("- streamlit: unknown")
    for lib in ("pandas", "numpy", "requests"):
        try:
            mod = __import__(lib)
            ver = getattr(mod, "__version__", "unknown")
            out.append(f"- {lib}: {ver}")
        except Exception:
            pass
    out.append(f"- platform: {platform.platform()}")
    out.append(f"- os: {platform.system()} {platform.release()} ({platform.version()})")
    return out

def _fmt_bytes(n: int) -> str:
    """人間可読のサイズ表記。"""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n //= 1024
    return f"{n:.0f}PB"

def _fmt_iso(ts: float) -> str:
    """UNIX秒をUTC ISO8601 Z に整形。"""
    try:
        return _dt.datetime.utcfromtimestamp(ts).isoformat(timespec="seconds") + "Z"
    except Exception:
        return str(ts)

def _list_files_brief(root: Path, limit: int = 100) -> list[str]:
    """直下ファイルのサイズ・mtime を列挙（最大 limit 行）。"""
    rows: list[tuple[str, int, float]] = []
    try:
        for p in list(root.glob("*"))[:limit]:
            try:
                if p.is_file():
                    stt = p.stat()
                    rows.append((str(p), stt.st_size, stt.st_mtime))
            except Exception:
                continue
    except Exception:
        pass
    rows.sort(key=lambda t: t[2], reverse=True)
    return [f"- {Path(path).name} ({_fmt_bytes(sz)}, mtime={_fmt_iso(mt)})" for path, sz, mt in rows[:limit]]

def _sha256_file(p: Path) -> str | None:
    """ファイルのSHA256（失敗時 None）。"""
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def _get_process_list_windows(max_rows: int = 15) -> list[str]:
    """Windows用の簡易プロセス一覧（Name/Id/CPU/WS）。失敗時は空。"""
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            (
                "Get-Process | "
                f"Select-Object -First {max_rows} Name,Id,CPU,WS | "
                "ConvertTo-Csv -NoTypeInformation"
            ),
        ]
        csv = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, text=True, timeout=3
        )
        lines = [l for l in (csv or "").splitlines() if l.strip()]
        if not lines:
            return []
        out: list[str] = []
        # 先頭は CSV ヘッダ行のためスキップ
        for row in lines[1:]:
            parts = [x.strip().strip('"') for x in row.split(",")]
            if len(parts) >= 4:
                name, pid, cpu, ws = parts[:4]
                out.append(f"- {name} pid={pid} cpu={cpu or '0'} ws={ws}")
        return out
    except Exception:
        # PowerShell 不在やタイムアウト時などは空で返す
        return []
  
def _audit_tail_errors_only(src: Path, max_lines: int = 150) -> list[str]:
    """
    dev_audit.jsonl から ERROR/CRITICAL/例外行だけを最大 max_lines 抽出。
    JSON/非JSON どちらでも、キーワードでざっくり拾う安全側実装。
    """
    if not src.exists():
        return ["- (dev_audit.jsonl not found)"]
    keys = ("ERROR", "CRITICAL", "TRACEBACK", '"LEVEL":"ERROR"', '"LEVEL": "ERROR"', '"LEVEL":"CRITICAL"', '"LEVEL": "CRITICAL"')
    out: list[str] = []
    try:
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            for ln in f.readlines()[-2000:]:  # 直近2000行だけ走査して軽量化
                s = ln.strip()
                if not s:
                    continue
                u = s.upper()
                if any(k in u for k in keys):
                    out.append(f"- {s}")
        if not out:
            return ["- (no ERROR/CRITICAL found in recent lines)"]
        return out[-max_lines:]
    except Exception as e:
        return [f"- (read error: {e!r})"]

def _git_status_brief(cwd: Path | None = None) -> list[str]:
    try:
        def _run(args):
            return subprocess.check_output(args, cwd=cwd, stderr=subprocess.DEVNULL, text=True, timeout=2).strip()
        root = _run(["git", "rev-parse", "--show-toplevel"])
        branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        commit = _run(["git", "rev-parse", "--short", "HEAD"])
        dirty = "1" if _run(["git", "status", "--porcelain"]) else "0"
        return [
            f"- root: {root}",
            f"- branch: {branch}",
            f"- commit: {commit}",
            f"- dirty: {dirty}",
        ]
    except Exception:
        return ["- (git N/A)"]

    except Exception:
        return []

def _path_probe(p: Path) -> list[str]:
    try:
        stt = p.stat()
        return [
            f"- path: {p}",
            f"- exists: True",
            f"- is_dir: {p.is_dir()}",
            f"- is_file: {p.is_file()}",
            f"- mtime: {_fmt_iso(stt.st_mtime)}",
        ]
    except Exception:
        return [f"- path: {p}", "- exists: False"]

def _disk_free_of(p: Path) -> list[str]:
    try:
        usage = shutil.disk_usage(str(p.resolve()))
        return [
            f"- total: {_fmt_bytes(usage.total)}",
            f"- used:  {_fmt_bytes(usage.used)}",
            f"- free:  {_fmt_bytes(usage.free)}",
        ]
    except Exception as e:
        return [f"- (disk_usage error: {e!r})"]

def _make_snapshot(mode: str) -> str:
    """開発監査向けの軽量スナップショットをその場で生成（ファイル出力なし）。"""
    ts = _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"

    # Roots
    try:
        data_root = str(paths.data_dir())
    except Exception:
        data_root = "(resolve failed)"
    try:
        logs_root = str(paths.logs_dir())
    except Exception:
        logs_root = "(resolve failed)"

    # Env
    btc_mode = os.environ.get("BTC_TS_MODE")
    py_contains = "btc_trade_system" in sys.modules or any("BtcTradeSystemV1" in p for p in sys.path)

    # Loaded modules（btc_trade_system* のみ・最大50）
    mods = [name for name in sorted(sys.modules.keys()) if name.startswith("btc_trade_system")]
    mods = mods[:50]

    # dev_audit tail
    log_path = _log_file()
    tail_lines: list[str] = []
    try:
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                buf = f.readlines()[-20:]
            for ln in buf:
                s = ln.strip()
                if s:
                    tail_lines.append(f"- {s}")
        else:
            tail_lines.append("- (dev_audit.jsonl not found)")
    except Exception as e:
        tail_lines.append(f"- (read error: {e!r})")

    # How to reproduce（固定手順・ENV に追従）
    howto = r"""```powershell
Set-Location $env:USERPROFILE\BtcTradeSystemV1
$env:PYTHONPATH = (Get-Location).Path
if (-not $env:BTC_TS_LOGS_DIR) { $env:BTC_TS_LOGS_DIR = "%s" }
python -m streamlit run .\btc_trade_system\features\dash\dashboard.py --server.port 8501
```""" % (logs_root if logs_root != "(resolve failed)" else "D:\\BtcTS_V1\\logs")

    # 組み立て（Markdown）
    parts = []
    parts.append(f"# BtcTradeSystemV1 Handover ({(mode or 'OFF').upper()})")
    parts.append(f"- ts: {ts}")
    parts.append("## Roots")
    parts.append(f"- data_root: {data_root}")
    parts.append(f"- logs_root: {logs_root}")
    parts.append("## Env")
    parts.append(f"- BTC_TS_MODE: {btc_mode}")
    parts.append(f"- PYTHONPATH_contains_repo: {py_contains}")
    parts.append("## Loaded modules (top 50)")
    for m in mods:
        parts.append(f"- {m}")
    parts.append("## Recent dev_audit tail (last 20)")
    parts.extend(tail_lines)
    parts.append("## How to reproduce (PowerShell)")
    parts.append(howto)

    # === 3.3 Full Snapshot (BOOST only) ===
    if (mode or "OFF").upper() == "BOOST":
        parts.append("## Full Snapshot")

        # 環境変数（マスク済み）
        parts.append("### Env (sanitized)")
        for k, v in _mask_env_items(os.environ):
            parts.append(f"- {k}={v}")

        # バージョン情報
        parts.append("### Versions")
        parts.extend(_collect_versions())

        # ファイル一覧（logs / data）
        parts.append("### Files (logs)")
        try:
            parts.extend(_list_files_brief(paths.logs_dir()))
        except Exception:
            parts.append("- (logs_dir list failed)")

        parts.append("### Files (data)")
        try:
            parts.extend(_list_files_brief(paths.data_dir()))
        except Exception:
            parts.append("- (data_dir list failed)")

        # audit_tail: 末尾200行
        parts.append("### audit_tail (last 200)")
        try:
            if log_path.exists():
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    tail200 = f.readlines()[-150:]
                for ln in tail200:
                    s = ln.rstrip("\n")
                    if s:
                        parts.append(f"- {s}")
            else:
                parts.append("- (dev_audit.jsonl not found)")
        except Exception as e:
            parts.append(f"- (read error: {e!r})")

        # 設定ファイルのダイジェスト
        parts.append("### config/settings.yaml (digest)")
        cand = [
            Path.cwd() / "config" / "settings.yaml",
            Path.cwd() / "config" / "settings.yml",
        ]
        hit = next((p for p in cand if p.exists()), None)
        if hit:
            digest = _sha256_file(hit)
            parts.append(f"- path: {hit}")
            parts.append(f"- sha256: {digest or '(error)'}")
            try:
                stt = hit.stat()
                parts.append(f"- size: {_fmt_bytes(stt.st_size)}")
                parts.append(f"- mtime: {_fmt_iso(stt.st_mtime)}")
            except Exception:
                pass
        else:
            parts.append("- (not found)")

        # プロセス一覧（Windows限定）
        parts.append("### Processes (top)")
        prows = _get_process_list_windows()
        parts.extend(prows if prows else ["- (unavailable)"])

        # DOM プローブ（UIが dom_probe を持つ場合のみ）
        parts.append("### DOM probe")
        try:
            dp = st.session_state.get("dom_probe")
            if dp:
                parts.append(f"- selector: {dp.get('selector')}")
                parts.append(f"- hits: {dp.get('hits')}")
                styles = dp.get("styles") or {}
                for k, v in styles.items():
                    parts.append(f"- style.{k}: {v}")
            else:
                parts.append("- (no data)")
        except Exception:
            parts.append("- (no data)")

    return "\n".join(parts)

# ▼ 追加: スナップショット表示用（コードウインドウ風/10行固定）
def _escape_html(s: str) -> str:
    try:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    except Exception:
        return s

def _render_snapshot_box(text: str) -> None:
    """GPTの[python]風ボックス。10行固定・横/縦スクロール・ラベル非コピー。"""
    # CSSは初回だけ注入（何度も描画してもDOMが太らないように）
    if not st.session_state.get("_snapbox_css_done"):
        st.markdown("""
        <style>
          .snapbox {
            position: relative;
            border: 1px solid rgba(140,140,140,.35);
            border-radius: 10px;
            background: #0d1117;
            color: #c9d1d9;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            line-height: 1.45;
            padding: 22px 14px 12px 14px;
            height: calc(1.45em * 10 + 24px); /* 10行固定 */
            overflow: auto;                  /* 横/縦スクロール */
            box-shadow: 0 1px 3px rgba(0,0,0,0.15);
            max-width: 100%;
          }
          @media (prefers-color-scheme: light) {
            .snapbox { background: #fafafa; color: #24292e; border-color: rgba(0,0,0,.15); }
          }
          .snapbox::before {
            content: "[snapshot]";
            position: absolute;
            top: 6px; left: 10px;
            color: #8b949e; font-size: 12px; letter-spacing: .2px;
            user-select: none; pointer-events: none;
          }
          .snapbox pre {
            margin: 0;
            white-space: pre;  /* 折り返さず横スクロール */
          }
        </style>
        """, unsafe_allow_html=True)
        st.session_state["_snapbox_css_done"] = True

    st.markdown(f'<div class="snapbox"><pre>{_escape_html(text or "")}</pre></div>', unsafe_allow_html=True)

def render():
    st.markdown("<div id='audit-area'>", unsafe_allow_html=True)

    # セッション最初の1回だけ、UI/Writer を OFF に強制同期する（リロード時は毎回OFFスタート）
    if "_init_off_done" not in st.session_state:
        try:
            _dev_set_mode("OFF")
        except Exception:
            pass
        st.session_state.dev_mode = "OFF"
        st.session_state["_init_off_done"] = True
        st.session_state["mode_changed_at_ms"] = int(time.time() * 1000)

    c0, c1 = st.columns([1.2, 6.8])

    with c0:
        cur = (st.session_state.get("dev_mode", "OFF") or "OFF").upper()
        next_mode = _mode_next(cur)

        # ボタンの表示は「現在モード」。クリックで next_mode に切替。
        label = cur
        if st.button(label, key="btn_mode_cycle", use_container_width=True, help=f"クリックで {next_mode} に切替"):
            try:
                _dev_set_mode(next_mode)
                st.session_state.dev_mode = next_mode
                st.session_state["mode_changed_at_ms"] = int(time.time() * 1000)

                # ▼ 追加：スナップショットのUI側キャッシュは毎回クリア
                st.session_state.snapshot_text = ""
                st.session_state.snapshot_meta = {"path": None, "size": 0, "mtime": 0.0}

                # ▼ 追加：BOOSTに入るタイミングで“公式”スナップショットを即時生成
                if (next_mode or "OFF").upper() == "BOOST":
                    try:
                        snap_path = Path(boost_export_snapshot(mode="BOOST", force=True))
                        # handover テキスト（公式ビルダー）を生成してテキスト窓に流し込む
                        try:
                            snap_json = json.loads(snap_path.read_text(encoding="utf-8", errors="ignore"))
                            txt = boost_build_handover_text(snap_json)
                            st.session_state.snapshot_text = txt
                            st.session_state.snapshot_meta = {
                                "path": str(snap_path),
                                "size": len(txt.encode("utf-8", errors="ignore")),
                                "mtime": time.time(),
                            }
                        except Exception:
                            pass
                    except Exception:
                        # 失敗時はUI内の簡易スナップショットでフォールバック
                        try:
                            st.session_state.snapshot_text = _make_snapshot(next_mode)
                            st.session_state.snapshot_meta = {"path": None, "size": len(st.session_state.snapshot_text.encode("utf-8")), "mtime": time.time()}
                        except Exception:
                            pass

                st.rerun()
            except Exception as e:
                st.warning(f"モード更新に失敗しました: {e!r}")

        ui_mode = (st.session_state.get("dev_mode", "OFF") or "OFF").upper()
        try:
            writer_mode = _dev_get_mode()
        except Exception:
            writer_mode = "UNKNOWN"
        ts_ms = st.session_state.get("mode_changed_at_ms")
        st.caption(
            f"現在モード: UI=`{ui_mode}` / writer=`{writer_mode}`"
            + (f"（changed_at={ts_ms}ms）" if ts_ms else "")
        )

    with c1:
        st.subheader("開発監査ログ（dev_audit.jsonl）")
        st.caption(r"Tail（PowerShell）: Get-Content D:\\BtcTS_V1\\logs\\dev_audit.jsonl -Tail 50 -Wait")

        # --- 追加: コピペ用テキスト窓 + スナップショット/コピー（OFFは無効） ---
        if "snapshot_text" not in st.session_state:
            st.session_state.snapshot_text = ""
        if "snapshot_meta" not in st.session_state:
            st.session_state.snapshot_meta = {"path": None, "size": 0, "mtime": 0.0}

        # UI モードと writer モードの両方を見て、実効モードを決める
        ui_mode = (st.session_state.get("dev_mode", "OFF") or "OFF").upper()
        try:
            writer_try = (_dev_get_mode() or "OFF").upper()
        except Exception:
            writer_try = "UNKNOWN"

        # 実効モード: writer が DEBUG/BOOST なら優先、そうでなければ UI モード
        eff_mode = writer_try if writer_try in ("DEBUG", "BOOST") else ui_mode

        # === 追加/変更 ===
        # OFF 判定とボタン活性は eff_mode を基準にする
        # （UIとwriterのズレがあっても「実際に動く/動かない」で判断され直感的）
        is_off = ((eff_mode or "OFF").upper() == "OFF")
        snapshot_disabled = is_off

        b1, b2, b3 = st.columns([1.6, 1.1, 3.3])

        with b1:
            regen = st.button("スナップショット", key="btn_snapshot_regen",
                            disabled=snapshot_disabled, use_container_width=True)

        # === 追加: 付加オプション（構成切替） ==========================
        st.session_state.setdefault("opt_repo_map", True)
        st.session_state.setdefault("opt_tail150", False)
        st.session_state.setdefault("opt_env_versions", False)

        with st.container():
            copt1, copt2, copt3 = st.columns([1.3, 1.3, 1.6])
            with copt1:
                st.checkbox("REPO_MAP 抜粋", key="opt_repo_map",
                            help="DEBUG/BOOST いずれでも末尾に REPO_MAP の抜粋を付けます。")
            with copt2:
                st.checkbox("audit_tail 150", key="opt_tail150",
                            help="dev_audit.jsonl の末尾150行を handover 末尾に付けます。（主に DEBUG 向け）")
            with copt3:
                st.checkbox("Env + Versions", key="opt_env_versions",
                            help="環境変数(マスク済)と主要バージョン表を付けます。BOOST では公式hander に概ね含まれます。")

        # 追加：エラー/クリティカル抽出 tail の付与
        st.session_state.setdefault("opt_err_tail", True)
        st.checkbox("Errors only tail", key="opt_err_tail",
                    help="dev_audit.jsonl から ERROR/CRITICAL/例外行だけを最大150行抽出して付与します。")

        # 1) 先に生成を反映
        if regen:
            try:
                snap_path = Path(boost_export_snapshot(mode=eff_mode, force=True))
                try:
                    snap_json = json.loads(snap_path.read_text(encoding="utf-8", errors="ignore"))
                    # 公式 handover を起点にする
                    snap_text = boost_build_handover_text(snap_json)

                    # 1) REPO_MAP 抜粋（任意）
                    if st.session_state.get("opt_repo_map", True):
                        try:
                            extra = repo_map_excerpt(snap_json, eff_mode)
                            if extra:
                                snap_text = f"{snap_text}\n{extra}"
                        except Exception:
                            pass

                    # 2) audit_tail 150（任意）
                    if st.session_state.get("opt_tail150", False):
                        try:
                            src = _log_file()
                            lines = []
                            if src.exists():
                                buf = src.read_text(encoding="utf-8", errors="ignore").splitlines()[-150:]
                                lines.append("")
                                lines.append("### audit_tail (last 150)")
                                lines.extend([f"- {ln}" for ln in buf if ln.strip()])
                            else:
                                lines.append("")
                                lines.append("### audit_tail (last 150)")
                                lines.append("- (dev_audit.jsonl not found)")
                            snap_text = f"{snap_text}\n" + "\n".join(lines)
                        except Exception:
                            pass
                    # 2b) Errors only tail（任意 / デフォルトON）
                    if st.session_state.get("opt_err_tail", True):
                        try:
                            src = _log_file()
                            lines = []
                            lines.append("")
                            lines.append("### audit_tail (errors/critical, up to 150)")
                            lines.extend(_audit_tail_errors_only(src, max_lines=150))
                            snap_text = f"{snap_text}\n" + "\n".join(lines)
                        except Exception:
                            pass

                    # 4) Git 状態（任意）
                    try:
                        lines = []
                        lines.append("")
                        lines.append("### Git (brief)")
                        lines.extend(_git_status_brief(Path.cwd()))
                        snap_text = f"{snap_text}\n" + "\n".join(lines)
                    except Exception:
                        pass

                    # 5) StorageRouter 実体（任意）
                    try:
                        lines = []
                        lines.append("")
                        lines.append("### StorageRouter (resolved)")
                        lines.append("#### logs_dir")
                        lines.extend(_path_probe(paths.logs_dir()))
                        lines.append("#### data_dir")
                        lines.extend(_path_probe(paths.data_dir()))
                        snap_text = f"{snap_text}\n" + "\n".join(lines)
                    except Exception:
                        pass

                    # 6) Disk free（任意）
                    try:
                        lines = []
                        lines.append("")
                        lines.append("### Disk free (by storage roots)")
                        lines.append("#### logs_dir drive")
                        lines.extend(_disk_free_of(paths.logs_dir()))
                        lines.append("#### data_dir drive")
                        lines.extend(_disk_free_of(paths.data_dir()))
                        snap_text = f"{snap_text}\n" + "\n".join(lines)
                    except Exception:
                        pass

                    # 3) Env + Versions（任意 / DEBUG で有用。BOOSTでは公式に概ね含有）
                    if st.session_state.get("opt_env_versions", False):
                        try:
                            lines = []
                            lines.append("")
                            lines.append("### Env (sanitized) — optional")
                            for k, v in _mask_env_items(os.environ):
                                lines.append(f"- {k}={v}")

                            lines.append("### Versions — optional")
                            lines.extend(_collect_versions())
                            snap_text = f"{snap_text}\n" + "\n".join(lines)
                        except Exception:
                            pass

                except Exception:
                    # 公式生成が失敗した場合は UI 内部の簡易スナップショットにフォールバック
                    base = _make_snapshot(eff_mode)
                    try:
                        # 可能なら REPO_MAP 抜粋を付ける（簡易スナップには repo_map が無い想定のためスキップ可）
                        extra = ""
                        if st.session_state.get("opt_repo_map", True):
                            # フォールバック経路では JSON が手元にないので付与はスキップ
                            extra = ""
                        snap_text = base + (("\n" + extra) if extra else "")
                    except Exception:
                        snap_text = base

                st.session_state.snapshot_text = snap_text
                st.session_state.snapshot_meta = {
                    "path": str(snap_path) if snap_path.exists() else None,
                    "size": len(snap_text.encode("utf-8", errors="ignore")),
                    "mtime": time.time(),
                }

                # ▼ 表示用の TextArea (key="snapshot_area") にも同期
                st.session_state["snapshot_area"] = snap_text

            except Exception:
                try:
                    snap_text = _make_snapshot(eff_mode)
                    st.session_state.snapshot_text = snap_text
                    st.session_state.snapshot_meta = {"path": None, "size": len(snap_text.encode("utf-8")), "mtime": time.time()}
                    st.session_state["snapshot_view"] = snap_text
                    # ▼ TextArea にも同期
                    st.session_state["snapshot_area"] = snap_text

                except Exception as e:
                    st.warning(f"スナップショット生成に失敗しました: {e!r}")

        # 2) 生成結果に基づいて鮮度/可否を再計算
        FRESH_SEC = 300
        _meta = st.session_state.snapshot_meta or {}
        fresh = False
        try:
            if _meta.get("mtime") is not None:
                fresh = (time.time() - float(_meta["mtime"])) <= FRESH_SEC
            elif _meta.get("path"):
                mtime = Path(_meta["path"]).stat().st_mtime
                fresh = (time.time() - float(mtime)) <= FRESH_SEC
        except Exception:
            fresh = False

        copy_disabled = is_off or (not st.session_state.snapshot_text) or (not fresh)

        # 3) ここで DBG を表示
        _dev_dbg = st.checkbox("dev/debug panel", value=False)
        if _dev_dbg:
            st.caption(
                f"[DBG] eff_mode={eff_mode} is_off={is_off} fresh={fresh} "
                f"snapshot_disabled={snapshot_disabled} copy_disabled={copy_disabled} "
                f"ui_mode={(st.session_state.get('dev_mode','OFF') or 'OFF').upper()} "
                f"writer_mode_try={eff_mode}"
            )

        # === スナップショット窓（code 版 / 10行固定 / 横縦スクロール / コピー可） ===
        snap_txt = st.session_state.get("snapshot_text") or ""
        if is_off:
            prefix = "監査停止中（OFF）"
            snap_txt = prefix + ("\n" + snap_txt if snap_txt else "")

        # ボックス内の先頭行に [[snapshot]] を含め、コピー対象にも含める
        display_txt = f"[[snapshot]]\n{snap_txt}" if snap_txt else "[[snapshot]]"

        # ※ CSS 注入は render_snapshot_code() 内で一度だけ行うので、これだけでOK
        render_snapshot_code(display_txt)
        _meta = st.session_state.get("snapshot_meta") or {}
        _path = _meta.get("path")
        _size = _meta.get("size")
        _mtime = _meta.get("mtime")
        _age_txt = "-"
        try:
            if _mtime:
                _age = max(0.0, time.time() - float(_mtime))
                _age_txt = f"{_age:.0f}s ago"
        except Exception:
            pass

        st.caption(
            f"snapshot: fresh={_age_txt}  "
            f"size={_size if _size is not None else '-'}B  "
            f"path={_path or '(memory only)'}"
        )

        # ダウンロード（常設）
        _txt = st.session_state.get("snapshot_text") or ""
        st.download_button(
            "Download handover_gpt.txt",
            data=_txt.encode("utf-8"),
            file_name="handover_gpt.txt",
            mime="text/plain",
            key="dl_handover_txt",
            use_container_width=False,
            disabled=not _txt,
        )

        # === Errors & Critical（recent） ===============================
        with st.expander("Errors & Critical（recent）", expanded=False):
            # ちょいフィルタ（キーワード）
            kw = st.text_input("キーワード", value="", placeholder='event=/feature=/payload など部分一致', key="err_kw")

            # 末尾から最大 200 行を読み込み → ERROR/CRITICAL を抽出
            src = _log_file()
            rows: list[str] = []
            try:
                if src.exists():
                    buf = src.read_text(encoding="utf-8", errors="ignore").splitlines()[-200:]
                    for ln in buf:
                        s = ln.strip()
                        if not s:
                            continue
                        # JSON 行なら level を厳密に、そうでなければ単純に文字含有で判定
                        hit = False
                        try:
                            obj = json.loads(s)
                            lvl = (obj.get("level") or "").upper()
                            if lvl in ("ERROR", "CRITICAL"):
                                hit = True
                                s = json.dumps(obj, ensure_ascii=False)
                        except Exception:
                            up = s.upper()
                            if (" ERROR " in up) or (" CRITICAL " in up):
                                hit = True
                        if not hit:
                            continue
                        if kw and (kw not in s):
                            continue
                        rows.append(s)
                else:
                    rows.append("(dev_audit.jsonl not found)")
            except Exception as e:
                rows.append(f"(read error: {e!r})")

            st.caption(f"hits: {len(rows)}  source: {str(src)} （末尾200→抽出, 上限50を表示）")
            if rows:
                st.code("\n".join(rows[-50:]), language="text")
            else:
                st.info("該当行はありません。")
