"""Measure one Qwen trial with upstream metric scripts; preserve raw judge responses."""
import argparse, json, os, subprocess, sys, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def _measure():
    parser=argparse.ArgumentParser();parser.add_argument("run",type=Path);args=parser.parse_args()
    run=args.run.resolve();result=json.loads((run/"result.json").read_text())
    task,instance=result["task_id"].split("/")
    mode=result["skill_config"];out=run/"metrics";out.mkdir(exist_ok=True)
    source_info=run/"skill_source.json"
    source=Path(json.loads(source_info.read_text())["path"]) if source_info.exists() and json.loads(source_info.read_text())["path"] else None
    if source is None and mode=="human_authored":source=ROOT/"skills/human_authored"/task
    if source is None and mode=="b1-one-shot" and result.get("skill_source_dir"):source=Path(result["skill_source_dir"])
    raw=next(run.rglob("qwen.txt"));events=[json.loads(x) for x in raw.read_text(encoding="utf-8").splitlines() if x.startswith("{")]
    messages=[];calls=0;skill_calls=0
    for e in events:
        if e.get("type")=="assistant":
            msg=e["response"]["choices"][0]["message"];tools=msg.get("tool_calls",[])
            calls+=len(tools);skill_calls+=sum(t["function"]["name"]=="Skill" for t in tools)
            messages.append({"role":"assistant","content":(msg.get("content") or "")+"\nTOOL_CALLS: "+json.dumps(tools,ensure_ascii=False)})
        elif e.get("type")=="tool":messages.append({"role":"tool","content":json.dumps(e["result"],ensure_ascii=False)})
    converted=out/"trajectory.json";converted.write_text(json.dumps({"messages":messages},ensure_ascii=False),encoding="utf-8")
    judge_trajectory=converted
    if os.environ.get("SLB_JUDGE_URL") and converted.stat().st_size>80000:
        reduced=[]
        per_message=max(100, min(1600, 62000 // max(1,len(messages))))
        for message in messages:
            content=message["content"].encode("utf-8")
            limit=min(per_message,400) if message["role"]=="tool" else per_message
            if len(content)>limit:
                head=limit*2//3
                tail=limit-head
                excerpt=content[:head].decode("utf-8","ignore")+" [excerpt] "+content[-tail:].decode("utf-8","ignore")
                message={**message,"content":excerpt}
            reduced.append(message)
        judge_trajectory=out/"trajectory-judge-excerpts.json"
        judge_trajectory.write_text(json.dumps({"messages":reduced},ensure_ascii=False),encoding="utf-8")
    available=len(list(source.rglob("SKILL.md"))) if source else 0
    (out/"usage_definition.json").write_text(json.dumps({"shell_tool_calls":calls,"explicit_skill_tool_calls":skill_calls,"available_skills":available,"official_explicit_invocation_ratio":0.0,"context_injection":available>0,"actual_causal_usage":"not identifiable from context injection alone","note":"This harness has no explicit Skill tool; zero is an event-structure measurement, not proof of nonuse."},indent=2))
    from local_metrics import write_skill_usage
    write_skill_usage(events,source,out)
    env=os.environ.copy();env["QWEN_JUDGE_LOG_DIR"]=str(out/"judge_raw");env["PYTHONUTF8"]="1"
    def execute(name,script,parameters):
        output=out/(name+".json")
        if output.exists():return
        cmd=[sys.executable,str(ROOT/"qwen/judge_entry.py"),str(ROOT/script),*parameters,"--model","qwen3.5-plus","--output",str(output)]
        with (out/(name+".log")).open("w",encoding="utf-8") as log:
            status=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        if status.returncode or not output.exists():raise RuntimeError(name+" failed; see "+str(out/(name+".log")))
    td=ROOT/"tasks"/task/instance;ref=ROOT/"eval_keypoints"/task/instance
    if source:
        for metric in ["executability","safety","coverage"]:
            p=["--task-id",task,"--task-dir",str(td),"--generated-root",str(source),"--raw-dir",str(out/(metric+"_raw"))]
            if metric=="coverage":p+=["--key-points-path",str(ref/"skill-key-points.generated.json")]
            execute(metric,"evaluation/skill/metrics/compute_"+metric+".py",p)
        execute("alignment", "qwen/alignment.py", ["--task-id",task,"--task-dir",str(td),"--generated-root",str(source)])
    else:(out/"skill_quality_not_applicable.json").write_text(json.dumps({"reason":"no skill documents in none baseline","coverage":None,"executability":None,"safety":None,"alignment":None}))
    for metric,filename in [("execution_order","metric_llm_execution_order.py"),("completeness","metric_llm_completeness.py"),("trajectory_key_point_recall","metric_llm_key_points.py")]:
        p=["--task-id",str(td),"--generated-trajectory",str(judge_trajectory)]
        if metric=="trajectory_key_point_recall":p+=["--oracle-key-points",str(ref/"traj-key-points.generated.json"),"--max-concurrency","2"]
        else:p+=["--oracle-compact-trajectory",str(ref/"traj-extracted-oracle.json")]
        execute(metric,"evaluation/trajectory/metrics/"+filename,p)
    (out/"complete.json").write_text(json.dumps({"complete":True,"judge_model":"qwen3.5-plus","upstream_rubrics":True,"trajectory_adapter":"bounded message excerpts for large traces" if judge_trajectory!=converted else "lossless event text; no provider spoofing"},indent=2))
    print("METRICS COMPLETE",run,flush=True)
def main():
    run=Path(sys.argv[1]).resolve();directory=run/"metrics";directory.mkdir(exist_ok=True)
    lock=directory/".measure.lock"
    try:
        descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(75)
    os.write(descriptor,str(os.getpid()).encode());os.close(descriptor)
    try:_measure()
    finally:lock.unlink(missing_ok=True)
if __name__=="__main__":main()

