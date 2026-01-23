# path: ./btcts_next/src/btcts/health/svc.py
# desc: status.json と monitoring.yaml（閾値）と audit.jsonl（根拠）から Health を分類し、UI向けサマリを返す（推論しない）。

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from btcts.core import audit as AUDIT
from btcts.core import paths as PATHS
from btcts.settings.load_yaml import load_yaml_with_path


@dataclass(frozen=True)
class HealthItem:
    exchange: str
    topic: str
    age_sec: float
    status: str  # OK / WARN / CRIT（分類）
    cause: Optional[str] = None
    retries: int = 0
    last_ok: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class HealthSummary:
    updated_at: str
    overall: str  # OK / WARN / CRIT（分類）
    counts: Dict[str, int]
    items: List[HealthItem]
    reasons: List[str]
    refs: Dict[str, str]  # 参照した根拠パス（status/audit/monitoring 等）
    audit_tail: List[Dict[str, Any]]  # 根拠（直近イベントをそのまま）


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _get_thresholds_from_cfg(cfg: Dict[str, Any]) -> Tuple[float, float]:
    """
    monitoring 実効値から warn/crit を取り出す（分類専用）。
    対応する形：
      - thresholds.default.age_sec.warn/crit（新・正）
      - thresholds.age_sec.warn/crit（旧）
    """
    # 1) 正：thresholds.default.age_sec
    age = ((cfg.get("thresholds") or {}).get("default") or {}).get("age_sec") or {}
    warn = age.get("warn", None)
    crit = age.get("crit", None)

    # 2) 旧：thresholds.age_sec
    if warn is None or crit is None:
        age2 = (cfg.get("thresholds") or {}).get("age_sec", {}) or {}
        if warn is None:
            warn = age2.get("warn", None)
        if crit is None:
            crit = age2.get("crit", None)

    # 強制デフォルト（運用で困らない値）
    if warn is None:
        warn = 60.0
    if crit is None:
        crit = 300.0

    try:
        warn_f = float(warn)
    except Exception:
        warn_f = 60.0
    try:
        crit_f = float(crit)
    except Exception:
        crit_f = 300.0

    if crit_f < warn_f:
        crit_f = warn_f

    return warn_f, crit_f


def _judge(age_sec: float, warn: float, crit: float) -> str:
    if age_sec >= crit:
        return "CRIT"
    if age_sec >= warn:
        return "WARN"
    return "OK"


def _overall_from(mode: str, counts: Dict[str, int], *, items_present: bool) -> str:
    m = (mode or "").upper()
    if m == "ERROR":
        return "CRIT"
    if m and m != "RUNNING":
        # STOPPED 等。推論せず、運用上は注意喚起。
        return "WARN"
    if not items_present:
        return "WARN"
    if counts.get("CRIT", 0) > 0:
        return "CRIT"
    if counts.get("WARN", 0) > 0:
        return "WARN"
    return "OK"


def read_health(*, audit_lines: int = 50) -> HealthSummary:
    """
    - 分類（OK/WARN/CRIT）のみを行う（推論しない）
    - 根拠として参照パスと audit の直近イベントを提示する
    - Collector 未起動/欠損でも落とさない
    """
    reasons: List[str] = []

    # --- refs（根拠パス）---
    refs: Dict[str, str] = {}
    try:
        hp = PATHS.health_paths()
        refs.update({f"paths.{k}": str(v) for k, v in hp.items()})
    except Exception as e:
        reasons.append(f"paths.health_paths failed: {type(e).__name__}: {e}")

    # monitoring（参照パス含む）
    loaded_mon = load_yaml_with_path("monitoring")
    refs["monitoring.path"] = str(loaded_mon.path) if loaded_mon.path else ""
    cfg = loaded_mon.data or {}

    warn_th, crit_th = _get_thresholds_from_cfg(cfg)

    # 閾値欠損の透明化（推論ではなく事実）
    age_default = ((cfg.get("thresholds") or {}).get("default") or {}).get("age_sec") or {}
    if age_default.get("warn", None) is None:
        reasons.append("monitoring.thresholds.default.age_sec.warn is missing -> default=60s")
    if age_default.get("crit", None) is None:
        reasons.append("monitoring.thresholds.default.age_sec.crit is missing -> default=300s")

    # status（参照パス含む）
    try:
        from btcts.collector import status as CST
        refs["status.path"] = str(CST.status_path())
        refs["rate_state.path"] = str(CST.rate_state_path())
        read_status = CST.read_status
    except Exception as e:
        return HealthSummary(
            updated_at=_now_iso(),
            overall="CRIT",
            counts={"OK": 0, "WARN": 0, "CRIT": 0},
            items=[],
            reasons=[f"import btcts.collector.status failed: {type(e).__name__}: {e}"],
            refs=refs,
            audit_tail=[],
        )

    st = read_status()

    # read_status() は dict を返す（現物）。念のため揺れも吸収。
    if isinstance(st, dict):
        mode = str(st.get("mode", "") or "")
        raw_items = st.get("items", None)
    else:
        mode = str(getattr(st, "mode", "") or "")
        raw_items = getattr(st, "items", None)

    if callable(raw_items):
        raw_items = None

    # audit tail（根拠：そのまま提示）
    refs["audit.path"] = str(PATHS.logs_dir(ensure=False) / "audit.jsonl")
    try:
        audit_tail = AUDIT.tail(max_lines=int(audit_lines))
    except Exception as e:
        audit_tail = []
        reasons.append(f"audit.tail failed: {type(e).__name__}: {e}")

    # items 欠損/空
    if raw_items is None:
        if (mode or "").upper() == "ERROR":
            reasons.append("collector mode=ERROR")
        reasons.append("status.items is None")
        return HealthSummary(
            updated_at=_now_iso(),
            overall=_overall_from(mode, {"OK": 0, "WARN": 0, "CRIT": 0}, items_present=False),
            counts={"OK": 0, "WARN": 0, "CRIT": 0},
            items=[],
            reasons=reasons,
            refs=refs,
            audit_tail=audit_tail,
        )

    if isinstance(raw_items, list) and len(raw_items) == 0:
        if (mode or "").upper() == "ERROR":
            reasons.append("collector mode=ERROR")
        reasons.append("status.items is empty (endpoints=0?)")
        return HealthSummary(
            updated_at=_now_iso(),
            overall=_overall_from(mode, {"OK": 0, "WARN": 0, "CRIT": 0}, items_present=False),
            counts={"OK": 0, "WARN": 0, "CRIT": 0},
            items=[],
            reasons=reasons,
            refs=refs,
            audit_tail=audit_tail,
        )

    # items を分類
    items: List[HealthItem] = []
    counts = {"OK": 0, "WARN": 0, "CRIT": 0}
    mode_u = (mode or "").upper()
    mode_is_error = mode_u == "ERROR"
    if mode_is_error:
        reasons.append("collector mode=ERROR -> force CRIT (classification)")

    for it in raw_items:
        if not isinstance(it, dict):
            continue

        ex = str(it.get("exchange", ""))
        tp = str(it.get("topic", ""))
        age = float(it.get("age_sec", 0.0) or 0.0)
        cause = it.get("cause")
        retries = int(it.get("retries", 0) or 0)
        last_ok = it.get("last_ok")
        notes = it.get("notes")

        stt = _judge(age, warn_th, crit_th)
        if mode_is_error:
            stt = "CRIT"

        counts[stt] += 1
        items.append(
            HealthItem(
                exchange=ex,
                topic=tp,
                age_sec=age,
                status=stt,
                cause=cause,
                retries=retries,
                last_ok=last_ok,
                notes=notes,
            )
        )

    order = {"CRIT": 0, "WARN": 1, "OK": 2}
    items.sort(key=lambda x: (order.get(x.status, 9), x.exchange, x.topic))

    overall = _overall_from(mode, counts, items_present=True)

    return HealthSummary(
        updated_at=_now_iso(),
        overall=overall,
        counts=counts,
        items=items,
        reasons=reasons,
        refs=refs,
        audit_tail=audit_tail,
    )
