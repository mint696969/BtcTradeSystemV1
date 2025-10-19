from pathlib import Path
from btc_trade_system.common import boost_svc

p1 = boost_svc.export_snapshot(force=True)
print("SNAP:", p1, Path(p1).exists(), Path(p1).stat().st_size)

txt = boost_svc.build_handover_text()
print("TXT_HEAD:", txt.splitlines()[:4])

p2 = boost_svc.export_handover_text(force=True)
print("HANDOVER:", p2, Path(p2).exists(), Path(p2).stat().st_size)
