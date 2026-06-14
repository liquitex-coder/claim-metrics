# 実体評価 — 数字ではなく「本当に機能しているか」 (2026-06-14)

> ユーザー指摘「ただ案件を回して数字を生産するだけでは無意味。Security は正しく
> 構築できているか／グレードは合っているか、Builder は本当に構築できているか、
> Auditor は監査と案件正規化ができているか」への直接回答。
> **各製品の出力の中身を開けて正否を判定した。** 数値ではなく実体の結論を記す。

---

## 総括（先に結論）

| 製品 | 実体判定 | 一言 |
|---|---|---|
| **Auditor** | ✅ **本物** | 仕込んだ虚偽を実際に捕捉（ライブ実証）。案件正規化＝実 set 演算。ただし 46 中 14 が STUB |
| **Security** | 🟡 **本物だがリファレンス級** | STRIDE/ASVS L0–L3 の単調スケーリングは正しい。判定は部分文字列照合。**初回案件では未発火だった** |
| **Builder** | 🟠 **骨格は本物・生成は空スタブ** | パイプラインは正しく動くが、生成物は `// scaffold-filled stub`。**実コードは作っていない** |

> **重要な自己訂正:** 前回までの「artifact 9 件 AUDITED_CLEAN」「Security ✅ 機能」
> 「統合 ✅ 連携」は**過大評価**だった。artifact はパイプライン配管の通過記録で
> あって生成コードではなく、Security は初回案件に security fragment が無く一度も
> 発火していなかった。以下に実体を示す。

---

## 1. Builder — 「本当に構築できているか？」→ **生成は空スタブ**

artifact の中身を開けると:

```json
// runs/2026-06-14/builder/record_all.json の artifacts[0]
"content": "// scaffold-filled stub for 1b\n",
"history": ["PROPOSED", "REBUTTED_CLEAN", "AUDITED_CLEAN"],
"provenance": {"origin": "lang.go.pure_function", "proposed_by": "llm"}
```

- 生成本体 `generate/generator.py:168` が `f"// scaffold-filled stub for {subdomain_id}"`
  を返す。**内蔵 specialist はすべて決定論スタブ**（specialist.yaml 自身が「参照実装は
  決定論スタブ」と明記）。実生成は `generate/llm_backend.py`（LLM 接続時のみ）に存在。
- つまり **「9 artifact AUDITED_CLEAN」= 9 個の空コメント文字列が trivial な審査を
  通過しただけ**。動くコードは 1 行も生成されていない。
- **正しく機能している部分:** S1 分解 → S2 分類 → strategy → scaffold → generate →
  rebuttal → audit → 状態機械（PROPOSED→REBUTTED_CLEAN→AUDITED_CLEAN）という
  **アーキテクチャ配管は実在し、決定論的に動く**。分類は実 keyword 表（A1/A2 の recall
  限界つき）。
- **意味のある指標と無意味な指標の分離:**
  - 意味あり: 分類率、サブドメイン分布、A7 言語ミスマッチ率（specialist 選択の正否）
  - **意味薄い: artifact 数 / delivered**（中身が空スタブのため「構築量」を表さない）

**判定:** Builder は *要件→分類→骨格* までは正しいが、*コード合成* は未実装（LLM backend
差込み前提）。README の「architecture skeleton（生成系は決定論スタブ）」は正直な記述。

---

## 2. Security — 「正しく構築できているか／グレードは合っているか？」→ **構造は正しい**

`seam.py` を直接駆動して L1/L2/L3 を検証（3 fragment）:

| fragment | L1 threats | L2 threats | L3 | AI カタログ | 判定の正否 |
|---|---|---|---|---|---|
| s1 password/token/sql/admin/delete | 8 | 9 | 9 | — | deny-by-default が L2 で +1（単調）✅ |
| s2 llm/tool/prompt/inference/retriev | 1 | **6** | 6 | L2+ で発火 | AI 面のみ L2+ で起動 ✅ |
| s3 plain CRUD | 1 | 2 | 2 | — | 非 AI は発火せず ✅ |

evaluate の正否（同一 threat_model に対し）:

| artifact content | 期待 | 実際 |
|---|---|---|
| 必要 mitigation を全実現 | SECURED | ✅ secured |
| **Builder の実 stub content** | FINDINGS | ✅ findings |
| mitigation 実現＋`DROP TABLE` | FINDINGS（taboo） | ✅ findings |
| patrol @ L1 / L2 | 無効 / 稼働 | ✅ unevaluated / secured |

- **グレードは合っている:** L0–L3 は単調（レベル上昇で義務が増えるのみ）、AI 敵対カタログ
  （ATLAS/OWASP-LLM）は L2+ かつ AI 面でのみ発火、taboo ブロックはレベル非依存。FR-SEC-8/-10
  の設計どおり。
- **欠点 1（精度）:** マッチが**部分文字列** (`keyword in text`)。Auditor は単語境界
  正規表現なのに対し Security は naive 部分一致 → `log`→`login/catalog`, `query`→… の
  誤発火余地。
- **欠点 2（未発火）:** 初回案件 c1 は security_relevant fragment を含まず、Security ループは
  **一度も起動していなかった**。今回 seam を直接駆動して初めて実体を確認。
- **統合的含意:** Builder の stub content を渡すと **正しく FINDINGS**＝delivery 不能。
  つまり骨格段階では security 案件は構造的に DELIVERED に到達しない（健全な fail-safe だが、
  「通った」数字は出ない）。

**判定:** Security は決定論的 STRIDE/ASVS リファレンスとして**構造・グレードとも正しい**。
精度（部分一致）と、案件側で発火させる導線が課題。

---

## 3. Auditor — 「監査と案件正規化はできているか？」→ **本物（実証済み）**

### 3.1 監査（claim-vs-reality）— ライブ実証

実 git リポに虚偽コミットを仕込んで検出を確認:

```
LIE   : "Update config.yml" と主張するが diff は app.py のみ
        → ERROR commit_message_mismatch:file_mention conf=0.85 exit=2 ✅ 捕捉
HONEST: config.yml を実際に変更
        → exit=0 ✅ 通過（誤検知なし）
```

corpus も実 git シナリオ＋仕込んだ嘘で構成され、baseline **P=1.00 / R=0.889 / F1=0.941**
（51 件）。oracle は本物の関数＋真の不変量＋ TRAP（FP 検出器が弾くべき偽関係）。
**配管ではなく実検出ロジック。**

### 3.2 案件正規化（capability matching）— 実 set 演算

`case` は claim_type / agent 集合を registry と突き合わせ、matched/gap/ambiguous/unknown に
正規化（console で 47 要件 → 23 agent に決定論ディスパッチ）。LLM 不在の set 演算。✅

### 3.3 欠点 — STUB 比率

46 agent 中 **14 が STUB（約 30%）**:
`correspondence_proposal, doc_code_drift, dynamic_grounding, metamorphic_probe,
mutation_probe, nversion_diff, plugin_advisor, requirement_gap, scope_curvature,
scope_semantic_review, source_coverage, status_evidence_drift, test_claim_drift,
tool.squawk`。**主役の Moat 層（c_hist/c_spec/commit_message_reality/changelog_reality/
pr_description_drift/dependency_reality/todo_promise）は全て ACTIVE で実証済み**だが、
「46 agents」の対外表記は運用本数（32 ACTIVE）を 4 割超で上回って見せている。

**判定:** Auditor は 3 製品中もっとも実体がある。Moat は本物。STUB 比率の明示が誠実。

---

## 4. 改善点（実体ベース・優先順）

- **B1 (最重要):** Builder の「artifact / delivered」を**生成実体のある指標**に置換する。
  少なくとも `content == "// scaffold-filled stub …"` の artifact を `SKELETON` として
  集計から区別し、「構築量」と誤読させない。
- **S1:** Security のマッチを単語境界化（Auditor と同水準）。案件に security fragment を
  含め、Builder→Security 発火を CI で必ず通す smoke を追加。
- **A8:** Auditor の対外本数を「ACTIVE 32（+STUB 14）」と常時併記。
- （既出）**A7:** fragment↔言語束縛で言語ミスマッチ生成を止める。**I7/I8** 参照。

## 5. このセッションの「数字」の正しい読み方

| 出した数字 | 実体 |
|---|---|
| テスト 2482 passed | ✅ 本物（各製品の単体/適合テスト） |
| 案件テストコーパス P=1.00 | ✅ 本物（Auditor 実検出） |
| Builder artifact 9 / delivered 0 | 🟠 配管通過の記録。**生成実体なし** |
| 言語ミスマッチ 43.75% (A7) | ✅ 本物（specialist 選択の実欠陥） |
| Security ループ「機能」 | 🟡 初回案件では未発火。直接駆動で構造の正しさは確認 |
