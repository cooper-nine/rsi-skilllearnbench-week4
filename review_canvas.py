"""Validate a submitted canvas and replay its archived platform checkpoints."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "platform/canvas/runner"), str(ROOT / "qwen")]
from run_canvas_campaign import KEYS, stages


def read(path):
    return json.loads(path.read_bytes())


def checkpoints(folder, task):
    if (folder / "qwen.txt").is_file():
        records = [json.loads(line) for line in (folder / "qwen.txt").read_text(encoding="utf8").splitlines()]
        return records, read(folder / "flow.json")
    records = []
    visited = set()
    spec = None
    while folder.is_dir() and folder not in visited:
        visited.add(folder)
        run = read(folder / "run.json")
        records[:0] = run["checkpoints"]
        if spec is None and (folder / "flow.json").is_file():
            spec = read(folder / "flow.json")
        source = run.get("source_run")
        if not source:
            break
        folder = folder.parent.parent / source / task
    if spec is None:
        raise ValueError("Missing archived Skill definitions")
    return records, spec


def review(request):
    with (ROOT / "results/platform/comparison.csv").open(encoding="utf8", newline="") as stream:
        cases = {row["task"]: row for row in csv.DictReader(stream)}
    target = request["target"]
    if target not in cases:
        raise ValueError("Choose one of the ten benchmark cases")
    family = target.rsplit("-", 1)[0]
    path = stages(request["graphs"][KEYS[family]])
    evidence = ROOT / cases[target]["platform_evidence"]
    records, spec = checkpoints(evidence, target)
    splits = {node["id"]: node for node in spec["nodes"]}
    ids = [node["id"] for node in path]
    if len(ids) != len(splits) or set(ids) != set(splits):
        raise ValueError("The submitted canvas must contain each archived Skill exactly once")
    recorded = {}
    for entry in records:
        if "output" in entry:
            recorded[entry["stage"]] = entry["output"]
    if ids != [node["id"] for node in spec["nodes"]]:
        raise ValueError("The submitted node order differs from the archived run")
    output = [
        {"id": node["id"], "title": node.get("name", node["id"]),
         "contract": node["pendant"]["data"]["detail"],
         "skill": splits[node["id"]]["text"], "output": recorded[node["id"]]}
        for node in path
    ]
    checks = read(evidence / "ctrf.json")["results"]["tests"]
    return {"mode": "archive", "task": target, "nodes": output,
            "official": {"passed": sum(test["status"] == "passed" for test in checks),
                         "total": len(checks), "reward": (evidence / "reward.txt").read_text().strip()}}


if __name__ == "__main__":
    try:
        print(json.dumps(review(json.loads(sys.stdin.buffer.read())), ensure_ascii=True))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True))
        sys.exit(1)
