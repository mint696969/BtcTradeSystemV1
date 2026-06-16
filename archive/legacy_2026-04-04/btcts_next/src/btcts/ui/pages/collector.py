# path: ./btcts_next/src/btcts/ui/pages/collector.py
# desc: Collectorの起動/停止と status.json 表示。ENV/パス不整合を“原因が分かる形”で提示する最小運用UI。

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import streamlit as st
from btcts.core import env as ENV


def _env(k: str) -> str:
    return os.environ.get(k, "") or ""


def _status_path() -> Tuple[str, str]:
    """(data_dir, status.json path)"""
    try:
        data_dir = str(ENV.data_dir())
    except Exception:
        return "", ""
    return data_dir, os.path.join(data_dir, "collector", "status.json")


def _read_status_file() -> Tuple[Optional[Dict[str, Any]], str]:
    """(json or None, reason)"""
    data_dir, p = _status_path()
    if not data_dir:
        return None, "ENV.data_dir() is not resolved (BTC_TS_DATA_DIR is empty?)"

    if not os.path.exists(p):
        return None, f"status.json not found: {p}"

    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f), ""
    except Exception as e:
        return None, f"status.json read failed: {type(e).__name__}: {e}"


def _expected_status_path_hint(data_dir: str) -> str:
    if not data_dir:
        return ""
    return os.path.join(data_dir, "collector", "status.json")


def _phase3_dir() -> Path:
    try:
        logs_dir = str(ENV.logs_dir())
    except Exception:
        return Path(".")
    return Path(logs_dir) / "phase3"


def _find_latest_soak_report_json() -> Tuple[Optional[Path], str]:
    phase3_dir = _phase3_dir()
    if not phase3_dir.exists():
        return None, f"phase3 dir not found: {phase3_dir}"

    files = sorted(
        phase3_dir.glob("soak_report_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        return None, f"soak_report_*.json not found under: {phase3_dir}"

    return files[0], ""


def _read_latest_soak_report() -> Tuple[Optional[Dict[str, Any]], str]:
    p, reason = _find_latest_soak_report_json()
    if p is None:
        return None, reason

    try:
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            return None, f"invalid soak report json: {p}"
        obj["_report_path"] = str(p)
        return obj, ""
    except Exception as e:
        return None, f"soak report read failed: {type(e).__name__}: {e}"


def render_collector_page() -> None:
    st.subheader("Collector Control")

    # Auto refresh（外部依存なしで確実に動く方式）
    ar1, ar2 = st.columns([1, 2])
    with ar1:
        auto = st.toggle("Auto refresh", value=False, key="collector_auto_refresh")
    with ar2:
        interval_sec = st.selectbox(
            "Interval (sec)",
            [1, 2, 3, 5, 10, 30, 60],
            index=3,  # 5秒
            key="collector_auto_refresh_sec",
        )

    # 遅延import：import時の副作用/重さを避ける
    from btcts.collector.control import restart, start, status, stop

    # status.json パスの表示（ENVミスはここで即わかる）
    data_dir, st_path = _status_path()
    with st.expander("Paths (collector)", expanded=False):
        st.write(
            {
                "BTC_TS_DATA_DIR": data_dir,
                "status.json": st_path,
            }
        )

    selected_mode = st.selectbox(
        "Collector mode",
        ["NORMAL", "DEBUG", "BOOST"],
        index=0,
        key="collector_mode_select",
    )

    # セッションキャッシュ（Refresh/Start/Stop でだけ更新）
    if "collector_status" not in st.session_state:
        st.session_state["collector_status"] = None
    if "collector_status_ts" not in st.session_state:
        st.session_state["collector_status_ts"] = 0.0
    if "collector_status_err" not in st.session_state:
        st.session_state["collector_status_err"] = ""

    def _refresh_status() -> None:
        try:
            st.session_state["collector_status"] = status()
            st.session_state["collector_status_err"] = ""
        except Exception as e:
            st.session_state["collector_status"] = None
            st.session_state["collector_status_err"] = f"status() failed: {type(e).__name__}: {e}"
        st.session_state["collector_status_ts"] = time.time()

    # --- Start disabled 判定（仕様: ready/reasons） ---
    # 遅延import：import時の副作用/重さを避ける
    from btcts.settings import svc as settings_svc

    ready, reasons, details = settings_svc.exchanges_ready()

    # 操作ボタン
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 2])

    with c1:
        if st.button("Start", use_container_width=True, disabled=(not ready), key="collector_start"):
            stt = start(
                desired_mode=selected_mode,
                requested_by="ui",
                reason=f"ui start mode={selected_mode}",
            )
            st.toast(f"start: {stt.mode} {stt.message}")
            _refresh_status()
            st.rerun()

    with c2:
        if st.button("Stop", use_container_width=True, key="collector_stop"):
            stt = stop()
            st.toast(f"stop: {stt.mode} {stt.message}")
            _refresh_status()
            st.rerun()

    with c3:
        if st.button("Restart", use_container_width=True, disabled=(not ready), key="collector_restart"):
            stt = restart(
                desired_mode=selected_mode,
                requested_by="ui",
                reason=f"ui restart mode={selected_mode}",
            )
            st.toast(f"restart: {stt.mode} {stt.message}")
            _refresh_status()
            st.rerun()

    with c4:
        if st.button("Refresh", use_container_width=True, key="collector_refresh"):
            _refresh_status()
            st.rerun()

    with c5:
        if st.session_state["collector_status"] is None and not st.session_state.get("collector_status_err"):
            # 初回表示だけ status() を叩く
            _refresh_status()

        err = st.session_state.get("collector_status_err", "")
        stt = st.session_state.get("collector_status")
        ts = st.session_state.get("collector_status_ts", 0.0)
        age = max(0.0, time.time() - ts) if ts else 0.0

        if err:
            st.caption(f"status(): ERROR (age={age:.1f}s)")
            st.error(err)
        elif stt is None:
            st.caption(f"status(): (no data) (age={age:.1f}s)")
        else:
            st.caption(f"status(): {stt.mode} / {stt.message} (age={age:.1f}s)")

    # Start が disabled の場合は理由を表示（事故防止）
    if not ready:
        for r in reasons:
            st.warning(r)

        # 取引所ごとの詳細（必要なら折りたたみ）
        with st.expander("取引所ごとの判定詳細", expanded=False):
            for ex_id, d in (details or {}).items():
                if not isinstance(d, dict):
                    continue
                ex_ready = bool(d.get("ready"))
                ex_reasons = d.get("reasons") if isinstance(d.get("reasons"), list) else []
                if ex_ready:
                    st.success(f"{ex_id}: ready")
                else:
                    st.error(f"{ex_id}: not ready")
                    for rr in ex_reasons:
                        st.write(f"- {rr}")

    st.divider()

    js, reason = _read_status_file()

    if js is not None and isinstance(js, dict):
        actual_state = str(js.get("actual_state") or js.get("mode") or "")
        actual_mode = str(js.get("actual_mode") or "")
        rc = js.get("rate_control") if isinstance(js.get("rate_control"), dict) else {}
        rc_state = str(rc.get("summary_state") or "")
        rc_reason = str(rc.get("last_reason") or "")

        st.write("status.json (summary)")
        st.json(
            {
                "actual_state": actual_state,
                "actual_mode": actual_mode,
                "rate_control.summary_state": rc_state,
                "rate_control.last_reason": rc_reason,
            }
        )

    soak_js, soak_reason = _read_latest_soak_report()

    st.write("latest soak report (summary)")
    if soak_js is None:
        st.info(soak_reason)
    else:
        decision = soak_js.get("decision") if isinstance(soak_js.get("decision"), dict) else {}
        findings = soak_js.get("findings") if isinstance(soak_js.get("findings"), list) else []
        summary = soak_js.get("summary") if isinstance(soak_js.get("summary"), dict) else {}
        rate = summary.get("rate_control") if isinstance(summary.get("rate_control"), dict) else {}
        top_reasons = rate.get("top_reasons") if isinstance(rate.get("top_reasons"), list) else []

        summary_obj = {
            "report_path": soak_js.get("_report_path", ""),
            "generated_at": soak_js.get("generated_at", ""),
            "decision.ui_parallel_safe": decision.get("ui_parallel_safe", ""),
            "decision.phase3c_required": decision.get("phase3c_required", ""),
            "decision.phase3c_recommended": decision.get("phase3c_recommended", ""),
            "rate_control.engaged_count": rate.get("engaged_count", 0),
            "rate_control.released_count": rate.get("released_count", 0),
            "findings.count": len(findings),
        }

        if top_reasons:
            summary_obj["rate_control.top_reason_1"] = (
                f"{top_reasons[0].get('reason')}: {top_reasons[0].get('count')}"
            )
        if len(top_reasons) >= 2:
            summary_obj["rate_control.top_reason_2"] = (
                f"{top_reasons[1].get('reason')}: {top_reasons[1].get('count')}"
            )

        st.json(summary_obj)

        with st.expander("latest soak findings", expanded=False):
            if findings:
                for f in findings:
                    sev = str(f.get("severity") or "")
                    title = str(f.get("title") or "")
                    detail = str(f.get("detail") or "")
                    st.write(f"- [{sev}] {title} :: {detail}")
            else:
                st.write("- (none)")

    st.write("status.json (raw)")

    if js is None:
        # ここは“原因が分かる”文言にする（妥協しない）
        if not data_dir:
            st.error("BTC_TS_DATA_DIR is empty. Set env and restart Streamlit.")
            st.code(
                "\n".join(
                    [
                        "reason: BTC_TS_DATA_DIR is empty",
                        f"expected: {_expected_status_path_hint(data_dir)}",
                        f"BTC_TS_DATA_DIR={_env('BTC_TS_DATA_DIR')}",
                        f"BTC_TS_LOGS_DIR={_env('BTC_TS_LOGS_DIR')}",
                        f"BTC_TS_CONFIG_DIR={_env('BTC_TS_CONFIG_DIR')}",
                    ]
                ),
                language="text",
            )

        else:
            st.warning("status.json is not available.")
            st.code(
                "\n".join(
                    [
                        f"reason: {reason}",
                        f"expected: {_expected_status_path_hint(data_dir)}",
                        f"BTC_TS_DATA_DIR={_env('BTC_TS_DATA_DIR')}",
                        f"BTC_TS_LOGS_DIR={_env('BTC_TS_LOGS_DIR')}",
                        f"BTC_TS_CONFIG_DIR={_env('BTC_TS_CONFIG_DIR')}",
                    ]
                ),
                language="text",
            )

    else:
        st.json(js)

    # 画面全体を描画し終えた後に更新をかける（押しボタン動作を邪魔しない）
    if st.session_state.get("collector_auto_refresh", False):
        sec = int(st.session_state.get("collector_auto_refresh_sec", 5))
        st.caption(f"Auto refresh: every {sec}s")
        time.sleep(max(1, sec))
        st.rerun()
