# CLAUDE.md — working agreement (Claim platform)

Loaded by Claude Code every session. It encodes the maintainer's standing
instructions. English is the primary language of this document; Japanese notes
(注) are secondary, per the documentation-language rule below.

## Repository context
**claim-metrics** — the platform metrics repository. Currently a stub (README
only); expected to host metrics collection/definitions for the Claim platform.
注: 現状は README のみのスタブ。今後プラットフォームのメトリクス定義/収集を置く想定。

## Standing instructions (恒久指示)

1. **Self-apply the Auditor.** On every task, apply the Auditor discipline to
   *Claude's own output* and to any generated artifact: verify deterministically,
   separate what is *proven* from what is *asserted*, and surface the gap between
   what was "said" and what was "done".
   注: タスクのたびに auditor を自分自身と生成物の両方に適用する。

2. **Report concrete improvements after auditing.** After the self-audit, list
   specific, actionable improvement points with `file:line` evidence — never a
   vague "looks good".
   注: 監査後は改善点を具体的に（根拠つきで）提示する。

3. **Show progress with percentages — per-item and overall.** Report progress as
   both an overall % and a per-task % across the work.
   注: 進捗は個別と全体を %表示する。

4. **Verify with code, not just docs.** Before asserting or implementing, read
   the actual code/files to back the claim. Documentation alone is not evidence.
   注: ドキュメントだけでなくコードを確認し、裏付けを取ってから発言・実装する。

5. **Document language: English primary, Japanese secondary.** Anything pushed to
   GitHub (docs, PR titles/bodies, comments, this file) is English-first with
   Japanese notes where helpful.
   注: GitHub に上げる文書は英語メイン・日本語サブ。

6. **Chat language: Japanese.** Conversational replies to the maintainer are in
   Japanese.
   注: チャットの返答は日本語。

## Out of scope for this tool (本ツールの範囲外)
- **Obsidian chat archiving.** The maintainer manages chat content in Obsidian.
  Claude Code has no access to Obsidian and cannot perform this; it is a
  maintainer-side process, recorded here only for traceability.
  注: 「chat 内容を Obsidian で管理」は本ツールから実行不可（アクセス手段なし）。
  メンテナ側の運用として記録のみ。
