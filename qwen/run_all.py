"""One-command launcher: smoke -> formal, plus independent metrics. Resume after a diagnosed error."""
import os,sys,time,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def stop(process):
    if process.poll() is None:
        if os.name=="nt":subprocess.run(["taskkill","/PID",str(process.pid),"/T","/F"],capture_output=True)
        else:process.terminate()
def main():
    hold=ROOT/"output/qwen_campaign/cost-review-required.json"
    if hold.exists() and os.environ.get("SLB_STATE")!="qwen_budget_campaign":
        raise SystemExit("Paid runs blocked pending token-budget and protocol review. See "+str(hold))
    if not os.environ.get("DASHSCOPE_API_KEY"):raise SystemExit("Set DASHSCOPE_API_KEY in your local environment; never put it in source.")
    import campaign
    server=None
    if os.environ.get("SLB_STATE")=="qwen_budget_campaign":
        from budget_proxy import start
        server,secret=start(campaign.STATE)
        port=server.server_port
        os.environ["DASHSCOPE_API_KEY"]=secret
        os.environ["QWEN_BASE_URL"]=f"http://host.docker.internal:{port}"
        os.environ["SLB_JUDGE_URL"]=f"http://127.0.0.1:{port}"
    campaign.save(campaign.load())
    env=os.environ.copy();env["PYTHONUTF8"]="1";env["PYTHONUNBUFFERED"]="1"
    out=ROOT/"output"/os.environ.get("SLB_STATE","qwen_campaign");handles=[];processes=[]
    try:
        for name in ["campaign","watch_metrics"]:
            handle=(out/(name+"-controller.log")).open("a",encoding="utf-8");handles.append(handle)
            processes.append(subprocess.Popen([sys.executable,str(ROOT/"qwen"/(name+".py"))],cwd=ROOT,env=env,stdout=handle,stderr=subprocess.STDOUT))
        while True:
            state=json.loads((out/"manifest.json").read_text())
            valid=[v for v in state["formal"].values() if v.get("complete")]
            metrics=sum(Path(v["run"],"metrics/complete.json").exists() for v in valid)
            print("formal",len(valid),"/69; metrics",metrics,"/69",flush=True)
            codes=[p.poll() for p in processes]
            if any(code not in (None,0) for code in codes):
                raise RuntimeError("Controller failed; inspect output/qwen_campaign/*-controller.log. State retained for resume.")
            if all(code==0 for code in codes):break
            time.sleep(30)
        subprocess.run([sys.executable,str(ROOT/"qwen/report_campaign.py")],cwd=ROOT,check=True)
    finally:
        for process in processes:stop(process)
        for handle in handles:handle.close()
        if server:server.shutdown();server.server_close()
if __name__=="__main__":main()

