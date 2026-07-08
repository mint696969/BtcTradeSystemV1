# path: ./btcts_next/src/btcts/prediction/market_regime/hypothesis_lane.py
# desc: Market-regime AI/GPT/operator hypothesis candidate lane. Records candidate ideas and trust snapshots as evidence-only artifacts; no GPT/API calls, classifier auto-apply, scheduler, broker, AutoTrade, or parameter auto-promotion.

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

MARKET_REGIME_HYPOTHESIS_LANE_VERSION = "prediction.market_regime.hypothesis_lane.2026_07_08.v1"
MARKET_REGIME_HYPOTHESIS_CANDIDATE_SCHEMA_VERSION = "market_regime_hypothesis_candidate.2026_07_08.v1"
MARKET_REGIME_HYPOTHESIS_TRUST_SCHEMA_VERSION = "market_regime_hypothesis_trust.2026_07_08.v1"
HYPOTHESIS_PART_FILENAME = "part-00001.jsonl"
_ALLOWED_ORIGINS = {"gpt", "operator", "replay", "manual_rule", "model_assisted"}
_ALLOWED_STATES = {"candidate", "shadow", "accepted_for_replay", "rejected", "deprecated"}
_FORBIDDEN_RAW_KEYS = {
    "raw_candles",
    "raw_orderbook",
    "raw_trades",
    "raw_executions",
    "raw_market_payload",
    "raw_source_payload",
    "bids",
    "asks",
    "trades",
    "executions",
}


def _date(value: object) -> str:
    text = str(value or "")
    if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
        return text[:10]
    return "unknown-date"


def hypothesis_candidate_part_relpath(created_at: str) -> str:
    return f"prediction/market_regime/hypotheses/candidates/date={_date(created_at)}/{HYPOTHESIS_PART_FILENAME}"


def hypothesis_trust_latest_relpath() -> str:
    return "prediction/market_regime/hypotheses/trust/latest.json"


def _hash_id(*parts: object) -> str:
    text = "|".join(str(part or "") for part in parts)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _has_forbidden_raw_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in _FORBIDDEN_RAW_KEYS:
                return True
            if _has_forbidden_raw_keys(nested):
                return True
    elif isinstance(value, list):
        return any(_has_forbidden_raw_keys(item) for item in value)
    return False


def _bounded_text(value: object, *, limit: int = 4000) -> str:
    text = str(value or "").strip()
    return text[:limit]


@dataclass(frozen=True)
class MarketRegimeHypothesisSafety:
    evidence_only: bool = True
    gpt_api_call_allowed: bool = False
    classifier_auto_apply_allowed: bool = False
    parameter_auto_promotion_allowed: bool = False
    live_parameter_apply_allowed: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    broker_private_api_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketRegimeHypothesisCandidate:
    hypothesis_id: str
    created_at: str
    origin: str
    title: str
    hypothesis_text: str
    target_regimes: tuple[str, ...] = ()
    target_horizons: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    proposed_signal_changes: Dict[str, Any] = field(default_factory=dict)
    proposed_parameter_changes: Dict[str, Any] = field(default_factory=dict)
    trust_rank: int = 0
    trust_state: str = "candidate"
    parent_hypothesis_id: str = ""
    operator_note: str = ""
    safety: MarketRegimeHypothesisSafety = field(default_factory=MarketRegimeHypothesisSafety)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": MARKET_REGIME_HYPOTHESIS_CANDIDATE_SCHEMA_VERSION,
            "hypothesis_lane_version": MARKET_REGIME_HYPOTHESIS_LANE_VERSION,
            "artifact_family": "prediction/market_regime",
            "artifact_kind": "hypothesis_candidate",
            "prediction_family_id": "market_regime",
            "hypothesis_id": self.hypothesis_id,
            "created_at": self.created_at,
            "origin": self.origin,
            "title": self.title,
            "hypothesis_text": self.hypothesis_text,
            "target_regimes": list(self.target_regimes),
            "target_horizons": list(self.target_horizons),
            "evidence_refs": list(self.evidence_refs),
            "proposed_signal_changes": dict(self.proposed_signal_changes),
            "proposed_parameter_changes": dict(self.proposed_parameter_changes),
            "trust_rank": int(self.trust_rank),
            "trust_state": self.trust_state,
            "parent_hypothesis_id": self.parent_hypothesis_id,
            "operator_note": self.operator_note,
            "candidate_part_jsonl": hypothesis_candidate_part_relpath(self.created_at),
            "safety": self.safety.to_dict(),
        }


def build_market_regime_hypothesis_candidate(
    *,
    created_at: str,
    origin: str,
    title: str,
    hypothesis_text: str,
    target_regimes: Sequence[str] = (),
    target_horizons: Sequence[str] = (),
    evidence_refs: Sequence[str] = (),
    proposed_signal_changes: Mapping[str, Any] | None = None,
    proposed_parameter_changes: Mapping[str, Any] | None = None,
    trust_rank: int = 0,
    trust_state: str = "candidate",
    parent_hypothesis_id: str = "",
    operator_note: str = "",
) -> Dict[str, Any]:
    origin_norm = str(origin or "").strip().lower()
    if origin_norm not in _ALLOWED_ORIGINS:
        raise ValueError(f"unsupported hypothesis origin: {origin}")
    state_norm = str(trust_state or "candidate").strip().lower()
    if state_norm not in _ALLOWED_STATES:
        raise ValueError(f"unsupported hypothesis trust_state: {trust_state}")
    safe_signal_changes = dict(proposed_signal_changes or {})
    safe_parameter_changes = dict(proposed_parameter_changes or {})
    payload_for_raw_check = {
        "hypothesis_text": hypothesis_text,
        "proposed_signal_changes": safe_signal_changes,
        "proposed_parameter_changes": safe_parameter_changes,
    }
    if _has_forbidden_raw_keys(payload_for_raw_check):
        raise ValueError("hypothesis candidate contains forbidden raw market payload keys")
    hypothesis_id = f"mrhyp_{_hash_id(created_at, origin_norm, title, hypothesis_text)}"
    candidate = MarketRegimeHypothesisCandidate(
        hypothesis_id=hypothesis_id,
        created_at=str(created_at),
        origin=origin_norm,
        title=_bounded_text(title, limit=200),
        hypothesis_text=_bounded_text(hypothesis_text, limit=4000),
        target_regimes=tuple(str(item).upper() for item in target_regimes),
        target_horizons=tuple(str(item) for item in target_horizons),
        evidence_refs=tuple(str(item) for item in evidence_refs),
        proposed_signal_changes=safe_signal_changes,
        proposed_parameter_changes=safe_parameter_changes,
        trust_rank=max(-100, min(int(trust_rank), 100)),
        trust_state=state_norm,
        parent_hypothesis_id=str(parent_hypothesis_id or ""),
        operator_note=_bounded_text(operator_note, limit=1000),
    ).to_dict()
    validation = validate_market_regime_hypothesis_candidate(candidate)
    if not validation.get("ok"):
        raise ValueError(f"market-regime hypothesis candidate validation failed: {validation}")
    return candidate


def validate_market_regime_hypothesis_candidate(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    failures: list[str] = []
    if candidate.get("schema_version") != MARKET_REGIME_HYPOTHESIS_CANDIDATE_SCHEMA_VERSION:
        failures.append("schema_version_mismatch")
    if candidate.get("artifact_kind") != "hypothesis_candidate":
        failures.append("artifact_kind_mismatch")
    if candidate.get("prediction_family_id") != "market_regime":
        failures.append("prediction_family_id_mismatch")
    if candidate.get("origin") not in _ALLOWED_ORIGINS:
        failures.append("origin_invalid")
    if candidate.get("trust_state") not in _ALLOWED_STATES:
        failures.append("trust_state_invalid")
    if not candidate.get("hypothesis_id"):
        failures.append("hypothesis_id_missing")
    if not candidate.get("title"):
        failures.append("title_missing")
    if not candidate.get("hypothesis_text"):
        failures.append("hypothesis_text_missing")
    if _has_forbidden_raw_keys(candidate):
        failures.append("forbidden_raw_payload_key_present")
    safety = candidate.get("safety") if isinstance(candidate.get("safety"), Mapping) else {}
    for key in (
        "gpt_api_call_allowed",
        "classifier_auto_apply_allowed",
        "parameter_auto_promotion_allowed",
        "live_parameter_apply_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "would_send_to_broker",
    ):
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    if safety.get("evidence_only") is not True:
        failures.append("safety_evidence_only_not_true")
    return {
        "ok": not failures,
        "hypothesis_lane_version": MARKET_REGIME_HYPOTHESIS_LANE_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "hypothesis_id": str(candidate.get("hypothesis_id") or ""),
    }


def build_market_regime_hypothesis_trust_snapshot(
    *,
    candidates: Sequence[Mapping[str, Any]],
    calibration_summary: Mapping[str, Any] | None = None,
    generated_at: str,
) -> Dict[str, Any]:
    calibration_summary = dict(calibration_summary or {})
    overall_score = None
    overall = calibration_summary.get("overall") if isinstance(calibration_summary.get("overall"), Mapping) else {}
    if isinstance(overall.get("calibration_score"), int | float):
        overall_score = float(overall.get("calibration_score"))
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        validation = validate_market_regime_hypothesis_candidate(candidate)
        if not validation.get("ok"):
            continue
        base_rank = int(candidate.get("trust_rank") or 0)
        evidence_count = len(candidate.get("evidence_refs") or [])
        calibration_bonus = 0
        if overall_score is not None:
            calibration_bonus = 5 if overall_score >= 0.65 else -5 if overall_score < 0.35 else 0
        adjusted_rank = max(-100, min(100, base_rank + min(evidence_count, 5) + calibration_bonus))
        rows.append({
            "hypothesis_id": candidate.get("hypothesis_id"),
            "origin": candidate.get("origin"),
            "title": candidate.get("title"),
            "trust_state": candidate.get("trust_state"),
            "base_trust_rank": base_rank,
            "adjusted_trust_rank": adjusted_rank,
            "evidence_count": evidence_count,
            "calibration_score_used": overall_score,
            "candidate_part_jsonl": candidate.get("candidate_part_jsonl"),
            "auto_apply_allowed": False,
            "human_gate_required": True,
        })
    rows.sort(key=lambda item: int(item.get("adjusted_trust_rank") or 0), reverse=True)
    return {
        "schema_version": MARKET_REGIME_HYPOTHESIS_TRUST_SCHEMA_VERSION,
        "hypothesis_lane_version": MARKET_REGIME_HYPOTHESIS_LANE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "hypothesis_trust_snapshot",
        "prediction_family_id": "market_regime",
        "generated_at": generated_at,
        "candidate_count": len(rows),
        "candidates": rows,
        "calibration_summary_ref": str(calibration_summary.get("daily_summary_json") or calibration_summary.get("date") or ""),
        "safety": MarketRegimeHypothesisSafety().to_dict() | {"human_gate_required_for_apply": True},
    }


def append_market_regime_hypothesis_candidate_once(root: str | Path, candidate: Mapping[str, Any]) -> Dict[str, Any]:
    validation = validate_market_regime_hypothesis_candidate(candidate)
    if not validation.get("ok"):
        raise ValueError(f"market-regime hypothesis candidate validation failed: {validation}")
    base = Path(root)
    relpath = str(candidate.get("candidate_part_jsonl") or hypothesis_candidate_part_relpath(str(candidate.get("created_at") or "")))
    path = base / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(dict(candidate), ensure_ascii=False, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
    row_count = sum(1 for raw in path.read_text(encoding="utf-8").splitlines() if raw.strip())
    return {
        "ok": True,
        "hypothesis_lane_version": MARKET_REGIME_HYPOTHESIS_LANE_VERSION,
        "candidate_part_jsonl": relpath,
        "row_count": row_count,
        "bytes_appended": len(line.encode("utf-8")),
        "gpt_api_call_allowed": False,
        "classifier_auto_apply_allowed": False,
        "parameter_auto_promotion_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }


def write_market_regime_hypothesis_trust_snapshot(root: str | Path, snapshot: Mapping[str, Any]) -> Dict[str, Any]:
    base = Path(root)
    relpath = hypothesis_trust_latest_relpath()
    path = base / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(snapshot), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "hypothesis_lane_version": MARKET_REGIME_HYPOTHESIS_LANE_VERSION,
        "trust_latest_json": relpath,
        "candidate_count": int(snapshot.get("candidate_count") or 0),
        "auto_apply_allowed": False,
        "human_gate_required": True,
    }
