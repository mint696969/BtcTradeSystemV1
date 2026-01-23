# V1参考 → NEXT要件抽出メモ

## 注意（必読）

本ドキュメントは **BtcTradeSystem V1 の仕様書・設計思想を参考にして抽出した、BTC TS Next 用の要件メモ** です。

* 本文書は **NEXT の正準仕様ではありません**
* 実装判断の最終正は `docs/README.md`・`handover.md`・現物コードです
* V1 のディレクトリ構造・ファイル名・配置を NEXT に復活させてはなりません
* 本文書は **事故防止・設計判断のガードレール**として利用します

---

## 1. 最重要方針（事故防止）

### 1.1 Collector は「収集量」より「安全性」を優先する

* API を可能な限り叩く設計は採らない
* **API 制限を受けないことを最優先目標**とする
* 収集量はレート制御の結果として決まる

### 1.2 二重起動・暴走は最悪の事故

* 同一マシン上で Collector は **必ず 1 プロセスのみ**
* UI rerun / Start 連打 / 例外時でも二重起動しない
* pidfile / ロックは「誤停止」より「誤起動防止」を優先

---

## 2. レート制御要件（Collector 中核）

### 2.1 レート制御は Collector の中心機構

* 収集処理は必ずレート制御を経由する
* レート制御をバイパスする経路を作らない

### 2.2 二段階制御モデル

* **Soft-limit（WARN）**

  * 上限接近を検知
  * 収集を抑制しつつ継続
* **Hard-limit（CRIT）**

  * 429 / Retry-After を受信した時点で即座に発動
  * cooldown 延長・ペナルティ増加

### 2.3 安全係数（safety_factor）

* 取引所の公式上限（official_max_rps）を直接使わない
* 実効上限は以下で決定する

```
effective_max_rps = official_max_rps * safety_factor
```

* safety_factor は **運用側（Health / monitoring）で調整可能**とする

---

## 3. 状態の可視化要件（観測できない制御は事故）

### 3.1 状態ファイルの役割分離

* **rate_state**

  * 詳細なレート制御内部状態
  * tokens / penalty / cooldown / last_429 等
* **status**

  * 外部参照用の集約状態
  * RUNNING / STOPPED / WARN / CRIT など

### 3.2 Health / UI は必ず状態を見る

* 内部挙動を推測しない
* status / rate_state を正準情報源とする

---

## 4. Collector 要件（NEXT 向け）

* データ出力は DATA 配下に統一
* rate_state / status も DATA 配下に配置
* LOGS 配下のログは補助情報（監査は別枠）
* endpoint / scheduler は設定で増減可能

---

## 5. Health 要件

* Collector の状態を **読むだけ**（制御しない）
* WARN / CRIT 判定基準を持つ
* 判定理由を UI に渡せる構造

---

## 6. UI 要件（運用安全装置）

* Collector の Start / Stop は任意操作可能
* Start 成功とは「プロセス起動」ではなく
  **制御が有効でループが回っていること**
* 二重起動を誘発する UI 操作を防ぐ

---

## 7. 監査（Audit）要件

* 429 / Retry-After は必ず記録
* 起動 / 停止 / 失敗 / 例外 / 設定読込を追跡可能に
* 後から GPT に提示して原因特定できる粒度

---

## 8. 将来構成（収集専用機）への配慮

* Collector と UI が別マシンになっても破綻しない
* 状態ファイルの共有・リモート参照を想定
* ただし当面は単機安定を最優先

---

## 9. 本メモの位置づけ（再確認）

* 本文書は **設計判断用メモ**である
* 完成仕様は `docs/仕様書一式/` に移す
* 実装が始まった後も、迷ったらここに立ち返る
