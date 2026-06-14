#!/usr/bin/env python3
"""全案件 (run1 + iterations/*) の summary を集計し leaderboard.json と トレンド図を生成。

言語ミスマッチ率: 無フィルタ build('all') が割り当てた specialist の言語が、案件の
intended_languages に含まれない artifact の割合 (A7 の定量化)。
"""
from __future__ import annotations
import json, collections
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as _fm

for _fp in ("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
            "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"):
    if Path(_fp).exists():
        _fm.fontManager.addfont(_fp)
        plt.rcParams["font.family"] = _fm.FontProperties(fname=_fp).get_name()
        break
plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "axes.axisbelow": True,
                     "grid.alpha": 0.3, "axes.unicode_minus": False})

RUN = Path(__file__).resolve().parents[1] / "runs/2026-06-14"
ITER = RUN / "iterations"


def lang_of(origin: str) -> str:
    p = origin.split(".")
    if p[0] == "lang":
        return p[1]
    if origin == "framework.react_component":
        return "typescript"
    if origin == "domain.ml_probabilistic":
        return "python"
    return p[0]


def row_from_summary(case_id, intended, summ):
    cl = summ["classification"]
    allb = summ["builder"]["all"]
    spec = allb["specialists_used"]
    mismatch = sum(n for o, n in spec.items() if lang_of(o) not in intended)
    matched = sum(n for o, n in spec.items() if lang_of(o) in intended)
    # gated artifacts = 正しい言語フィルタ軸の artifact 合計 (all を除く)
    gated = {ax: v["artifacts_total"] for ax, v in summ["builder"].items() if ax != "all"}
    return {
        "case_id": case_id,
        "intended_languages": intended,
        "fragments": cl["fragments"],
        "classified_rate": cl["classified_rate"],
        "artifacts_all": allb["artifacts_total"],
        "open_questions_all": allb["open_questions"],
        "lang_matched_artifacts": matched,
        "lang_mismatched_artifacts": mismatch,
        "lang_mismatch_rate": round(mismatch / allb["artifacts_total"], 4) if allb["artifacts_total"] else 0.0,
        "gated_artifacts": gated,
    }


rows = []
# run1 (claim-feedback) from the main stats.json
s1 = json.load(open(RUN / "stats.json"))
b1 = s1["builder"]["all"]
spec1 = b1["specialists_used"]
intended1 = ["go", "typescript", "python"]
mm1 = sum(n for o, n in spec1.items() if lang_of(o) not in intended1)
rows.append({
    "case_id": "c1-claim-feedback", "intended_languages": intended1,
    "fragments": 10, "classified_rate": 0.9,
    "artifacts_all": b1["artifacts_total"], "open_questions_all": b1["open_questions"],
    "lang_matched_artifacts": b1["artifacts_total"] - mm1, "lang_mismatched_artifacts": mm1,
    "lang_mismatch_rate": round(mm1 / b1["artifacts_total"], 4),
    "gated_artifacts": {k: s1["builder"][k]["artifacts_total"] for k in ("go", "typescript", "react", "python")},
})
# iterations
for cdir in sorted(ITER.glob("c*-*")):
    summ = json.loads((cdir / "summary.json").read_text())
    meta = json.loads((cdir / "meta.json").read_text())
    rows.append(row_from_summary(cdir.name, meta["intended_languages"], summ))

overall = {
    "cases": len(rows),
    "total_fragments": sum(r["fragments"] for r in rows),
    "total_artifacts_all": sum(r["artifacts_all"] for r in rows),
    "total_lang_mismatched": sum(r["lang_mismatched_artifacts"] for r in rows),
    "mean_classified_rate": round(sum(r["classified_rate"] for r in rows) / len(rows), 4),
}
overall["overall_lang_mismatch_rate"] = round(
    overall["total_lang_mismatched"] / overall["total_artifacts_all"], 4) if overall["total_artifacts_all"] else 0.0

lb = {"overall": overall, "cases": rows}
(RUN / "leaderboard.json").write_text(json.dumps(lb, indent=1, ensure_ascii=False))
print(json.dumps(overall, indent=1, ensure_ascii=False))

# ---- trend chart: per-case classified vs mismatch ----
ids = [r["case_id"].split("-", 1)[1] for r in rows]
crate = [r["classified_rate"] * 100 for r in rows]
mrate = [r["lang_mismatch_rate"] * 100 for r in rows]
fig, ax = plt.subplots(figsize=(9, 4.4))
x = range(len(ids)); w = 0.38
ax.bar([i - w / 2 for i in x], crate, w, label="分類率 %", color="#2c6fbb")
ax.bar([i + w / 2 for i in x], mrate, w, label="言語ミスマッチ率 % (A7)", color="#c0392b")
ax.set_xticks(list(x)); ax.set_xticklabels(ids, rotation=20, ha="right")
ax.set_ylim(0, 109); ax.set_ylabel("%")
ax.set_title(f"案件ループ {len(rows)} 件: 分類率 vs 言語ミスマッチ率")
ax.legend()
for i, v in enumerate(crate): ax.text(i - w / 2, v + 1, f"{v:.0f}", ha="center", fontsize=8)
for i, v in enumerate(mrate): ax.text(i + w / 2, v + 1, f"{v:.0f}", ha="center", fontsize=8)
fig.tight_layout()
out = RUN / "charts" / "08_case_loop_trend.png"
fig.savefig(out, bbox_inches="tight")
print("wrote", out)
