# 実体評価 — 数字ではなく「本当に機能しているか」 (2026-06-14)

> ユーザー指摘「ただ案件を回して数字を生産するだけでは無意味。Security は正しく
> 構築できているか／グレードは合っているか、Builder は本当に構築できているか、
> Auditor は監査と案件正規化ができているか」への直接回答。
> **各製品の出力の中身を開けて正否を判定した。** 数値ではなく実体の結論を記す。

---

## 製品の本質（評価軸の訂正）

> **この製品群は「コード生成器」ではない。** 巨大な DB も推論エンジンも持たず、コードを
> 生むのは LLM の役目。3 製品の価値は **LLM 生成物に嘘がないか（＝真か）を、LLM 非依存で
> 決定論的に判定する「真偽ゲート」** にある（INV-R2 / INV-S2：判定に LLM を入れない）。
> よって正しい評価軸は「コードを生成できたか」ではなく
> **「真を通し、嘘を弾けるか」**。スタブ生成器は LLM が差し込まれるシームに過ぎない。

## 総括（先に結論 — 真偽ゲートとして評価）

| 製品 | 判定対象 | 実体判定（ライブ実証） |
|---|---|---|
| **Auditor** | コミット/PR/変更の主張 vs 実体 | ✅ **本物** 仕込んだ虚偽を捕捉、正直は通過。案件正規化＝実 set 演算 |
| **Builder** | LLM 生成 artifact が主張どおり真か | ✅ **本物** 偽の代数則・捏造引用を実行/接地検査で棄却、真は CLEAN |
| **Security** | 生成物が secure-behavior を実現したか | ✅ **本物** stub→FINDINGS、mitigation実現→SECURED、taboo→FINDINGS、L0–L3 単調 |

3 製品はすべて**同一の思想**＝決定論的・LLM 非依存の真偽ゲート。差は判定対象だけ。

> **自己訂正:** 前回「Builder は生成が空スタブ＝無意味」としたのは**評価軸の誤り**。
> 生成は LLM の仕事で、スタブは LLM 不在時のプレースホルダ（設計どおり）。測るべきは
> 真偽ゲートの正否で、それは下記のとおり本物。なお Security が初回案件で未発火だった点
> （案件側に security fragment が無かった）は事実の訂正として残す。

---

## 1. Builder — 「LLM 生成物の嘘を弾けるか？」→ **真偽ゲートは本物（ライブ実証）**

生成本体（`generator.py:168`）は LLM 不在時に `// scaffold-filled stub` を返すだけ。
**これは欠陥ではない** — 生成は LLM の役目（`generate/llm_backend.py` が差込み点）。
評価すべきは S5 反証 + S6 監査の**真偽ゲート**。同一 ProbeRebuttal に 3 種を投入:

| 投入 artifact | 期待 | 実際 |
|---|---|---|
| 真: 実 involution `f(x)=-x`、引用接地 | CLEAN | ✅ CLEAN |
| 嘘: involution と主張するが `f(x)=x+1` | 棄却 | ✅ REJECTED `metamorphic violation: fn(fn(1)) != 1` |
| 嘘: 本文に無い `ghost` を引用（捏造） | 棄却 | ✅ REJECTED `ungrounded token: ghost` |

真偽ゲートの実体（`rebuttal/probes.py`）:
- **MetamorphicProbe** — artifact が自ら宣言した代数則を Auditor のカタログで**実行**して
  検証（嘘の主張は反例で露見）。claim_auditor 接続時のみ登録、未接続は `unavailable` を
  保持（沈黙して clean にしない）。
- **BoundaryProbe** — 宣言境界で関数を実行、例外＝反例。
- **SpecContradictionProbe** — 引用 `spec:` 句が本文で実現されてなければ矛盾。
- **grounding** — token の引用識別子が本文に無ければ「捏造された自己申告」として棄却。
- **S6 監査** — ungrounded token を `c_spec/c_hist/dependency_reality` 相当で finding 化。

判定は決定論・生成器から独立（FR-BLD-7 `assert_independent`）・LLM 非依存（INV-R2）。

**判定:** Builder の真偽ゲートは**本物**。LLM が生成したコードでも、宣言した性質が偽なら
実行で露見させ、引用の捏造を接地検査で弾く。「真なら通す」も確認済み。
（補足: artifact 数 / delivered は配管通過の計数で「構築量」ではない。意味ある指標は
真偽ゲートの pass/reject 正否と A7 言語ミスマッチ率。）

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
| Builder artifact 9 / delivered 0 | ⚪ 配管通過の計数（生成は LLM の役目）。製品価値は真偽ゲートで、それは✅実証 |
| 言語ミスマッチ 43.75% (A7) | ✅ 本物（specialist 選択の実欠陥） |
| Builder 真偽ゲート pass/reject | ✅ 本物（真→CLEAN、偽の代数則/捏造引用→REJECTED） |
| Security ループ「機能」 | 🟡 初回案件では未発火。直接駆動で構造の正しさは確認 |
