# Health 機能 仕様書（ドラフト）

本ドキュメントは、BtcTradeSystem NEXT における **Health 機能**の初期仕様（フェーズ1）を定義するためのドラフトである。
Collector を 24時間・常駐運用させるために必要な **最小かつ壊れにくい Health** を目標とし、推測・自動復旧・高度分析は意図的に含めない。

---

## 0. 目的と位置づけ

Health は「判断する存在」ではなく、**現状を正しく・即座に可視化する存在**である。

* Collector / 周辺プロセスを **止めない**
* 運用者が「今ヤバいかどうか」を **1画面で判断できる**
* GPT や人間がログを読み解くための **一次資料（根拠）** を提示する

Health 自身は以下を行わない：

* 原因推定
* 復旧提案
* 相関分析
* 自動制御

---

## 1. 基本原則（最重要）

### 1.1 分類と推論の厳密分離

* **分類（Classification）＝ OK**

  * monitoring.yaml に定義された閾値に基づき、機械的に状態をラベル付けする
  * OK / WARN / CRIT のみ

* **推論（Inference）＝ NG**

  * 「おそらく原因は〜」
  * 「ネットワーク障害と思われる」
    などの判断は禁止

※ 表示できるのは「ヒント」「次に見るべき場所」まで

---

## 2. Health が参照する正準データ

Health が扱う **真実の入力** は以下の2点のみとする。

### 2.1 status.json

* 生成主体：Collector
* 正準パス：

  * `<DATA_DIR>/collector/status.json`
* 主な用途：

  * 現在の稼働状態（mode）
  * 各 endpoint / topic の最新状態（items）

Health はこの内容を **加工せず** 読み取り、分類に使用する。

### 2.2 audit.jsonl

* 生成主体：core.audit
* 正準パス：

  * `<LOGS_DIR>/audit.jsonl`
* 主な用途：

  * status.json の「根拠」
  * Collector 内部で何が起きたかの時系列

Health は audit を **解釈せず**、該当イベントをそのまま提示する。

---

## 3. monitoring.yaml の扱い

monitoring.yaml は **役割別に分離して解釈**する。

### 3.1 Collector が読む領域

* safety_factor

  * exchange 名 → float
  * 例：bitflyer: 0.8

※ この領域を Health が解釈・変更してはならない

### 3.2 Health が読む領域（フェーズ1）

Health 用の閾値定義は、monitoring.yaml 内の **独立した領域**として扱う。

例（想定）：

* thresholds.default.age_sec.warn
* thresholds.default.age_sec.crit

これらは **分類専用**であり、Collector の挙動には一切影響しない。

---

## 4. 分類ルール（フェーズ1）

以下は代表的な分類例であり、すべて **機械的判定**とする。

* status.mode == ERROR → CRIT
* item.age_sec >= crit → CRIT
* item.age_sec >= warn → WARN
* 上記以外 → OK

※ last_ok / cause / notes は表示に使うが、分類ロジックを変えない

---

## 5. 根拠提示の原則

Health は、分類結果に対して **必ず根拠を提示**する。

### 5.1 根拠として提示してよいもの

* status.json の該当フィールド
* audit.jsonl の直近イベント（event / level / payload）
* 実際に参照しているファイルパス

### 5.2 根拠として提示してはいけないもの

* 解釈文
* 推測文
* 原因断定

---

## 6. UI の責務

* UI は **表示専用**
* Health svc が返した結果をそのまま描画する
* パス解決・分類・判断を UI に書かない

UI が表示すべき最低限の情報：

* 現在時刻との差（age）
* OK / WARN / CRIT 件数
* 各 item の状態一覧
* Reasons（分類の根拠）
* Paths（実際に参照している data / logs / config）

---

## 7. フェーズ分割

### フェーズ1（現在）

* Streamlit UI（pages/health.py）
* status / audit の可視化
* 分類のみ

### フェーズ2（将来）

* CLI health_check
* audit の要約・日次/週次レポート
* 異常近傍抽出

※ フェーズ1が安定するまで着手しない

---

## 8. 非目標（明示）

以下は **やらないこと** として明示する。

* Health から Collector を制御する
* 自動復旧
* 状態遷移の推論
* ログの自然言語要約による判定変更

---

## 9. この仕様書の使い方

* 本仕様書は **コード修正の前提条件**とする
* 仕様とコードがズレた場合は、

  * どちらが正かを明示した上で差し替える
* GPT が迷った場合は、この仕様を最優先で参照する
