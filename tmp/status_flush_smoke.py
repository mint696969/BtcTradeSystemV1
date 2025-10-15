from btc_trade_system.features.collector.core.status import StatusWriter
sw = StatusWriter()
sw.set_leader("HOST", 999, 111, 222)
sw.set_storage(logs_root="LROOT", data_root="DROOT", primary_ok=True)
sw.update("bitflyer","board", ok=True, last_iso="2025-10-15T00:00:00Z")
p = sw.flush()
print("ok:", p)
