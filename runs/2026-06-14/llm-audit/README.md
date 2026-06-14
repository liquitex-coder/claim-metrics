# Auditor を LLM（生成エージェント）に適用

Claim-Auditor の Moat 層（claim-vs-reality）を、本セッションの LLM エージェント自身が
作成したコミットの主張へ向けて適用した結果。「AI が言ったこと」と「実際の diff」の
乖離を決定論的に検証する、という Auditor のコア用途を LLM へ self-apply している。

- 対象: `claim-metrics` HEAD コミット（統合検証ランの追加）
- case: [`../../../.claim-auditor/case.yaml`](../../../.claim-auditor/case.yaml)
- 生結果: [`llm_claim_audit.json`](llm_claim_audit.json)

## 結果

| agent | claims | exit |
|---|---|---|
| process.commit_message_reality | 0 | 0 |
| process.changelog_reality | 0 | 0 |
| process.todo_promise | 0 | 0 |
| process.pr_description_drift | 0 | 0 |

**判定: CLEAN（虚偽申告 0 件）** — コミットメッセージで述べたファイル言及・変更主張が
実 diff と一致。Auditor の LLM 主張監査機能は正常に動作している。
