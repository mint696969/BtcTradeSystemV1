Git バックアップ・復元システム仕様書（NEXT 正準・改訂版）
1. 目的（再定義・固定）

本仕様書は BtcTS NEXT プロジェクトにおける Git 履歴・作業状態・環境情報を、安全かつ最小構成で退避・復元するための正準仕様を定める。

ChatGPT（GPT）が 次チャットで迷わず開発を再開できることを最優先目的とする

V1 系プロジェクト（btc_trade_system 等）との混在を防止する

バックアップは「保全目的」であり、運用データ・巨大ファイルの保存は対象外とする

2. 正準ディレクトリ構成（確定）
2.1 Repo 正準

Repo root：
C:\BtcTradeSystem

2.2 作業ディレクトリ（非Git管理）

作業場：
C:\BtcTradeSystem\tmp

tmp は常に「作業場」であり、保管庫ではない。

tmp 配下のファイル・ディレクトリは：

実験

検証

一時生成物
を目的とし、Git 管理対象外とする

3. バックアップ種別（正準）
3.1 git bundle（完全履歴バックアップ）

用途：
リポジトリ全履歴の完全保全

生成例：

git bundle create ..\tmp\handoff\pre_reset.bundle --all


特徴：

履歴・タグ・ブランチをすべて含む

通常運用では頻繁に使わない（大容量）

3.2 Restore Point（rp タグ）

命名規則：

rp-YYYYMMDD_HHMMSS


用途：

作業節目の軽量スナップショット

ローカル復元・履歴参照用

管理対象：

Git tag のみ

実データ・zip は含めない

3.3 CTX（ハンドオフ ZIP）【最重要】
3.3.1 目的

CTX は ChatGPT に渡すための最小・正準スナップショットである。

次チャットで GPT が迷わないこと

V1 由来の情報を含まないこと

巨大データ・秘密情報を含まないこと

3.3.2 出力先（固定）

出力ディレクトリ：

C:\BtcTradeSystem\tmp\handoff


出力ファイル名：

CTX-YYYYMMDD_HHMMSS.zip


※ docs/handoff/ は 廃止
※ CTX は tmp/handoff のみを使用する

3.3.3 CTX 同梱物（正準）

CTX ZIP には 以下のみを含める。

必須（欠けたら失敗）

handover.md

直近1日分のみ

過去履歴・長文ログは禁止

SUMMARY.md

次 GPT が最短で状況把握するための要約

REPO_MAP.extract.md

repo_structure.yaml

補助情報

env/environment.txt

env/env_manifest.yaml

git/

BRANCH.txt

HEAD.txt

recent_commits.txt

restore_points.txt

created_tag.txt（存在する場合）

diag/

各ツールの stdout / stderr

3.3.4 絶対に含めてはならないもの

V1 系文字列を含むもの
（例：btc_trade_system, BtcTradeSystemV1 等）

secrets / APIキー

data / logs の実データ

.venv

tmp 作業ファイル（handoff 生成物を除く）

巨大ファイル（目安：10MB 超）

3.3.5 生成失敗時の挙動（確定）

SUMMARY.md は 必須

gen_summary.py が失敗した場合：

CTX 生成は 失敗扱い

ZIP は作らない

diag/gen_summary_stdout_stderr.txt に原因を残す

※ 「ランダムで生成されない」状態は仕様上存在しない
→ 失敗は 必ず環境・引数・パスの問題

4. 復元ポリシー（安全側）
4.1 git bundle 復元

空ディレクトリにのみ復元すること

既存作業ディレクトリへの上書きは禁止

4.2 rp タグ復元

git checkout <tag> を基本

worktree 使用を推奨

危険操作はスクリプトでは防がず、手順で縛る

5. GPT 迷走防止ルール（明文化）

以下に違反した場合、仕様違反＝回帰とみなす。

CTX 内に V1 由来文字列が含まれる

docs/handoff/ が再登場する

tmp が保管庫扱いされる

handover.md に複数日分の履歴が書かれる