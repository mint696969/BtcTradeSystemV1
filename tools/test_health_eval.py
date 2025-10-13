# path: tools/test_health_eval.py
from pathlib import Path
from btc_trade_system.core.svc_health import evaluate
from btc_trade_system.common import paths

cfg_root = Path(__file__).resolve().parents[1] / "btc_trade_system"
status = paths.data_dir() / "collector" / "status.json"
summary = evaluate(status, cfg_root)
print("updated_at:", summary["updated_at"])
print("all_ok:", summary["all_ok"])
for it in summary["items"]:
    print(f"{it['exchange']}/{it['topic']}: {it['status']}  age={it['age_sec']:.1f}s  notes={it['notes']}")
