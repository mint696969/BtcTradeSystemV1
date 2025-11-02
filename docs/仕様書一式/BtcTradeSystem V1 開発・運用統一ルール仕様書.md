BtcTradeSystem V1 開発・運用統一ルール仕様書

ver 1.1 — Hybrid Feature Architecture Model ＋ Full Runtime Specs

🎯 目的

BtcTradeSystem V1 の開発・運用における唯一のルールブック。
全開発者・自動化タスク・将来拡張は本仕様に従う。

🧩 1. 開発基本方針
項目 方針
目的 各機能を features/ 配下に閉じ込め、ダッシュボード／設定は読むだけ構造にする。
思想 “機能追加 ＝ フォルダ追加＋設定登録だけ”。既存コード改変を最小化。
構成単位 機能 ＝ 1 フォルダ（UI／設定／サービスを内包）。
保存方式 ハイブリッド型：既定は機能フォルダ、実値は外部設定ディレクトリ。
命名規則 ui*<feature>.py／set*<feature>.py／svc\_<feature>.py。
原子的保存 .tmp → fsync → replace 手順。破損を残さない。
🗂️ 2. ディレクトリ構成（標準）
btc_trade_system/
├── config/
│ └── ui/
│ └── tabs.yaml
└── features/
├── dash/
│ ├── ui_main.py
│ ├── set_dash.py
│ ├── svc_dash.py
│ └── config/
│ ├── dash_def.yaml
│ └── schema.yaml
├── health/
│ ├── ui_health.py
│ ├── set_health.py
│ ├── svc_health.py
│ └── config/health_def.yaml
└── audit_dev/
├── ui_audit.py
├── set_audit.py
├── svc_audit.py
└── config/audit_def.yaml

⚙️ 3. 設定ファイル管理ルール（ハイブリッド方式）
ファイル 置き場所 役割
<feature>\_def.yaml features/<feature>/config/ 機能同梱の既定値。Git 管理対象。
<feature>.yaml 外部設定 DIR（例 D:\BtcTS_V1\config\ui） 実行時に自動生成。ユーザー固有。Git 管理外。
外部設定 DIR 指定 BTC_TS_CONFIG_DIR 環境変数。未指定時 data/config/ui/ へ。
バックアップ 保存時 tmp/<feature>\_YYYYMMDD_HHMMSS.yaml.bak へ。
監査記録 features/audit_dev/writer.emit() で保存／復元イベント記録。
🧮 4. タブ構成と並び順
tabs.yaml スキーマ v2

# schema_rev: 2

dashboard:

- key: main
  title: メイン
  module: btc_trade_system.features.dash.ui_main
  view: render
  order: 0
  enabled: true
- key: health
  title: 健全性
  module: btc_trade_system.features.health.ui_health
  view: render
  order: 10
  enabled: true
- key: audit
  title: 開発監査
  module: btc_trade_system.features.audit_dev.ui_audit
  view: render
  order: 20
  enabled: true
- key: dash
  title: 基本設定
  module: btc_trade_system.features.settings.set_dash
  view: render
  order: 200
  enabled: false
  settings:
- key: health
  title: 健全性
  module: btc_trade_system.features.settings.set_health
  view: render
  order: 10
  enabled: true
- key: audit
  title: 開発監査
  module: btc_trade_system.features.settings.set_audit
  view: render
  order: 20
  enabled: true
- key: dash
  title: 基本設定
  module: btc_trade_system.features.settings.set_dash
  view: render
  order: 200
  enabled: true

🧰 5. サービス層 (svc\_) 共通 I/F
FEATURE = "<feature>"
DEF_FILE = f"{FEATURE}\_def.yaml"
CUR_FILE = f"{FEATURE}.yaml"

def get_paths() -> tuple[pathlib.Path, pathlib.Path]:
"""def_path, active_path を返す。ENV 優先。"""

def load_yaml() -> dict:
"""active ＋ def を shallow merge。"""

def save_yaml(data: dict) -> None:
""".tmp→fsync→replace 原子的保存。バックアップ → 監査 emit。"""

def reset_to_default() -> dict:
"""def_yaml を返す。"""

🔢 6. タブ順序番号体系
範囲 用途 備考
0 main 固定
10 – 190 各機能 10 刻み推奨
200 基本設定 (dash) Dashboard 非表示／Settings 最右端
🧩 7. 開発ルール（命名・コメント）
分類 命名 説明
UI ui*<feature>.py ダッシュ表示
設定 set*<feature>.py 設定タブ
サービス svc*<feature>.py I/O
コメント 1 行目 # path: ／ 2 行目 # desc: 必須
禁止 from x import \* ・ ハブ直書き ・ \_def 書換
🧾 8. チェックワンライナー
tabs 整合
$tabs=(Get-Content .\btc_trade_system\config\ui\tabs.yaml -Raw|ConvertFrom-Yaml)
$tabs.dashboard|Group-Object key|?{$*.Count -gt 1}
$tabs.dashboard|Group-Object order|?{$\_.Count -gt 1}

モジュール検証
$py=".\\.venv\\Scripts\\python.exe";if(-not(Test-Path$py)){$py="python"}
$code=@'
import importlib,yaml
cfg=yaml.safe_load(open("btc_trade_system/config/ui/tabs.yaml",encoding="utf-8"))
for sect in ("dashboard","settings"):
for it in cfg.get(sect,[]):
m,v=it.get("module"),it.get("view")
try:
fn=getattr(importlib.import_module(m),v)
print("OK",sect,it["key"]) if callable(fn) else print("NG",sect,it["key"])
except Exception as e:
print("FAIL",sect,it["key"],e)
'@
$code|&$py-

🔒 9. 禁止事項

features 外から svc/config/alert へ直接アクセス禁止

dashboard.py や settings.py へ機能固有コードを追加禁止

Git 管理ファイルへの自動書換禁止

order 衝突禁止

1 ファイル 1 キャンバス 厳守

🧭 10. 将来拡張

各機能に manifest.yaml を追加し自己登録制へ移行可能

外部設定のローテーション自動化

audit_dev で設定差分プレビュー機能追加予定

📦 追補 A〜I （内部仕様）
A. 環境変数

BTC_TS_CONFIG_DIR／BTC_TS_DATA_DIR／BTC_TS_LOGS_DIR／BTC_TS_MODE

B. サービス層関数詳細

（省略せず上記 5 章の完全版と同一）

C. UI 層 I/F

render()／on_default()／on_save() を持つ。

D. セッションキー

\_alerts_palette_overrides／settings_open／\_\_toast

E. アトミック保存手順

mkdir → 2) 退避 → 3) tmp 書出 → 4) flush+fsync → 5) os.replace → 6) emit log

F. tabs.yaml 形式定義

schema_rev:2／order 固定 (0,10–190,200)

G. 監査イベント

settings.write / settings.default.apply / settings.read

H. インポート規約

絶対インポート必須・先頭コメント義務・UI → svc 経由のみ

I. 検証ワンライナー集

タブ衝突 2) module 存在 3) 設定ファイル解決

制定：2025-11-02
改訂：ver 1.1 — 内部定義・I/F・環境仕様 追補完了
