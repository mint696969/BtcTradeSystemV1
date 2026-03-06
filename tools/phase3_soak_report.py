# path: ./tools/phase3_soak_report.py
# desc: Phase3 の長時間運用ログを集計し、JSON/Markdown の soak report を生成する。

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.core import io, paths  # noqa: E402


UTC = timezone.utc


@dataclass
class LogStat:
    path: str
    exists: bool
    rows: int
    warn: int
    error: int
    by_event: Dict[str, int]


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _iso_z(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_ts(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=UTC)
        except Exception:
            return None

    s = str(value).strip()
    if not s:
        return None

    # "2026-03-06T05:21:22Z"
    # "2026-03-06T05:21:22.123Z"
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    try:
        return datetime.fromisoformat(s).astimezone(UTC)
    except Exception:
        return None


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def _filter_rows_since(rows: Iterable[Dict[str, Any]], since_dt: datetime) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in rows:
        dt = _parse_ts(row.get("ts"))
        if dt is None:
            continue
        if dt >= since_dt:
            out.append(row)
    return out


def _build_log_stat(path: Path, rows: List[Dict[str, Any]]) -> LogStat:
    by_event = Counter()
    warn = 0
    error = 0

    for row in rows:
        ev = str(row.get("event") or "")
        lv = str(row.get("level") or "").upper()
        if ev:
            by_event[ev] += 1
        if lv == "WARN":
            warn += 1
        elif lv == "ERROR":
            error += 1

    return LogStat(
        path=str(path),
        exists=path.exists(),
        rows=len(rows),
        warn=warn,
        error=error,
        by_event=dict(by_event),
    )


def _payload(row: Dict[str, Any]) -> Dict[str, Any]:
    p = row.get("payload")
    return p if isinstance(p, dict) else {}


def _count_event(rows: List[Dict[str, Any]], name: str) -> int:
    n = 0
    for row in rows:
        if str(row.get("event") or "") == name:
            n += 1
    return n


def _collect_rate_control(audit_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    engaged = 0
    released = 0
    by_exchange = Counter()
    reasons = Counter()
    transitions = Counter()
    reasons_by_exchange: Dict[str, Counter] = {}

    last_engaged_reason_by_exchange: Dict[str, str] = {}
    last_released_reason_by_exchange: Dict[str, str] = {}
    last_transition_by_exchange: Dict[str, str] = {}

    for row in audit_rows:
        ev = str(row.get("event") or "")
        if ev not in (
            "rate_control.engaged",
            "rate_control.released",
            "rate_control.reason",
            "rate_control.backoff_changed",
            "rate_control.hold_started",
            "rate_control.hold_finished",
            "collector.http.429",
        ):
            continue

        p = _payload(row)
        ex = str(p.get("exchange") or p.get("provider") or "unknown")
        reason = str(p.get("reason") or "")
        prev_mode = str(p.get("prev_mode") or "")
        new_mode = str(p.get("new_mode") or "")
        tr = f"{prev_mode}->{new_mode}" if (prev_mode or new_mode) else ""

        by_exchange[ex] += 1
        if ex not in reasons_by_exchange:
            reasons_by_exchange[ex] = Counter()

        if reason:
            reasons[reason] += 1
            reasons_by_exchange[ex][reason] += 1

        if tr:
            transitions[tr] += 1
            last_transition_by_exchange[ex] = tr

        if ev == "rate_control.engaged":
            engaged += 1
            if reason:
                last_engaged_reason_by_exchange[ex] = reason
        elif ev == "rate_control.released":
            released += 1
            if reason:
                last_released_reason_by_exchange[ex] = reason

    top_reasons = [
        {"reason": k, "count": v}
        for k, v in reasons.most_common(10)
    ]

    by_exchange_detail: Dict[str, Dict[str, Any]] = {}
    for ex in sorted(by_exchange.keys()):
        by_exchange_detail[ex] = {
            "event_count": int(by_exchange[ex]),
            "top_reasons": [
                {"reason": k, "count": v}
                for k, v in reasons_by_exchange.get(ex, Counter()).most_common(5)
            ],
            "last_engaged_reason": last_engaged_reason_by_exchange.get(ex, ""),
            "last_released_reason": last_released_reason_by_exchange.get(ex, ""),
            "last_transition": last_transition_by_exchange.get(ex, ""),
        }

    return {
        "engaged_count": engaged,
        "released_count": released,
        "by_exchange": dict(by_exchange),
        "reasons": dict(reasons),
        "top_reasons": top_reasons,
        "transitions": dict(transitions),
        "by_exchange_detail": by_exchange_detail,
    }

def _collect_phase3_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    nas_ok = 0
    nas_warn = 0
    evidence_ok = 0
    evidence_fail = 0
    watchdog_respawn = 0
    watchdog_exited = 0
    derived_respawn = 0
    derived_exited = 0
    disk_guard_count = 0
    min_free_gb: Optional[float] = None
    max_logs_gb: Optional[float] = None
    max_data_gb: Optional[float] = None

    for row in rows:
        ev = str(row.get("event") or "")
        if ev == "nas.sync.done":
            if bool(row.get("ok")):
                nas_ok += 1
            else:
                nas_warn += 1
        elif ev == "evidence_pack.done":
            if bool(row.get("ok")):
                evidence_ok += 1
            else:
                evidence_fail += 1
        elif ev == "watchdog.respawn":
            watchdog_respawn += 1
        elif ev == "watchdog.exited":
            watchdog_exited += 1
        elif ev == "derived.respawn":
            derived_respawn += 1
        elif ev == "derived.exited":
            derived_exited += 1
        elif ev == "disk.guard":
            disk_guard_count += 1
            try:
                free_gb = float(row.get("free_gb"))
                min_free_gb = free_gb if min_free_gb is None else min(min_free_gb, free_gb)
            except Exception:
                pass
            try:
                logs_gb = float(row.get("logs_gb"))
                max_logs_gb = logs_gb if max_logs_gb is None else max(max_logs_gb, logs_gb)
            except Exception:
                pass
            try:
                data_gb = float(row.get("data_gb"))
                max_data_gb = data_gb if max_data_gb is None else max(max_data_gb, data_gb)
            except Exception:
                pass

    return {
        "nas_sync_ok": nas_ok,
        "nas_sync_warn": nas_warn,
        "evidence_pack_ok": evidence_ok,
        "evidence_pack_fail": evidence_fail,
        "watchdog_respawn": watchdog_respawn,
        "watchdog_exited": watchdog_exited,
        "derived_respawn": derived_respawn,
        "derived_exited": derived_exited,
        "disk_guard_count": disk_guard_count,
        "min_free_gb": min_free_gb,
        "max_logs_gb": max_logs_gb,
        "max_data_gb": max_data_gb,
    }


def _collect_supervisor_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "collector_start": _count_event(rows, "collector.start"),
        "collector_exited": _count_event(rows, "collector.exited"),
        "fails_reset": _count_event(rows, "fails.reset"),
        "backoff_sleep": _count_event(rows, "backoff.sleep"),
        "preflight_ok": _count_event(rows, "preflight.btcts.ok"),
    }


def _collect_derived_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "runner_start": _count_event(rows, "runner.start"),
        "runner_exit": _count_event(rows, "runner.exit"),
        "hourly_ok": _count_event(rows, "hourly.ok"),
        "daily_ok": _count_event(rows, "daily.ok"),
        "coverage_ok": _count_event(rows, "coverage.ok"),
        "gaps_ok": _count_event(rows, "gaps.ok"),
        "anomaly_ok": _count_event(rows, "anomaly.ok"),
    }


def _build_findings(
    phase3: Dict[str, Any],
    supervisor: Dict[str, Any],
    derived: Dict[str, Any],
    rate: Dict[str, Any],
    stats: Dict[str, LogStat],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    if phase3["evidence_pack_fail"] > 0:
        findings.append(
            {
                "severity": "critical",
                "title": "evidence pack failure detected",
                "detail": f"evidence_pack_fail={phase3['evidence_pack_fail']}",
            }
        )

    if phase3["nas_sync_warn"] > 0:
        findings.append(
            {
                "severity": "recommended",
                "title": "NAS sync warnings detected",
                "detail": f"nas_sync_warn={phase3['nas_sync_warn']}",
            }
        )

    if phase3["watchdog_exited"] > 0 or phase3["derived_exited"] > 0:
        findings.append(
            {
                "severity": "recommended",
                "title": "runtime respawn/exited events detected",
                "detail": (
                    f"watchdog_exited={phase3['watchdog_exited']} "
                    f"derived_exited={phase3['derived_exited']}"
                ),
            }
        )

    if supervisor["collector_exited"] > 0:
        findings.append(
            {
                "severity": "recommended",
                "title": "collector exited during soak window",
                "detail": f"collector_exited={supervisor['collector_exited']}",
            }
        )

    if rate["engaged_count"] > 0 and rate["released_count"] == 0:
        findings.append(
            {
                "severity": "minor",
                "title": "rate control engaged but no release observed",
                "detail": f"engaged={rate['engaged_count']} released={rate['released_count']}",
            }
        )

    total_warn = sum(v.warn for v in stats.values())
    total_error = sum(v.error for v in stats.values())
    if total_error > 0:
        findings.append(
            {
                "severity": "recommended",
                "title": "error-level log entries detected",
                "detail": f"error_count={total_error}",
            }
        )
    elif total_warn > 0:
        findings.append(
            {
                "severity": "minor",
                "title": "warn-level log entries detected",
                "detail": f"warn_count={total_warn}",
            }
        )

    if not findings:
        findings.append(
            {
                "severity": "ok",
                "title": "no major soak findings",
                "detail": "no critical/recommended issues were detected in the selected window",
            }
        )

    return findings


def _decision(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    has_critical = any(f["severity"] == "critical" for f in findings)
    has_recommended = any(f["severity"] == "recommended" for f in findings)

    return {
        "ui_parallel_safe": not has_critical,
        "phase3c_required": has_critical,
        "phase3c_recommended": (not has_critical) and has_recommended,
    }


def _md_section(title: str, body: str) -> str:
    return f"## {title}\n\n{body.rstrip()}\n"


def _fmt_kv(d: Dict[str, Any]) -> str:
    lines = []
    for k, v in d.items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines) if lines else "- (none)"


def build_report(hours: float) -> Dict[str, Any]:
    logs_dir = paths.logs_dir()
    phase3_dir = logs_dir / "phase3"
    derived_dir = logs_dir / "derived"

    now = _now_utc()
    since_dt = now - timedelta(hours=float(hours))

    files = {
        "phase3": phase3_dir / "phase3_runner.jsonl",
        "supervisor": logs_dir / "supervisor_collector.jsonl",
        "derived": derived_dir / "derived_runner.jsonl",
        "audit": logs_dir / "audit.jsonl",
    }

    rows_map: Dict[str, List[Dict[str, Any]]] = {}
    stats: Dict[str, LogStat] = {}

    for name, path in files.items():
        rows = _filter_rows_since(_iter_jsonl(path), since_dt)
        rows_map[name] = rows
        stats[name] = _build_log_stat(path, rows)

    phase3_metrics = _collect_phase3_metrics(rows_map["phase3"])
    supervisor_metrics = _collect_supervisor_metrics(rows_map["supervisor"])
    derived_metrics = _collect_derived_metrics(rows_map["derived"])
    rate_metrics = _collect_rate_control(rows_map["audit"])

    findings = _build_findings(
        phase3_metrics,
        supervisor_metrics,
        derived_metrics,
        rate_metrics,
        stats,
    )
    decision = _decision(findings)

    report = {
        "generated_at": _iso_z(now),
        "window": {
            "hours": float(hours),
            "since": _iso_z(since_dt),
            "until": _iso_z(now),
        },
        "paths": {k: str(v) for k, v in files.items()},
        "logs": {
            k: {
                "path": v.path,
                "exists": v.exists,
                "rows": v.rows,
                "warn": v.warn,
                "error": v.error,
                "by_event": v.by_event,
            }
            for k, v in stats.items()
        },
        "summary": {
            "phase3": phase3_metrics,
            "supervisor": supervisor_metrics,
            "derived": derived_metrics,
            "rate_control": rate_metrics,
        },
        "findings": findings,
        "decision": decision,
    }
    return report


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Phase3 Soak Report")
    lines.append("")
    lines.append(f"- generated_at: {report['generated_at']}")
    lines.append(f"- window.hours: {report['window']['hours']}")
    lines.append(f"- since: {report['window']['since']}")
    lines.append(f"- until: {report['window']['until']}")
    lines.append("")

    lines.append(_md_section("Decision", _fmt_kv(report["decision"])))
    lines.append(_md_section("Phase3 Summary", _fmt_kv(report["summary"]["phase3"])))
    lines.append(_md_section("Supervisor Summary", _fmt_kv(report["summary"]["supervisor"])))
    lines.append(_md_section("Derived Summary", _fmt_kv(report["summary"]["derived"])))
    rc = report["summary"]["rate_control"]

    rc_lines: List[str] = []
    rc_lines.append(f"- engaged_count: {rc.get('engaged_count')}")
    rc_lines.append(f"- released_count: {rc.get('released_count')}")

    top_reasons = rc.get("top_reasons") or []
    if top_reasons:
        rc_lines.append("- top_reasons:")
        for item in top_reasons:
            rc_lines.append(f"  - {item.get('reason')}: {item.get('count')}")
    else:
        rc_lines.append("- top_reasons: (none)")

    by_ex_detail = rc.get("by_exchange_detail") or {}
    if by_ex_detail:
        rc_lines.append("- by_exchange_detail:")
        for ex in sorted(by_ex_detail.keys()):
            info = by_ex_detail.get(ex) or {}
            rc_lines.append(f"  - {ex}:")
            rc_lines.append(f"    - event_count: {info.get('event_count')}")
            rc_lines.append(f"    - last_transition: {info.get('last_transition')}")
            rc_lines.append(f"    - last_engaged_reason: {info.get('last_engaged_reason')}")
            rc_lines.append(f"    - last_released_reason: {info.get('last_released_reason')}")
            tops = info.get('top_reasons') or []
            if tops:
                rc_lines.append("    - top_reasons:")
                for item in tops:
                    rc_lines.append(f"      - {item.get('reason')}: {item.get('count')}")
            else:
                rc_lines.append("    - top_reasons: (none)")
    else:
        rc_lines.append("- by_exchange_detail: (none)")

    lines.append(_md_section("Rate Control Summary", "\n".join(rc_lines)))

    findings_body = "\n".join(
        f"- [{f['severity']}] {f['title']} :: {f['detail']}" for f in report["findings"]
    )
    lines.append(_md_section("Findings", findings_body or "- (none)"))

    log_parts: List[str] = []
    for name, info in report["logs"].items():
        log_parts.append(f"### {name}")
        log_parts.append("")
        log_parts.append(_fmt_kv(info))
        log_parts.append("")
    lines.append("## Log Stats\n")
    lines.extend(log_parts)

    return "\n".join(lines).rstrip() + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Phase3 soak report from existing logs.")
    parser.add_argument("--hours", type=float, default=168.0, help="Lookback window in hours (default: 168)")
    args = parser.parse_args(argv)

    report = build_report(hours=args.hours)

    phase3_dir = paths.logs_dir() / "phase3"
    phase3_dir.mkdir(parents=True, exist_ok=True)

    stamp = _now_utc().strftime("%Y%m%d_%H%M%SZ")
    json_path = phase3_dir / f"soak_report_{stamp}.json"
    md_path = phase3_dir / f"soak_report_{stamp}.md"

    io.write_json(json_path, report)
    io.atomic_write_text(md_path, render_markdown(report))

    print(f"OK soak_report_json: {json_path}")
    print(f"OK soak_report_md: {md_path}")
    print(f"decision: {report['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())