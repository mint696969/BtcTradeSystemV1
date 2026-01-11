# BtcTradeSystem NEXT 開発・運用統一ルール仕様書
制定: 2026-01-07
対象: メインPC本番運用（NEXT）
一次資料: 「BtcTradeSystem 開発・運用統一ルール仕様書.md（V1）」※思想・原則の出典として固定

---

## 0. 最重要：V1 と NEXT の境界（絶対に迷わないための宣言）

- 本番運用の正準は **NEXT（btcts）** である。
- 旧V1（`btc_trade_system`）は **リポジトリから削除済み**。参照・復活・import を禁止する。
- NEXT 正準（現物）:
  - Code: `C:\BtcTradeSystem\btcts_next\src\btcts`
  - 外部設定: `E:\btc_ts\config\ui`
  - Data: `E:\btc_ts\data`
  - Logs: `E:\btc_ts\logs`
  - Secrets: `E:\btc_ts\secrets`（※存在する場合。Git管理外）

---

## 1. 目的

本書は BtcTradeSystem（NEXT）の本番運用における「迷いを排除するためのルールブック」である。

- “思想・原則（原子的保存、監査、境界、禁止事項）”は V1 一次資料に準拠し継承する。
- “パス、構造、モジュール、起動経路、設定の正準”は NEXT（提出物の現物）に合わせて刷新する。

---

## 2. ディレクトリ正準（NEXT）

### 2.1 コード正準（リポジトリ内）
`C:\BtcTradeSystem\btcts_next\src\btcts` が唯一の正。

- btcts/
  - core/        : 環境変数・パス解決・共通基盤
  - collector/   : 収集器（起動・制御・status表示等）
  - health/      : 監視・健全性評価
  - settings/    : 設定サービス（読込/保存/バリデーション）
  - ui/          : Streamlit UI
    - app.py
    - pages/
      - collector.py
      - health.py
      - （今後追加）

※UIページは `btcts/ui/pages/*.py` を正とする（現物に存在）。

### 2.2 運用外部ルート（リポジトリ外）
`E:\btc_ts\` を本番運用の正準ルートとする。

- E:\btc_ts\
  - config\
    - ui\          : 実運用設定（唯一の正）
  - data\          : 実データ
  - logs\          : 実ログ
  - secrets\       : 秘密情報（Git管理外）

---

## 3. 環境変数（現物：btcts/core/env.py）

本番運用は以下の環境変数を前提とする。

- BTC_TS_CONFIG_DIR : 外部設定ルート（例: `E:\btc_ts\config\ui`）
- BTC_TS_DATA_DIR   : data ルート（例: `E:\btc_ts\data`）
- BTC_TS_LOGS_DIR   : logs ルート（例: `E:\btc_ts\logs`）
- BTC_TS_SECRETS_DIR: secrets ルート（例: `E:\btc_ts\secrets`）

補足（コード既定）:
- 未指定時の既定は「リポジトリ内」に落ちる設計になっている。
  - config: `<repo_root>/config/ui`
  - data  : `<repo_root>/data`
  - logs  : `<repo_root>/logs`
  - secrets: `<repo_root>/secrets`
本番では必ず E:\btc_ts\ を指すように設定して運用する。

---

## 4. 設定ファイルの正準と優先順位（NEXT）

### 4.1 正準
本番で参照される設定は **E:\btc_ts\config\ui\*.yaml** を唯一の正とする。

（提出物の現物で中身が存在することを確認済み）
- E:\btc_ts\config\ui\collector.yaml
- E:\btc_ts\config\ui\endpoints.yaml
- E:\btc_ts\config\ui\exchanges.yaml
- E:\btc_ts\config\ui\monitoring.yaml

### 4.2 注意（混乱源の排除）
`E:\btc_ts\config\*.yaml` に `{}` のプレースホルダが存在する場合、
それは本番設定の正準ではない。以下のどちらかに統一する。

- 方針A（推奨）: `E:\btc_ts\config\` 直下の `{}` を削除し、`config\ui\` のみに統一
- 方針B: `{}` を docs/placeholders/ 等へ退避し、「運用設定ではない」ことを明記

---

## 5. UI構造（現物：btcts/ui/app.py）

UIは Streamlit を前提とし、現物ではタブ構成をコード側で保持している。

- app.py がページ（collector/health 等）を読み込んで表示する
- ページは `btcts/ui/pages/*.py` に追加する
- 将来的に tabs.yaml 等へ寄せる場合でも、移行完了まで「現物の正」は app.py とする

---

## 6. 原子的保存（思想はV1継承、実装はNEXTで確定する）

保存は破損耐性を優先し、以下を原則とする。

- `.tmp` へ書く
- flush + fsync
- `os.replace` で原子的に差し替える
- 必要に応じてバックアップ（世代管理）を残す

※NEXTで「settings保存I/F（関数名・責務）」は btcts/settings 配下の現物に合わせて確定する。
（この章は “原則” のみ固定し、I/Fは次の作業で確定させる）

---

## 7. 禁止事項（V1原則をNEXTに適用）

- 旧V1のモジュール名（btc_trade_system）を docs / config / コードに復活させない
- 設定の正準（E:\btc_ts\config\ui）を二重化しない
- secrets を Git 管理しない
- 「動けばよい」場当たり修正は禁止（原因を潰して正準に反映する）

---

## 8. 運用チェック（本番の最小確認）

- ENV が本番を指していること
  - BTC_TS_CONFIG_DIR = E:\btc_ts\config\ui
  - BTC_TS_DATA_DIR   = E:\btc_ts\data
  - BTC_TS_LOGS_DIR   = E:\btc_ts\logs
- collector.yaml の status.path が data 配下を指していること
- endpoints.yaml が Collector の参照正準になっていること

（ワンライナー類は “本番の起動経路” を確認した上で次章として追加する）

---

## 9. 変更履歴

- 2026-01-07: NEXT本番仕様書 初版（提出物.zip現物反映）
