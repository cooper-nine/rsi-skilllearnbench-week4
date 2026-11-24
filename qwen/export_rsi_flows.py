"""Export four reusable Skill graphs from the exact historical human-authored sources."""
import csv
import hashlib
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
SOURCE = WORKSPACE / "upstream-sparse/skills/human_authored"
DEST = Path(__file__).resolve().parent / "flows"

DESIGNS = {
    "earthquake-plate-calculation": ([5], {
        "geospatial-analysis": [("prepare", None), ("filter", "## Spatial Filtering"),
            ("measure", "## Distance Calculations"), ("verify", "## Common Pitfalls")]}),
    "financial-analysis": ([1, 3], {
        "fuzzy-name-search": [("identify", None)],
        "13f-analyzer": [("calculate", None), ("verify", "### Analyze which funds hold a stock to the most extent")]}),
    "weighted-gdp-calculation": ([1, 4, 5], {
        "xlsx": [("requirements", None), ("read", "## Reading and analyzing data"),
            ("calculate", "## Excel File Workflows"), ("verify", "## Recalculating formulas")]}),
    "stock-data-visualization": ([1, 2, 3, 4], {
        "d3-visualization": [("prepare", None), ("render", "## Determinism rules (non-negotiable)"),
            ("interact", "## Interactive features (tooltips, click handlers, hover effects)"),
            ("verify", None)]}),
}


def export():
    with (WORKSPACE / "submission/results/trials.csv").open(encoding="utf-8-sig", newline="") as file:
        trials = {(r["task"], int(r["instance"])): r for r in csv.DictReader(file)
                  if r["mode"] == "human_authored"}
    DEST.mkdir(exist_ok=True)
    cases = []
    for family, (instances, design) in DESIGNS.items():
        nodes = []
        for skill, stages in design.items():
            path = SOURCE / family / skill / "SKILL.md"
            raw = path.read_bytes()
            lines = raw.decode("utf-8").splitlines(keepends=True)
            offsets = [0] + [lines.index(anchor + next(
                ending for ending in ("\r\n", "\n", "") if anchor + ending in lines))
                if anchor else len(lines) for _, anchor in stages[1:]] + [len(lines)]
            assert offsets == sorted(offsets)
            parts = []
            for idx, (node, _) in enumerate(stages):
                content = "".join(lines[offsets[idx]:offsets[idx + 1]])
                parts.append(content)
                nodes.append({"id": node, "skill": skill, "sourceSha256": hashlib.sha256(raw).hexdigest(),
                              "text": content})
            assert "".join(parts).encode("utf-8") == raw
        flow = {"id": family, "entry": nodes[0]["id"], "nodes": nodes,
                "edges": [{"from": a["id"], "to": b["id"], "on": "complete"} for a, b in zip(nodes, nodes[1:])],
                "retry": {"on": "shell_failure", "limitPerNode": 1}}
        (DEST / f"{family}.json").write_text(json.dumps(flow, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        for instance in instances:
            row = trials[family, instance]
            assert row["passed"] == "0" and row["metrics_complete"] == "True"
            cases.append({"family": family, "instance": instance, "baseline_passed": False,
                          "baseline_run": Path(row["run"]).name})
    assert len(cases) == 10
    (DEST.parent / "cases.json").write_text(json.dumps(cases, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    export()
