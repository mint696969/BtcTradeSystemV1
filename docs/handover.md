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

🧭 BtcTradeSystem V1 — 情報収集ドメイン 開発引き継ぎ書（Collector / Health 現行）

最終更新：2025-11-07

🎯 現在の開発段階
フェーズ 名称 状況 備考
Phase 1 Collector 基盤構築 ✅ 完了（基礎レイヤ） heartbeat → status 連携・レート制御の足場整備済み
Phase 2 Health システム ⚙️ 進行中（UI まで完了） 健全性 UI・設定 UI・status 反映は実装済、制御命令部分未実装
Phase 3 Ops-Audit 構築 ⏸ 未着手 Collector/Health の監査イベントを蓄積開始予定
✅ 完了済み項目（ロードマップ対照）
🧱 Collector 基盤構築（Phase 1）

collector_status.py：status.json の原子的更新／fsync 対応済み。

collector_rate.py：取引所ごと rate 制御（bucket 制御／burst 制限）導入。

collector_scheduler.py：周期制御・優先度スケジュール稼働確認。

collector_entry.py / ops/collector/entry.py：

start / status CLI 実装。

PID ロック／多重起動防止（--force 対応）。

endpoints_def.yaml：

唯一の正として collector endpoints を集中管理。

atomic 書込・defaults/current の混在禁止。

set_collector.py：

Streamlit 設定 UI（取引所・endpoint・rate 編集）。

commit() による安全保存＋監査出力実装。

UI 統合：

ダッシュボードタブなし設計（Collector はバックグラウンド専用）。

設定 UI から Collector 制御可能（後述拡張予定）。

動作確認：

heartbeat / status 両方が数秒単位で更新されることを確認済。

🩺 Health システム構築（Phase 2）

ui_health.py：

健全性カード／タイムライン表示／自動更新切替／閾値スロット UI 実装。

get_status() でヘッダー色を反映（normal/warn/crit）。

health_svc.py：status.json 読込・整形ロジック確立。

設定連携：

tabs.yaml + set_health.py 設計ルールにより、dashboard.py/settings.py 改変不要 で UI 追加完了。

UI 登録ルール仕様書作成済み（GPT 混乱防止仕様）。

⚙️ 進行中タスク
項目 内容 状況
bitFlyer 実 API 化 ダミー → 実ランナーへ差替（orderbook/trades） 着手前
RateController 拡張 各 exchange 毎に動的 burst 調整 設計検討中
Health⇄Collector 連携 Health による Collector 停止/slow_down 制御 未実装
set_collector の検証 UI 保存 →endpoints_def.yaml の diff 追跡 動作検証済（軽度）
dev_audit 監査 設定・heartbeat イベント出力 一部出力済み（粒度調整必要）
📋 次に行うこと（Phase 2〜3 ブリッジ）

bitflyer_public.py 実 API 化

REST/WS どちらでも heartbeat 更新を継続。

API キー認証・例外捕捉・再試行・429 抑制を collector_rate と統合。

Health→Collector 制御連携

health_actions.py に slow_down() / restart() / disable() 実装。

Health UI の閾値超過で collector 停止命令を発行。

Ops-Audit 導入

collector / health / settings のイベントを監査ファイル（dev_audit.jsonl）に一元出力。

ops_audit_writer.py と ui_ops_audit.py のプロトタイプ開始。

UI 拡張

health タブ下に “Collector 起動/停止” トグル + 稼働中プロセス数表示（開発モードのみ）。

ドキュメント整備

docs/ui_addition_spec.md 追加済仕様書をドキュメント化。

Collector/Health の Phase2 完了報告をハンドオフ仕様書に反映。

⚠️ 課題・注意点
区分 内容 対応予定
Windows ファイルロック heartbeat 原子的書込で一部タイミング競合発生 \_atomic_write_text() に retry/backoff 導入予定
typing 警告 Streamlit 型ヒントで pylance 警告 cast() 方式に統一で解消済み
PYTHONPATH 問題 PowerShell タブを分けると path 無効 起動時 Set-Location + PYTHONPATH を明示
Collector 停止 UI Health タブ下で開発中のみ有効化予定 st.toggle() 実装で制御
dev_audit 出力過多 minor イベントが多くノイズ化 イベントレベルで抑制機構を導入予定
🧾 今後の必須拡張（Phase3 以降見据え）

Ops-Audit 統合
→ 監査ログを Health/Collector/Settings に統合
→ DQ/Resource/Timeline レポート出力

学習連携前処理
→ status.json と trade 履歴を統合フォーマット化（AI 学習基盤用）

長時間運転テスト
→ 8〜12h 連続稼働＋ status 整合性検証

NAS 同期対応
→ Leader/Secondary 構成テストへ移行（Phase7 準備）

📚 ファイル改変禁止リスト
ファイル 理由
features/dash/dashboard.py タブ自動登録制。手動追加禁止。
features/settings/settings.py 設定セクション自動検出。手動編集禁止。
config/ui/tabs_def.yaml defaults 専用（ユーザー編集禁止）。
✅ 引き継ぎメモ（次 GPT 向け）

本プロジェクトは「Collector と Health の安定連携フェーズ」中。
既に UI 自動登録・設定反映・heartbeat/status 更新は安定稼働済。
次セッションでは bitFlyer API の実ランナー置換と、Health 制御連携から開始すること。
dashboard.py/settings.py の改変は禁止。
tabs.yaml と set\_\*.py のみでタブ追加可能。

---

# BtcTradeSystemV1 — 引き継ぎメモ（2025-11-08）

## 今日の作業

- **健全性タブ（features/settings/set_health.py）** の保存不具合を調査。
- 保存ボタン押下時の `apply_pending()` 呼び出し・dev_audit 出力・mtime 変化を確認。
- Streamlit のセッション管理 (`st.session_state`) を用いた dirty フラグ、pending データ構築ロジックを検証。
- 結果、保存処理が動作しているものの、UI 閉じ操作でも保存が走る、保存ボタン無反応、デフォルト復元不全といった複合バグを確認。
- 問題の根本が `features/settings/settings.py` のハンドラ実装にある可能性を特定。

## 次のタスク

1. **features/settings/settings.py の検証・修正**
   - 「保存」ボタン押下時のみ各タブの `on_save()` を呼ぶように明確化。
   - 「閉じる」「外部クリック」で保存されないよう、pending 破棄処理を追加。
   - `on_default()` 実行時の UI 再反映ロジックを統一。
2. **保存フロー統一テスト**
   - health / dash / audit / collector 全設定で `on_save()` → `settings_svc.save_yaml()` の動作確認。
   - dev_audit.jsonl に `"settings.*.update"` ログが正しく出るかを再確認。
3. **UI 動作確認**
   - 保存ボタンの活性化条件が正しいか（dirty フラグと連動）。
   - 外側クリックで保存されないこと。
   - デフォルト復元時に正しい初期値が表示されること。

## 気づいたこと・改善案

- 設定保存処理は個別タブごとに `on_save()` が存在するが、settings ハブ側が全タブ共通で管理しているため、**pending キー名の統一と破棄処理の共通化**が必要。
- `on_default()` が即書き込みを行う現仕様は UX 的に混乱を生む。→ UI 値のみ復元・保存で確定する方式に統一すべき。
- Streamlit のセッションがタブを跨いで dirty 状態を保持しているため、設定ハブでセッションキー初期化を明示的に行う必要あり。
- 今後の機能追加（collector, health, monitor など）でも同じ保存制御が再利用できるよう、**settings ハブを共通 I/F に整理**すべき。

---

本日の作業記録

設定 UI の統一化を完了

ui_common.py 新規作成（閉じる／デフォルト／保存＋確認ダイアログ＋即時反映、dirty 管理、未保存破棄を共通提供）。

set_dash.py / set_health.py / set_collector.py を共通フッターに統一。

「閉じる」で確実にモーダル終了（破棄＋ rerun）。「保存／デフォルト」は確認 → 実行 → 即時反映に統一。

保存挙動の是正

set_collector.py の commit() を修正。UI の順序を正としてそのまま保存し、削除も正しく反映。

表示と実体の整合

set_health.py 冒頭キャプションを settings_svc.get_paths() に揃え、**適用先（外部 CONFIG）／既定（def）**を明示。

各所の微修正（未使用 import 削除、重複関数除去、軽バリデーション）。

ダッシュボード側の安全化

dashboard.py：\_clamp_dashboard_order() で main 最左固定／collector・basic を Dash から非表示、initial 不整合の自動補正。

運用支援

監査ログの静音フィルタ（PowerShell 3 種）提示。

明日のタスク（不具合と修正方針・テスト）
P1: Collector 設定タブで初期化エラー

症状: st.session_state has no key "set.collector.add_names" エラー。
原因想定:

set_collector.py の初期描画で set.collector.add_names を setdefault していない。

あるいは settings.py（ハブ）でタブ切替時の初期化順より先に参照している箇所がある。

修正案（方針）:

render() の先頭で st.session_state.setdefault("set.collector.add_names", []) を一括初期化。

追加ポップオーバーや一時保持で参照する他のキーも同様に setdefault をそろえる（例：set.collector.pending）。

依存が複数箇所にある場合は、ui_common.py に「prefix キー群の初期化ヘルパ」を追加し、set_collector.py 冒頭で 1 行呼び出しに統一。

テスト:

Dashboard 起動 → 設定 →「コレクター」タブを開く。

エラーが出ないこと。新規追加ポップオーバーが開くこと。

取引所追加 → 保存 →endpoints_def.yaml に反映（順序／削除も）。

P1: 健全性ビューで「Health 情報の取得に失敗」

症状: ヘルス画面冒頭に失敗トースト。
原因想定（優先順）:

config/ui/health.yaml / monitoring.yaml の欠落または形式不整合（デフォルト反映不足）。

health_svc.py のロード時パス分解が settings_svc.get_paths() と不整合。

収集側のデータが未生成／参照パス不一致で eval() が空／例外。

修正案（方針）:

settings_svc.reset_to_default("health") / ("monitoring") を一度実行して正準ファイルを外部 CONFIG へ強制展開。

health_svc.py で参照する既定パスを def/current 一本化（settings_svc.get_paths() を使う）。

依存データ（例：data/collector/status.json 等）必須の場合、空でも動作するフォールバックロジック（空時は“データなし”扱いで落とさない）。

テスト:

設定 → 健全性 →「デフォルト」実行 → 反映後にダッシュへ戻り、エラーが消えること。

閾値変更 → 保存 → カード／タイムラインの見た目が更新。

ログに settings.write.health / settings.write.monitoring が出る。

P2: 保存直後に視覚反映が遅れるケース

症状: 「閉じる」で反映されず、再度設定を開くと反映している。
原因想定:

_exec_\* 実行内の例外で UI.render_section_controls() の mark_dirty()+rerun が到達しない。

ハブ(settings.py)の \_\_settings_dirty 監視が、特定条件で早期 return。

修正案（方針）:

\_exec_save/\_exec_default に try/except を入れて必ず UI 側の処理完了まで到達させる。

settings.py の dirty 検知 →st.rerun() のブロックを一番最後に残し、先に別の rerun/return が走らないよう整序。

テスト:

各タブで保存／デフォルト後、即ヘッダやタブ構成が変わること。

例外を意図的に発生させた場合でも（色値に不正入力等）、UI が固まらないこと。

気づき・課題

初期化と参照の順序

st.session_state は参照前に必ず初期化（setdefault）を徹底。今回の collector のように、追加 UI のポップオーバーで未初期化キーを即参照しがち。

def/current の一本化

settings_svc.get_paths(area) を単一ソースとし、\*\_svc.py 側のハードコードを徐々に排除。

監査の静音運用

本番運用を見据え、今日の PowerShell フィルタを tools/audit_tail_settings.ps1 として常設すると便利。

UI ガイド文

collector のカードに追加した一文（削除の確定方法）、効果的。各タブでも誤操作ポイントに 1 行説明を置くと事故が減る。

---

日報（2025-11-12 JST）
今日やったこと

設定 UI 共通コンポーネントの確定（ui_common.py）

誤操作防止の確認チェック・三ボタン・dirty フラグ・即時反映（rerun）を整理。

折りたたみ時の完全無効化、開閉やタブ切替時のチェック自動リセットを実装。

監査ログ（try/done/error）を追加。

設定 SVC の保存まわりの整備（settings_svc.py）

def スキーマによる未知キー排除、差分保存（def との差分のみ current へ）。

原子的保存、キー単位ロック。

UI 以外からの保存抑止のためのガードとバイパス API（force_save_yaml）を用意。

監査ログ（settings.write._ / settings.default.apply._）を実装。

フォールバック環境での安全動作確認用スモークスクリプトで検証。

旧 config/ui 撤去と参照の整理

旧 current/def を所定の新配置へ移動。

参照取りこぼしの検出 → 修正 → 最終削除。

tabs.yaml は btc_trade_system/config/tabs.yaml を唯一の制御源に。

def ファイルのスキーマ整合

health_def.yaml / collector_def.yaml / exchanges_def.yaml / monitoring_def.yaml / dash_def.yaml などの整合を確認・修正。

YAML 書式エラー（:{→: {）を正規化。

デバッグ用一時実装の撤去

ヘッダーの一時診断関数 \_debug_gear_decision と表示の完全削除、残骸確認済み。

気づいたこと / リスク

保存先の一元化により、環境変数 BTC_TS_CONFIG_DIR が設定されていると current はそちらに出ます。運用で“あるはずの場所”とズレると「保存されていない」と誤認しやすい。運用上は 常にどちらを使うかを統一してください。

settings_svc.load_yaml() は def にないキーを破棄します。つまり「キーを先に保存 → 後で def 追加」という運用は不可。新項目追加は必ず先に def へが原則。

BOM 混入やインデント不整合など YAML エンコード由来の例外が散見されました。保存ファイルは UTF-8（BOM なし）で統一を推奨。

「歯車がアクティブにならない」可能性と切り分け

歯車（設定モーダル）可否の判定は次の 2 条件の AND です。

tabs.yaml の設定有効化

tabs: <key>: の下に settings: true（または文字列で別名キー）になっていること。

例

tabs:
main:
enabled: true
dashboard: true
settings: true # ← これがない/false だと常にグレー

文字列を与えると set\_<その値>.py を見る運用も可（現状は true 推奨）。

対応する settings ビューの存在

btc*trade_system/features/settings/set*<key>.py が存在し、render(st, key=...) など **tabs.yaml の view 指定（既定は render）**をエクスポートしていること。

例：tabs.yaml 側が view: "render" なら、set\_<key>.py に def render(...): が必要。

さらに、実運ログでのチェックが最短です（DEBUG/BOOST 時）：

dev_audit.jsonl に dev.dash.gear.state が出ている場合

reason="tabs.yaml: settings=false-or-missing" → tabs.yaml 側の設定が不足。

reason="module-missing: btc*trade_system.features.settings.set*<key>" → 対応モジュール欠落 or import 失敗。

enabled=true で出ていれば、UI 側の disable 判定の実装がズレている可能性。

切り分け手順（最小実効）

tabs.yaml を確認：対象キーの settings: true を明示。

set\_<key>.py の存在とエクスポート関数名（view 既定は render）を確認。

起動してタブを切り替え、dev_audit.jsonl の dev.dash.gear.state を確認（理由がそのまま根拠）。

それでも無効なら、ダッシュボード側の「アクティブキー伝播」ロジック（session_state['_active_dash_tab']→settings 呼出）を再点検。

---

📘 BtcTradeSystemV1 — ハンドオーバー引き継ぎ書（2025-11-13）
✅ 1. 今チャットで完了した主な成果
1-1. 設定システムの完全再構築（安定版）

settings.py / ui*common.py / settings_svc.py / 各 set*\*.py を総点検し
保存・デフォルト・UI 再描画すべてが安定動作 するように修正完了。

健全性（health/monitoring）の複合 UI も
数値 / カード順 / 色パレットの完全反映＋デフォルト復元 が 100%成功。

デフォルト処理は 差分ファイルの物理削除 に統一し、
UI 表示と実ファイルの整合性を確保。

保存時の外部 CONFIG に
ヘッダー（path/desc）＋差分 YAML のみ を書く最終仕様に統一。

1-2. 外部 CONFIG 正式ルート確立

外部設定ルートは
BTC_TS_CONFIG_DIR（例：D:\BtcTS_V1\config）
を最優先し、存在しなければ repo 内 fallback。

health / monitoring / dash / collector / main 含む全エリアが
正しく差分書き込み＋デフォルト復元されることを確認済。

1-3. 健全性 UI（set_health）の安定版

monitoring.yaml と health.yaml の 二重配線 を完全に整備。

UI は 3 セクション方式（thresholds/order/palette）。

フルセクション構造で pending を作る「安全方式」へ統一。

デフォルト時に UI 値を即座に初期化 → そのまま保存可能。

1-4. settings_svc.py の完全仕上げ

差分抽出ロジックの安定化

\_deep_merge, \_filter_by_schema の最適化

セッションオーバーライド（palette）動作も正常

この構造により：

今後どの set\_\*.py を追加しても、settings_svc を一切触らずに拡張できる状態
が完成しています。

1-5. tabs.yaml/tabs_def.yaml の仕様確定

旧 config/ui/ は正式に廃止し、
btc_trade_system/config/tabs_def.yaml（正準）
外部 CONFIG/tabs.yaml（差分）
の２レイヤで確定。

期待どおり、dashboard.py/settings.py は 新機能追加時に一切編集不要 の構造に調整済。

1-6. 総合テストスクリプト test_settings_full.ps1 完成

dev_audit / CONFIG の差分 / BOOST snapshot の異常値検知をまとめてチェック。

成果物：
tmp/test_settings_full.out.txt にすべての検査結果が出力
→ GPT が読み取りデバッグ可能。

✅ 2. 今チャットで確定した “最終仕様”
2-1. 外部 CONFIG 保存仕様（確定版）
操作 ファイル状態
保存 <area>.yaml に ヘッダー 2 行＋差分のみ を書く
デフォルト <area>.yaml を物理削除（空書き込みしない）
読込 load_yaml = def + current(差分)
2-2. UI の挙動（統一仕様）

設定モーダルを開いた場合は必ず メイン設定タブに統一（ズレ防止）

モーダル閉じたらダッシュボードヘッダー＋タブまとめて再描画

設定モーダル内部：

閉じる → 変更破棄

保存 → CONFIG 更新＋再描画要求

デフォルト → CONFIG 削除＋再描画要求

2-3. 健全性設定（health/monitoring）の仕様

UI は 3 セクション（thresholds/order/palette）

実ファイルは health.yaml / monitoring.yaml の 2 枚に分離

書き込みは 両方へ差分を書き込む（無矛盾化）

2-4. 新規機能追加マニュアル v4 は最新仕様へ完全追従

headers / settings_svc / tabs.yaml の最新仕様反映済

今後の新機能追加は
dashboard.py / settings.py / settings_svc.py を絶対に触らなくて良い

✅ 3. 次チャットで引き継ぐべき “重要ポイント”
3-1. 新規機能追加時の作業順

<feature>\_def.yaml を作る

set\_<feature>.py を作る（テンプレート有）

ui\_<feature>.py を作る（必要であれば）

tabs_def.yaml に登録

（必要なら）providers.py に alert 経路を作る

audit_dev のイベントは自前で emit しない

3-2. 設定タブ追加で注意すること

session_state key は必ず **set.<feature>.\*** 名前空間へ閉じ込める

pending は \_deep_merge で構成

デフォルトは reset_to_default() を必ず呼ぶ

1 UI 内で複数の area を扱う場合は health/monitoring の方式を踏襲

3-3. 開発監査 BOOST スナップショットに注意

BOOST スナップショットには 古い仕様が残る場合あり
→ 解析前に GPT が settings_svc_deprecated の有無を必ずチェックする想定。

✅ 4. 次回タスク案

collector / health / board 更新間隔の API rate 制御の設計

アラート体系の統合（collector の WARN/CRIT をヘッダー本線へ反映）

メインタブ（main）の情報カード群の実装

boards（板）／trades（約定）の可視化カードの再設計

設定モーダルの UI コンポーネント整理（Accordion → Section 化等）
