"""Validate published Qwen pairs and export their comparison CSV."""
import csv
import hashlib
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_bytes())


def official_checks(directory):
    tests = read_json(directory / "ctrf.json")["results"]["tests"]
    if not tests:
        raise ValueError(f"Empty official report: {directory}")
    reward = (directory / "reward.txt").read_text().strip()
    return tests, reward


def export(results):
    rows = []
    for case in read_json(PROJECT / "qwen/cases.json"):
        family, instance = case["family"], case["instance"]
        name = f"{family}-{instance}"
        pair = results / "paired-evidence" / name
        baseline = pair / "baseline"
        treatment = pair / "treatment"
        before, baseline_reward = official_checks(baseline)
        after, treatment_reward = official_checks(treatment)
        base_run = read_json(baseline / "run.json")
        qwen_run = read_json(treatment / "run.json")
        failed = [test["name"] for test in before if test["status"] == "failed"]
        if baseline_reward != "0" or not failed or base_run["run"] != case["baseline_run"]:
            raise ValueError(f"Missing paired baseline failure: {name}")
        if (treatment_reward != "1" or not qwen_run["official_pass"]
                or qwen_run["model"] != "qwen3.5-plus" or qwen_run["verifier_exit"] != 0
                or len(after) != qwen_run["checks"]
                or any(test["status"] != "passed" for test in after)):
            raise ValueError(f"Missing full Qwen pass: {name}")
        if hashlib.sha256((treatment / "flow.json").read_bytes()).hexdigest() != qwen_run["flow_sha256"]:
            raise ValueError(f"Flow hash mismatch: {name}")
        platform_evidence = treatment / "platform-run.json"
        checkpoints = treatment / "checkpoints.json"
        if checkpoints.is_file():
            stages = [item["stage"] for item in read_json(checkpoints)]
            if stages != qwen_run["delivered_checkpoints"]:
                raise ValueError(f"Checkpoint mismatch: {name}")
        elif qwen_run["delivered_checkpoints"]:
            raise ValueError(f"Missing checkpoints: {name}")
        rows.append(dict(
            family=family, instance=instance, baseline_run=base_run["run"],
            baseline_passed=False, checks_failed_before=" | ".join(failed),
            status="valid", checks_passed_before=sum(test["status"] == "passed" for test in before),
            checks_passed_after=len(after), treatment_run=qwen_run["run_id"],
            treatment_passed=True, checks_before=len(before), checks_after=len(after),
            checks_failed_after="", treatment_origin="platform" if platform_evidence.is_file() else "local-qwen-api",
            platform_run_id=read_json(platform_evidence)["platform_run_id"] if platform_evidence.is_file() else "",
        ))
    with (results / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    pairs = export(PROJECT / "results")
    print(f"Verified {len(pairs)} official Qwen passes against {len(pairs)} failing baselines.")
