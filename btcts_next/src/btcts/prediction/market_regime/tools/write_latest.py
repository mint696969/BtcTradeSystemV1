# path: ./btcts_next/src/btcts/prediction/market_regime/tools/write_latest.py
# desc: Manual once-run writer for market-regime latest artifacts. Reads explicit root and atomically writes prediction/market_regime latest artifacts. No scheduler, UI import, broker, AutoTrade, or ledger append.

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.prediction.market_regime.artifact_contracts import (
    LATEST_CARDS_JSON_RELPATH,
    LATEST_JSON_RELPATH,
    LATEST_READ_MODEL_JSON_RELPATH,
    STATUS_JSON_RELPATH,
    MarketRegimeArtifactRefs,
    build_market_regime_latest_artifact,
    build_market_regime_latest_cards_artifact,
    build_market_regime_latest_read_model_artifact,
    build_market_regime_run_manifest_artifact,
    build_market_regime_status_artifact,
    validate_market_regime_latest_cards_artifact,
)
from btcts.prediction.market_regime.artifact_projection import (
    MARKET_REGIME_ARTIFACT_PROJECTION_VERSION,
    build_market_regime_cards_from_packet,
    build_market_regime_read_model_horizons,
    build_market_regime_read_model_summaries,
    build_market_regime_source_refs_from_snapshot,
)
from btcts.prediction.market_regime.features import build_market_regime_feature_bundle
from btcts.prediction.market_regime.signal_scoring import MARKET_REGIME_SIGNAL_SCORING_VERSION, score_market_regime_signals
from btcts.prediction.market_regime.inference import MARKET_REGIME_CLASSIFIER_VERSION, classify_market_regime_feature_bundle
from btcts.prediction.market_regime.parameter_set_registry import (
    MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION,
    build_default_market_regime_parameter_set_registry,
    validate_market_regime_parameter_set_registry,
)
from btcts.prediction.market_regime.sources import build_market_regime_source_snapshot

MARKET_REGIME_WRITE_LATEST_TOOL_VERSION = "prediction.market_regime.tools.write_latest.2026_07_08.v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_run_id(generated_at: str) -> str:
    compact = generated_at.replace("-", "").replace(":", "").replace(".", "").replace("Z", "Z")
    compact = compact.replace("T", "T")
    safe = "".join(ch for ch in compact if ch.isalnum() or ch in ("T", "Z", "_"))
    return f"market_regime_{safe}_once"


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _run_manifest_relpath(run_id: str) -> str:
    return f"prediction/market_regime/runs/{run_id}/manifest.json"


def _refs(run_id: str) -> MarketRegimeArtifactRefs:
    return MarketRegimeArtifactRefs(run_manifest_json=_run_manifest_relpath(run_id))


def build_market_regime_latest_artifact_set(*, hot_root: str | Path, generated_at: str, run_id: str | None = None) -> dict[str, Any]:
    root = Path(hot_root)
    effective_run_id = run_id or _safe_run_id(generated_at)
    parameter_set_registry = build_default_market_regime_parameter_set_registry()
    active_parameter_set = parameter_set_registry.active_parameter_set()
    parameter_set_registry_validation = validate_market_regime_parameter_set_registry(parameter_set_registry)
    if not parameter_set_registry_validation.get("ok"):
        raise ValueError(f"parameter-set registry validation failed: {parameter_set_registry_validation}")
    source_snapshot = build_market_regime_source_snapshot(root)
    feature_bundle = build_market_regime_feature_bundle(source_snapshot, generated_at=generated_at)
    prediction_packet = classify_market_regime_feature_bundle(feature_bundle, generated_at=generated_at)
    signal_score_report = score_market_regime_signals(feature_bundle)
    cards = build_market_regime_cards_from_packet(prediction_packet)
    source_refs = build_market_regime_source_refs_from_snapshot(source_snapshot)
    summaries = build_market_regime_read_model_summaries(prediction_packet)
    latest = build_market_regime_latest_artifact(packet=prediction_packet, run_id=effective_run_id)
    latest_cards = build_market_regime_latest_cards_artifact(
        generated_at=generated_at,
        run_id=effective_run_id,
        prediction_id=f"{effective_run_id}:latest",
        parameter_set_id=active_parameter_set.parameter_set_id,
        cards=cards,
        source_refs=source_refs,
        compact_summary={
            "tool_version": MARKET_REGIME_WRITE_LATEST_TOOL_VERSION,
            "projection_version": MARKET_REGIME_ARTIFACT_PROJECTION_VERSION,
            "classifier_version": MARKET_REGIME_CLASSIFIER_VERSION,
            "signal_scoring_version": MARKET_REGIME_SIGNAL_SCORING_VERSION,
            "signal_votes_available": bool(signal_score_report.get("total_vote_count")),
            "parameter_set_registry_version": MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION,
            "active_parameter_set_id": active_parameter_set.parameter_set_id,
            "parameter_set_registry_ok": bool(parameter_set_registry_validation.get("ok")),
            "source_snapshot_ok": source_snapshot.ok,
            "feature_bundle_available_signal_count": feature_bundle.available_signal_count(),
            "missing_sources": list(source_snapshot.missing_sources),
            "warnings": list(source_snapshot.warnings),
        },
    )
    validation = validate_market_regime_latest_cards_artifact(latest_cards)
    if not validation.get("ok"):
        raise ValueError(f"latest_cards validation failed: {validation}")
    read_model_horizons = build_market_regime_read_model_horizons(prediction_packet)
    signal_horizons = {str(row.get("horizon_key")): row for row in signal_score_report.get("horizons", []) if isinstance(row, Mapping)}
    for horizon_row in read_model_horizons:
        signal_row = signal_horizons.get(str(horizon_row.get("horizon_key")), {})
        horizon_row["signal_votes_top_n"] = list(signal_row.get("signal_votes_top_n", []))
        horizon_row["signal_conflicts_top_n"] = list(signal_row.get("signal_conflicts_top_n", []))
        horizon_row["source_family_scores"] = dict(signal_row.get("source_family_scores", {}))
        horizon_row["source_family_weights_used"] = dict(signal_row.get("source_family_weights_used", {}))
        horizon_row["regime_scores"] = dict(signal_row.get("regime_scores", {}))
        horizon_row["active_parameter_set_id"] = active_parameter_set.parameter_set_id
        horizon_row["parameter_set_registry_version"] = MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION
    source_summary = dict(summaries["source_contribution_summary"])
    source_summary["signal_score_report"] = signal_score_report
    source_summary["parameter_set_registry"] = parameter_set_registry.to_dict()
    source_summary["parameter_set_registry_validation"] = parameter_set_registry_validation
    source_summary["active_parameter_set"] = active_parameter_set.to_dict()
    latest_read_model = build_market_regime_latest_read_model_artifact(
        generated_at=generated_at,
        run_id=effective_run_id,
        horizons=read_model_horizons,
        source_contribution_summary=source_summary,
        conflict_summary=summaries["conflict_summary"],
        invalidation_summary=summaries["invalidation_summary"],
    )
    status = build_market_regime_status_artifact(generated_at=generated_at, status="latest_ready", latest_run_id=effective_run_id)
    manifest = build_market_regime_run_manifest_artifact(generated_at=generated_at, run_id=effective_run_id, refs=_refs(effective_run_id))
    return {
        "run_id": effective_run_id,
        "generated_at": generated_at,
        "latest": latest,
        "latest_cards": latest_cards,
        "latest_read_model": latest_read_model,
        "status": status,
        "manifest": manifest,
        "validation": validation,
        "source_snapshot_ok": source_snapshot.ok,
        "feature_bundle_available_signal_count": feature_bundle.available_signal_count(),
        "card_count": len(cards),
    }


def write_market_regime_latest_artifacts_once(*, hot_root: str | Path, generated_at: str | None = None, run_id: str | None = None) -> dict[str, Any]:
    root = Path(hot_root)
    effective_generated_at = generated_at or _utc_now_iso()
    artifacts = build_market_regime_latest_artifact_set(hot_root=root, generated_at=effective_generated_at, run_id=run_id)
    effective_run_id = str(artifacts["run_id"])
    rel_payloads = {
        LATEST_JSON_RELPATH: artifacts["latest"],
        LATEST_CARDS_JSON_RELPATH: artifacts["latest_cards"],
        LATEST_READ_MODEL_JSON_RELPATH: artifacts["latest_read_model"],
        STATUS_JSON_RELPATH: artifacts["status"],
        _run_manifest_relpath(effective_run_id): artifacts["manifest"],
    }
    written: list[str] = []
    for relpath, payload in rel_payloads.items():
        _write_json_atomic(root / relpath, payload)
        written.append(relpath)
    return {
        "ok": True,
        "tool_version": MARKET_REGIME_WRITE_LATEST_TOOL_VERSION,
        "hot_root": str(root),
        "run_id": effective_run_id,
        "generated_at": effective_generated_at,
        "written": written,
        "latest_cards_validation": artifacts["validation"],
        "source_snapshot_ok": bool(artifacts["source_snapshot_ok"]),
        "feature_bundle_available_signal_count": int(artifacts["feature_bundle_available_signal_count"]),
        "card_count": int(artifacts["card_count"]),
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "ledger_append_allowed": False,
        "would_send_to_broker": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write market-regime latest artifacts once from an explicit hot/fixture root.")
    parser.add_argument("--hot-root", required=True, help="Hot or fixture root containing source artifacts and receiving prediction/market_regime outputs.")
    parser.add_argument("--generated-at", default=None, help="UTC generation timestamp. Defaults to current UTC.")
    parser.add_argument("--run-id", default=None, help="Optional stable run id. Defaults to generated_at-derived id.")
    parser.add_argument("--once", action="store_true", help="Required safety acknowledgement for one-shot write.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.once:
        parser.error("--once is required; scheduler/producer loop is intentionally not available in this tool")
    result = write_market_regime_latest_artifacts_once(hot_root=args.hot_root, generated_at=args.generated_at, run_id=args.run_id)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
