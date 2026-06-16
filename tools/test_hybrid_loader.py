# path: ./tools/test_hybrid_loader.py
# desc: Minimal probe for hybrid loader source resolution.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from pathlib import Path

from btcts.core.hybrid_loader import resolve_single_date_hybrid_sources


def main() -> None:
    parser = argparse.ArgumentParser(description="Test hybrid loader source resolution.")
    parser.add_argument("--cold-root", default=r"E:\btc_ts\data")
    parser.add_argument("--hot-root", default=r"D:\btc_ts_hot\data")
    parser.add_argument("--relative-prefix", required=True)
    parser.add_argument("--date", required=True)
    args = parser.parse_args()

    plan = resolve_single_date_hybrid_sources(
        cold_root=Path(args.cold_root),
        hot_root=Path(args.hot_root),
        relative_prefix=args.relative_prefix,
        date_str=args.date,
    )

    print(
        json.dumps(
            {
                "relative_prefix": plan.relative_prefix,
                "dates": plan.dates,
                "cold_count": len(plan.cold_files),
                "hot_tail_count": len(plan.hot_tail_files),
                "ordered_count": len(plan.ordered_files),
                "cold_sample": [str(p) for p in plan.cold_files[:10]],
                "hot_tail_sample": [str(p) for p in plan.hot_tail_files[:10]],
                "ordered_sample": [str(p) for p in plan.ordered_files[:10]],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()