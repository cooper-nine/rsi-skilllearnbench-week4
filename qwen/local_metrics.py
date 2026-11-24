import json,re
from pathlib import Path

def write_skill_usage(events,source,out):
    names=sorted(x.parent.name for x in source.rglob("SKILL.md")) if source else []
    evidence={name:[] for name in names}
    for event in events:
        if event.get("type")!="assistant":continue
        for call in event["response"]["choices"][0]["message"].get("tool_calls",[]):
            try:command=json.loads(call["function"]["arguments"]).get("command","")
            except (ValueError,TypeError):continue
            for name in names:
                paths=["/root/.claude/skills/"+name+"/","/root/environment/skills/"+name+"/"]
                if any(path in command for path in paths) and re.search(r"\b(cat|head|tail|sed|python3?|bash|sh|source|cd)\b",command):evidence[name].append(command)
    used=[name for name,commands in evidence.items() if commands]
    (out/"skill_usage_path_evidence.json").write_text(json.dumps({"origin":"project-adapted observable path-reference proxy; NOT native Skill-tool detection","available_skills":names,"skills_with_path_evidence":used,"rate":len(used)/len(names) if names else None,"evidence":evidence,"limitation":"Context-only use without a file/script reference remains unobservable; rate is not causal usage."},ensure_ascii=False,indent=2),encoding="utf-8")
