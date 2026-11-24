"""Two-stage resumable experiment controller; infrastructure failures never count as task answers."""
import os, sys, json, subprocess, time, hashlib, shutil, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TASKS={"earthquake-plate-calculation":6,"financial-analysis":6,"weighted-gdp-calculation":6,"stock-data-visualization":5}
MODES=["none","human_authored","b1-one-shot"]
STATE=ROOT/"output"/os.environ.get("SLB_STATE","qwen_campaign");STATE.mkdir(parents=True,exist_ok=True)
MANIFEST=STATE/"manifest.json"
LOCK=threading.RLock()
STOP=threading.Event()
def load():
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"version":1,"parameters":{"model":"qwen3.5-plus","temperature":0,"thinking":False,"max_tokens":4096,"max_steps":100,"stdout_chars":6000,"stderr_chars":2000},"smoke":{},"formal":{},"generated_skills":{},"images":{}}
def save(state):
    with LOCK:
        tmp=MANIFEST.with_suffix(".tmp");tmp.write_text(json.dumps(state,indent=2),encoding="utf-8");tmp.replace(MANIFEST)
def fingerprint(task,instance):
    env=ROOT/"tasks"/task/f"{task}-{instance}"/"environment"
    h=hashlib.sha256()
    for p in sorted(env.rglob("*")):
        if p.is_file() and "skills" not in p.relative_to(env).parts:
            h.update(p.relative_to(env).as_posix().encode());h.update(p.read_bytes())
    return h.hexdigest()
def trial(state,stage,task,instance,mode):
    key=f"{task}/{instance}/{mode}"
    if key in state[stage] and state[stage][key].get("complete"): return state[stage][key]
    fp=fingerprint(task,instance);image=state["images"].get(fp)
    if mode!="none" and not image:raise RuntimeError("Missing validated empty-skill image")
    cmd=[sys.executable,str(ROOT/"qwen/run_qwen_smoke.py"),"--mode",mode,"--task",task,"--instance",str(instance),"--stage",stage]
    if image:cmd+=["--image",image]
    if mode=="b1-one-shot" and task in state["generated_skills"]:cmd+=["--generated-skill",state["generated_skills"][task]]
    leases=json.loads((STATE/"inflight.json").read_text()) if (STATE/"inflight.json").exists() else {}
    leased=leases.get(key) if stage=="formal" else None
    if leased:
        run=Path(leased["run"]);resultfile=run/"result.json";log=Path(leased["log"])
        print("ADOPT IN-FLIGHT WITHOUT NEW MODEL CALL",key,flush=True)
        deadline=time.monotonic()+2400
        while True:
            try:
                json.loads(resultfile.read_text());break
            except (FileNotFoundError,json.JSONDecodeError):
                if time.monotonic()>deadline:raise RuntimeError("In-flight trial did not save result; inspect original process")
                time.sleep(5)
    else:
        before=set((ROOT/"output"/("qwen_"+stage)).glob("*"))
        log=STATE/(stage+"-"+task+"-"+str(instance)+"-"+mode+".log")
        print("START",stage,key,flush=True)
        with log.open("w",encoding="utf-8") as f:
            completed=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        created=set((ROOT/"output"/("qwen_"+stage)).glob("*"))-before
        selected=set()
        for candidate in created:
            config=candidate/"config.json"
            if config.exists():
                data=json.loads(config.read_text())
                if data.get("task")==task and data.get("instance")==instance and data.get("mode")==mode:selected.add(candidate)
        created=selected
        if len(created)!=1: raise RuntimeError("Ambiguous output; inspect "+str(log))
        run=created.pop();resultfile=run/"result.json"
        if not resultfile.exists():raise RuntimeError("Trial terminated without result: "+str(log))
    result=json.loads(resultfile.read_text())
    valid=result.get("agent_exit") is not None and result.get("verifier_exit")==0 and bool(list(run.rglob("reward.txt")))
    item={"run":str(run),"complete":valid,"result":result,"log":str(log)}
    with LOCK:
        state[stage][key]=item
        if not result.get("error") and result.get("agent_exit") is not None:
            if not image:
                image=f"evaluation_{task}-{task}-{instance}_{mode}:"+result["trial_id"].lower()
                state["images"][fp]=image
        if mode=="b1-one-shot" and (run/"skill_source.json").exists():
            state["generated_skills"][task]=json.loads((run/"skill_source.json").read_text())["path"]
        save(state)
    print("END",key,"valid="+str(valid),"passed="+str(result.get("passed")),flush=True)
    if not valid:raise RuntimeError("Infrastructure/recording error: "+str(log))
    return item
def main():
    state=load();save(state)
    # Exactly one new task instance under the frozen configuration before formal.
    for mode in MODES:trial(state,"smoke","financial-analysis",1,mode)
    state["smoke_gate_passed"]=True;save(state)
    while not (STATE/"metrics-ready.json").exists():time.sleep(5)
    print("SMOKE GATE PASSED; BEGIN FORMAL 69 TRIALS",flush=True)
    def family(task,count):
        try:
            for instance in range(1,count+1):
                for mode in MODES:
                    if STOP.is_set():return
                    trial(state,"formal",task,instance,mode)
        except Exception:
            STOP.set();raise
    with ThreadPoolExecutor(max_workers=2) as workers:
        futures=[workers.submit(family,task,count) for task,count in TASKS.items()]
        for future in as_completed(futures):future.result()
    state["formal_complete"]=len(state["formal"])==69 and all(v.get("complete") for v in state["formal"].values());save(state)
    print("FORMAL COMPLETE",flush=True)
if __name__=="__main__":main()

