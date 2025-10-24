# path: ./tmp/test_snapshot_once.py
# desc: BOOSTスナップショットを生成し、JSONの主要キーとテキスト章立てを検証する
import sys, json, time, pathlib
from btc_trade_system.features.audit_dev.boost import export_and_build_text

LOG_DIR = pathlib.Path(r"D:\BtcTS_V1\logs")
JSON_PATH = LOG_DIR / "boost_snapshot.json"
HANDOVER_PATH = LOG_DIR / "handover_gpt.txt"

# 1) 生成（強制）
json_path_str, txt = export_and_build_text(mode="BOOST", force=True)

# 2) handover_gpt.txt を作成（UIでは自動だがテストはここで書き出す）
HANDOVER_PATH.write_text(txt, encoding="utf-8")

# 3) JSON 妥当性と必須キー
data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
must = ["roots","env","versions","files","recent"]
miss = [k for k in must if k not in data]
print("JSON:", JSON_PATH, "size=", JSON_PATH.stat().st_size)
print("Handover:", HANDOVER_PATH, "size=", HANDOVER_PATH.stat().st_size)
print("MissKeys:", ",".join(miss) if miss else "<none>")

# 4) recent が空でないこと（監査末尾）
recent_len = len(str(data.get("recent","")))
print("recent_len:", recent_len)

# 5) handover の章立て（最低限）
need = ["Roots","Env","Versions","Files","REPO_MAP","How to reproduce"]
missing_sections = [s for s in need if f"## {s}" not in txt]
print("MissingSections:", ",".join(missing_sections) if missing_sections else "<none>")

# Exit code
ok = (not miss) and recent_len>0 and (not missing_sections)
sys.exit(0 if ok else 2)
