"""Run an upstream metric script using a logged, fixed Qwen judge configuration."""
import sys, os, runpy, json, uuid
from pathlib import Path
import openai
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
def main():
    script=Path(sys.argv[1]).resolve()
    raw=Path(os.environ["QWEN_JUDGE_LOG_DIR"]);raw.mkdir(parents=True,exist_ok=True)
    os.environ["OPENAI_API_KEY"]=os.environ["DASHSCOPE_API_KEY"]
    os.environ["OPENAI_BASE_URL"]=os.environ.get("SLB_JUDGE_URL","https://dashscope.aliyuncs.com/compatible-mode/v1")
    OriginalAsync,OriginalSync=openai.AsyncOpenAI,openai.OpenAI
    def normalize(kw):
        kw=dict(kw);kw["temperature"]=0
        if "max_completion_tokens" in kw:kw["max_tokens"]=kw.pop("max_completion_tokens")
        kw["extra_body"]={**(kw.get("extra_body") or {}),"enable_thinking":False}
        if os.environ.get("SLB_JUDGE_URL"):
            kw["max_tokens"]=min(kw.get("max_tokens") or 2048,2048)
        return kw
    def save(kw,r):
        (raw/(uuid.uuid4().hex+".json")).write_text(json.dumps({"request":kw,"response":r.model_dump()},ensure_ascii=False,indent=2),encoding="utf-8")
    def response_arguments(model,input,reasoning_effort=None):
        if not isinstance(input,str):
            raise TypeError("Skill judge Responses input must be a text string")
        if script.name in ("compute_safety.py", "compute_executability.py"):
            dimensions = ("data_privacy", "prompt_injection", "illegal_or_offensive_content",
                          "bias_or_discrimination", "system_integrity", "untrusted_communication")
            if script.name == "compute_executability.py":
                dimensions = ("completeness", "determinism", "consistency", "usability")
            keys = ", ".join(name + "_score" for name in dimensions)
            template = "{" + ", ".join(f'"{name}_score": <integer 1-5>' for name in dimensions) + "}"
            format_instruction = (
                "Use the user rubric to evaluate the provided skill. Return JSON. "
                "Start the object with every numeric field in this template: " + template +
                ". Then add one short sentence per reason using the corresponding _reason keys. "
                "Replace each placeholder with your rubric-based score."
            )
            input += ("\nReturn a JSON object. Include every top-level numeric score field: "
                      + keys + ". Include the original rubric's reasons and overall_score. "
                      "Reason fields cannot substitute for numeric scores.")
            return {"model":model,"messages":[{"role":"system","content":format_instruction},
                        {"role":"user","content":input}],
                    "max_tokens":2048,"response_format":{"type":"json_object"}}
        return {"model":model,"messages":[{"role":"user","content":input}],"max_tokens":2048}
    class LoggedAsync(OriginalAsync):
        def __init__(self,*a,**kw):
            kw.update(timeout=90,max_retries=0);super().__init__(*a,**kw)
            original=self.chat.completions.create
            async def create(**kwargs):
                kwargs=normalize(kwargs);r=await original(**kwargs);save(kwargs,r);return r
            self.chat.completions.create=create
            async def create_response(**kwargs):
                result=await create(**response_arguments(**kwargs))
                return SimpleNamespace(output_text=result.choices[0].message.content)
            self.responses.create=create_response
    class LoggedSync(OriginalSync):
        def __init__(self,*a,**kw):
            kw.update(timeout=90,max_retries=0);super().__init__(*a,**kw)
            original=self.chat.completions.create
            def create(**kwargs):
                kwargs=normalize(kwargs);r=original(**kwargs);save(kwargs,r);return r
            self.chat.completions.create=create
            def create_response(**kwargs):
                result=create(**response_arguments(**kwargs))
                return SimpleNamespace(output_text=result.choices[0].message.content)
            self.responses.create=create_response
    openai.AsyncOpenAI,openai.OpenAI=LoggedAsync,LoggedSync
    sys.path.insert(0,str(script.parent))
    sys.argv=[str(script)]+sys.argv[2:]
    runpy.run_path(str(script),run_name="__main__")
if __name__=="__main__":main()

