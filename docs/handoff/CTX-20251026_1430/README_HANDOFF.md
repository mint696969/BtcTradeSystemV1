# BtcTradeSystemV1 Handoff QuickStart

## 起動（ダッシュボード）
PowerShell:
  & "C:\Users\mint777\BtcTradeSystemV1\scripts\run.ps1"

## WhatIf（環境確認のみ）
  & "C:\Users\mint777\BtcTradeSystemV1\scripts\run.ps1" -WhatIf

## データ/ログ実体
  DATA = D:\BtcTS_V1\data
  LOGS = D:\BtcTS_V1\logs

## 含まれる主要ファイル
- env/env_manifest.yaml        : 実行環境（Python/Streamlit/Dirs）
- repo_structure.yaml          : リポ構造＋各ファイル先頭2行
- gpt_context_map.yaml         : GPT再開用の文脈マップ（ポインタ類）
- handover.md                  : ライブ引継ぎメモ（次タスク・気づき）
- diagnostics/status_excerpt.json : 最新 status 抜粋
- diagnostics/audit.tail.jsonl : 監査末尾
- git/HEAD.txt / BRANCH.txt    : 現在のHEAD/ブランチ
- git/recent_commits.txt       : 直近コミット
- git/restore_points.txt       : rp-* タグ一覧
- （任意）git/scripts/*        : -IncludeGitScripts 指定時のみ同梱

