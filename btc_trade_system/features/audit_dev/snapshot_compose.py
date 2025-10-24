# path: ./btc_trade_system/features/audit_dev/snapshot_compose.py
# desc: スナップショット本文の強化（ヘッダメタ/エラー要約/レンジ）を組み立てる非UIロジック

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Tuple
import json, hashlib, time, datetime as _dt

from btc_trade_system.features.audit_dev.envinfo import fmt_iso
from btc_trade_system.features.audit_dev.search import tail_lines, errors_only_tail
from btc_trade_system.features.audit_dev.boost import git_status_brief
from btc_trade_system.common import paths

def _json_sha256(obj: Any) -> str:
    try:
        b = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8", "ignore")
        return hashlib.sha256(b).hexdigest()
    except Exception:
        return hashlib.sha256(str(obj).encode("utf-8", "ignore")).hexdigest()

def build_header_meta(*, mode: str, snap_json: Dict[str, Any]) -> str:
    """
    [[snapshot]] の直後に差し込むメタブロックを返す（文字列）。
    - snapshot_id（JSONのSHA256）
    - created_utc（現在UTC）
    - mode / repo / branch / commit / dirty
    - logs_dir / data_dir
    """
    try:
        snapshot_id = _json_sha256(snap_json)
        created_utc = _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
        git_lines = git_status_brief()
        git_map = {"repo": "-", "branch": "-", "commit": "-", "dirty": "-"}
        for ln in git_lines:
            if ln.startswith("- root:"):
                git_map["repo"] = ln.split(":", 1)[1].strip()
            elif ln.startswith("- branch:"):
                git_map["branch"] = ln.split(":", 1)[1].strip()
            elif ln.startswith("- commit:"):
                git_map["commit"] = ln.split(":", 1)[1].strip()
            elif ln.startswith("- dirty:"):
                git_map["dirty"] = ln.split(":", 1)[1].strip()

        ld = str(paths.logs_dir())
        dd = str(paths.data_dir())

        lines = []
        lines.append(f"snapshot_id: {snapshot_id}")
        lines.append(f"created_utc: {created_utc}")
        lines.append(f"mode: {(mode or 'OFF').upper()}")
        lines.append(f"repo: {git_map['repo']}  branch: {git_map['branch']}  commit: {git_map['commit']}  dirty: {git_map['dirty']}")
        lines.append(f"logs_dir: {ld}  data_dir: {dd}")
        return "\n".join(lines)
    except Exception:
        return ""

def _range_from_jsonl_tail(path: Path, limit: int) -> Tuple[str | None, str | None]:
    """
    dev_audit.jsonl の末尾 limit*? 行を見て ts の最初/最後を返す（ISO文字列）。
    JSONでない行は無視。
    """
    try:
        lines = tail_lines(path, limit=limit * 4)
        ts_vals = []
        for s in lines:
            try:
                o = json.loads(s)
                if isinstance(o, dict) and "ts" in o:
                    ts_vals.append(str(o["ts"]))
            except Exception:
                continue
        if not ts_vals:
            return None, None
        first = ts_vals[0]
        last = ts_vals[-1]
        return first, last
    except Exception:
        return None, None

def build_errors_summary(*, limit: int = 150) -> str:
    """
    Errors only tail の要約ブロックを返す。
    - last_N / counts / top_event / range（先頭/末尾 ts）
    """
    try:
        dev_audit = paths.logs_dir() / "dev_audit.jsonl"
        rows = errors_only_tail(dev_audit, limit=limit)
        # カウント
        c_err = sum(1 for s in rows if "\"level\":\"ERROR\"" in s or "\"level\":\"ERR\"" in s)
        c_crit = sum(1 for s in rows if "\"level\":\"CRIT\"" in s or "\"level\":\"CRITICAL\"" in s)
        # ざっくり top_event（event フィールドの最多）
        freq: Dict[str, int] = {}
        for s in rows:
            try:
                o = json.loads(s)
                ev = str(o.get("event", ""))
            except Exception:
                ev = ""
            if ev:
                freq[ev] = freq.get(ev, 0) + 1
        top_event = "-"
        if freq:
            ev, cnt = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[0]
            top_event = f"{ev}({cnt})"
        # レンジ（全 tail から推定）
        first, last = _range_from_jsonl_tail(dev_audit, limit=limit)
        range_txt = f"{first} .. {last}" if first and last else "-"

        lines = []
        lines.append("## errors_summary")
        lines.append(f"- last_N: {limit}  counts: ERROR={c_err}, CRIT={c_crit}  top_event: {top_event}")
        lines.append(f"- range: {range_txt}")
        return "\n".join(lines)
    except Exception:
        return "## errors_summary\n- last_N: 0  counts: ERROR=0, CRIT=0\n- range: -"

def parse_header_meta(text: str) -> dict:
    """
    handover本文先頭の key: value ブロックを辞書化して返す。
    先頭行が [[snapshot]] の場合はその次行から、無い場合は先頭から
    空行が現れるまでをメタブロックとして解釈する。
    """
    if not text:
        return {}
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "[[snapshot]]":
        start = 1
    meta: dict[str, str] = {}
    for ln in lines[start:]:
        s = ln.strip()
        if not s:
            break
            # ラベルや見出しが来たらメタ終端とみなす
            break
        k, v = s.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta

# === 追加: handoverテキストへの安全な章追加ヘルパ & モード別 tail 章 ===

def ensure_errors_summary_in_text(text: str, *, limit: int = 150) -> str:
    """
    handover本文内に '## errors_summary' が無ければ末尾に追記して返す（重複しない安全な後付け）。
    """
    try:
        if "## errors_summary" in (text or ""):
            return text
        block = build_errors_summary(limit=limit)
        if not text:
            return block + "\n"
        return text + ("\n" if not text.endswith("\n") else "") + block + "\n"
    except Exception:
        return text

def build_tail_block(*, mode: str, last_n: int = 20) -> str:
    """
    モード別に tail 章を構築して返す。
      - DEBUG: errors_only_tail() を使い「errors-only」表記で出力
      - BOOST: 従来 tail_lines() を使いそのまま出力
    """
    try:
        dev_audit = paths.logs_dir() / "dev_audit.jsonl"
        m = (mode or "OFF").upper()
        if m == "DEBUG":
            rows = errors_only_tail(dev_audit, limit=last_n)
            title = f"## audit_tail (errors-only, last {last_n})"
        else:
            rows = tail_lines(dev_audit, limit=last_n)
            title = f"## audit_tail (last {last_n})"

        body = []
        for s in rows:
            s2 = s.rstrip("\n")
            if not s2:
                continue
            body.append(f"- {s2}")
        return "\n".join([title] + body) if body else f"{title}\n- (no rows)"
    except Exception as e:
        return f"## audit_tail (last {last_n})\n- (error: {e!r})"
