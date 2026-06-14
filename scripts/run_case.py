#!/usr/bin/env python3
"""1 案件を Builder→(分類/生成)→Auditor 視点で回し、per-case summary.json を書く。

  python3 scripts/run_case.py <case_dir> [--axes go,typescript,python,...]

<case_dir>/requirements.md を入力に、classify と axis 別 build を実行し、
<case_dir>/summary.json と <case_dir>/records/ を生成する。決定論的。
"""
from __future__ import annotations
import argparse, json, subprocess, sys, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]            # claim-metrics/
WS = ROOT.parent                                       # /home/user
BUILDER = WS / "Claim-builder"


def build_env():
    import os
    e = dict(os.environ)
    e["PYTHONPATH"] = str(BUILDER / "src")
    return e


def cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "claim_builder.cli", *args],
                          capture_output=True, text=True, env=build_env())


def classify_counts(req: Path) -> dict:
    cp = cli(["classify", str(req)])
    counts: collections.Counter = collections.Counter()
    for line in cp.stdout.splitlines():
        parts = line.split()
        # frag-001   1b (PROVABLE) ...
        if len(parts) >= 2 and parts[0].startswith("frag-"):
            counts[parts[1]] += 1
    total = sum(counts.values())
    classified = total - counts.get("8", 0)
    return {"by_subdomain": dict(counts), "fragments": total,
            "classified": classified,
            "classified_rate": round(classified / total, 4) if total else 0.0}


def build_axis(req: Path, recdir: Path, axis: str, flag: list[str]) -> dict:
    rec = recdir / f"record_{axis}.json"
    cli(["build", str(req), *flag, "--record", str(rec)])
    d = json.loads(rec.read_text())
    arts = d["artifacts"]
    return {
        "artifacts_total": len(arts),
        "artifact_states": dict(collections.Counter(a["state"] for a in arts)),
        "assurance": dict(collections.Counter(a["assurance"] for a in arts)),
        "specialists_used": dict(collections.Counter(a["provenance"]["origin"] for a in arts)),
        "open_questions": len(d["open_questions"]),
        "stage_records": len(d["stage_records"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("case_dir")
    ap.add_argument("--axes", default="all")
    a = ap.parse_args()
    cdir = Path(a.case_dir)
    req = cdir / "requirements.md"
    recdir = cdir / "records"; recdir.mkdir(exist_ok=True)

    flags = {"go": ["--language", "go"], "typescript": ["--language", "typescript"],
             "python": ["--language", "python"], "rust": ["--language", "rust"],
             "sql": ["--language", "sql"], "shell": ["--language", "shell"],
             "react": ["--framework", "react"], "all": []}
    axes = [x.strip() for x in a.axes.split(",") if x.strip()]
    if "all" not in axes:
        axes.append("all")

    summary = {"case_id": cdir.name, "classification": classify_counts(req), "builder": {}}
    for ax in axes:
        summary["builder"][ax] = build_axis(req, recdir, ax, flags.get(ax, []))

    (cdir / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    b = summary["builder"]["all"]
    print(f"[{cdir.name}] frags={summary['classification']['fragments']} "
          f"classified={summary['classification']['classified_rate']*100:.0f}% "
          f"artifacts(all)={b['artifacts_total']} open_q={b['open_questions']} "
          f"specialists={sorted(b['specialists_used'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
