"""Run the ten preselected paired trials through the official task runner."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
QWEN = ROOT / "qwen"
OUTPUT = ROOT / "output/qwen_rsi_flow"
STATE = ROOT / "output/qwen_budget_campaign"
FIELDS = ["family", "instance", "baseline_run", "baseline_passed", "flow_sha256",
          "status", "treatment_passed", "treatment_run"]


def main():
    from budget_proxy import start

    cases = json.loads((QWEN / "cases.json").read_bytes())
    for case in cases:
        graph = QWEN / "flows" / (case["family"] + ".json")
        case["flow_sha256"] = hashlib.sha256(graph.read_bytes()).hexdigest()
        case["status"] = "pending"
    subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"], check=True, timeout=15)
    if not (STATE / "budget-limit.json").exists():
        raise SystemExit("Existing experiment budget configuration is required")
    if not (STATE / "metrics-ready.json").exists():
        raise SystemExit("Existing baseline metrics gate is required")
    if not os.environ.get("DASHSCOPE_API_KEY"):
        raise SystemExit("DASHSCOPE_API_KEY is unavailable")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    server, secret = start(STATE)
    env = dict(os.environ, SLB_STATE="qwen_budget_campaign",
               DASHSCOPE_API_KEY=secret, QWEN_BASE_URL=f"http://host.docker.internal:{server.server_port}",
               PYTHONUTF8="1")
    try:
        for case in cases:
            family, instance, digest = case["family"], case["instance"], case["flow_sha256"]
            previous = set(OUTPUT.glob("*/config.json"))
            matching = []
            for config in previous:
                data = json.loads(config.read_bytes())
                if (data.get("task"), data.get("instance"), data.get("flow_sha256")) == (family, instance, digest):
                    matching.append(config.parent)
            valid = next((p for p in sorted(matching, reverse=True) if completed_status(p)), None)
            if not valid:
                log = OUTPUT / f"{family}-{instance}.log"
                with log.open("a", encoding="utf-8") as stream:
                    subprocess.run([sys.executable, str(QWEN / "run_qwen_smoke.py"), "--mode", "human_authored",
                                    "--task", family, "--instance", str(instance), "--stage", "formal",
                                    "--flow", str(QWEN / "flows" / (family + ".json"))],
                                   cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
                valid = next((p.parent for p in set(OUTPUT.glob("*/config.json")) - previous
                              if completed_status(p.parent)), None)
            if valid:
                result = json.loads((valid / "result.json").read_bytes())
                status = completed_status(valid)
                case.update(status=status, treatment_passed=result["passed"], treatment_run=valid.name)
            else:
                case["status"] = "infrastructure_error"
            with (OUTPUT / "paired-results.csv").open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(cases)
            print(f"{family}/{instance}: {case['status']}, {case.get('treatment_passed')}", flush=True)
            if not valid:
                raise SystemExit("Trial has no valid verifier result. Inspect the case log before resuming.")
    finally:
        server.shutdown()
        server.server_close()


def completed_status(path):
    report = path / "result.json"
    if not report.exists():
        return False
    result = json.loads(report.read_bytes())
    if result.get("error") or result.get("agent_exit") is None or not isinstance(result.get("passed"), bool):
        return None
    if result.get("verifier_exit") == 0 and any(path.rglob("reward.txt")):
        return "valid"
    if result.get("verifier_exit") != -1 or result["passed"]:
        return None

    # An outer timeout never qualifies as a pass. Preserve a conclusive failed
    # assertion when the verifier managed to save its completed report.
    for report in path.rglob("verifier/ctrf.json"):
        try:
            evidence = json.loads(report.read_bytes())["results"]
            summary = evidence["summary"]
            complete = summary["tests"] == len(evidence["tests"]) and summary["pending"] == 0
            if complete and any(test["status"] == "failed" for test in evidence["tests"]):
                return "assertion_failed_outer_timeout"
        except (ValueError, KeyError, TypeError):
            continue
    return None


if __name__ == "__main__":
    main()
