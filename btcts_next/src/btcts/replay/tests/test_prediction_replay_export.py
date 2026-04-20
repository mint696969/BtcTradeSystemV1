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
                        "parameter_trace": {
                            "profile_kind": "candidate",
                        }
                    },
                }
            ],
            tactic_review_records=[
                {
                    "review_type": "tactic_review_record",
                    "selected_tactic_key": "cautious_probe",
                    "decision_state": "proposed",
                    "rollback_target_ref": "baseline-default",
                }
            ],
            tactic_operation_records=[
                {
                    "operation_type": "tactic_operation_record",
                    "operation_state": "propose",
                    "selected_tactic_key": "cautious_probe",
                    "rollback_target_ref": "baseline-default",
                }
            ],
        )

        assert exported["session_dir"]
        assert exported["results_path"]
        assert exported["report_path"]
        assert exported["manifest_path"]
        assert exported["prediction_evaluation_report_path"]
        assert exported["prediction_calibration_review_path"]
        assert exported["tactic_proposal_output_path"]
        assert exported["tactic_review_record_path"]
        assert exported["tactic_operation_record_path"]

        manifest = _read_json(exported["manifest_path"])
        assert manifest["name"] == "prediction_eval_export"
        assert manifest["result_count"] == 2
        assert manifest["prediction_evaluation_entry_count"] == 1
        assert manifest["prediction_evaluation_report_path"]
        assert manifest["prediction_calibration_review_count"] == 1
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
        assert replay_report["tactic_proposal_summary"] == {
            "proposal_count": 1,
            "latest_primary_tactic_key": "cautious_probe",
            "latest_proposal_state": "proposed",
            "latest_scenario_regime": "continuation",
            "latest_profile_kind": "candidate",
        }
        assert replay_report["tactic_review_record_summary"] == {
            "review_count": 1,
            "latest_selected_tactic_key": "cautious_probe",
            "latest_decision_state": "proposed",
            "latest_rollback_target_ref": "baseline-default",
        }
        assert replay_report["tactic_operation_record_summary"] == {
            "operation_count": 1,
            "latest_operation_state": "propose",
            "latest_selected_tactic_key": "cautious_probe",
            "latest_rollback_target_ref": "baseline-default",
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
        assert replay_report["tactic_proposal_summary"] is None
        assert replay_report["tactic_review_record_summary"] is None
        assert replay_report["tactic_operation_record_summary"] is None

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())