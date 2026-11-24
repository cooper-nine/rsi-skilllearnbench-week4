"""Re-run the untouched GDP verifier on an already generated workbook."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import uuid

from network_build import preload_verifier_uv


def docker(*args, **options):
    return subprocess.run(["docker", *map(str, args)], timeout=options.pop("timeout", 60),
                          check=options.pop("check", True), **options)


def main(workspace, run_id):
    if not re.fullmatch(r"\d{8}-\d{6}-[a-f0-9]{6}", run_id):
        raise ValueError("Expected an original Week 4 trial ID")
    output = workspace / "output/qwen_rsi_flow"
    original = output / run_id
    config = json.loads((original / "config.json").read_bytes())
    before = json.loads((original / "result.json").read_bytes())
    family = "weighted-gdp-calculation"
    if config["task"] != family or not config.get("baseline_image", "").startswith(f"evaluation_{family}-"):
        raise ValueError("Expected an original GDP trial with its baseline image")
    if before["agent_exit"] is None or before.get("error") or list(original.rglob("verifier/ctrf.json")):
        raise ValueError("Expected a saved agent output without an official CTRF")

    image = config["baseline_image"]
    workbook = original / "artifacts/gdp.xlsx"
    tests = workspace / "tasks" / family / f"{family}-{config['instance']}" / "tests"
    test_path = tests.relative_to(workspace).as_posix()
    subprocess.run(["git", "-C", str(workspace), "-c", "core.safecrlf=false", "diff", "--quiet",
                    config["upstream_commit"], "--", test_path], check=True)
    cache = workspace / "qwen/uv-cache"

    replay = output / f"{run_id}-verifier-replay"
    verifier = replay / "verifier"
    verifier.mkdir(parents=True)
    artifacts = replay / "artifacts"
    artifacts.mkdir()
    shutil.copyfile(workbook, artifacts / workbook.name)
    container = f"rsi-week4-gdp-verifier-{uuid.uuid4().hex[:10]}"
    docker("run", "-d", "--name", container, "--mount", f"type=bind,source={replay},target=/logs",
           image, "sleep", "1200", stdout=subprocess.DEVNULL)
    try:
        docker("cp", workbook, f"{container}:/root/gdp.xlsx")
        docker("cp", tests, f"{container}:/tests")
        preload_verifier_uv(container, cache)
        with (replay / "verifier.stdout.log").open("wb") as stdout, (replay / "verifier.stderr.log").open("wb") as stderr:
            judged = docker("exec", "-e", "UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/", container,
                            "bash", "/tests/test.sh", stdout=stdout, stderr=stderr, timeout=900, check=False)
    finally:
        docker("rm", "-f", container, check=False, stdout=subprocess.DEVNULL)
    reward = (verifier / "reward.txt").read_text().strip()
    report = json.loads((verifier / "ctrf.json").read_bytes())["results"]
    if not report["tests"] or report["summary"]["pending"] != 0 or reward not in {"0", "1"}:
        raise ValueError("Official replay did not produce a complete verdict")
    passed = judged.returncode == 0 and reward == "1" and all(t["status"] == "passed" for t in report["tests"])
    config["verifier_replay_of"] = run_id
    (replay / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    result = {key: before.get(key) for key in ("task_id", "agent_exit", "agent_timed_out", "token_usage")}
    result.update(verifier_exit=judged.returncode, passed=passed, reward=int(reward))
    (replay / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{replay.name}: {report['summary']['passed']}/{len(report['tests'])}; reward={reward}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("run_id")
    args = parser.parse_args()
    main(args.workspace.resolve(), args.run_id)
