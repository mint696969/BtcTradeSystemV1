# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_pair_writer.py
# desc: MR-F8.6 explicit-once append-only paired-trace writer with dedicated namespace, conflict detection, and post-write verification.

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from btcts.core.io import atomic_write_text, file_lock

MR_F8_PAIR_WRITER_VERSION = "prediction.market_regime.future_shadow_pair_writer.mr_f8_6.v1"
MR_F8_PAIR_NAMESPACE = "prediction/market_regime/mr_f8/shadow_pairs"


def _canonical_payload(pair: Mapping[str, Any]) -> dict[str, Any]:
    if pair.get("artifact_kind") != "future_shadow_candidate_pair":
        raise ValueError("mr_f8_pair_writer_pair_kind_invalid")
    pair_id = str(pair.get("pair_id") or "").strip()
    slot = pair.get("slot_identity")
    forecasts = pair.get("forecasts")
    trace_plan = pair.get("trace_plan")
    if not pair_id or not isinstance(slot, Mapping):
        raise ValueError("mr_f8_pair_writer_identity_missing")
    if not isinstance(forecasts, Sequence) or isinstance(forecasts, (str, bytes)) or len(forecasts) < 2:
        raise ValueError("mr_f8_pair_writer_forecasts_invalid")
    if not isinstance(trace_plan, Mapping):
        raise ValueError("mr_f8_pair_writer_trace_plan_missing")
    persistence = trace_plan.get("persistence_plan")
    if not isinstance(persistence, Mapping) or persistence.get("would_write") is not False:
        raise ValueError("mr_f8_pair_writer_trace_plan_safety_invalid")
    if trace_plan.get("trace_count") != len(forecasts):
        raise ValueError("mr_f8_pair_writer_trace_count_mismatch")

    trace_ids = tuple(str(item.get("trace_id") or "") for item in forecasts if isinstance(item, Mapping))
    parameter_sets = tuple(str(item.get("parameter_set_id") or "") for item in forecasts if isinstance(item, Mapping))
    if len(trace_ids) != len(forecasts) or any(not item for item in trace_ids):
        raise ValueError("mr_f8_pair_writer_trace_identity_invalid")
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("mr_f8_pair_writer_trace_duplicate")
    if len(parameter_sets) != len(forecasts) or any(not item for item in parameter_sets):
        raise ValueError("mr_f8_pair_writer_parameter_identity_invalid")
    if len(parameter_sets) != len(set(parameter_sets)):
        raise ValueError("mr_f8_pair_writer_parameter_duplicate")
    if tuple(sorted(trace_ids)) != tuple(sorted(str(item) for item in trace_plan.get("trace_ids", ()))):
        raise ValueError("mr_f8_pair_writer_trace_plan_identity_mismatch")
    if tuple(sorted(parameter_sets)) != tuple(sorted(str(item) for item in trace_plan.get("parameter_set_ids", ()))):
        raise ValueError("mr_f8_pair_writer_parameter_plan_identity_mismatch")

    origin = str(slot.get("origin_timestamp") or "").strip()
    if len(origin) < 10:
        raise ValueError("mr_f8_pair_writer_origin_invalid")
    return {
        "schema_version": MR_F8_PAIR_WRITER_VERSION,
        "artifact_kind": "mr_f8_shadow_pair_evidence",
        "pair_id": pair_id,
        "slot_identity": dict(slot),
        "candidate_count": int(pair.get("candidate_count") or 0),
        "candidate_identities": [dict(item) for item in pair.get("candidate_identities", ())],
        "forecasts": [dict(item) for item in forecasts],
        "trace_plan": {
            "schema_version": trace_plan.get("schema_version"),
            "trace_count": trace_plan.get("trace_count"),
            "trace_ids": list(trace_plan.get("trace_ids", ())),
            "parameter_set_ids": list(trace_plan.get("parameter_set_ids", ())),
            "persistence_plan": dict(persistence),
        },
        "safety": {
            "append_only": True,
            "canonical_replacement": False,
            "scheduler_enabled": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        },
    }


def _validate_canonical_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    canonical = dict(payload)
    if canonical.get("schema_version") != MR_F8_PAIR_WRITER_VERSION:
        raise ValueError("mr_f8_pair_writer_payload_schema_invalid")
    if canonical.get("artifact_kind") != "mr_f8_shadow_pair_evidence":
        raise ValueError("mr_f8_pair_writer_payload_kind_invalid")
    pair_id = str(canonical.get("pair_id") or "").strip()
    slot = canonical.get("slot_identity")
    forecasts = canonical.get("forecasts")
    trace_plan = canonical.get("trace_plan")
    safety = canonical.get("safety")
    if not pair_id or not isinstance(slot, Mapping):
        raise ValueError("mr_f8_pair_writer_payload_identity_missing")
    if not isinstance(forecasts, Sequence) or isinstance(forecasts, (str, bytes)) or len(forecasts) < 2:
        raise ValueError("mr_f8_pair_writer_payload_forecasts_invalid")
    if not isinstance(trace_plan, Mapping):
        raise ValueError("mr_f8_pair_writer_payload_trace_plan_invalid")
    persistence = trace_plan.get("persistence_plan")
    if not isinstance(persistence, Mapping) or persistence.get("would_write") is not False:
        raise ValueError("mr_f8_pair_writer_payload_trace_plan_safety_invalid")
    if trace_plan.get("trace_count") != len(forecasts):
        raise ValueError("mr_f8_pair_writer_payload_trace_count_mismatch")

    trace_ids = tuple(str(item.get("trace_id") or "") for item in forecasts if isinstance(item, Mapping))
    parameter_sets = tuple(str(item.get("parameter_set_id") or "") for item in forecasts if isinstance(item, Mapping))
    if len(trace_ids) != len(forecasts) or any(not item for item in trace_ids) or len(trace_ids) != len(set(trace_ids)):
        raise ValueError("mr_f8_pair_writer_payload_trace_identity_invalid")
    if len(parameter_sets) != len(forecasts) or any(not item for item in parameter_sets) or len(parameter_sets) != len(set(parameter_sets)):
        raise ValueError("mr_f8_pair_writer_payload_parameter_identity_invalid")
    if tuple(sorted(trace_ids)) != tuple(sorted(str(item) for item in trace_plan.get("trace_ids", ()))):
        raise ValueError("mr_f8_pair_writer_payload_trace_plan_identity_mismatch")
    if tuple(sorted(parameter_sets)) != tuple(sorted(str(item) for item in trace_plan.get("parameter_set_ids", ()))):
        raise ValueError("mr_f8_pair_writer_payload_parameter_plan_identity_mismatch")

    expected_safety = {
        "append_only": True,
        "canonical_replacement": False,
        "scheduler_enabled": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
    }
    if not isinstance(safety, Mapping) or any(safety.get(key) is not value for key, value in expected_safety.items()):
        raise ValueError("mr_f8_pair_writer_payload_safety_invalid")
    return json.loads(json.dumps(canonical, ensure_ascii=False, sort_keys=True))


def build_mr_f8_shadow_pair_write_plan(*, pair: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = _canonical_payload(pair)
    origin = str(payload["slot_identity"]["origin_timestamp"])
    digest = hashlib.sha256(str(payload["pair_id"]).encode("utf-8")).hexdigest()[:32]
    relpath = f"{MR_F8_PAIR_NAMESPACE}/date={origin[:10]}/pair-{digest}.json"
    return {
        "schema_version": MR_F8_PAIR_WRITER_VERSION,
        "artifact_kind": "mr_f8_shadow_pair_write_plan",
        "namespace": MR_F8_PAIR_NAMESPACE,
        "artifact_relpath": relpath,
        "payload": payload,
        "disabled_by_default": True,
        "once_ack_required": True,
        "explicit_write_ack_required": True,
        "would_write": False,
    }


def persist_mr_f8_shadow_pair_once(
    root: str | Path,
    *,
    plan: Mapping[str, Any],
    enabled: bool = False,
    once: bool = False,
    explicit_write_ack: bool = False,
) -> Mapping[str, Any]:
    if type(enabled) is not bool or type(once) is not bool or type(explicit_write_ack) is not bool:
        raise ValueError("mr_f8_pair_writer_flags_invalid")
    if enabled is not True:
        raise PermissionError("mr_f8_pair_writer_disabled_by_default")
    if once is not True:
        raise PermissionError("mr_f8_pair_writer_once_ack_required")
    if explicit_write_ack is not True:
        raise PermissionError("mr_f8_pair_writer_explicit_write_ack_required")
    if plan.get("schema_version") != MR_F8_PAIR_WRITER_VERSION:
        raise ValueError("mr_f8_pair_writer_plan_schema_invalid")
    if plan.get("artifact_kind") != "mr_f8_shadow_pair_write_plan":
        raise ValueError("mr_f8_pair_writer_plan_kind_invalid")
    if plan.get("namespace") != MR_F8_PAIR_NAMESPACE:
        raise ValueError("mr_f8_pair_writer_namespace_invalid")
    expected = {
        "disabled_by_default": True,
        "once_ack_required": True,
        "explicit_write_ack_required": True,
        "would_write": False,
    }
    if any(plan.get(key) is not value for key, value in expected.items()):
        raise ValueError("mr_f8_pair_writer_plan_safety_invalid")

    relpath = str(plan.get("artifact_relpath") or "")
    rel = Path(relpath)
    if rel.is_absolute() or ".." in rel.parts or "\\" in relpath or not relpath.startswith(MR_F8_PAIR_NAMESPACE + "/date="):
        raise ValueError("mr_f8_pair_writer_relpath_invalid")
    payload = plan.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("mr_f8_pair_writer_payload_invalid")
    canonical = _validate_canonical_payload(payload)

    root_path = Path(root).resolve()
    path = (root_path / rel).resolve()
    try:
        path.relative_to(root_path)
    except ValueError as exc:
        raise ValueError("mr_f8_pair_writer_path_escape") from exc
    text = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"

    with file_lock(path, timeout_sec=5.0, stale_sec=60.0):
        if path.exists():
            existing = path.read_text(encoding="utf-8-sig")
            if existing != text:
                raise RuntimeError("mr_f8_pair_writer_existing_conflict")
            parsed = json.loads(existing)
            if parsed != canonical:
                raise RuntimeError("mr_f8_pair_writer_existing_verify_failed")
            return {"written": False, "duplicate": True, "verified": True, "artifact_relpath": relpath}
        atomic_write_text(path, text)
        parsed = json.loads(path.read_text(encoding="utf-8-sig"))
        if parsed != canonical:
            raise RuntimeError("mr_f8_pair_writer_post_write_verify_failed")
    return {"written": True, "duplicate": False, "verified": True, "artifact_relpath": relpath}
