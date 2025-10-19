from pathlib import Path
from btc_trade_system.common import boost_svc
from btc_trade_system.common import paths

logs = Path(paths.logs_dir())
snap = boost_svc.export_snapshot(force=True)       # logs/boost_snapshot.json を原子的置換で出す想定
hand = boost_svc.export_handover_text(force=True)  # logs/handover_gpt.txt を原子的置換で出す想定

print("LOGS_DIR =", logs)
print("SNAPSHOT =", snap, "exists=", Path(snap).exists(), "size=", Path(snap).stat().st_size if Path(snap).exists() else 0)
print("HANDOVER =", hand, "exists=", Path(hand).exists(), "size=", Path(hand).stat().st_size if Path(hand).exists() else 0)
