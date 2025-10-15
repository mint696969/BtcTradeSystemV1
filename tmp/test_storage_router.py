from pathlib import Path
from btc_trade_system.common.storage_router import StorageRouter

sr = StorageRouter(Path("."))

# 1) 現在の書込先（primary/secondary）表示
print("root.logs =", sr.current_root("logs"))
print("root.data =", sr.current_root("data"))

# 2) 正常動作: JSONL 追記・CSV 原子的置換
p1 = sr.append_jsonl("logs", "router/test.jsonl", {"t": 1})
p2 = sr.write_atomic_csv("data", "router/test.csv", [["a","b"],["1","2"]])
print("paths:", str(p1), str(p2))

# 3) 脱出パス防止の確認（../ を渡すと例外）
try:
    sr.append_jsonl("logs", "../escape.jsonl", {"x":1})
    print("NG: escape allowed")
except Exception as e:
    print("escape blocked:", type(e).__name__)

# 4) 生成物の軽確認（CSV 先頭を出力）
try:
    with open(p2, "r", encoding="utf-8") as f:
        head = f.read().strip().splitlines()[:2]
    print("csv.head:", head)
except Exception as e:
    print("csv.read.fail:", e)
