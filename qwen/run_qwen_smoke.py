"""Run one official earthquake instance with the Qwen adapter. No custom verifier."""
import argparse, base64, json, os, sys, time, uuid, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agents import AGENTS
from core.eval_runner import run_task
import core.eval_runner as eval_runner
from network_build import install_build_workaround
from qwen_agent import request

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=["none","human_authored","b1-one-shot"],required=True)
    parser.add_argument("--ping",action="store_true")
    parser.add_argument("--image", help="Previously built EMPTY-skill image for this exact task")
    parser.add_argument("--task",default="earthquake-plate-calculation")
    parser.add_argument("--instance",type=int,default=1)
    parser.add_argument("--stage",choices=["smoke","formal"],default="smoke")
    parser.add_argument("--generated-skill",type=Path)
    parser.add_argument("--flow", type=Path, help="Treatment graph for the human-authored baseline")
    args=parser.parse_args()
    if args.flow and (args.mode != "human_authored" or os.environ.get("SLB_STATE") != "qwen_budget_campaign"):
        parser.error("--flow requires human_authored and the original budget-v3 protocol")
    if args.stage == "formal":
        gate=ROOT/"output"/os.environ.get("SLB_STATE","qwen_campaign")/"metrics-ready.json"
        print("Waiting for smoke metrics gate",flush=True)
        while not gate.exists():time.sleep(10)
    stamp=time.strftime("%Y%m%d-%H%M%S")+"-"+uuid.uuid4().hex[:6]
    output_group = "qwen_rsi_flow" if args.flow else "qwen_" + args.stage
    out=ROOT/"output"/output_group/stamp
    out.mkdir(parents=True)
    install_build_workaround(eval_runner, out)
    config={"model":"qwen3.5-plus","temperature":0,"max_steps":100,"max_tokens":4096,"enable_thinking":False,"mode":args.mode,"task":args.task,"instance":args.instance,"stage":args.stage,"verifier_isolation":"tests-copied-only-after-agent","tool_stdout_chars":6000,"tool_stderr_chars":2000,"build_network":"aliyun-debian-and-pypi-timeout20-retry1"}
    config["agent_source_sha256"]=hashlib.sha256((ROOT/"qwen/qwen_agent.py").read_bytes()).hexdigest()
    config["upstream_commit"]="726e1f79b96b0cb3d729d0e55a1c847e0b5353ae"
    (out/"config.json").write_text(json.dumps(config,indent=2))
    if args.ping:
        response=request([{"role":"user","content":"Reply with OK."}])
        (out/"ping.json").write_text(json.dumps(response,ensure_ascii=False,indent=2),encoding="utf-8")
        print("API connected:",response.get("model"),response.get("usage"))
        return
    agent_source=(ROOT/"qwen"/"qwen_agent.py").read_text(encoding="utf-8")
    if os.environ.get("SLB_STATE")=="qwen_budget_campaign":
        compact_source=(ROOT/"qwen/context_policy.py").read_text(encoding="utf-8")
        agent_source=compact_source+"\n"+agent_source
        agent_source=agent_source.replace("response=request(messages,tools)","response=request(compact(messages),tools)")
        agent_source=agent_source.replace("max_tokens=4096","max_tokens=2048")
        agent_source=agent_source.replace("p.stdout[-6000:]","p.stdout[-2000:]").replace("p.stderr[-2000:]","p.stderr[-1000:]")
        config.update(protocol="budget-v3",max_tokens=2048,tool_stdout_chars=2000,tool_stderr_chars=1000)
        config["agent_source_sha256"]=hashlib.sha256(agent_source.encode()).hexdigest()
        (out/"config.json").write_text(json.dumps(config,indent=2),encoding="utf-8")
    if args.flow:
        from rsi_instrument import instrument
        flow_bytes = args.flow.read_bytes()
        flow = json.loads(flow_bytes)
        if flow["id"] != args.task:
            parser.error("Flow family does not match task family")
        skill_root = ROOT / "skills/human_authored" / args.task
        sources = {p.parent.name: p.read_bytes() for p in skill_root.rglob("SKILL.md")}
        if set(sources) != {node["skill"] for node in flow["nodes"]}:
            parser.error("Flow source set differs from the historical human-authored source set")
        for skill, original in sources.items():
            nodes = [node for node in flow["nodes"] if node["skill"] == skill]
            if "".join(node["text"] for node in nodes).encode("utf-8") != original:
                parser.error(f"Flow text differs from original Skill: {skill}")
        agent_source = instrument(agent_source, flow)
        (out / "flow.json").write_bytes(flow_bytes)
        config.update(treatment="rsi_flow", flow_sha256=hashlib.sha256(flow_bytes).hexdigest(),
                      agent_source_sha256=hashlib.sha256(agent_source.encode()).hexdigest())
        if os.environ.get("RSI_WEEK4_PLATFORM_RUN"):
            config["platform_run_id"] = os.environ["RSI_WEEK4_PLATFORM_RUN"]
        if args.image:
            config["baseline_image"] = args.image
        (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    encoded=base64.b64encode(agent_source.encode()).decode()
    os.environ["PIP_INDEX_URL"]="https://mirrors.aliyun.com/pypi/simple/"
    os.environ["PIP_DEFAULT_TIMEOUT"]="120"
    os.environ["UV_INDEX_URL"]="https://mirrors.aliyun.com/pypi/simple/"
    AGENTS["qwen"]={"name":"Qwen OpenAI-compatible shell adapter","env":["DASHSCOPE_API_KEY","QWEN_BASE_URL","UV_INDEX_URL","PIP_INDEX_URL","PIP_DEFAULT_TIMEOUT"],
       "install":"echo "+encoded+" | base64 -d > /tmp/qwen_agent.py",
       "run":"python3 /tmp/qwen_agent.py --instruction {instruction_file} --max-steps {max_steps}",
       "trajectory_tee":"/logs/agent/qwen.txt","default_model":"qwen3.5-plus"}
    task=f"{args.task}/{args.task}-{args.instance}"
    source=ROOT/"skills"/"human_authored"/args.task
    if args.mode=="none":
        source=None
    elif args.mode=="b1-one-shot" and args.generated_skill:
        source=args.generated_skill.resolve()
    elif args.mode=="b1-one-shot":
        if not args.image:
            parser.error("Official one-shot requires --image from the successful none build")
        import core.skill_runner as generator
        generator.subprocess=eval_runner.subprocess
        if os.environ.get("SLB_STATE")=="qwen_budget_campaign":
            generator.TRIALS_DIR=ROOT/"output/qwen_budget_generation"
        gen_root=generator.TRIALS_DIR/"b1-one-shot-qwen3.5-plus"/args.task
        before=set(gen_root.rglob("artifacts")) if gen_root.exists() else set()
        generation_exit,generation=generator.run_task(args.task,agent_id="qwen",
            model="qwen3.5-plus",method="b1-one-shot",skills_only=True,max_steps=100,
            artifacts=["/root/environment/skills"],prebuilt_image_tag=args.image)
        (out/"generation_result.json").write_text(json.dumps(generation,ensure_ascii=False,indent=2),encoding="utf-8")
        created=set(gen_root.rglob("artifacts"))-before
        candidates=[p/"skills" for p in created if list((p/"skills").rglob("SKILL.md"))]
        if len(candidates)!=1:
            raise RuntimeError("Official generation did not produce a unique nonempty Skill artifact")
        source=candidates[0]
    (out/"skill_source.json").write_text(json.dumps({"path":str(source) if source else None}))
    exit_code,result=run_task(task,agent_id="qwen",model="qwen3.5-plus",skill_config=args.mode,
          skill_source_dir=source,prebuilt_image_tag=args.image,max_steps=100,trial_id="qwen-"+stamp,trials_dir=out/"trials")
    traces=list((out/"trials").rglob("qwen.txt"))
    if traces:
        events=[]
        for line in traces[0].read_text(encoding="utf-8",errors="replace").splitlines():
            try:events.append(json.loads(line))
            except ValueError:pass
        observed={"input_tokens":0,"output_tokens":0,"total_tokens":0}
        for e in events:
            if e.get("type")=="assistant":
                u=e["response"].get("usage",{})
                for target,key in [("input_tokens","prompt_tokens"),("output_tokens","completion_tokens"),("total_tokens","total_tokens")]:observed[target]+=u.get(key,0)
        result["raw_reported_token_usage"]=result.get("token_usage")
        result["token_usage"]=observed
        result["token_usage_scope"]="sum of all logged completed API responses; unreturned billing unobservable"
        finals=[e for e in events if e.get("type")=="result"]
        calls=sum(e.get("type")=="assistant" for e in events)
        if finals and not finals[-1].get("completed") and calls<100 and not result.get("agent_timed_out"):
            result["raw_reported_shell_exit"]=result.get("agent_exit")
            result["agent_exit"]=None
            result["error"]="agent_api_or_runtime_aborted; tee exit does not report actual agent status"
    if result.get("agent_timed_out"):
        result["raw_reported_agent_exit"]=result.get("agent_exit")
        result["agent_exit"]=124
        result["agent_exit_scope"]="normalized timeout status, raw core value preserved separately"
    (out/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    pause=ROOT/"output/qwen_campaign/pause-for-scheduler"
    if args.stage=="formal" and pause.exists():
        (out/"scheduler-pause-ready.json").write_text(json.dumps({"task":args.task,"instance":args.instance,"mode":args.mode}))
        print("Result saved; paused for scheduler handoff",flush=True)
        while pause.exists():time.sleep(5)
    sys.exit(exit_code)

if __name__=="__main__":
    main()

