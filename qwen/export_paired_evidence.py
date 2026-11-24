"""Collect raw verifier reports and paired evidence from a prepared benchmark workspace."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil

from run_rsi_retests import completed_status

PROJECT = Path(__file__).resolve().parents[1]
FIELDS = ("family", "instance", "baseline_run", "baseline_passed", "checks_failed_before",
          "status", "checks_passed_before", "checks_passed_after", "treatment_run",
          "treatment_passed", "checks_before", "checks_after", "checks_failed_after",
          "treatment_origin", "platform_run_id")


def read_json(path):
    return json.loads(path.read_bytes())


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verdict(run, destination):
    reports = list(run.rglob("verifier/ctrf.json"))
    if not (run / "config.json").is_file():
        return {}
    result_file = run / "result.json"
    result = read_json(result_file) if result_file.is_file() else {}
    report = reports[0] if len(reports) == 1 else None
    tests = []
    reward = None
    destination.mkdir(parents=True, exist_ok=True)
    if report:
        tests = read_json(report)["results"]["tests"]
        shutil.copyfile(report, destination / "ctrf.json")
        reward_path = report.with_name("reward.txt")
        if reward_path.is_file():
            reward = reward_path.read_text().strip()
            shutil.copyfile(reward_path, destination / "reward.txt")
    config = read_json(run / "config.json")
    original_run = config.get("verifier_replay_of")
    trace_root = run.with_name(original_run) if original_run else run
    trace = next(trace_root.rglob("agent/qwen.txt"), None)
    events = []
    if trace:
        for line in trace.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "flow":
                events.append({key: event[key] for key in ("event", "node", "retries")})
    outputs = list((run / "artifacts").rglob("*"))
    if (run / "answer.json").is_file():
        outputs.append(run / "answer.json")
    official_status = completed_status(run) or None
    family, instance = config["task"], config["instance"]
    evidence = {
        "task": result.get("task_id", f"{family}/{family}-{instance}"), "run": run.name,
        "official_pass": result.get("passed") is True if official_status else None,
        "official_status": official_status, "verifier_exit": result.get("verifier_exit"),
        "agent_exit": result.get("agent_exit"), "agent_timed_out": result.get("agent_timed_out"),
        "error": result.get("error"), "reward": reward,
        "checks": len(tests) if report else None,
        "checks_passed": sum(test["status"] == "passed" for test in tests) if report else None,
        "checks_failed": [test["name"] for test in tests if test["status"] == "failed"],
        "protocol": config.get("protocol"), "upstream_commit": config.get("upstream_commit"),
        "model": config.get("model"), "flow_sha256": config.get("flow_sha256"),
        "baseline_image": config.get("baseline_image"), "platform_run_id": config.get("platform_run_id"),
        "verifier_replay_of": original_run, "flow_events": events,
        "official_report_sha256": digest(report) if report else None,
        "retained_outputs": [{"path": path.relative_to(run).as_posix(), "sha256": digest(path)}
                             for path in sorted(outputs) if path.is_file() and not path.is_symlink()],
    }
    (destination / "run.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")
    return evidence


def export(workspace, results_dir):
    flow_output = workspace / "output/qwen_rsi_flow"
    with (flow_output / "paired-results.csv").open(newline="", encoding="utf-8") as stream:
        paired = {(row["family"], int(row["instance"])): row for row in csv.DictReader(stream)}
    cases = read_json(PROJECT / "qwen/cases.json")
    rows = []
    for case in cases:
        family, instance = case["family"], case["instance"]
        row = paired[(family, instance)]
        root = results_dir / "paired-evidence" / f"{family}-{instance}"
        baseline = verdict(workspace / "output/qwen_formal" / case["baseline_run"], root / "baseline")
        if baseline.get("official_status") != "valid" or baseline["official_pass"]:
            raise ValueError(f"Baseline lacks an official failure for {family}/{instance}")
        treatment = {}
        if row["treatment_run"]:
            trial = flow_output / row["treatment_run"]
            replay = trial.with_name(trial.name + "-verifier-replay")
            if row["status"] == "infrastructure_error" and completed_status(replay) == "valid":
                verdict(trial, root / "original-infrastructure-error")
                trial = replay
                row = dict(row, status="valid", treatment_run=trial.name)
            treatment = verdict(trial, root / "treatment")
        if row["status"] == "valid" and treatment.get("official_status") != "valid":
            raise ValueError(f"Treatment is inconsistent with the verifier for {family}/{instance}")
        if treatment:
            for field in ("model", "protocol", "upstream_commit", "task"):
                if treatment[field] != baseline[field]:
                    raise ValueError(f"Paired {field} differs for {family}/{instance}")
            if treatment["flow_sha256"] != row["flow_sha256"]:
                raise ValueError(f"Flow hash differs for {family}/{instance}")
        rows.append(dict(
            family=family, instance=instance, baseline_run=case["baseline_run"], baseline_passed=False,
            checks_failed_before=" | ".join(baseline["checks_failed"]), status=row["status"],
            checks_passed_before=baseline["checks_passed"], checks_passed_after=treatment.get("checks_passed"),
            treatment_run=row["treatment_run"], treatment_passed=treatment.get("official_pass"),
            checks_before=baseline["checks"], checks_after=treatment.get("checks"),
            checks_failed_after=" | ".join(treatment.get("checks_failed", [])),
            treatment_origin=row.get("treatment_origin"), platform_run_id=row.get("platform_run_id"),
        ))
    with (results_dir / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    for row in export(args.workspace.resolve(), PROJECT / "results"):
        print(row["family"], row["instance"], row["status"], row["treatment_passed"])
