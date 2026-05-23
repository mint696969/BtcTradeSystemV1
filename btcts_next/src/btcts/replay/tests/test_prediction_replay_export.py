# path: ./btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py
# desc: Verify replay export can add prediction evaluation aggregate artifacts without disturbing base replay export.

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.replay.replay_export import export_replay_results  # noqa: E402


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_dir:
        exported = export_replay_results(
            name="prediction_eval_export",
            source_paths=[Path("D:/dummy/source_a.jsonl")],
            results=[
                {"kind": "board", "result": {"signal": "watch", "events": []}},
                {"kind": "trade", "microstructure": []},
            ],
            out_root=Path(tmp_dir),
            prediction_evaluation_entries=[
                {
                    "regime_alignment": "partial",
                    "replay_priority": "high",
                    "confidence_gap": -0.18,
                    "caution_gap": 2,
                    "confidence_gap_signal": "overstated_confidence",
                    "confidence_bias_hint": "balanced",
                    "caution_bias_hint": "balanced",
                }
            ],
            prediction_calibration_reviews=[
                {
                    "review_type": "prediction_calibration_review",
                    "review_priority": "high",
                    "primary_focus": "confidence_downside_review",
                    "confidence_review": "lower_confidence_weight",
                    "caution_review": "raise_caution_weight",
                    "invalidation_review": "raise_invalidation_sensitivity",
                }
            ],
            tactic_proposal_outputs=[
                {
                    "proposal_type": "scenario_tactic_proposal_output",
                    "primary_tactic_key": "cautious_probe",
                    "proposal_state": "proposed",
                    "scenario_regime": "continuation",
                    "diagnostics": {
                        "adoption_ready": True,
                        "selected_set_id": "candidate-cautious-probe",
                        "parameter_trace": {
                            "profile_kind": "candidate",
                            "rollback_target_ref": "baseline-default",
                            "comparison_profile_kinds": (
                                "baseline",
                                "candidate",
                            ),
                            "comparison_active_index": 1,
                            "comparison_baseline_available": True,
                            "comparison_relation": "candidate_vs_baseline",
                            "overlay_influence": "overlay_bias",
                        },
                        "selection_trace": {
                            "overlay_application_mode": "primary_only",
                        },
                    },
                }
            ],
            tactic_review_records=[
                {
                    "review_type": "tactic_review_record",
                    "selected_tactic_key": "cautious_probe",
                    "decision_state": "proposed",
                    "rollback_target_ref": "baseline-default",
                    "selection_trace": {
                        "overlay_application_mode": "support_only",
                    },
                    "parameter_trace": {
                        "comparison_profile_kinds": (
                            "baseline",
                            "candidate",
                        ),
                        "comparison_active_index": 1,
                        "comparison_baseline_available": True,
                        "comparison_relation": "candidate_vs_baseline",
                        "overlay_influence": "none",
                    },
                    "diagnostics": {
                        "adoption_ready": True,
                        "selected_set_id": "candidate-cautious-probe",
                        "comparison_ref_count": 2,
                    },
                }
            ],
            prediction_direction_snapshots=[
                {
                    "prediction_type": "direction",
                    "prediction_version": "phase4a.direction.v1",
                    "source_kind": "replay_artifact_only",
                    "market_uid": "bitflyer.spot.BTC_JPY",
                    "event_ts": "2026-05-23T00:00:00Z",
                    "scenario_ref": "replay.scenario.test",
                    "primary_direction_bias": "continuation",
                    "horizon_direction_readings": [
                        {"horizon": "5m", "caution_flag": False},
                        {"horizon": "10m", "caution_flag": True},
                    ],
                    "evidence_trace_refs": ["scenario:continuation"],
                    "diagnostics": {
                        "artifact_only": True,
                        "diagnostic_quality": {
                            "quality_version": "phase4a.direction_artifact_diagnostics.v1",
                            "scenario_ref_present": True,
                            "market_uid_present": True,
                            "event_ts_present": True,
                            "scenario_regime_bias_present": True,
                            "artifact_only_marker_present": True,
                            "read_only_marker_present": True,
                            "runtime_wiring_closed": True,
                            "ui_wiring_closed": True,
                            "market_engine_wiring_closed": True,
                        },
                    },
                    "read_only_contract": True,
                    "not_runtime_wiring": True,
                    "not_ui_wiring": True,
                }
            ],
            tactic_operation_records=[
                {
                    "operation_type": "tactic_operation_record",
                    "operation_state": "propose",
                    "selected_tactic_key": "cautious_probe",
                    "rollback_target_ref": "baseline-default",
                    "selection_trace": {
                        "overlay_application_mode": "support_only",
                    },
                    "parameter_trace": {
                        "comparison_profile_kinds": (
                            "baseline",
                            "candidate",
                        ),
                        "comparison_active_index": 1,
                        "comparison_baseline_available": True,
                        "comparison_relation": "candidate_vs_baseline",
                        "overlay_influence": "none",
                    },
                    "diagnostics": {
                        "adoption_ready": True,
                        "selected_set_id": "candidate-cautious-probe",
                        "comparison_ref_count": 2,
                    },
                }
            ],
        )

        assert exported["session_dir"]
        assert exported["results_path"]
        assert exported["report_path"]
        assert exported["manifest_path"]
        assert exported["prediction_evaluation_report_path"]
        assert exported["prediction_calibration_review_path"]
        assert exported["prediction_direction_snapshot_path"]
        assert exported["tactic_proposal_output_path"]
        assert exported["tactic_review_record_path"]
        assert exported["tactic_operation_record_path"]

        manifest = _read_json(exported["manifest_path"])
        assert manifest["name"] == "prediction_eval_export"
        assert manifest["result_count"] == 2
        assert manifest["prediction_evaluation_entry_count"] == 1
        assert manifest["prediction_evaluation_report_path"]
        assert manifest["prediction_calibration_review_count"] == 1
        assert manifest["prediction_direction_snapshot_count"] == 1
        assert manifest["prediction_direction_snapshot_path"]
        assert manifest["prediction_calibration_review_path"]
        assert manifest["tactic_proposal_output_count"] == 1
        assert manifest["tactic_proposal_output_path"]
        assert manifest["tactic_review_record_count"] == 1
        assert manifest["tactic_review_record_path"]
        assert manifest["tactic_operation_record_count"] == 1
        assert manifest["tactic_operation_record_path"]

        prediction_report = _read_json(exported["prediction_evaluation_report_path"])
        assert prediction_report["name"] == "prediction_eval_export_prediction_evaluation"
        assert prediction_report["entry_type"] == "prediction_evaluation_report"
        assert prediction_report["entry_count"] == 1
        assert prediction_report["partial_count"] == 1
        assert prediction_report["high_priority_count"] == 1
        assert prediction_report["average_confidence_gap"] == -0.18
        assert prediction_report["average_caution_gap"] == 2.0

        calibration_review = _read_json(exported["prediction_calibration_review_path"])
        assert calibration_review["review_type"] == "prediction_calibration_review"
        assert calibration_review["review_priority"] == "high"
        assert calibration_review["primary_focus"] == "confidence_downside_review"

        replay_report = _read_json(exported["report_path"])
        assert replay_report["prediction_evaluation_summary"] == {
            "entry_count": 1,
            "matched_count": 0,
            "partial_count": 1,
            "missed_count": 0,
            "high_priority_count": 1,
            "average_confidence_gap": -0.18,
            "average_caution_gap": 2.0,
        }
        assert replay_report["prediction_calibration_review_summary"] == {
            "review_count": 1,
            "latest_review_priority": "high",
            "latest_primary_focus": "confidence_downside_review",
            "latest_confidence_review": "lower_confidence_weight",
            "latest_caution_review": "raise_caution_weight",
            "latest_invalidation_review": "raise_invalidation_sensitivity",
        }
        assert replay_report["prediction_direction_summary"] == {
            "snapshot_count": 1,
            "latest_prediction_type": "direction",
            "latest_source_kind": "replay_artifact_only",
            "latest_market_uid": "bitflyer.spot.BTC_JPY",
            "latest_event_ts": "2026-05-23T00:00:00Z",
            "latest_scenario_ref": "replay.scenario.test",
            "latest_primary_direction_bias": "continuation",
            "latest_horizon_count": 2,
            "latest_horizons": ["5m", "10m"],
            "latest_caution_horizon_count": 1,
            "latest_evidence_trace_ref_count": 1,
            "latest_artifact_only": True,
            "latest_read_only_contract": True,
            "latest_not_runtime_wiring": True,
            "latest_not_ui_wiring": True,
            "latest_diagnostic_quality_version": (
                "phase4a.direction_artifact_diagnostics.v1"
            ),
            "latest_diagnostic_quality_passed_count": 9,
            "latest_diagnostic_quality_required_count": 9,
            "latest_diagnostic_quality_ok": True,
        }
        assert replay_report["direction_replay_calibration_review_material"] == {
            "material_type": "direction_replay_calibration_review_material",
            "material_version": "phase4a.direction_replay_calibration_review.v1",
            "source_kind": "replay_report_prediction_direction_summary",
            "review_only": True,
            "read_only_contract": True,
            "not_runtime_wiring": True,
            "not_ui_wiring": True,
            "not_market_engine_wiring": True,
            "snapshot_count": 1,
            "latest_primary_direction_bias": "continuation",
            "latest_horizon_count": 2,
            "latest_caution_horizon_count": 1,
            "latest_evidence_trace_ref_count": 1,
            "latest_diagnostic_quality_ok": True,
            "review_priority": "medium",
            "review_flags": ["caution_horizon_review"],
        }
        assert replay_report["tactic_proposal_summary"] == {
            "proposal_count": 1,
            "latest_primary_tactic_key": "cautious_probe",
            "latest_proposal_state": "proposed",
            "latest_scenario_regime": "continuation",
            "latest_profile_kind": "candidate",
            "latest_adoption_ready": True,
            "latest_selected_set_id": "candidate-cautious-probe",
            "latest_rollback_target_ref": "baseline-default",
            "latest_comparison_profile_kinds": [
                "baseline",
                "candidate",
            ],
            "latest_comparison_active_index": 1,
            "latest_comparison_baseline_available": True,
            "latest_comparison_relation": "candidate_vs_baseline",
            "latest_overlay_influence": "overlay_bias",
            "latest_overlay_application_mode": "primary_only",
            "latest_compare_friendly_summary_line": (
                "cautious_probe | "
                "candidate_vs_baseline | "
                "overlay_bias_present | "
                "overlay_primary | "
                "selected_set=candidate-cautious-probe | "
                "rollback_target=baseline-default | "
                "adoption_ready_for_review | "
                "review_only"
            ),
        }
        assert replay_report["tactic_review_record_summary"] == {
            "review_count": 1,
            "latest_selected_tactic_key": "cautious_probe",
            "latest_decision_state": "proposed",
            "latest_rollback_target_ref": "baseline-default",
            "latest_adoption_ready": True,
            "latest_selected_set_id": "candidate-cautious-probe",
            "latest_comparison_ref_count": 2,
            "latest_comparison_profile_kinds": [
                "baseline",
                "candidate",
            ],
            "latest_comparison_active_index": 1,
            "latest_comparison_baseline_available": True,
            "latest_comparison_relation": "candidate_vs_baseline",
            "latest_overlay_influence": "none",
            "latest_overlay_application_mode": "support_only",
            "latest_compare_friendly_summary_line": (
                "cautious_probe | "
                "candidate_vs_baseline | "
                "overlay_support_only | "
                "selected_set=candidate-cautious-probe | "
                "rollback_target=baseline-default | "
                "adoption_ready_for_review | "
                "review_only"
            ),
        }
        assert replay_report["tactic_operation_record_summary"] == {
            "operation_count": 1,
            "latest_operation_state": "propose",
            "latest_selected_tactic_key": "cautious_probe",
            "latest_rollback_target_ref": "baseline-default",
            "latest_adoption_ready": True,
            "latest_selected_set_id": "candidate-cautious-probe",
            "latest_comparison_ref_count": 2,
            "latest_comparison_profile_kinds": [
                "baseline",
                "candidate",
            ],
            "latest_comparison_active_index": 1,
            "latest_comparison_baseline_available": True,
            "latest_comparison_relation": "candidate_vs_baseline",
            "latest_overlay_influence": "none",
            "latest_overlay_application_mode": "support_only",
            "latest_compare_friendly_summary_line": (
                "cautious_probe | "
                "candidate_vs_baseline | "
                "overlay_support_only | "
                "selected_set=candidate-cautious-probe | "
                "rollback_target=baseline-default | "
                "adoption_ready_for_review | "
                "review_only"
            ),
        }

    with tempfile.TemporaryDirectory() as tmp_dir:
        exported = export_replay_results(
            name="prediction_eval_export_empty",
            source_paths=[Path("D:/dummy/source_b.jsonl")],
            results=[],
            out_root=Path(tmp_dir),
        )

        manifest = _read_json(exported["manifest_path"])
        assert manifest["prediction_evaluation_entry_count"] == 0
        assert manifest["prediction_evaluation_report_path"] is None
        assert exported["prediction_evaluation_report_path"] is None
        assert manifest["prediction_calibration_review_count"] == 0
        assert manifest["prediction_calibration_review_path"] is None
        assert exported["prediction_calibration_review_path"] is None
        assert manifest["tactic_proposal_output_count"] == 0
        assert manifest["tactic_proposal_output_path"] is None
        assert exported["tactic_proposal_output_path"] is None
        assert manifest["tactic_review_record_count"] == 0
        assert manifest["tactic_review_record_path"] is None
        assert exported["tactic_review_record_path"] is None
        assert manifest["tactic_operation_record_count"] == 0
        assert manifest["tactic_operation_record_path"] is None
        assert exported["tactic_operation_record_path"] is None

        replay_report = _read_json(exported["report_path"])
        assert replay_report["prediction_evaluation_summary"] is None
        assert replay_report["prediction_calibration_review_summary"] is None
        assert replay_report["prediction_direction_summary"] is None
        assert replay_report["direction_replay_calibration_review_material"] is None
        assert replay_report["tactic_proposal_summary"] is None
        assert replay_report["tactic_review_record_summary"] is None
        assert replay_report["tactic_operation_record_summary"] is None

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())