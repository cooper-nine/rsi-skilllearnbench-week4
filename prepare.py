"""Prepare a fresh, pinned upstream workspace and overlay the submitted adapter."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
COMMIT="726e1f79b96b0cb3d729d0e55a1c847e0b5353ae"

def build_images(target):
    cases = json.loads((target / "qwen/cases.json").read_text(encoding="utf8"))
    for case in cases:
        family, instance = case["family"], case["instance"]
        task = f"{family}-{instance}"
        environment = target / "tasks" / family / task / "environment"
        with tempfile.TemporaryDirectory(prefix="week4-image-", dir=target) as staging:
            context = Path(staging) / "environment"
            shutil.copytree(environment, context, ignore=shutil.ignore_patterns("skills"))
            (context / "skills").mkdir()
            subprocess.run(["docker", "build", "--tag", f"week4-{task}:upstream", str(context)], check=True)

def main():
    p=argparse.ArgumentParser();p.add_argument("--workspace",type=Path,required=True);p.add_argument("--install",action="store_true");p.add_argument("--build-images",action="store_true")
    p.add_argument("--source",type=Path,help="Reuse a local SkillLearnBench clone containing the pinned upstream commit")
    p.add_argument("--images-only",action="store_true",help="Build or retry images in an already prepared workspace")
    a=p.parse_args()
    target=a.workspace.resolve();source=Path(__file__).resolve().parent
    if a.images_only:
        subprocess.run(["git", "-C", str(target), "diff", "--quiet", COMMIT, "--", "tasks"],check=True)
        build_images(target)
        return
    if target.exists() and any(target.iterdir()):raise SystemExit("Use an empty new workspace; existing files will not be overwritten.")
    target.parent.mkdir(parents=True,exist_ok=True)
    def run(*cmd):subprocess.run(list(cmd),check=True)
    if a.source:
        original = a.source.resolve() / ".git"
        if not (original / "objects").is_dir():
            p.error("--source must be a standalone SkillLearnBench clone")
        run("git","init",str(target))
        shutil.copytree(original / "objects", target / ".git/objects",
                        ignore=shutil.ignore_patterns("tmp_*", "*.lock", "alternates"), dirs_exist_ok=True)
        if (original / "shallow").is_file():
            shutil.copy2(original / "shallow", target / ".git/shallow")
    else:
        run("git","clone","--filter=blob:none","--no-checkout","--depth","1","https://github.com/cxcscmu/SkillLearnBench.git",str(target))
    def git(*args):run("git","-C",str(target),*args)
    git("config","core.autocrlf","false")
    git("sparse-checkout","init","--no-cone")
    patterns=["/*.py","/README.md","/BASELINES.md","/LICENSE","/agents/","/core/","/evaluation/","/eval_keypoints/","/baselines/b1-one-shot/"]
    for task in ["earthquake-plate-calculation","financial-analysis","weighted-gdp-calculation","stock-data-visualization"]:
        patterns+=["/tasks/"+task+"/","/skills/human_authored/"+task+"/"]
    git("sparse-checkout","set","--no-cone",*patterns)
    if a.source:
        git("cat-file","-e",COMMIT + "^{commit}")
    else:
        git("fetch","--depth","1","origin",COMMIT)
    for attempt in range(3):
        try:
            git("checkout","--detach",COMMIT)
            break
        except subprocess.CalledProcessError:
            if attempt == 2:
                raise
            time.sleep(3)
    shutil.copytree(source/"qwen",target/"qwen",ignore=shutil.ignore_patterns("__pycache__","*.pyc","HANDOFF.md"),dirs_exist_ok=True)
    for entry in (source / "platform/canvas/runner").glob("*.py"):
        shutil.copy2(entry, target / "qwen" / entry.name)
    vendor = target / "qwen/vendor"
    vendor.mkdir(exist_ok=True)
    with urllib.request.urlopen("https://cdn.jsdelivr.net/npm/d3@6.7.0/dist/d3.min.js", timeout=60) as response:
        library = response.read()
    if hashlib.sha256(library).hexdigest() != "fbb8da602a76f4ed49bac3561da62d8149fa121b8fd15685bacc21355d3a3322":
        raise RuntimeError("D3 checksum mismatch")
    (vendor / "d3.v6.min.js").write_bytes(library)
    state=target/"output/qwen_budget_campaign"
    state.mkdir(parents=True,exist_ok=True)
    protocol=json.loads((source/"protocol.json").read_text(encoding="utf-8"))
    shutil.copy2(source/"protocol.json",state/"protocol.json")
    manifest={"version":3,"parameters":protocol,"smoke":{},"formal":{},"generated_skills":{},"images":{}}
    (state/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    for shell in (target/"tasks").rglob("*.sh"):shell.write_bytes(shell.read_bytes().replace(b"\r\n",b"\n"))
    provenance=json.loads((target/"qwen/uv-cache/provenance.json").read_text())
    cache=target/"qwen/uv-cache/uv-x86_64-unknown-linux-gnu.tar.gz"
    if not cache.exists():
        temporary=cache.with_suffix(".download")
        existing = a.source / "qwen/uv-cache" / cache.name if a.source else None
        if existing and existing.is_file():
            shutil.copyfile(existing, temporary)
        else:
            with urllib.request.urlopen(provenance["url"],timeout=120) as response,temporary.open("wb") as f:
                shutil.copyfileobj(response,f)
        if hashlib.sha256(temporary.read_bytes()).hexdigest()!=provenance["sha256"]:raise RuntimeError("uv checksum mismatch; cache not accepted")
        temporary.replace(cache)
    if a.install:
        run(sys.executable,"-m","venv",str(target/".venv"))
        python=target/".venv"/("Scripts/python.exe" if sys.platform=="win32" else "bin/python")
        run(str(python),"-m","pip","install","--index-url","https://mirrors.aliyun.com/pypi/simple/","-r",str(target/"qwen/requirements-lock.txt"))
    if a.build_images:
        build_images(target)
    print("Prepared:",target)
    print("Set DASHSCOPE_API_KEY, start Docker, then run .venv python qwen/run_all.py")
if __name__=="__main__":main()
