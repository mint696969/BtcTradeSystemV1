# path: ./tools/sample_phase4a_prediction_system_ps_q20j_disabled_helper_real_data_dry_run_sample.py
# desc: PS-Q20J sample-only real-data dry-run for the disabled explicit read-only loader binding helper. Reads bounded hot inputs and writes no artifacts.

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from btcts.apps.operator_ui.components.prediction_warroom_preferred_row_adapter import (  # noqa: E402
    build_prediction_warroom_preferred_row_adapter,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.explicit_read_only_loader_binding_helper import (  # noqa: E402
    build_explicit_read_only_loader_binding_helper,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    build_latest_prediction_warroom_read_model,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.preferred_row_observation_section import (  # noqa: E402
    PREFERRED_ROW_OBSERVATION_SECTION_KEY,
)
from btcts.market_engine.market_state.consumer_integration_design import LANE_WARROOM_READ  # noqa: E402

SAMPLE_VERSION = "prediction_warroom.disabled_helper_real_data_dry_run_sample.ps_q20j.v1"
DEFAULT_DATA_ROOT = Path(os.environ.get("BTC_TS_HOT_ROOT", r"D:\btc_ts_hot"))
DEFAULT_PREDICTION_RELATIVE_PATH = Path("prediction/latest_prediction_system_result.json")
DEFAULT_MARKET_OVERVIEW_GLOB = "data/market_state/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.overview/date=*/part-*.jsonl"
DEFAULT_TAIL_ROWS = 200
DEFAULT_TAIL_BYTES = 4_000_000
DEFAULT_MAX_PREDICTION_BYTES = 12_000_000


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _resolve_under_root(data_root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    resolved = candidate if candidate.is_absolute() else data_root / candidate
    resolved = resolved.resolve()
    root = data_root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path is outside data root: {resolved}") from exc
    return resolved


def _load_json(path: Path, *, max_bytes: int) -> Mapping[str, Any]:
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"json input too large: {path} bytes={size} max_bytes={max_bytes}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, Mapping):
        raise ValueError(f"json input is not an object: {path}")
    return data


def _tail_lines(path: Path, *, max_lines: int, max_bytes: int) -> list[str]:
    if max_lines <= 0:
        return []
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        read_size = min(size, max(1, int(max_bytes)))
        handle.seek(max(0, size - read_size))
        chunk = handle.read(read_size)
    text = chunk.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > 1 and not text.startswith("{"):
        lines = lines[1:]
    return lines[-max_lines:]


def _load_tail_jsonl(path: Path, *, max_rows: int, max_bytes: int) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    for line in _tail_lines(path, max_lines=max_rows, max_bytes=max_bytes):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(value, Mapping):
            rows.append(value)
    return rows[-max_rows:]


def _latest_market_overview_path(data_root: Path) -> Path:
    candidates = sorted(data_root.glob(DEFAULT_MARKET_OVERVIEW_GLOB), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"market overview input not found under {data_root}")
    return candidates[-1]


def _latest_market_row(rows: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    values = [row for row in rows if isinstance(row, Mapping)]
    return values[-1] if values else {}


def build_disabled_helper_real_data_dry_run_sample(
    *,
    prediction_payload: Mapping[str, Any],
    market_overview_rows: list[Mapping[str, Any]],
    prediction_path: str,
    market_overview_path: str,
    enable_explicit_read_only_loader_binding: bool = False,
    now_utc: str | None = None,
) -> dict[str, Any]:
    """Build a sample-only dry-run packet from already loaded real-data inputs.

    This function performs no IO and writes no artifacts. File reading is isolated to the
    CLI wrapper, and runtime loaders are never invoked.
    """

    market_row = _latest_market_row(market_overview_rows)
    read_model = build_latest_prediction_warroom_read_model(
        payload=prediction_payload,
        market_state=market_row,
        market_diag={},
        source_path=prediction_path,
        now_utc=now_utc,
    )
    adapter = build_prediction_warroom_preferred_row_adapter(market_overview_rows, lane=LANE_WARROOM_READ).to_dict()
    helper = build_explicit_read_only_loader_binding_helper(
        read_model=read_model,
        preferred_row_adapter_packet=adapter,
        enable_explicit_read_only_loader_binding=enable_explicit_read_only_loader_binding,
    ).to_dict()
    output_model = _as_mapping(helper.get("output_read_model"))
    selected_row = _as_mapping(adapter.get("selected_row"))

    dry_run_ready = helper.get("dry_run_ready") is True
    sample_state = "disabled_helper_real_data_dry_run_sample_ready" if dry_run_ready else "disabled_helper_real_data_dry_run_sample_observe_only"
    return {
        "ok": bool(dry_run_ready),
        "sample_version": SAMPLE_VERSION,
        "sample_state": sample_state,
        "sample_only": True,
        "hot_data_read_only": True,
        "stdout_only": True,
        "prediction_path": prediction_path,
        "market_overview_path": market_overview_path,
        "market_overview_tail_row_count": len(market_overview_rows),
        "read_model_ok": read_model.get("ok") is True,
        "read_model_state": read_model.get("read_model_state"),
        "read_model_version": read_model.get("read_model_version"),
        "adapter_state": adapter.get("adapter_state"),
        "adapter_allowed_for_requested_lane": adapter.get("allowed_for_requested_lane") is True,
        "adapter_selected_row_available": isinstance(adapter.get("selected_row"), Mapping),
        "adapter_consumer_preferred_count": adapter.get("consumer_preferred_count"),
        "adapter_diagnostic_transition_count": adapter.get("diagnostic_transition_count"),
        "selected_row_summary": {
            "collector_ts": selected_row.get("collector_ts"),
            "trust_state": selected_row.get("trust_state"),
            "interpretation_bucket": selected_row.get("interpretation_bucket"),
            "semantic_observer_status": selected_row.get("semantic_observer_status"),
            "best_bid": selected_row.get("best_bid"),
            "best_ask": selected_row.get("best_ask"),
            "spread": selected_row.get("spread"),
            "source_series_id": selected_row.get("source_series_id"),
        },
        "helper_state": helper.get("helper_state"),
        "helper_disabled_by_default": helper.get("disabled_by_default") is True,
        "enable_explicit_read_only_loader_binding": helper.get("enable_explicit_read_only_loader_binding") is True,
        "dry_run_ready": dry_run_ready,
        "optional_section_attached": helper.get("optional_section_attached") is True,
        "output_model_has_optional_section": PREFERRED_ROW_OBSERVATION_SECTION_KEY in output_model,
        "target_loader_invoked": False,
        "runtime_loader_invoked": False,
        "latest_prediction_warroom_read_model_loader_changed": False,
        "existing_market_snapshot_replaced": False,
        "existing_market_state_service_changed": False,
        "existing_warroom_runtime_rewired": False,
        "component_runtime_binding_allowed": False,
        "ui_code_changed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "runtime_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "would_write_warroom_view_artifact": False,
        "ps_q19r_scoring_policy_changed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "blocked_reasons": helper.get("blocked_reasons", []),
        "warning_reasons": helper.get("warning_reasons", []),
    }


def run_disabled_helper_real_data_dry_run_sample(
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
    prediction_path: str | Path = DEFAULT_PREDICTION_RELATIVE_PATH,
    market_overview_path: str | Path | None = None,
    tail_rows: int = DEFAULT_TAIL_ROWS,
    tail_bytes: int = DEFAULT_TAIL_BYTES,
    max_prediction_bytes: int = DEFAULT_MAX_PREDICTION_BYTES,
    enable_explicit_read_only_loader_binding: bool = False,
    now_utc: str | None = None,
) -> dict[str, Any]:
    root = data_root.resolve()
    prediction = _resolve_under_root(root, prediction_path)
    overview = _resolve_under_root(root, market_overview_path) if market_overview_path else _latest_market_overview_path(root)
    payload = _load_json(prediction, max_bytes=max_prediction_bytes)
    rows = _load_tail_jsonl(overview, max_rows=max(1, int(tail_rows)), max_bytes=max(1, int(tail_bytes)))
    return build_disabled_helper_real_data_dry_run_sample(
        prediction_payload=payload,
        market_overview_rows=rows,
        prediction_path=str(prediction),
        market_overview_path=str(overview),
        enable_explicit_read_only_loader_binding=enable_explicit_read_only_loader_binding,
        now_utc=now_utc,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q20J disabled helper real-data dry-run sample. Writes no artifacts.")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--prediction-path", default=str(DEFAULT_PREDICTION_RELATIVE_PATH))
    parser.add_argument("--market-overview-path", default=None)
    parser.add_argument("--tail-rows", type=int, default=DEFAULT_TAIL_ROWS)
    parser.add_argument("--tail-bytes", type=int, default=DEFAULT_TAIL_BYTES)
    parser.add_argument("--max-prediction-bytes", type=int, default=DEFAULT_MAX_PREDICTION_BYTES)
    parser.add_argument("--now-utc", default=None)
    parser.add_argument("--enable-explicit-read-only-loader-binding", action="store_true")
    args = parser.parse_args(argv)

    result = run_disabled_helper_real_data_dry_run_sample(
        data_root=Path(args.data_root),
        prediction_path=args.prediction_path,
        market_overview_path=args.market_overview_path,
        tail_rows=args.tail_rows,
        tail_bytes=args.tail_bytes,
        max_prediction_bytes=args.max_prediction_bytes,
        enable_explicit_read_only_loader_binding=args.enable_explicit_read_only_loader_binding,
        now_utc=args.now_utc,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
