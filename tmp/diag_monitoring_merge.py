# path: ./tmp/diag_monitoring_merge.py
# desc: monitoring.yaml と monitoring_def.yaml のマージ結果を表示（読み取りのみ・無改変）
import json, yaml, pathlib
base = pathlib.Path("btc_trade_system/config/ui")
cur = yaml.safe_load((base/"monitoring.yaml").read_text(encoding="utf-8"))
default = yaml.safe_load((base/"monitoring_def.yaml").read_text(encoding="utf-8"))
def deep_merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return {k: deep_merge(a.get(k), b.get(k)) for k in set(a)|set(b)}
    return a if a is not None else b
effective = deep_merge(cur, default)
print(json.dumps(effective, ensure_ascii=False, indent=2))
