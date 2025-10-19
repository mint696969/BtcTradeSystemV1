from pathlib import Path
from btc_trade_system.features.audit_dev import writer
from btc_trade_system.common import paths

writer.set_mode("DEBUG")  # UIの単一真実は session_state 側だが、テストでは直接同期
writer.emit("ui.test", level="INFO", feature="audit_dev", payload={"msg":"emit smoke"})

p = Path(paths.logs_dir()) / "dev_audit.jsonl"
print("DEV_AUDIT:", p, "exists=", p.exists())
if p.exists():
    tail = p.read_text(encoding="utf-8").splitlines()[-3:]
    print("TAIL:")
    for line in tail: print(line)
