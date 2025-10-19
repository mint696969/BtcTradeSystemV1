import inspect, os
from btc_trade_system.features.audit_dev import writer
print("writer module =", inspect.getfile(writer))
print("log path (writer solution) =", writer._resolve_log_path() if hasattr(writer, "_resolve_log_path") else "no helper")
