import os
"""Continuously fill two independent metric workers, honoring in-flight cross-process locks."""
import json,sys,time,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];STATE=ROOT/"output"/os.environ.get("SLB_STATE","qwen_campaign")
def measure(item):
    phase,key,run=item
    print("METRICS START",phase,key,flush=True)
    with (run/"metrics-controller.log").open("w",encoding="utf-8") as f:
        code=subprocess.run([sys.executable,str(ROOT/"qwen/measure.py"),str(run)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
    if code not in (0,75):raise RuntimeError("Metric failure: "+str(run/"metrics-controller.log"))
    if code==0:print("METRICS END",key,flush=True)
def main():
    active={}
    failed=set()
    with ThreadPoolExecutor(max_workers=2) as workers:
        while True:
            for run,future in list(active.items()):
                if future.done():
                    try:
                        future.result()
                    except RuntimeError as exc:
                        failed.add(run)
                        print("METRIC DEFERRED", exc, flush=True)
                    del active[run]
            state=json.loads((STATE/"manifest.json").read_text());pending=[]
            for phase in ["smoke","formal"]:
                for key,item in state.get(phase,{}).items():
                    run=Path(item["run"])
                    if item.get("complete") and not (run/"metrics/complete.json").exists():pending.append((phase,key,run))
            external=sum((run/"metrics/.measure.lock").exists() and run not in active for _,_,run in pending)
            for item in pending:
                run=item[2]
                if len(active)+external>=2:break
                if run not in active and run not in failed and not (run/"metrics/.measure.lock").exists():active[run]=workers.submit(measure,item)
            if len(state.get("smoke",{}))==3 and not (STATE/"metrics-ready.json").exists() and all(Path(v["run"],"metrics/complete.json").exists() for v in state["smoke"].values()):
                (STATE/"metrics-ready.json").write_text(json.dumps({"all_smoke_metrics_complete":True,"frozen_parameters":state["parameters"]},indent=2))
            if state.get("formal_complete") and not active and all(run in failed for _,_,run in pending):
                if pending:
                    raise RuntimeError("Formal execution complete; deferred metrics require repair")

                print("ALL METRICS COMPLETE",flush=True);return
            time.sleep(5)
if __name__=="__main__":main()

