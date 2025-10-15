from btc_trade_system.features.collector.core.status import StatusWriter
sw = StatusWriter()
sw.set_leader(host="TEST-HOST", pid=12345, started_ms=111, heartbeat_ms=222)
sw.update("bitflyer","board", ok=True, last_iso="2025-10-15T00:00:00Z")
sw.flush()
