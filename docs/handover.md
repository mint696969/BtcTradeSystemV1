## Btc Ts-ライブ引継ぎ（固定）

※このキャンバスは引継ぎの内容以外書き込みを禁ずる
　大切な内容につきその他の目的で使用せず上書きは禁止です

## 目的

-日々の作業・課題・決定・次アクションを \*\*1 か所\*\に集約し、チャットをまたいだ瞬時の再開を可能にする。

## 記入フォーマット（必須）

```
## <YYYY-MM-DD <短い見出し
  - 作業メモ
    ...

  - 完了タスク
    ...

  - 次の候補タスク
    A) ...

    B) ...

  - 参照: PR/コミット/スクショ/ログ へのリンク or 要約
```

- 作業報告は末尾に追記していくこと。
- 無駄な改行は避け無駄に長くしない事。
- “意味のある粒度”で書く（誰でも追従できるように）。
- 決定事項は `docs/` の該当ファイル（計画/ADR 等）へ\*\*要約のみ\*\*反映。

---

##### 以下直近の作業報告

---

作業引き継ぎ書（最新）
■ 1. 現在のロードマップ（収集器まわり）

進行順として確定しているロードマップ：

RateController（APIレート制御）設計

取引所登録（exchanges）UI／設定体系の統一

RateController 設計の collector_scheduler への本組み込み

Health（健全性）タブの正常化・UI完成

Collector の起動管理（外部プロセス）統合

タイムライン履歴（1h/24h/10d）設計／実装

Collector 本番実装 → Health/status.json 更新制御

最終テスト（実APIキー投入前の全体テスト）

■ 2. 本日までに完了したタスク
✔ 2-1. 設定体系の統一

D:\BtcTS_V1\config\ui を UIと運用設定の唯一のディレクトリ として明確化

exchanges.yaml / health.yaml / monitoring.yaml など UI 設定をまとめる構成へ統一

ENV の BTC_TS_CONFIG_DIR を D:\BtcTS_V1\config\ui に正式決定

settings_svc の読み込み参照先も全て修正済み

✔ 2-2. 取引所登録（exchanges）仕様の構築

exchanges_def.yaml を正しいパスに配置

exchanges.yaml の初期構造を整備

set_exchanges.py の get_exchange_policy() の本番ロジック実装

safety factor（bitFlyer=0.8、他=0.9）反映済み

→ policy(bitflyer, 0.8) が正しく

official_max_rps:100, effective_max_rps:80
burst_base_sec:2.0 → burst=160


を返していることを確認済み。

✔ 2-3. RateController の動作テスト（dummy）

バースト動作テストで binance/bybit の制御挙動を確認済み

wait_ms の正常発生を確認済み

okx（無効扱い）の扱いも仕様通り

✔ 2-4. Health タブ全体の再構築

カード正常表示（health level / rate border）

タイムライン（1h/24h/10day）の切り替え正常

プレースホルダ対応済み

パレット（card_fill / card_border / bar_fill）統合

timeline の間引きロジック・描画成功

header アラート（normal/warn/crit）も正常

✔ 2-5. Collector 起動制御の独立化

collector_control.py の

RUNNING/STＯPPED 判定

pid ファイル管理

taskkill /PID 成功確認
をすべてクリア

ui_health へ Collector 起動停止ボタンを統合

ダッシュボード independent（閉じても collector は動く）

✔ 2-6. Collector の dummy 実行成功
python -m btc_trade_system.features.collector.collector_main


正常起動
→ scheduler がなくても起動できる状態

■ 3. 現在の状態・進捗の正確な把握
項目	状態
Health UI	ほぼ完成（カード・タイムライン・collector制御 完了）
RateController（核）	設計・dummyテスト完了 / 本番統合前
exchanges 設定	読み込み・policy計算まで完成
collector_main 起動管理	完全動作
scheduler 本体	まだ本番実装前（ここが次の核心タスク）
status.json の本番更新	scheduler 統合後に仕上げ
実APIキーの投入前段階	Ready（構造固まった）
■ 4. 次回タスク（優先順）

次に着手すべき順はこれです。

🟦 1) collector_scheduler への RateController の本組み込み

RateController.check(exchange, endpoint) を scheduler の各 call 前に統合

soft/hard の状態を health_svc へ反映

429 のハード検知 → rate_hard → status.json

soft 時 → warn → status.json

collector 健全性（health）の最重要ロジック

➡ これが収集器の「本体の頭脳」になる。

🟦 2) scheduler の構造最適化とログ入出力確立

公式エンドポイント（board, ticker, execution の各 fetch）に対し
RateController → fetch → status 更新 → timeline 更新

処理単位を固定（1sごと / endpointごと）

🟦 3) collector 起動時のバックグラウンド化

現在：外部ウィンドウが開く
対応：

subprocess.CREATE_NO_WINDOW（Windows）

または DETACHED_PROCESS で非表示起動

UI 側には pid だけ出す

🟦 4) 健全性タブの UI 調整（要望対応）

Collector ボタンを「自動更新（このタブ）」と同じ行右側に配置

行折り返し回避

横一列でレイアウト調整
（コードは既に90%完了。細部調整だけ。）

🟦 5) 本番API投入前の preflight validation

各取引所の official_max_rps のデフォルト値レビュー

未入力がある場合の表示チェック

secret/exchange.ini の読取り状態

collector_main → scheduler → health → UI の統合テスト

■ 5. 気が付いた点（重要）
● A）設定体系の統一が非常にうまく行っている

BTC_TS_CONFIG_DIR = D:\BtcTS_V1\config\ui
で collector / health / settings / monitoring が全て同じ root を参照できる状態。

これは
「3台運用（開発機 / メイン機 / NAS）」
の構成において
設定ファイルの同期だけで全デバイスの挙動を統一できる
という設計的に理想状態。

● B）健康状態のレート境界も設計が整った

WARN＝soft_limit
CRIT＝hard_limit（429またはそれに準ずる状態）
→ health_svc 側とカード表示の整合性が完璧。

● C）collector_control（UI）は完全に独立化成功

UI 側で collector の起動／停止

ダッシュボードを閉じても collector は落ちない

メイン機／開発機の使い分けに必須の仕組みが完成

■ 6. 残る問題点と注意点
⚠ 1. scheduler がまだ空で collector は「動いているだけ」

現在は collector_main が起動しているだけで
本番の収集サイクルはまだ動いていない
（status.json は dummy または空のまま）

次回はここを埋めるのが最重要。

⚠ 2. RateController（本体）は dummy テストのみ

まだ実 API のレスポンスや429挙動と結びついていない。

⚠ 3. health_timeline の書き込みは最小限

本番では収集のたびに timeline に追記する必要がある。
→ scheduler で要実装。

⚠ 4. ダッシュボードと collector が独立したことで

「どちらが status.json を書くのか」が明確に collector 側になった。
→ UI 側では書かない設計でOK。

■ 7. 最後に

いまの状態は 「本番収集器を組み込み始められる直前」 です。
ここまでの土台作りは完璧と言えます。

次は本格的な

collector_scheduler の実装 → collector の本稼働化

これが収集器の中核で、いよいよ“実働系”の段階に入ります。