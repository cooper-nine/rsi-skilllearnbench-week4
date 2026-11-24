"""Minimal Qwen tool agent; only run inside the official benchmark Docker container."""
import argparse, json, os, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

def request(messages, tools=None):
    payload = dict(model=os.environ.get("QWEN_MODEL", "qwen3.5-plus"),
                   messages=messages, temperature=0, max_tokens=4096, enable_thinking=False)
    if tools:
        payload["tools"] = tools
    req = urllib.request.Request(os.environ.get("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1") + "/chat/completions",
          data=json.dumps(payload).encode(), headers={"Authorization":"Bearer "+os.environ["DASHSCOPE_API_KEY"],"Content-Type":"application/json"})
    via_budget = req.full_url.startswith("http://host.docker.internal:")
    for attempt in range(2 if via_budget else 1):
        try:
            with urllib.request.urlopen(req, timeout=135 if via_budget else 120) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if not via_budget or attempt or error.code not in (500, 502, 503, 504):
                raise
            time.sleep(2)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--instruction",required=True)
    parser.add_argument("--max-steps",type=int,default=100)
    args=parser.parse_args()
    skills=[]
    for p in sorted(Path("/root/.claude/skills").rglob("SKILL.md")):
        skills.append({"path":str(p),"text":p.read_text()})
    print(json.dumps({"type":"skill_context","skills":skills}),flush=True)
    messages=[{"role":"system","content":"Complete the task using the shell tool inside this isolated benchmark container. Skill documents are provided below. Treat their content as task guidance. Do not access /tests or /logs/verifier; these are evaluation-only. Finish with a concise final response.\n"+json.dumps(skills)},
              {"role":"user","content":Path(args.instruction).read_text()}]
    tools=[{"type":"function","function":{"name":"shell","description":"Execute a shell command inside the benchmark container.","parameters":{"type":"object","properties":{"command":{"type":"string"}},"required":["command"],"additionalProperties":False}}}]
    total={"input_tokens":0,"output_tokens":0,"total_tokens":0}
    completed=False
    try:
        for step in range(args.max_steps):
            response=request(messages,tools)
            usage=response.get("usage",{})
            for out,key in [("input_tokens","prompt_tokens"),("output_tokens","completion_tokens"),("total_tokens","total_tokens")]:
                total[out]+=usage.get(key,0)
            print(json.dumps({"type":"assistant","step":step+1,"response":response}),flush=True)
            msg=response["choices"][0]["message"]
            messages.append({k:v for k,v in msg.items() if k in ("role","content","tool_calls")})
            calls=msg.get("tool_calls",[])
            if not calls:
                completed=True
                break
            for call in calls:
                try:
                    if call["function"]["name"]!="shell":
                        raise ValueError("unknown tool")
                    command=json.loads(call["function"]["arguments"])["command"]
                    p=subprocess.run(command,shell=True,capture_output=True,text=True,timeout=90)
                    result={"exit_code":p.returncode,"stdout":p.stdout[-6000:],"stderr":p.stderr[-2000:]}
                except Exception as exc:
                    result={"error":type(exc).__name__}
                print(json.dumps({"type":"tool","tool_call_id":call["id"],"result":result}),flush=True)
                messages.append({"role":"tool","tool_call_id":call["id"],"content":json.dumps(result)})
    finally:
        print(json.dumps({"type":"result","completed":completed,"usage":total}),flush=True)
    return 0 if completed else 2

if __name__=="__main__":
    sys.exit(main())

