"""Network-only adjustments applied to disposable official build contexts."""
from pathlib import Path

def install_build_workaround(runner, evidence_dir):
    original=runner._prepare_build_env
    def prepare(*args,**kwargs):
        directory=original(*args,**kwargs)
        dockerfile=directory/"Dockerfile"
        text=dockerfile.read_text()
        anchor="RUN apt-get update"
        replacement=("RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then "
            "sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources; fi"
            " && if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then "
            "sed -i -E 's#http://(archive.ubuntu.com|security.ubuntu.com)/ubuntu#https://mirrors.aliyun.com/ubuntu#g' /etc/apt/sources.list.d/ubuntu.sources; fi"
            " && printf 'Acquire::http::Timeout \"20\";\\nAcquire::https::Timeout \"20\";\\nAcquire::Retries \"1\";\\n' > /etc/apt/apt.conf.d/99-benchmark-timeouts"
            " && apt-get update")
        if anchor not in text:
            raise RuntimeError("Unrecognized official Dockerfile; refusing automatic adjustment")
        text=text.replace(anchor,replacement,1)
        text=text.replace("RUN pip install", "RUN pip install --timeout 120 --retries 3 --index-url https://mirrors.aliyun.com/pypi/simple/")
        text=text.replace("RUN pip3 install", "RUN pip3 install --timeout 120 --retries 3 --index-url https://mirrors.aliyun.com/pypi/simple/")
        if text.startswith("FROM ubuntu:"):
            bundle=Path(__file__).parent/"build-ca.pem"
            (directory/"slb-build-ca.pem").write_bytes(bundle.read_bytes())
            first,rest=text.split("\n",1)
            text=first+"\nCOPY slb-build-ca.pem /etc/ssl/certs/ca-certificates.crt\n"+rest
        dockerfile.write_text(text)
        Path(evidence_dir,"Dockerfile.effective").write_text(text)
        return directory
    runner._prepare_build_env=prepare


    import subprocess, os
    class BoundedBuild:
        def __init__(self):
            self.verifier_mounts={}
        def __getattr__(self, name):
            return getattr(subprocess, name)
        def run(self, command, *args, **kwargs):
            if isinstance(command,list) and command[:2]==["docker","run"]:
                command=list(command)
                container=command[command.index("--name")+1]
                filtered=[];i=0
                while i<len(command):
                    if command[i]=="-v" and i+1<len(command) and command[i+1].endswith(":/tests:ro"):
                        self.verifier_mounts[container]=command[i+1].rsplit(":/tests:",1)[0];i+=2
                    else:filtered.append(command[i]);i+=1
                command=filtered
            if isinstance(command,list) and command[:2]==["docker","exec"] and command[-1]=="pkill -f claude || true":
                cleanup=r"""import os,signal,re
from pathlib import Path
parents={};targets=set()
for directory in Path('/proc').glob('[0-9]*'):
    try:
        pid=int(directory.name)
        parents[pid]=int(re.search(r'^PPid:\s*(\d+)',(directory/'status').read_text(),re.M).group(1))
        if b'/tmp/qwen_agent.py' in (directory/'cmdline').read_bytes().split(bytes([0])):targets.add(pid)
    except (OSError,ValueError,AttributeError):pass
while True:
    expanded=targets|{pid for pid,parent in parents.items() if parent in targets}
    if expanded==targets:break
    targets=expanded
for pid in sorted(targets,reverse=True):
    try:os.kill(pid,signal.SIGKILL)
    except ProcessLookupError:pass
"""
                command=["docker","exec",command[2],"python3","-c",cleanup]
            if kwargs.get("text") or kwargs.get("universal_newlines"):
                kwargs.setdefault("encoding", "utf-8")
                kwargs.setdefault("errors", "replace")
            if isinstance(command, list) and command[:2] == ["docker", "build"]:
                kwargs["timeout"] = 1800
                if kwargs.pop("capture_output", False):
                    kwargs["stdout"] = subprocess.PIPE
                    kwargs["stderr"] = subprocess.PIPE
                process = subprocess.Popen(command, *args, **{k:v for k,v in kwargs.items() if k != "timeout"})
                try:
                    stdout, stderr = process.communicate(timeout=1800)
                    result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
                except subprocess.TimeoutExpired:
                    if os.name == "nt":
                        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
                    else:
                        process.kill()
                    stdout, stderr = process.communicate(timeout=15)
                    result = subprocess.CompletedProcess(command, 124, stdout, (stderr or "") + "\nBUILD_WALL_TIMEOUT_1800_SECONDS")
                Path(evidence_dir, "build.stdout.log").write_text(result.stdout or "", encoding="utf-8")
                Path(evidence_dir, "build.stderr.log").write_text(result.stderr or "", encoding="utf-8")
                return result
            if isinstance(command,list) and command[:2] == ["docker","exec"] and command[-1] == "/tests/test.sh":
                packages=subprocess.run(["docker","exec",command[2],"python3","-m","pip","freeze"],capture_output=True,text=True,encoding="utf-8",errors="replace")
                Path(evidence_dir,"runtime-packages.txt").write_text(packages.stdout or "",encoding="utf-8")
                tests=self.verifier_mounts.get(command[2])
                if tests:
                    subprocess.run(["docker","cp",tests,command[2]+":/tests"],capture_output=True,check=True)
                subprocess.run(["docker","cp",command[2]+":/root/answer.json",str(Path(evidence_dir,"answer.json"))],capture_output=True)
                family=Path(tests).parent.parent.name if tests else ""
                outputs={"financial-analysis":"/root/answers.json","weighted-gdp-calculation":"/root/gdp.xlsx","stock-data-visualization":"/root/output"}
                if family in outputs:
                    destination=Path(evidence_dir,"artifacts");destination.mkdir(exist_ok=True)
                    copied=subprocess.run(["docker","cp",command[2]+":"+outputs[family],str(destination)],capture_output=True,text=True,encoding="utf-8",errors="replace")
                    import json
                    Path(evidence_dir,"artifact-copy.json").write_text(json.dumps({"source":outputs[family],"exit_code":copied.returncode,"stderr":copied.stderr},indent=2),encoding="utf-8")
                cache=Path(__file__).parent/"uv-cache"
                if tests and "astral.sh/uv/0.9.7/install.sh" in (Path(tests)/"test.sh").read_text(encoding="utf-8") and (cache/"uv-x86_64-unknown-linux-gnu.tar.gz").exists():
                    subprocess.run(["docker","cp",str(cache),command[2]+":/tmp/slb-uv-cache"],capture_output=True,check=True)
                    command=["docker","exec","-e","UV_DOWNLOAD_URL=file:///tmp/slb-uv-cache",*command[2:]]
                result = subprocess.run(command,*args,**kwargs)
                Path(evidence_dir,"verifier.stdout.log").write_text(result.stdout or "",encoding="utf-8")
                Path(evidence_dir,"verifier.stderr.log").write_text(result.stderr or "",encoding="utf-8")
                return result
            return subprocess.run(command, *args, **kwargs)
    runner.subprocess = BoundedBuild()
