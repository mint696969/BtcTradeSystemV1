# BtcTradeSystem V1 — 情報収集ドメイン 設計仕様書 v2

本書は _BtcTradeSystem V1_ における **Collector／Rate 制御／Scheduler／Health／Dashboard Alert／Ops Audit** を統合的に定義した最新版の完全仕様である。
設計思想・YAML スキーマ・状態遷移・処理フローをすべて明文化し、将来の拡張（取引所追加・GPT 解析連携）にも耐える構造とする。

---

# 1. 概要

本ドメインは、暗号資産取引所からの市場データを安定かつ継続的に収集し、加工し、システム全体へ提供するための中核コンポーネントである。構成要素は以下の 6 層で構成される：

1. **取引所登録（Exchanges）** – 公式 API 上限・サポート endpoint の定義（※安全係数は Health 設定側へ移動）
2. **エンドポイント定義（Endpoints）** – priority／target_interval の SLA
3. **API レート制御（RateController）** – Soft-limit（warn）／Hard-limit（crit）
4. **Collector スケジューラ（Scheduler）** – 巡回実行・429 例外処理
5. **状態集約（collector_status.json）** – Heartbeat と Rate 状態の統合
6. **健全性判定（Health）→ Dashboard Alert** – warn/crit チップ表示

---

# 2. Collector 全体構造

```
             ┌──────────┐
             │ Exchanges │ 公式レート
             └─────┬────┘
                   │
                   ▼
         ┌──────────────────┐
         │ Endpoints (SLA)  │ priority / target_interval
         └──────────┬───────┘
                    │
                    ▼
         ┌──────────────────┐
         │ RateController    │ ← soft-limit / hard-limit
         └──────────┬───────┘
                    │ request_permit()
                    ▼
         ┌──────────────────┐
         │  Scheduler       │ 巡回
         └──────────┬───────┘
                    │ runner()
                    ▼
        API 呼び出し（bitFlyer 等）
                    │
                    ▼
 Heartbeat → collector_status.json → health → dashboard alert chips
```

---

# 3. 取引所登録（Exchanges）

取引所ごとの **公式 API レート上限（official_max_rps）** と
サポートする endpoint を定義する。

注意：
- 「運用上の安全係数（safety_factor）」は Exchange 側には置かない。
- safety_factor は Health 設定タブにて集中管理する。
- Exchange 設定は“公式ドキュメントの事実情報”のみ保持する。

## 3.1 exchanges_def.yaml（例）
```yaml
yaml_version: 1

bitflyer:
  official_max_rps: 10
  burst_base_sec: 2
  endpoints:
    - orderbook
    - trades

binance:
  official_max_rps: 20
  burst_base_sec: 2
  endpoints:
    - trades
    - ticker

## **📌 修正 3 — 「5. API レート制御」へ安全係数の説明を追加**

### **現状問題**
- RateController 内の「max_rps = official × safety_ratio」が Exchange 依存で書かれている

### **修正指示**
以下の項目を **5. API レート制御** の最下部へ **追記**：

---

### **🆕 追記内容**

---

## 3.2 Settings モーダルのタブ構成

Settings モーダルは以下のタブで構成する。

- Basic … 全体設定（テーマ色、言語、時刻表示など）
- Network … ネットワーク関連（接続タイムアウト等）
- Health … 健全性しきい値／アラート制御
- Exchanges … 取引所登録（公式レート・有効/無効・API キー状態）

# 4. エンドポイント定義（Endpoints）

各取引所の API エンドポイントは、collector の実行順序と頻度を統制するため **priority** と **target_interval** を持つ。

## 4.1 endpoints_def.yaml（例）

```yaml
yaml_version: 1
bitflyer:
  orderbook:
    priority: 1
    target_interval: 0.20
  trades:
    priority: 2
    target_interval: 0.50
```

- **priority**：小さいほど優先
- **target_interval**：許容される最短 API 呼び出し間隔（秒）

---

## 4.2 Exchanges タブ（取引所登録）

### 4.2.1 目的

暗号資産取引所ごとの「公式情報」と「API キー状態」を一元管理し、
Collector／将来の自動売買が参照するための登録窓口とする。

- 公式情報（非秘匿） … Git 管理下の config/ui/exchanges.yaml
- 秘匿情報（API キー類） … DATA ルート配下の secrets/exchanges.ini

### 4.2.2 UI レイアウト（1 取引所 = 1 カード）

Exchanges タブ内では、サポート対象の取引所ごとにカードを 1 枚ずつ表示する。

カード構成：

- ヘッダ行
  - 左：表示名（例: bitFlyer, Binance）
  - 右：有効トグル（enabled）
- 中段（公式レート）
  - 数値入力: 公式 API 上限 (req/sec) → `official_max_rps`
  - 数値入力: バースト基準（秒） → `burst_base_sec`
  - 補足ラベル: 「burst = effective_max_rps × burst_base_sec」
- 中段右（API キー状態）
  - ラベル: 「API キー: 未登録 / 登録済み」
  - ボタン: 「API キー編集…」 → 別ダイアログで secrets を編集
- 下段
  - テキストエリア: メモ（任意） → `notes`
- フッタ
  - 「この取引所の登録を削除」ボタン（確認ダイアログ付き）

### 4.2.3 設定ファイルとの対応

- 非秘匿設定（公式情報）は Git 管理下：

  - `btc_trade_system/config/ui/exchanges.yaml`
  - `btc_trade_system/config/ui_defaults/exchanges.defaults.yaml`

  想定構造（抜粋）:

  ```yaml
  yaml_version: 1

  exchanges:
    bitflyer:
      enabled: true
      display_name: "bitFlyer"
      official_max_rps: 10.0
      burst_base_sec: 2.0
      notes: ""

    binance:
      enabled: false
      display_name: "Binance"
      official_max_rps: 20.0
      burst_base_sec: 2.0
      notes: ""
秘匿設定（API キー）は DATA ルート配下：

ルート: D:\BtcTS_V1（または DATA_ROOT）

パス: D:\BtcTS_V1\secrets\exchanges.ini

想定構造（抜粋）:

ini
コードをコピーする
; path: <DATA_ROOT>\secrets\exchanges.ini
; desc: 取引所ごとの API 認証情報（collector／将来の自動売買が共用）

[bitflyer]
; collector 用 REST キー
collector_key =
collector_secret =
collector_passphrase =

; trading 用（将来利用）
trade_key =
trade_secret =
trade_passphrase =

[binance]
collector_key =
collector_secret =
collector_subaccount =

### 4.2.4 API キー編集ダイアログ
「API キー編集…」ボタンを押すと、小さなモーダルを開く。

項目（例）

collector_key（パスワード表示）

collector_secret（パスワード表示）

collector_passphrase（必要な取引所のみ）

trade_key / trade_secret / trade_passphrase（将来利用）

挙動

保存: exchanges.ini の該当セクションへ atomic 書き込み

既存値は「登録済み」の有無のみ表示し、中身はマスキング（***）や非表示

「キーを消去」ボタンで、該当セクションの値を空文字クリア

### 4.2.5 キー無しで利用できる場合
一部のエンドポイント（板／約定など）は API キー不要で利用可能。

exchanges.yaml の enabled: true であっても、

対象 endpoint が requires_api_key: false の場合はキー未登録でも収集可能。

UI 上は、API キー未登録の場合に「公開 API のみ利用中」といった説明を添える。

### 4.2.6 取引所単位での削除
「この取引所の登録を削除」ボタンの挙動：

確認ダイアログを表示（取引所名を明記）

OK の場合：

config/ui/exchanges.yaml から該当 exchange エントリを削除

secrets/exchanges.ini の該当セクションも削除（または全キーを空文字にクリア）

dev_audit に settings.exchanges.delete を出力

---

テスト＆確認チェックリスト
タブ切替          色・下線の切替             全状態正常
Basic 保存        設定変更 → YAML 更新       即反映／再起動不要
Exchanges 保存    公式上限・有効フラグ更新   exchanges.yaml 更新／即反映
Exchanges API キー 編集／消去 → secrets.ini 更新  collector 起動時に参照可能
↺ 復元            ホバー確認 → 戻す         defaults 値と一致
Undo              5 秒以内操作で復帰         値が元通り

---

# 5. API レート制御（RateController）

Collector の心臓部。以下の三層構造で制御する：

## 5.1 Exchange レベル（外枠）

- max_rps：1 秒あたりの許容リクエスト数
- burst：同時許容数
- safety_ratio により公式制限より低めに設定

### Soft-limit 判定材料

- tokens == 0（枯渇）
- cooldown 中
- penalty > 0
  → **warn** 判定に使用

## 5.2 Endpoint レベル（SLA）

- target_interval により API 最低インターバルを保証

## 5.3 Hard-limit（429 / Retry-After）

- RateLimited 例外を受けた瞬間に hard_limit=true
- penalty++ と cooldown_until を強制延長
  → **crit** 判定に使用

## 5.4 外部公開 API

```python
get_exchange_state(exchange) -> {
  tokens, burst, penalty,
  cooldown_until, is_cooldown,
  last_rate_limited_ts,
  soft_limit: bool
}

## 5.5 運用安全係数（safety_factor）— Health 設定タブで集中管理

公式レート上限（official_max_rps）は取引所ごとに Exchange 設定で保持する。

一方で、実運用で攻める/余裕を持つための調整値である
「安全係数（safety_factor）」は Health 設定タブで一元管理する。

構造：
rate_control:
safety_factor:
default: 0.90
per_exchange:
bitflyer: 0.80

RateController 初期化時の実効値は：

effective_max_rps = official_max_rps * safety_factor

として計算される。


---

## **📌 修正 4 — 「7. 状態集約」への追記**

### **必要理由**
- 現状、rate.soft/hard の生成元が公式上限×安全係数であることが仕様上曖昧

### **追記指示（7. 状態集約の末尾へ）**



rate.soft_limit / rate.hard_limit の判定は
「公式レート × safety_factor」を超過した場合に決定される。

この計算は RateController 内で行われ、
collector_status.json には “最終結果” のみが書き込まれる。


---

## **📌 修正 5 — 「8. 健全性判定（Health）」に安全係数の参照先を明記**

**追記：**



※ 安全係数（safety_factor）は Exchange 設定には存在せず、
Health 設定タブ（monitoring.yaml）から読み取られる。


---

## **📌 修正 6 — 設定ファイルの所在を追記**

**追記（付録 or セクション 3 の下などへ）：**



設定ファイルの整理：

取引所登録：config/ui/exchanges.yaml

健全性設定（安全係数含む）：config/ui/monitoring.yaml


---

## **📌 修正 7 — 「1. 概要」図の更新**

### **現状の図**


Exchanges │ 公式レート + safety_ratio


### **修正**



Exchanges │ 公式レート
Health設定 │ safety_factor（運用マージン）


（図の文字列のみ差し替え）

```

---

# 6. Collector Scheduler

Scheduler は以下の責務を持つ：

1. priority 昇順に endpoint を巡回
2. API 呼び出し前に `rc.request_permit()` を必ず通す
3. RateLimited → rc.on_rate_limited() + hard_limit を rate_state.json へ
4. 成功時 → rc.on_success()
5. dev_audit_emit による監査記録

---

# 7. 状態集約（collector_status.json）

Collector の観測値を **一元的にまとめたスナップショット**。
Heartbeat だけでなく、今回追加された **rate** ブロックも集約する。

## 7.1 status.json スキーマ

```json
{
  "updated_at": "...",
  "leader": {...},
  "storage": {...},
  "sync": {...},
  "items": [...],
  "rate": {
    "bitflyer": {
      "soft_limit": true,
      "hard_limit": false,
      "penalty": 1,
      "cooldown_until": "2025-11-17T09:00:00Z",
      "last_rate_limited_at": "2025-11-17T08:59:10Z",
      "tokens": 0.0,
      "burst": 2
    }
  }
}
```

---

# 8. 健全性判定（Health）

Health は status.json を入力とし、警告レベルを算出する。

## 8.1 Rate 由来の評価規則

- soft_limit == true → **WARN**
- hard_limit == true → **CRIT**

これにより dashboard が即座にアラートを反映できる。

---

# 9. ダッシュボード連携（Alert Chips）

Health で判定されたレベルを dashboard header の chip として表示。

- warn → 黄色 chip
- crit → 赤 chip
- urgent → 今回の rate 制御では使用しない（通信断など上位の異常専用）

カラーは dash.yaml にてユーザー上書き可能。

---

# 10. 運用監査（Audit）

開発監査（`audit_dev`）とは別に、運用監査は **audit** フォルダで提供される。

目的：

- Collector 実行状況
- Rate 状態（soft/hard）
- endpoint 実行成功/失敗
- インシデント（429 等）

を時系列で記録し、運用者が状態を把握できるようにする。

---

# 11. GPT 解析向けデータ拡張方針

将来の自動最適化・バックテスト・戦略分析のため、以下を収集する：

- 取引所別の連続トレース
- API 呼び出し詳細（成功/失敗/待機）
- RateController の tokens/penalty 推移
- scheduler loop latency

これらは **GPT-解析用サイドログ** として独立管理し、collector の軽量性を損なわない構造とする。

---

# 12. 付録

## 12.1 Rate 状態遷移図

```
          +-------------------+
          |   normal (ok)     |
          +----------+--------+
                     |
           tokens==0 / penalty>0
                     |
                     v
          +----------+--------+
          | soft-limit (warn) |
          +----------+--------+
                     |
               429 / Retry-After
                     |
                     v
          +----------+--------+
          | hard-limit (crit) |
          +-------------------+
```

## 12.2 scheduler 実行シーケンス

```
loop:
  for ep in endpoints_sorted_by_priority:
    allowed, wait = rc.request_permit()
    if not allowed: continue

    try:
      ep.runner()
      rc.on_success()
    except RateLimited:
      rc.on_rate_limited()
      write hard_limit to rate_state.json
```

---

# 完了

本書は BtcTradeSystemV1 における Collector 情報収集ドメインの基準仕様であり、今後の開発・拡張の基礎となる。
