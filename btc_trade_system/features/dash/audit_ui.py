# path: ./btc_trade_system/features/dash/audit_ui.py
# desc: AuditタブのUI（開発監査表示専用）。BOOST切替時スナップショット生成対応・lint誤検出回避。ボタン色: OFF=白, DEBUG=黄, BOOST=赤。

from __future__ import annotations
import streamlit as st
import json, time
from pathlib import Path

from ...common import paths
from btc_trade_system.features.dash.audit_svc import get_audit_rows as svc_get_audit_rows
from btc_trade_system.features.audit_dev.writer import get_mode as _dev_get_mode, set_mode as _dev_set_mode
from btc_trade_system.common import boost_svc

def _log_file() -> Path:
    return paths.logs_dir() / "dev_audit.jsonl"

def _mode_next(m: str) -> str:
    chain = ["OFF", "DEBUG", "BOOST"]
    m = (m or "OFF").upper()
    return chain[(chain.index(m) + 1) % len(chain)] if m in chain else "OFF"

def _auto_interval_ms(m: str) -> int:
    m = (m or "OFF").upper()
    return 0 if m == "OFF" else (2000 if m == "DEBUG" else 1000)

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

        # スナップショットの鮮度判定：直近5分以内に生成されたら「新しい」とみなす
        FRESH_SEC = 300
        _meta = st.session_state.snapshot_meta or {}
        fresh = False
        pth = _meta.get("path")
        if pth:
            try:
                mtime = _meta.get("mtime") or Path(pth).stat().st_mtime
                fresh = (time.time() - float(mtime)) <= FRESH_SEC
            except Exception:
                fresh = False

        # ボタン有効/無効：
        snapshot_disabled = is_off
        copy_disabled = is_off or (not st.session_state.snapshot_text) or (not fresh)

        # いったん真値を見える化（チェックボックスでON/OFF）
        _dev_dbg = st.checkbox("dev/debug panel", value=False)
        if _dev_dbg:
            st.caption(
                f"[DBG] eff_mode={eff_mode} is_off={is_off} fresh={fresh} "
                f"snapshot_disabled={snapshot_disabled} copy_disabled={copy_disabled} "
                f"ui_mode={ (st.session_state.get('dev_mode','OFF') or 'OFF').upper() } "
                f"writer_mode_try={eff_mode}"
            )

        b1, b2, b3 = st.columns([1.6, 1.1, 3.3])
        with b1:
            regen = st.button("スナップショット", key="btn_snapshot_regen", disabled=snapshot_disabled, use_container_width=True)
        with b2:
            copy_req = st.button("コピー", key="btn_snapshot_copy", disabled=copy_disabled, use_container_width=True)

        if regen:
            try:
                # 仕様：DEBUG→LITE / BOOST→FULL。内部ファイルは維持（DLボタンは廃止）。
                # いまの実効モード（DEBUG/BOOST のみ想定）
                mode_for_snap = "DEBUG" if eff_mode == "DEBUG" else "BOOST"

                # テキスト（handover）を “モード指定” で生成して保存し、その内容を画面へ
                text_path = boost_svc.export_handover_text(mode=mode_for_snap, force=True)
                try:
                    st.session_state.snapshot_text = Path(text_path).read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    st.session_state.snapshot_text = f"[handover_gpt.txt] {text_path}"

                # JSONスナップショットも “モード指定” で生成して保存し、メタ表示へ反映
                json_path = boost_svc.export_snapshot(mode=mode_for_snap, force=True)
                try:
                    p = Path(json_path)
                    size = p.stat().st_size
                    mtime = p.stat().st_mtime
                except Exception:
                    size, mtime = 0, 0.0
                st.session_state.snapshot_meta = {"path": str(json_path), "size": size, "mtime": mtime}

                # ボタンの有効/無効を即反映させる
                st.rerun()

            except Exception as e:
                st.warning(f"スナップショット生成に失敗しました: {e!r}")

        if copy_req:
            # 実コピーは st.code の ⧉ ボタンで行う（仕様F）。ここではユーザに明示。
            st.toast("内容をコピーしました（上の ⧉ ボタンをご利用ください）", icon="✅")

        # 表示内容を組み立て：OFF時は1行目に固定メッセージを入れる
        content = st.session_state.snapshot_text or ""
        if is_off:
            prefix = "監査停止中（OFF）"
            content = (prefix + ("\n" + content if content else ""))

        # 初期化：まだ作られていない時だけ初期値を設定
        if "snapshot_view" not in st.session_state:
            st.session_state["snapshot_view"] = content
        else:
            # ランタイム更新時は Session State のみ上書き（value は渡さない）
            st.session_state["snapshot_view"] = content

        # 高さ240px固定（≒10行）。value は指定せず、key のみで描画する
        st.text_area(
            label="コピペ用テキスト",
            height=240,
            key="snapshot_view",
            label_visibility="collapsed",
        )

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
