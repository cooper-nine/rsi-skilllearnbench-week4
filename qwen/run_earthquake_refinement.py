"""Retest the earthquake plate-edge interpretation under the original model and budget."""
import hashlib
import json
import os
import subprocess

from budget_proxy import start
from run_rsi_retests import OUTPUT, QWEN, STATE, campaign_lock, run_case

FAMILY = "earthquake-plate-calculation"
PREPARE_GUIDANCE = (
    "Resolve contradictory distance instructions before analyzing the data. Use the main objective: "
    "select the plate with the most earthquake records, then measure the selected earthquake to that "
    "same plate’s edge. If the distance field names a different plate, retain the plate selected by "
    "the main objective. Cross-check the projected distance against the selected plate’s boundary segments."
)
FILTER_GUIDANCE = (
    "Record the selected plate code and earthquake together before proceeding. If a field description "
    "names a reference plate that conflicts with the main objective, carry the main objective’s "
    "reference plate into the distance stage."
)
MEASURE_GUIDANCE = (
    "Carry forward the plate ID and the earthquake selected by the filter node. "
    "If the task’s main objective and the field description name conflicting reference plates, "
    "follow the main objective. Measure to the selected plate’s edge in a metric projection. "
    "Cross-check the polygon edge distance against the nearest recorded boundary segment "
    "incident to the same plate. Keep the verified earthquake ID and round only the final distance."
)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with campaign_lock():
        subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"], check=True, timeout=15)
        if not all((STATE / name).is_file() for name in ("metrics-ready.json", "budget-limit.json")):
            raise SystemExit("The existing controlled-experiment budget and metrics gate are required")
        case = next(case for case in json.loads((QWEN / "cases.json").read_bytes())
                    if (case["family"], case["instance"]) == (FAMILY, 5))
        flow = json.loads((QWEN / "flows" / f"{FAMILY}.json").read_bytes())
        guidance = {"prepare": PREPARE_GUIDANCE, "filter": FILTER_GUIDANCE, "measure": MEASURE_GUIDANCE}
        for node in flow["nodes"]:
            if node["id"] in guidance:
                node["guidance"] = guidance[node["id"]]
        data = (json.dumps(flow, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        flow_path = OUTPUT / "earthquake-5-guided-flow.json"
        flow_path.write_bytes(data)
        case["flow_sha256"] = hashlib.sha256(data).hexdigest()
        server, secret = start(STATE)
        env = dict(os.environ, SLB_STATE="qwen_budget_campaign", DASHSCOPE_API_KEY=secret,
                   QWEN_BASE_URL=f"http://host.docker.internal:{server.server_port}", PYTHONUTF8="1")
        try:
            result = run_case(case, env, flow_path)
        finally:
            server.shutdown()
            server.server_close()
        summary = json.dumps(result, indent=2) + "\n"
        (OUTPUT / "earthquake-5-guided-result.json").write_text(summary, encoding="utf-8")
        print(summary, end="")
        return 0 if result.get("treatment_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
