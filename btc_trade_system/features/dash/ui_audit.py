# path: ./btc_trade_system/features/dash/audit_ui.py
# desc: 開発監査UI。モード3ボタン（現在モードのみprimary＝灰ベタ/白抜き）、BOOST切替時は任意で自動スナップショット。

from __future__ import annotations

import streamlit as st
import json, time
from pathlib import Path
import os, sys, datetime as _dt
import subprocess
from ...common import paths
from btc_trade_system.features.audit_dev.writer import get_mode as _dev_get_mode, set_mode as _dev_set_mode
from btc_trade_system.features.audit_dev.search import errors_only_tail
from btc_trade_system.features.audit_dev.snapshot_compose import build_header_meta, build_errors_summary
from btc_trade_system.features.audit_dev.boost import export_and_build_text
from btc_trade_system.features.audit_dev.snapshot_compose import parse_header_meta
from btc_trade_system.features.audit_dev.snapshot_ui import (
    render_snapshot_code,   # CSS 注入は内部で一度だけ行う
)

def _inject_current_mode_css(_: str) -> None:
    """現在モードのボタン（type='primary'）を灰ベタ＋白抜きに。その他は既存の色設計のまま。"""
    st.markdown(
        """
        <style>
        /* 左列ブロックのボタン間隔（少し詰める） */
        .mode-col .stButton>button { margin-bottom: 6px; padding-top: 6px; padding-bottom: 6px; }

        /* 現在モードだけ type='primary' にし、ここで色を強制 */
        .mode-col [data-testid="baseButton-primary"] {
            background-color: #6b7280 !important;   /* gray-500 */
            color: #ffffff !important;
            border-color: #6b7280 !important;
        }
        .mode-col [data-testid="baseButton-primary"]:hover {
            filter: brightness(0.95);
        }

        /* ▼ スナップショット / Download 行のボタン高さを揃える */
        .snap-row .stButton>button,
        .snap-row .stDownloadButton>button {
            padding-top: 6px !important;
            padding-bottom: 6px !important;
            line-height: 1.2 !important;
            min-height: 38px !important;   /* 目安: Streamlit標準に近い高さ */
            white-space: nowrap !important; /* ラベル改行を防ぐ */
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

from btc_trade_system.features.audit_dev.envinfo import (
    mask_env_items as _mask_env_items,
    collect_versions as _collect_versions,
    list_files_brief as _list_files_brief,
    sha256_file as _sha256_file,
    fmt_bytes as _fmt_bytes,
    fmt_iso as _fmt_iso,
)

def _log_file() -> Path:
    return paths.logs_dir() / "dev_audit.jsonl"

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

        # audit_tail: 末尾150行
        parts.append("### audit_tail (last 150)")
        try:
            if log_path.exists():
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    tail150 = f.readlines()[-150:]

                for ln in tail150:
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

            def _apply_mode_change(target: str) -> None:
                try:
                    _dev_set_mode(target)
                    st.session_state.dev_mode = target
                    st.session_state["mode_changed_at_ms"] = int(time.time() * 1000)
                    st.session_state.snapshot_text = ""
                    st.session_state.snapshot_meta = {"path": None, "size": 0, "mtime": 0.0}

                    if (target or "OFF").upper() == "BOOST" and st.session_state.get("auto_snap_on_boost", False):
                        try:
                            snap_path_str, txt = export_and_build_text(mode="BOOST", force=True)
                            st.session_state.snapshot_text = txt
                            st.session_state.snapshot_meta = {
                                "path": snap_path_str,
                                "size": len(txt.encode("utf-8", errors="ignore")),
                                "mtime": time.time(),
                            }
                        except Exception:
                            try:
                                st.session_state.snapshot_text = _make_snapshot(target)
                                st.session_state.snapshot_meta = {
                                    "path": None,
                                    "size": len(st.session_state.snapshot_text.encode("utf-8")),
                                    "mtime": time.time(),
                                }
                            except Exception:
                                pass
                    st.rerun()
                except Exception as e:
                    st.warning(f"モード更新に失敗しました: {e!r}")

            # ボタンの親をクラス指定（CSSの適用スコープ）
            with st.container():
                st.markdown("<div class='mode-col'>", unsafe_allow_html=True)

                # OFF
                btn_type = "primary" if cur == "OFF" else "secondary"
                if st.button("OFF", key="btn_mode_OFF", use_container_width=True, type=btn_type,
                             help="監査を停止します（軽量）"):
                    if cur != "OFF":
                        _apply_mode_change("OFF")

                # DEBUG
                btn_type = "primary" if cur == "DEBUG" else "secondary"
                if st.button("DEBUG", key="btn_mode_DEBUG", use_container_width=True, type=btn_type,
                             help="開発監査（要点＋1/Nサンプル）"):
                    if cur != "DEBUG":
                        _apply_mode_change("DEBUG")

                # BOOST
                btn_type = "primary" if cur == "BOOST" else "secondary"
                if st.button("BOOST", key="btn_mode_BOOST", use_container_width=True, type=btn_type,
                             help="原因特定モード（詳細、短時間のみ）"):
                    if cur != "BOOST":
                        _apply_mode_change("BOOST")
                
                st.markdown("</div>", unsafe_allow_html=True)

            # 現在モードのボタンだけ灰ベタ＋白抜き（primaryにCSSを当てる）
            _inject_current_mode_css(cur)

            # BOOST自動撮影（左列へ移動）
            st.session_state.setdefault("auto_snap_on_boost", False)
            st.checkbox("BOOST自動撮影", key="auto_snap_on_boost", help="BOOST切替時に自動で1枚撮影します。", value=st.session_state.get("auto_snap_on_boost", False))

            # 表示（UI / writer） — A仕様で '◯s前' を表示
            ui_mode = (st.session_state.get("dev_mode", "OFF") or "OFF").upper()
            try:
                writer_mode = _dev_get_mode()
            except Exception:
                writer_mode = "UNKNOWN"
            ts_ms = st.session_state.get("mode_changed_at_ms")
            ago_txt = ""
            if isinstance(ts_ms, (int, float)) and ts_ms:
                try:
                    ago_s = max(0, int(time.time() - (ts_ms/1000.0)))
                    ago_txt = f"（{ago_s}s前）"
                except Exception:
                    ago_txt = ""
            st.caption(f"現在モード: UI=`{ui_mode}` / writer=`{writer_mode}` {ago_txt}")

            # オートリフレッシュ（左列へ移動）
            st.session_state.setdefault("auto_refresh_on", True)  # 既定をONに
            st.session_state.setdefault("auto_refresh_sec", 2)
            st.checkbox(
                f"オートリフレッシュ ({st.session_state['auto_refresh_sec']}s)",
                key="auto_refresh_on",
                help="下部ログ/エラー表示を自動更新します。",
            )

    with c1:
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
        
        # ▼ ボタン行（同一の columns に収め、同じ div スコープ内で横並びにする）
        st.markdown("<div class='snap-row'>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns([1.6, 1.1, 3.3])

        with b1:
            regen = st.button(
                "スナップショット",
                key="btn_snapshot_regen",
                disabled=snapshot_disabled,
                use_container_width=True,
            )

        with b2:
            _txt_now = st.session_state.get("snapshot_text") or ""
            st.download_button(
                label="Download",  # ← 短くして改行を防ぐ
                help="現在のスナップショット本文を handover_gpt.txt として保存します。",
                data=_txt_now.encode("utf-8"),
                file_name="handover_gpt.txt",
                mime="text/plain",
                key="dl_handover_txt_top",
                use_container_width=True,
                disabled=not _txt_now,
            )

        # b3 はスペーサ（未使用）— 横位置のバランス用に残す
        st.markdown("</div>", unsafe_allow_html=True)

        # （重要）ボタン行とオプション行を“別の行”に分けるための区切り
        st.markdown("")  # 空行でレイアウトを確実に分離

        # === 追加: 付加オプション（構成切替） ==========================
        st.session_state.setdefault("opt_repo_map", True)
        st.session_state.setdefault("opt_tail150", False)
        st.session_state.setdefault("opt_env_versions", False)

        # REPO_MAP 抜粋の既定行数（DEBUG/BOOST）
        st.session_state.setdefault("repo_map_limit_debug", 50)
        st.session_state.setdefault("repo_map_limit_boost", 200)

        # ▼ オプション行（ボタン行とは独立させ、等幅で横一列）
        with st.container():
            o1, o2, o3, o4 = st.columns([1, 1, 1, 1])
            with o1:
                st.checkbox("REPO_MAP", key="opt_repo_map",
                            help="handover末尾に REPO_MAP の抜粋を付与")
            with o2:
                st.checkbox("tail150", key="opt_tail150",
                            help="dev_audit.jsonl の末尾150行を付与")
            with o3:
                st.checkbox("Env+Ver", key="opt_env_versions",
                            help="環境変数(マスク済)と主要バージョン表を付与")
            with o4:
                st.checkbox("ErrOnly", key="opt_err_tail",
                            help="ERROR/CRITICAL だけを最大150行抽出して付与")

        # 1) 先に生成を反映
        if regen:
            try:
                # 新ラッパで「公式生成→handover本文」まで取得し、その後の“追加セクション”は従来通りUI側で付与
                snap_path_str, snap_text = export_and_build_text(mode=eff_mode, force=True)

                # [[snapshot]] の直後にメタ情報を追記（ID/UTC/Git/paths）
                try:
                    meta_block = build_header_meta(mode=eff_mode, snap_json=json.loads(Path(snap_path_str).read_text(encoding="utf-8", errors="ignore")))
                    if meta_block:
                        snap_text = snap_text.replace("[[snapshot]]", f"[[snapshot]]\n{meta_block}", 1)
                except Exception:
                    pass

                # Errors only tail の要約を本文に追加（件数/Top/レンジ）
                # ※ DEBUG は boost.py 側で付与済みなので、UIでは重複させない
                if (eff_mode or "OFF").upper() != "DEBUG":
                    try:
                        limit = int(st.session_state.get("audit_tail_limit", 150) or 150)
                        snap_text += "\n\n" + build_errors_summary(limit=limit)
                    except Exception:
                        pass

                # 公式結果をUIセッションにも反映（鮮度表示/ダウンロード可否を安定化）
                st.session_state.snapshot_text = snap_text

                # === オプション追記（REPO_MAP抜粋 / audit_tail / Env+Versions）===
                try:
                    mode_upper = (eff_mode or "OFF").upper()

                    # 1) REPO_MAP 抜粋
                    if st.session_state.get("opt_repo_map", False):
                        # 代表的な候補を順に当てる（存在すれば採用）
                        repo_map_cands = [
                            Path.cwd() / "REPO_MAP.extract.md",
                            paths.data_dir() / "REPO_MAP.extract.md",
                            paths.logs_dir() / "REPO_MAP.extract.md",
                            paths.data_dir() / "ctx" / "REPO_MAP.extract.md",
                        ]
                        hit = next((p for p in repo_map_cands if p.exists()), None)
                        if hit:
                            limit = (
                                int(st.session_state.get("repo_map_limit_boost", 200))
                                if mode_upper == "BOOST"
                                else int(st.session_state.get("repo_map_limit_debug", 50))
                            )
                            try:
                                with open(hit, "r", encoding="utf-8", errors="ignore") as f:
                                    lines = [ln.rstrip("\n") for ln in f.readlines()[:limit]]
                                if lines:
                                    snap_text += "\n\n## REPO_MAP (excerpt)\n" + "\n".join(lines)
                            except Exception:
                                pass

                    # 2) audit_tail（dev_audit.jsonl の末尾 N 行）
                    if st.session_state.get("opt_tail150", False):
                        try:
                            N = 150
                            dev_audit = paths.logs_dir() / "dev_audit.jsonl"
                            if dev_audit.exists():
                                with open(dev_audit, "r", encoding="utf-8", errors="ignore") as f:
                                    tail = [ln.rstrip("\n") for ln in f.readlines()[-N:]]
                                if tail:
                                    snap_text += "\n\n## audit_tail (last 150)\n" + "\n".join(f"- {s}" for s in tail if s)
                            else:
                                snap_text += "\n\n## audit_tail (last 150)\n- (dev_audit.jsonl not found)"
                        except Exception as _e_tail:
                            snap_text += f"\n\n## audit_tail (last 150)\n- (read error: {_e_tail!r})"

                    # 3) Env + Versions
                    if st.session_state.get("opt_env_versions", False):
                        try:
                            snap_text += "\n\n## Env (sanitized)\n" + "\n".join(
                                f"- {k}={v}" for k, v in _mask_env_items(os.environ)
                            )
                        except Exception:
                            snap_text += "\n\n## Env (sanitized)\n- (failed)"
                        try:
                            snap_text += "\n\n## Versions\n" + "\n".join(_collect_versions())
                        except Exception:
                            snap_text += "\n\n## Versions\n- (failed)"
                except Exception:
                    # 追記はベストエフォート（本体テキストが壊れないことを優先）
                    pass

                # 追記後の本文で session_state を上書き（DL/表示に反映）
                st.session_state.snapshot_text = snap_text
                st.session_state.snapshot_meta = {
                    "path": snap_path_str or None,
                    "size": len(snap_text.encode("utf-8", errors="ignore")),
                    "mtime": time.time(),
                }
                st.session_state["snapshot_area"] = snap_text
                st.rerun()

                # 以降（REPO_MAP抜粋／audit_tail／Errors only／Git／Storage／Disk／Env+Versions）は
                # 既存ロジックをこのまま活かして続行（＝従来の表示・オプションは維持）

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
        copy_disabled = is_off or (not st.session_state.snapshot_text)

        # 3) ここで DBG を表示
        
        # === スナップショット窓（code 版 / 10行固定 / 横縦スクロール / コピー可） ===
        snap_txt = st.session_state.get("snapshot_text") or ""

        # OFF のときは何も表示しない（空表示）。DEBUG/BOOST は中身だけをそのまま表示。
        display_txt = "" if is_off else snap_txt

        try:
            _txt = st.session_state.get("snapshot_text") or st.session_state.get("snapshot_area") or ""
            _meta_hdr = parse_header_meta(_txt)  # 非UIでパース
            _meta = st.session_state.get("snapshot_meta") or {}
            _age = "-"
            if _meta.get("mtime"):
                _age = f"{int(time.time() - float(_meta['mtime']))}s"
            cap = " | ".join([
                f"id: {_meta_hdr.get('snapshot_id','-')}",
                f"utc: {_meta_hdr.get('created_utc','-')}",
                f"size: {(_meta.get('size') or 0)}B",
                f"path: {(_meta.get('path') or '-')}",
                f"age: {_age}",
            ])
            st.caption(cap)
        except Exception:
            pass

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

        # === 監査サマリ（UI最小） ===
        from btc_trade_system.features.audit_dev.summary_panels import (
            render_health_panel, render_quota_panel, render_orders_timeline
        )
        src_path = _log_file()
        with st.expander("Collector Health", expanded=False):
            render_health_panel(src_path)
        with st.expander("API Quota", expanded=False):
            render_quota_panel(src_path)
        with st.expander("Orders Timeline", expanded=False):
            render_orders_timeline(src_path)

        # === Errors & Critical（recent） ===============================
        with st.expander("Errors & Critical（recent）", expanded=False):
            # ちょいフィルタ（キーワード）
            kw = st.text_input("キーワード", value="", placeholder='event=/feature=/payload など部分一致', key="err_kw")

            src = _log_file()
            rows: list[str] = []
            # 先にデフォルトを定義しておく（例外時の未定義を防ぐ）
            limit = int(st.session_state.get("audit_tail_limit", 150) or 150)
            try:
                # 末尾から Errors/Critical のみを抽出（search.py へ集約）
                rows = errors_only_tail(src, limit=limit)
                if kw:
                    rows = [s for s in rows if kw in s]
            except Exception as e:
                rows = [f"(errors_only_tail error: {e!r})"]

            st.caption(f"hits: {len(rows)}  source: {str(src)}（末尾{limit}抽出）")
            if rows:
                st.code("\n".join(rows[-50:]), language="text")
            else:
                st.info("該当行はありません。")

        # --- 開発監査ログ（最下部）: 10行固定・最大50行（JST表示）、DLはJST付き最大500行 ---
        from btc_trade_system.features.audit_dev.log_ui import render_log_panel
        render_log_panel(eff_mode)  # eff_mode はこの関数内で定義済みの実効モード
