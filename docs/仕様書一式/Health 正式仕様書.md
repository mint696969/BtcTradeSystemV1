Health 正式仕様書（確定版 / Phase 1）
1. 目的

Health は Collector を 24 時間連続稼働させるための監視・可視化機構である。
本フェーズ（Phase 1）において Health は以下を保証する。

Collector が 正常か / 危険兆候があるか / 致命的か を即時に判定できる

判定は 設定値に基づく機械的分類のみで行う

判定の根拠となる 参照ファイル・値・ログを明示する

Health 自身は 運用判断・推論・自動制御を行わない

2. 対象範囲（Phase 1）
含まれるもの

status.json を用いた Collector 状態判定

audit.jsonl を用いた事実ログの表示

monitoring.yaml による閾値定義

Streamlit UI による可視化

テスト用ワークスペース生成（tmp 配下）

含まれないもの

原因分析・推論

自動復旧・自動停止

通知（Slack / Mail 等）

スケジューラ連携

CLI / exit code 出力（Phase 2）

3. 入力仕様
3.1 status.json（必須）

役割
Collector の「現在状態」を 1 ファイルで表現する。

参照パス

$BTC_TS_DATA_DIR/collector/status.json


主要フィールド

mode : RUNNING / ERROR

items[]

exchange

topic

age_sec

last_ok

retries

cause

notes

Health は age_sec / retries / mode を主に使用する。

3.2 audit.jsonl（任意だが推奨）

役割
Collector の事実イベントログ（時系列）

参照パス

$BTC_TS_LOGS_DIR/audit.jsonl


仕様

JSON Lines 形式

Health は 末尾 N 件のみを表示

集計・解析は行わない（Phase 1）

3.3 monitoring.yaml（必須）

役割
Health の判定基準を定義する唯一の設定ファイル。

参照パス

$BTC_TS_CONFIG_DIR/monitoring.yaml


例

schema_rev: 1
thresholds:
  default:
    age_sec: { warn: 10.0, crit: 30.0 }
    retries: { warn: 1, crit: 3 }
recovery:
  back_to_normal_min_ok: 3


重要原則

Health の判定ロジックは この YAML に完全依存

コード内ハードコードは禁止

本番 / テストの切替は 配置パスで分離

4. 判定仕様
4.1 判定レベル
レベル	意味
OK	正常稼働
WARN	異常兆候あり（運用判断が必要）
CRIT	致命的状態（即時対応が必要）
4.2 判定ルール

age_sec が warn 以上 → WARN

age_sec が crit 以上 → CRIT

retries が閾値超過 → WARN / CRIT

mode == ERROR → CRIT

※ 複数 items がある場合は 最悪値を overall に反映

5. 出力仕様（UI）
5.1 Paths (effective)

Health が実際に参照している ENV / パスの確定値を表示

「どこを見ているか」を曖昧にしない

5.2 Refs (evidence)

以下を明示表示する

status.json のパス

audit.jsonl のパス

monitoring.yaml のパス

判定の 証拠リンク集として機能

5.3 状態テーブル

exchange / topic 単位で表示

age_sec / status / retries / last_ok を表示

判定結果と数値の乖離が起きない構造

5.4 Audit tail

audit.jsonl の末尾イベントをそのまま表示

加工・解釈は行わない

6. テスト仕様（Phase 1）
6.1 テスト方法

tmp/health_test.ps1 により 完全独立ワークスペースを生成

ENV を固定して UI を起動

本番設定を一切汚さない

6.2 テストケース
Case	内容
OK	age_sec < warn
WARN	warn <= age_sec < crit
CRIT	age_sec >= crit
ERROR	mode=ERROR
6.3 成功条件

UI に期待通りの OK/WARN/CRIT が表示される

monitoring.yaml の変更が即反映される

警告・未使用コード・不明瞭な挙動が残らない

7. 設計原則（厳守）

Health は 分類器であって判断者ではない

推論・憶測・自動対応を入れない

参照元を必ず表示する

Phase 1 で 24h 運用できることを最優先

Phase 2 は 後付け前提で分離

8. Phase 1 完了条件（達成済）

 Collector を 24 時間回し続けられる

 異常が UI 上で即座に可視化される

 判定根拠が追跡可能

 テスト環境と本番環境が完全分離