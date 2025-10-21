# path: ./btc_trade_system/features/dash/audit_ui.py
# desc: AuditタブのUI（開発監査表示専用）。BOOST切替時スナップショット生成対応・lint誤検出回避。ボタン色: OFF=白, DEBUG=黄, BOOST=赤。

from __future__ import annotations

import streamlit as st
import json, time
from pathlib import Path
import streamlit.components.v1 as components
import os, sys, datetime as _dt
import platform, hashlib, subprocess

from ...common import paths
from btc_trade_system.features.dash.audit_svc import get_audit_rows as svc_get_audit_rows
from btc_trade_system.features.audit_dev.writer import get_mode as _dev_get_mode, set_mode as _dev_set_mode

from btc_trade_system.common.boost_svc import (
    export_snapshot as boost_export_snapshot,
    build_handover_text as boost_build_handover_text,
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
            f"Get-Process | Select-Object -First {max_rows} Name,Id,CPU,WS | ConvertTo-Csv -NoTypeInformation"
        ]
        csv = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=3)
        lines = [l for l in csv.splitlines() if l.strip()]
        out: list[str] = []
        for row in lines[1:]:
            parts = [x.strip().strip('"') for x in row.split(",")]
            if len(parts) >= 4:
                name, pid, cpu, ws = parts[:4]
                out.append(f"- {name} pid={pid} cpu={cpu or '0'} ws={ws}")
        return out
    except Exception:
        return []

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
                st.session_state["snapshot_view"] = ""

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
            # path/size/mtime（UNIX秒）を持つ。copy可否の鮮度判定に使用。
            st.session_state.snapshot_meta = {"path": None, "size": 0, "mtime": 0.0}

        # 実効モードは毎回 writer から直接取得（UI表示とズレないようにする）
        try:
            eff_mode = (_dev_get_mode() or "OFF").upper()
        except Exception:
            eff_mode = (st.session_state.get("dev_mode", "OFF") or "OFF").upper()
        is_off = (eff_mode == "OFF")

        snapshot_disabled = is_off  # ← ボタン描画より前に定義しておく

        # いったん真値を見える化（チェックボックスでON/OFF）
        b1, b2, b3 = st.columns([1.6, 1.1, 3.3])

        with b1:
            regen = st.button("スナップショット", key="btn_snapshot_regen",
                              disabled=snapshot_disabled, use_container_width=True)

        # 1) 先に生成を反映
        if regen:
            try:
                # 1) 公式スナップショットを出力（連打時も force=True で最新化）
                snap_path = Path(boost_export_snapshot(mode=eff_mode, force=True))
                # 2) JSON → handover テキスト化
                try:
                    snap_json = json.loads(snap_path.read_text(encoding="utf-8", errors="ignore"))
                    snap_text = boost_build_handover_text(snap_json)
                except Exception:
                    # JSON読み込みに失敗したらフォールバック
                    snap_text = _make_snapshot(eff_mode)

                st.session_state.snapshot_text = snap_text
                st.session_state.snapshot_meta = {
                    "path": str(snap_path) if snap_path.exists() else None,
                    "size": len(snap_text.encode("utf-8", errors="ignore")),
                    "mtime": time.time(),
                }
                st.session_state["snapshot_view"] = snap_text

            except Exception:
                # export が失敗したら完全フォールバック（従来の軽量生成）
                try:
                    snap_text = _make_snapshot(eff_mode)
                    st.session_state.snapshot_text = snap_text
                    st.session_state.snapshot_meta = {"path": None, "size": len(snap_text.encode("utf-8")), "mtime": time.time()}
                    st.session_state["snapshot_view"] = snap_text
                except Exception as e:
                    st.warning(f"スナップショット生成に失敗しました: {e!r}")

        # 2) 生成結果に基づいて鮮度/可否を再計算（←これが copy の可否に直結）
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

        # 3) ここで DBG を表示（定義済みの値のみ参照）
        _dev_dbg = st.checkbox("dev/debug panel", value=False)
        if _dev_dbg:
            st.caption(
                f"[DBG] eff_mode={eff_mode} is_off={is_off} fresh={fresh} "
                f"snapshot_disabled={snapshot_disabled} copy_disabled={copy_disabled} "
                f"ui_mode={(st.session_state.get('dev_mode','OFF') or 'OFF').upper()} "
                f"writer_mode_try={eff_mode}"
            )

        # b2 は空けてスペーサーとして使用
        with b2:
            st.write("")

        # コピー＋表示を iframe 内で完結（コピー成功時に空へ）
        with b3:
            _txt = st.session_state.get("snapshot_text") or ""
            _disabled_attr = "disabled" if copy_disabled else ""
            components.html(f"""
            <!DOCTYPE html><html><head><meta charset="utf-8"></head>
            <body>
                <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px;">
                <button id="copy" style="height:38px;min-width:120px" {_disabled_attr}>コピー</button>
                <small style="color:#888;">コピーすると下の枠は空になります</small>
                </div>
                <textarea id="snap" readonly style="width:100%;height:240px;"></textarea>
                <script>
                const txt = {json.dumps(_txt)};
                const area = document.getElementById('snap');
                area.value = txt;  // 表示
                const btn = document.getElementById('copy');
                btn.addEventListener('click', async () => {{
                    try {{
                    await navigator.clipboard.writeText(area.value);
                    area.value = '';  // コピー成功で即空
                    btn.innerText = 'コピー済み';
                    setTimeout(() => btn.innerText = 'コピー', 900);
                    }} catch (e) {{
                    btn.innerText = 'コピー失敗';
                    setTimeout(() => btn.innerText = 'コピー', 1200);
                    }}
                }});
                </script>
            </body></html>
            """, height=300)

        # 表示内容を組み立て：OFF時は1行目に固定メッセージを入れる
        content = st.session_state.snapshot_text or ""

        if is_off:
            prefix = "監査停止中（OFF）"
            content = (prefix + ("\n" + content if content else ""))

        meta = st.session_state.snapshot_meta or {}
        if meta.get("path"):
            st.caption(f"snapshot: {meta['path']} ({meta.get('size', 0)} bytes)")

        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
        with c1:
            q = st.text_input("キーワード", "", placeholder="event=/feature=/payload 内を部分一致（例: RATE_LIMIT）")
        with c2:
            level = st.selectbox("レベル", ["ALL", "INFO", "WARN", "ERROR", "CRIT"], index=0)
        with c3:
            exchange = st.text_input("exchange", "", placeholder="binance / bitflyer / ...")
        with c4:
            component = st.text_input("component", "", placeholder="collector / dashboard / ...")
        with c5:
            limit = st.selectbox("件数", [200, 500, 1000], index=1)

        rows = svc_get_audit_rows(
            max_lines=int(limit),
            level=None if level == "ALL" else level,
            q=(q or None),
            exchange=(exchange or None),
            component=(component or None),
        )

        st.caption(f"{len(rows)} 件")
        try:
            st.caption(f"source: {(_log_file())}")
        except Exception:
            pass

        if rows:
            import pandas as pd
            import json as _json

            df = pd.DataFrame(rows)
            prefer = [
                "ts", "level", "feature", "event", "exchange", "topic", "actor", "site", "session",
                "latency_ms", "rows", "retries", "payload",
            ]
            show_cols = [c for c in prefer if c in df.columns]
            if show_cols:
                df = df[show_cols]

            for col in ("latency_ms", "rows", "retries"):
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

            if "payload" in df.columns:
                df["payload"] = df["payload"].apply(
                    lambda x: _json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else ("" if x is None else x)
                )

            st.dataframe(df, use_container_width=True, hide_index=True, height=480)
        else:
            st.info("dev_audit.jsonl が無いか、条件に一致する行がありません。")

        st.markdown("</div>", unsafe_allow_html=True)
