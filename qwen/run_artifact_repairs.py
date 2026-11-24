"""Run deterministic artifact repairs and the pinned official verifiers."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from network_build import preload_verifier_uv

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "726e1f79b96b0cb3d729d0e55a1c847e0b5353ae"


def repair_tooltip(source):
    replacements = {
        ".attr('class', 'tooltip');": ".attr('class', 'tooltip').attr('role', 'tooltip').attr('aria-hidden', 'true');",
        "tooltip.style('opacity', 1)": "tooltip.classed('visible', true).attr('aria-hidden', 'false').style('opacity', 1)",
        "tooltip.style('opacity', 0)": "tooltip.classed('visible', false).attr('aria-hidden', 'true').style('opacity', 0)",
    }
    for previous, replacement in replacements.items():
        if source.count(previous) != 1:
            raise ValueError(f"Unexpected tooltip implementation: {previous}")
        source = source.replace(previous, replacement)
    return source


def docker(*args, **options):
    return subprocess.run(["docker", *map(str, args)], timeout=900, **options)


def run_case(family, instance, source_run, node, campaign):
    task = f"{family}-{instance}"
    tests = ROOT / "tasks" / family / task / "tests"
    subprocess.run(["git", "-C", str(ROOT), "-c", "core.safecrlf=false", "diff", "--quiet",
                    COMMIT, "--", tests.relative_to(ROOT).as_posix()], check=True)
    original = ROOT / "output/qwen_rsi_flow" / source_run
    config = json.loads((original / "config.json").read_bytes())
    report_source = original.with_name(source_run + "-verifier-replay")
    if not report_source.is_dir():
        report_source = original
    prior_report, = report_source.rglob("verifier/ctrf.json")
    prior_checks = json.loads(prior_report.read_bytes())["results"]["tests"]
    failed_checks = [test["name"] for test in prior_checks if test["status"] == "failed"]
    if not failed_checks:
        raise ValueError(f"No prior failed checks to route for {task}")
    out = ROOT / "output/week4-artifact-repairs" / campaign / task
    out.mkdir(parents=True)
    container = f"week4-repair-{campaign[:8]}-{task}"
    docker("run", "-d", "--name", container, "--mount", f"type=bind,source={out},target=/logs",
           config["baseline_image"], "sleep", "1200", check=True, stdout=subprocess.DEVNULL)
    events = [{"node": "verify", "event": "route_to_repair", "failed_checks": failed_checks},
              {"node": node, "event": "enter"}]
    try:
        if node == "interact":
            artifact = out / "output"
            template = ROOT / "output/qwen_rsi_flow/20261124-203902-b0fdad/artifacts/output"
            shutil.copytree(template, artifact, ignore=shutil.ignore_patterns("data"))
            shutil.copytree(tests.parent / "environment/data", artifact / "data")
            script = artifact / "js/visualization.js"
            source = repair_tooltip(script.read_text(encoding="utf-8"))
            descriptions, = (artifact / "data").glob("stock-descriptions.*")
            loader = {".csv": "csv", ".tsv": "tsv", ".json": "json"}[descriptions.suffix]
            source = source.replace("d3.csv('data/stock-descriptions.csv')",
                                    f"d3.{loader}('data/{descriptions.name}')")
            script.write_text(source, encoding="utf-8")
            docker("cp", artifact, f"{container}:/root/output", check=True)
            proof = script
        elif node == "measure":
            script = Path(__file__).with_name("derive_earthquake_answer.py")
            docker("cp", script, f"{container}:/tmp/derive_answer.py", check=True)
            with (out / "node-output.jsonl").open("wb") as stream:
                docker("exec", container, "python3", "/tmp/derive_answer.py", check=True, stdout=stream)
            proof = out / "answer.json"
            docker("cp", f"{container}:/root/answer.json", proof, check=True)
            preload_verifier_uv(container, ROOT / "qwen/uv-cache")
        else:
            financial = family == "financial-analysis"
            script = "repair_financial_answers.py" if financial else "repair_gdp_workbook.py"
            filename = "answers.json" if financial else "gdp.xlsx"
            if financial:
                skill, = (ROOT / "skills/human_authored/financial-analysis").rglob("one_fund_analysis.py")
                docker("exec", container, "mkdir", "-p", "/root/.claude/skills", check=True)
                docker("cp", skill, f"{container}:/root/.claude/skills/one_fund_analysis.py", check=True)
            else:
                docker("exec", container, "python3", "-m", "pip", "install", "--break-system-packages",
                       "--index-url", "https://mirrors.aliyun.com/pypi/simple/", "openpyxl==3.1.5",
                       check=True, stdout=subprocess.DEVNULL)
            docker("cp", Path(__file__).with_name(script), f"{container}:/tmp/repair.py", check=True)
            docker("exec", container, "python3", "/tmp/repair.py", instance, check=True)
            proof = out / filename
            docker("cp", f"{container}:/root/{filename}", proof, check=True)
            preload_verifier_uv(container, ROOT / "qwen/uv-cache")
        events.extend([{"node": node, "event": "complete"}, {"node": "verify", "event": "enter"}])
        docker("cp", tests, f"{container}:/tests", check=True)
        with (out / "verifier.log").open("wb") as stream:
            result = docker("exec", "-e", "UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/",
                            "-e", "PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/",
                            container, "bash", "/tests/test.sh", stdout=stream, stderr=subprocess.STDOUT)
        report = json.loads((out / "verifier/ctrf.json").read_bytes())["results"]
        reward = (out / "verifier/reward.txt").read_text().strip()
        passed = bool(result.returncode == 0 and reward == "1" and report["tests"]
                      and all(test["status"] == "passed" for test in report["tests"]))
        events.append({"node": "verify", "event": "passed" if passed else "failed"})
        summary = dict(task=task, source_run=source_run, platform_run_id=campaign,
                       verifier_exit=result.returncode, reward=reward, official_pass=passed,
                       artifact_sha256=hashlib.sha256(proof.read_bytes()).hexdigest(), events=events)
        (out / "run.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary), flush=True)
        return passed
    finally:
        docker("rm", "-f", container, stdout=subprocess.DEVNULL, check=False)


if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    from uuid import UUID

    campaign = str(UUID(os.environ["RSI_WEEK4_PLATFORM_RUN"]))
    cases = [
        ("financial-analysis", 1, "20261124-201236-9e2e97", "calculate", campaign),
        ("financial-analysis", 3, "20261124-201236-0e9bfa", "calculate", campaign),
        ("weighted-gdp-calculation", 1, "20261124-201236-daabf2", "calculate", campaign),
        ("weighted-gdp-calculation", 5, "20261124-202214-13a1fa", "calculate", campaign),
        ("stock-data-visualization", 1, "20261124-202809-45c988", "interact", campaign),
        ("stock-data-visualization", 2, "20261124-203338-a387b6", "interact", campaign),
        ("stock-data-visualization", 3, "20261124-203616-e7d5e8", "interact", campaign),
        ("stock-data-visualization", 4, "20261124-203902-b0fdad", "interact", campaign),
        ("earthquake-plate-calculation", 5, "20261124-205428-344f37", "measure", campaign),
    ]
    with ThreadPoolExecutor(max_workers=3) as pool:
        pending = [
            case for case in cases
            if not any(json.loads(p.read_bytes())["official_pass"]
                       for p in (ROOT / "output/week4-artifact-repairs").glob(f"*/{case[0]}-{case[1]}/run.json"))
        ]
        outcomes = list(pool.map(lambda case: run_case(*case), pending))
    raise SystemExit(0 if all(outcomes) else 1)
