"""Run the ten preselected paired trials through the official task runner."""
import csv
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
QWEN = ROOT / "qwen"
OUTPUT = ROOT / "output/qwen_rsi_flow"
STATE = ROOT / "output/qwen_budget_campaign"
FIELDS = ["family", "instance", "baseline_run", "baseline_passed", "flow_sha256",
          "status", "treatment_passed", "treatment_run", "treatment_origin", "platform_run_id"]


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with campaign_lock():
        run_cases()


@contextmanager
def campaign_lock():
    with (OUTPUT / "campaign.lock").open("a+b") as lock:
        try:
            if os.name == "nt":
                import msvcrt
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise SystemExit("Another Week 4 campaign holds the output lock") from error
        yield


def run_cases():
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
    server, secret = start(STATE)
    env = dict(os.environ, SLB_STATE="qwen_budget_campaign",
               DASHSCOPE_API_KEY=secret, QWEN_BASE_URL=f"http://host.docker.internal:{server.server_port}",
               PYTHONUTF8="1")
    try:
        with ThreadPoolExecutor(max_workers=3) as workers:
            pending = {workers.submit(run_case, case, env): index for index, case in enumerate(cases)}
            for trial in as_completed(pending):
                case = trial.result()
                cases[pending[trial]] = case
                save_results(cases)
                print(f"{case['family']}/{case['instance']}: {case['status']}, {case.get('treatment_passed')}", flush=True)
        if any(case["status"] == "infrastructure_error" for case in cases):
            raise SystemExit("Some trials have no valid verifier result. Inspect their case logs before resuming.")
    finally:
        server.shutdown()
        server.server_close()


def save_results(cases):
    pending_csv = OUTPUT / "paired-results.tmp"
    with pending_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(cases)
    pending_csv.replace(OUTPUT / "paired-results.csv")


def matching_runs(case):
    expected = case["family"], case["instance"], case["flow_sha256"]
    for config in sorted(OUTPUT.glob("*/config.json"), reverse=True):
        try:
            data = json.loads(config.read_bytes())
        except (OSError, ValueError):
            # Another worker can be writing its configuration.
            continue
        if (data.get("task"), data.get("instance"), data.get("flow_sha256")) == expected:
            yield config.parent


def baseline_image(family, instance):
    baseline_log = STATE / f"formal-{family}-{instance}-human_authored.log"
    if not baseline_log.is_file():
        return None
    match = re.search(r"^\[1/5\] Using prebuilt image ([\w.:-]+) \(human_authored\)",
                      baseline_log.read_text(encoding="utf-8", errors="replace"), re.MULTILINE)
    if not match or not match[1].startswith(f"evaluation_{family}-"):
        return None
    result = subprocess.run(["docker", "image", "inspect", match[1]], capture_output=True, timeout=15)
    return match[1] if result.returncode == 0 else None


def run_case(case, env):
    family, instance = case["family"], case["instance"]
    previous = list(matching_runs(case))
    valid = next((path for path in previous if completed_status(path)), None)
    if not valid:
        command = [sys.executable, "-u", str(QWEN / "run_qwen_smoke.py"), "--mode", "human_authored",
                   "--task", family, "--instance", str(instance), "--stage", "formal",
                   "--flow", str(QWEN / "flows" / (family + ".json"))]
        image = baseline_image(family, instance)
        if image:
            command.extend(["--image", image])
        log = OUTPUT / f"{family}-{instance}.log"
        with log.open("a", encoding="utf-8") as stream:
            subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        created = [path for path in matching_runs(case) if path not in previous]
        valid = next((path for path in created if completed_status(path)), None)
        if not valid:
            return dict(case, status="infrastructure_error", **run_identity(created[0] if created else None))
    result = json.loads((valid / "result.json").read_bytes())
    return dict(case, status=completed_status(valid), treatment_passed=result["passed"], **run_identity(valid))


def run_identity(path):
    if path is None:
        return {}
    config = json.loads((path / "config.json").read_bytes())
    platform_run = config.get("platform_run_id", "")
    return dict(treatment_run=path.name, treatment_origin="platform" if platform_run else "cli",
                platform_run_id=platform_run)


def completed_status(path):
    report = path / "result.json"
    if not report.exists():
        return False
    result = json.loads(report.read_bytes())
    if result.get("error") or result.get("agent_exit") is None or not isinstance(result.get("passed"), bool):
        return None
    exit_code = result.get("verifier_exit")
    for report in path.rglob("verifier/ctrf.json"):
        try:
            evidence = json.loads(report.read_bytes())["results"]
            summary = evidence["summary"]
            tests = evidence["tests"]
            if not tests or summary["tests"] != len(tests) or summary["pending"] != 0:
                continue
            if exit_code == 0:
                reward = (report.parent / "reward.txt").read_text(encoding="utf-8").strip()
                if result["passed"]:
                    if reward == "1" and all(test["status"] == "passed" for test in tests):
                        return "valid"
                elif reward == "0" and any(test["status"] == "failed" for test in tests):
                    return "valid"
            elif exit_code == -1 and not result["passed"]:
                if any(test["status"] == "failed" for test in tests):
                    return "assertion_failed_outer_timeout"
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return None


if __name__ == "__main__":
    main()
