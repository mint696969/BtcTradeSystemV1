# path: ./btcts_next/src/btcts/prediction/market_regime/tools/shadow_pair_write_once.py
# desc: MR-F8.6 explicit-once CLI for dry-run or guarded append-only persistence of one preflighted shadow pair.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from btcts.prediction.market_regime.future_shadow_pair_writer import (
    build_mr_f8_shadow_pair_write_plan,
    persist_mr_f8_shadow_pair_once,
)

MR_F8_SHADOW_PAIR_WRITE_ONCE_TOOL_VERSION = (
    "prediction.market_regime.tools.shadow_pair_write_once.mr_f8_6.v1"
)
DEFAULT_HOT_ROOT = Path("D:/btc_ts_hot")
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _select_pair(report: Any, pair_index: int) -> Mapping[str, Any]:
    if not isinstance(report, Mapping):
        raise ValueError("mr_f8_write_once_report_invalid")
    if report.get("schema_version") != "market_regime_shadow_pair_once_report.mr_f8_6.v1":
        raise ValueError("mr_f8_write_once_report_schema_invalid")
    if report.get("ok") is not True:
        raise ValueError("mr_f8_write_once_report_not_ok")
    pairs = report.get("pairs")
    if not isinstance(pairs, Sequence) or isinstance(pairs, (str, bytes)):
        raise ValueError("mr_f8_write_once_pairs_invalid")
    if pair_index < 0 or pair_index >= len(pairs):
        raise ValueError("mr_f8_write_once_pair_index_invalid")
    pair = pairs[pair_index]
    if not isinstance(pair, Mapping):
        raise ValueError("mr_f8_write_once_pair_invalid")
    return pair


def classify_output_root(
    output_root: str | Path,
    *,
    repository_root: str | Path = REPOSITORY_ROOT,
    hot_root: str | Path = DEFAULT_HOT_ROOT,
) -> str:
    resolved = Path(output_root).resolve()
    repo_tmp = (Path(repository_root).resolve() / "tmp").resolve()
    hot = Path(hot_root).resolve()
    try:
        resolved.relative_to(repo_tmp)
        return "repo_tmp"
    except ValueError:
        pass
    if resolved == hot:
        return "d_hot"
    raise ValueError("mr_f8_write_once_output_root_not_allowed")


def execute_shadow_pair_write_once(
    *,
    preflight_report: Any,
    pair_index: int,
    output_root: str | Path,
    write: bool = False,
    once: bool = False,
    explicit_write_ack: bool = False,
    allow_dhot_write: bool = False,
    repository_root: str | Path = REPOSITORY_ROOT,
    hot_root: str | Path = DEFAULT_HOT_ROOT,
) -> Mapping[str, Any]:
    if any(type(value) is not bool for value in (write, once, explicit_write_ack, allow_dhot_write)):
        raise ValueError("mr_f8_write_once_flags_invalid")
    pair = _select_pair(preflight_report, pair_index)
    plan = build_mr_f8_shadow_pair_write_plan(pair=pair)
    root_kind = classify_output_root(
        output_root,
        repository_root=repository_root,
        hot_root=hot_root,
    )
    if root_kind == "d_hot" and allow_dhot_write is not True:
        raise PermissionError("mr_f8_write_once_dhot_ack_required")

    base = {
        "schema_version": MR_F8_SHADOW_PAIR_WRITE_ONCE_TOOL_VERSION,
        "artifact_kind": "mr_f8_shadow_pair_write_once_result",
        "pair_id": pair.get("pair_id"),
        "pair_index": pair_index,
        "output_root_kind": root_kind,
        "artifact_relpath": plan.get("artifact_relpath"),
        "write_requested": write,
        "dhot_write_acknowledged": allow_dhot_write,
        "scheduler_enabled": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
    }
    if write is not True:
        return {
            **base,
            "dry_run": True,
            "written": False,
            "duplicate": False,
            "verified": True,
        }

    result = persist_mr_f8_shadow_pair_once(
        output_root,
        plan=plan,
        enabled=True,
        once=once,
        explicit_write_ack=explicit_write_ack,
    )
    return {**base, "dry_run": False, **dict(result)}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dry-run or explicitly persist one MR-F8 preflighted shadow pair."
    )
    parser.add_argument("--preflight-json", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--pair-index", type=int, default=0)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--explicit-write-ack", action="store_true")
    parser.add_argument("--allow-dhot-write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    result = execute_shadow_pair_write_once(
        preflight_report=_load_json(args.preflight_json),
        pair_index=args.pair_index,
        output_root=args.output_root,
        write=args.write,
        once=args.once,
        explicit_write_ack=args.explicit_write_ack,
        allow_dhot_write=args.allow_dhot_write,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
