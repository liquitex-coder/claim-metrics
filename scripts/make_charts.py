#!/usr/bin/env python3
"""stats.json から統計グラフ (PNG) を生成する。依存: matplotlib のみ。

  python3 scripts/make_charts.py runs/2026-06-14
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as _fm

# 日本語フォント (CJK) を登録。無ければ DejaVu のまま (豆腐化)。
for _fp in ("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
            "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"):
    if Path(_fp).exists():
        _fm.fontManager.addfont(_fp)
        plt.rcParams["font.family"] = _fm.FontProperties(fname=_fp).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False

RUN = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/2026-06-14")
OUT = RUN / "charts"
OUT.mkdir(exist_ok=True)
S = json.load(open(RUN / "stats.json"))

# 共通スタイル
plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "axes.axisbelow": True, "grid.alpha": 0.3})
C = {"ok": "#2e8b57", "warn": "#e0a800", "bad": "#c0392b", "blue": "#2c6fbb",
     "purple": "#7d5ba6", "gray": "#888"}


def save(fig, name):
    p = OUT / name
    fig.tight_layout()
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)


# 1) Builder: artifacts vs open questions per axis -------------------------
b = S["builder"]
axes = ["go", "typescript", "react", "python", "all"]
arts = [b[a]["artifacts_total"] for a in axes]
oq = [b[a]["open_questions"] for a in axes]
fig, ax = plt.subplots(figsize=(7, 4))
x = range(len(axes))
ax.bar([i - 0.2 for i in x], arts, 0.4, label="AUDITED_CLEAN artifacts", color=C["ok"])
ax.bar([i + 0.2 for i in x], oq, 0.4, label="open questions", color=C["warn"])
ax.set_xticks(list(x)); ax.set_xticklabels(axes)
ax.set_title("Builder: 言語/ツール/FW 軸別 生成被覆 (10 fragment 中)")
ax.set_ylabel("count"); ax.legend()
for i, v in enumerate(arts): ax.text(i - 0.2, v + 0.1, str(v), ha="center", fontsize=8)
for i, v in enumerate(oq): ax.text(i + 0.2, v + 0.1, str(v), ha="center", fontsize=8)
save(fig, "01_builder_axis_coverage.png")

# 2) Classification distribution ------------------------------------------
cls = b["all"]["classifications"]
order = sorted(cls, key=lambda k: (-cls[k], k))
fig, ax = plt.subplots(figsize=(7, 4))
cols = [C["bad"] if k == "8" else C["blue"] for k in order]
ax.bar(order, [cls[k] for k in order], color=cols)
ax.set_title("Builder: サブドメイン分類分布 (赤=⑧ UNCLASSIFIED)")
ax.set_ylabel("fragments")
for i, k in enumerate(order): ax.text(i, cls[k] + 0.03, str(cls[k]), ha="center", fontsize=8)
save(fig, "02_classification_dist.png")

# 3) Auditor self-apply: claims per repo ----------------------------------
au = S["auditor"]
repos = list(au)
claims = [au[r]["total_claims"] for r in repos]
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(repos, claims, color=C["purple"])
ax.set_title("Auditor 自己適用: リポ別 claim 数 (全て types-PyYAML 起因 / real defect 0)")
ax.set_ylabel("claims")
for i, v in enumerate(claims): ax.text(i, v + 0.1, str(v), ha="center", fontsize=8)
save(fig, "03_auditor_self_claims.png")

# 4) Case-test corpus precision/recall/f1 ---------------------------------
pd = S["existing_case_tests"]["synthetic_corpus"]["per_detector"]
dets = list(pd)
short = [d.split(".")[-1] for d in dets]
prec = [pd[d]["precision"] for d in dets]
rec = [pd[d]["recall"] for d in dets]
f1 = [pd[d]["f1"] for d in dets]
fig, ax = plt.subplots(figsize=(9, 4.2))
x = range(len(dets)); w = 0.27
ax.bar([i - w for i in x], prec, w, label="precision", color=C["ok"])
ax.bar(list(x), rec, w, label="recall", color=C["blue"])
ax.bar([i + w for i in x], f1, w, label="f1", color=C["purple"])
ax.set_xticks(list(x)); ax.set_xticklabels(short, rotation=30, ha="right")
ax.set_ylim(0, 1.08); ax.set_title("既存案件テストコーパス (51 ケース): detector 別 P/R/F1")
ax.legend(ncol=3, loc="lower right")
save(fig, "04_corpus_prf.png")

# 5) Inventory donuts: status + tier --------------------------------------
inv = S["inventory"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4))
st = inv["by_status"]
a1.pie(list(st.values()), labels=[f"{k} ({v})" for k, v in st.items()],
       colors=[C["ok"], C["gray"]], autopct="%1.0f%%", startangle=90,
       wedgeprops={"width": 0.42})
a1.set_title(f"Auditor agents 状態 (計 {inv['auditor_agents_total']})")
tier = inv["by_tier"]
tk = sorted(tier)
a2.bar([f"Tier{t}" for t in tk], [tier[t] for t in tk], color=C["blue"])
a2.set_title("Auditor agents tier 分布")
for i, t in enumerate(tk): a2.text(i, tier[t] + 0.2, str(tier[t]), ha="center", fontsize=8)
save(fig, "05_inventory.png")

# 6) Tests passed per repo ------------------------------------------------
t = S["tests"]
trepos = [k for k in t if k != "total_passed"]
passed = [t[r]["passed"] for r in trepos]
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(trepos, passed, color=C["ok"])
ax.set_title(f"テスト横断: passed (合計 {t['total_passed']}, failed 0)")
ax.set_ylabel("passed")
for i, v in enumerate(passed): ax.text(i, v + max(passed) * 0.01, str(v), ha="center", fontsize=8)
save(fig, "06_tests.png")

# 7) Anomaly disposition --------------------------------------------------
disp = {"環境修正で解消\n(A4,A5)": 2, "設計どおり\n(A6)": 1, "改善提案として残置\n(A1,A2,A3)": 3}
fig, ax = plt.subplots(figsize=(6, 4))
ax.pie(list(disp.values()), labels=list(disp.keys()),
       colors=[C["ok"], C["gray"], C["warn"]], autopct=lambda p: f"{round(p*6/100)}",
       startangle=120)
ax.set_title("検出した異常 6 件の対応区分")
save(fig, "07_anomaly_disposition.png")

print("OK ->", OUT)
