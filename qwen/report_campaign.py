import os
"""Aggregate only recorded formal trials; keep missing metrics distinct from zero."""
import csv,json,statistics,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];STATE=ROOT/"output"/os.environ.get("SLB_STATE","qwen_campaign")
def read(path,default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
def avg(values):
    values=[x for x in values if isinstance(x,(int,float)) and not isinstance(x,bool)]
    return sum(values)/len(values) if values else None
def first_config(d):
    return next(iter((d or {}).get("by_config",{}).values()),{})
def main():
    manifest=read(STATE/"manifest.json",{});rows=[];issues=[]
    for key,item in manifest.get("formal",{}).items():
        task,instance,mode=key.split("/");run=Path(item["run"]);r=item["result"];metrics=run/"metrics"
        if not item.get("complete"):issues.append({"trial":key,"kind":"infrastructure","run":str(run)});continue
        trace=next(run.rglob("qwen.txt"));events=[]
        for line in trace.read_text(encoding="utf-8").splitlines():
            try:events.append(json.loads(line))
            except ValueError:pass
        ends=[x for x in events if x.get("type")=="result"]
        calls=sum(x.get("type")=="assistant" for x in events)
        api_aborted=bool(ends and not ends[-1].get("completed") and calls<100 and not r.get("agent_timed_out"))
        if api_aborted:issues.append({"trial":key,"kind":"agent/API aborted; requires review and retry","run":str(run)})
        c=first_config(read(metrics/"coverage.json"));coverage=avg([x.get("coverage") for x in c.get("by_run",{}).values()])
        executable=first_config(read(metrics/"executability.json")).get("aggregate",{})
        safety=first_config(read(metrics/"safety.json")).get("aggregate",{})
        usage=r.get("token_usage",{});judge_usage=collections.Counter()
        for p in (metrics/"judge_raw").glob("*.json"):
            u=read(p,{}).get("response",{}).get("usage",{})
            for k in ["prompt_tokens","completion_tokens","total_tokens"]:judge_usage[k]+=u.get(k,0)
        row={"task":task,"instance":int(instance),"mode":mode,"passed":int(bool(r.get("passed"))),"reward":r.get("reward"),"agent_completed":ends[-1].get("completed") if ends else None,"agent_calls":calls,
             "input_tokens":usage.get("input_tokens"),"output_tokens":usage.get("output_tokens"),"solving_tokens":usage.get("total_tokens"),
             "coverage":coverage,"executability":executable.get("overall_score_avg"),"safety":safety.get("overall_score_avg"),
             "alignment":read(metrics/"alignment.json",{}).get("score"),"execution_order":read(metrics/"execution_order.json",{}).get("score"),
             "completeness":read(metrics/"completeness.json",{}).get("score"),"trajectory_key_point_recall":read(metrics/"trajectory_key_point_recall.json",{}).get("trajectory_key_point_recall"),
             "explicit_skill_invocation_ratio":read(metrics/"usage_definition.json",{}).get("official_explicit_invocation_ratio"),
             "judge_tokens":judge_usage["total_tokens"],"metrics_complete":(metrics/"complete.json").exists(),"run":str(run)}
        if not (metrics/"skill_usage_path_evidence.json").exists():
            from local_metrics import write_skill_usage
            metrics.mkdir(exist_ok=True)
            source=Path(r["skill_source_dir"]) if r.get("skill_source_dir") else None
            write_skill_usage(events,source,metrics)
        row["skill_usage_path_evidence"]=read(metrics/"skill_usage_path_evidence.json",{}).get("rate")
        components=[row["trajectory_key_point_recall"]*100 if row["trajectory_key_point_recall"] is not None else None,(row["execution_order"]-1)/4*100 if row["execution_order"] is not None else None,(row["completeness"]-1)/4*100 if row["completeness"] is not None else None]
        row["trajectory_alignment_100"]=sum(components)/3 if all(x is not None for x in components) else None
        row.update({"executability_"+k:v for k,v in executable.items() if k.endswith("_avg")})
        row.update({"safety_"+k:v for k,v in safety.items() if k.endswith("_avg")})
        if not row["passed"]:
            ctrfs=list(run.rglob("ctrf.json"));failed=[]
            if ctrfs:
                failed=[t for t in read(ctrfs[0],{}).get("results",{}).get("tests",[]) if t.get("status") not in ("passed","skipped")]
            evidence=json.dumps(failed,ensure_ascii=False)
            if r.get("agent_timed_out"):category="execution_timeout"
            elif not row["agent_completed"] and calls>=100:category="max_turns"
            elif api_aborted:category="api_or_runtime_error"
            elif any(s in evidence.lower() for s in ["filenotfounderror","does not exist","jsondecodeerror","not found","missing required"]):category="missing_or_invalid_output"
            else:category="task_requirement_or_computation_mismatch"
            row["failure_category"]=category
            issues.append({"trial":key,"kind":category,"failed_checks":failed,"run":str(run)})
        else:row["failure_category"]=""
        rows.append(row)
    out=STATE/"reports";out.mkdir(exist_ok=True)
    fields=list(dict.fromkeys(k for row in rows for k in row))
    if fields:
        with (out/"trials.csv").open("w",newline="",encoding="utf-8-sig") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    summary={}
    scalar=["trajectory_alignment_100","skill_usage_path_evidence","passed","coverage","executability","safety","alignment","execution_order","completeness","trajectory_key_point_recall","explicit_skill_invocation_ratio","solving_tokens","judge_tokens"]
    for mode in ["none","human_authored","b1-one-shot"]:
        selected=[r for r in rows if r["mode"]==mode];per_task={}
        for task in sorted(set(r["task"] for r in selected)):
            group=[r for r in selected if r["task"]==task];per_task[task]={"n":len(group),**{k:avg([r.get(k) for r in group]) for k in scalar}}
        failed=[r for r in selected if not r["passed"]]
        summary[mode]={"n":len(selected),"per_task":per_task,"micro":{k:avg([r.get(k) for r in selected]) for k in scalar},"macro":{k:avg([v.get(k) for v in per_task.values()]) for k in scalar},"failure_counts":dict(collections.Counter(r["failure_category"] for r in failed)),"failure_denominator":len(failed)}
    complete=len(rows)==69 and len({(r["task"],r["instance"],r["mode"]) for r in rows})==69 and all(r["metrics_complete"] for r in rows) and not any(i["kind"].startswith("agent/API") or i["kind"]=="infrastructure" for i in issues)
    generation={}
    for task,source in manifest.get("generated_skills",{}).items():
        traces=list((Path(source).parents[1]/"agent").glob("qwen.txt"))
        total=collections.Counter();count=0
        if traces:
            for line in traces[0].read_text(encoding="utf-8").splitlines():
                try:event=json.loads(line)
                except ValueError:continue
                if event.get("type")=="assistant":
                    count+=1
                    total.update({k:event["response"].get("usage",{}).get(k,0) for k in ["prompt_tokens","completion_tokens","total_tokens"]})
        generation[task]={"completed_response_calls":count,"observed_usage":dict(total),"skill_source":source,"unreturned_request_billing_not_observable":True}
    cost={"formal_solving_tokens":sum(r.get("solving_tokens") or 0 for r in rows),"formal_judge_tokens":sum(r.get("judge_tokens") or 0 for r in rows),"task_family_generation_observed_tokens":sum(v["observed_usage"].get("total_tokens",0) for v in generation.values())}
    cost["observed_total_tokens"]=sum(cost.values())
    payload={"complete":complete,"formal_trials":len(rows),"generation":generation,"cost":cost,"summary":summary,"issues":issues,"protocol":read(STATE/"protocol.json")}
    (out/"report.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"failure_cases.json").write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding="utf-8")
    print("REPORT",len(rows),"/69 formal trials; all metrics and execution complete:",complete)
if __name__=="__main__":main()

