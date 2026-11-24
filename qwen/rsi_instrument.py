"""Insert the treatment into a copy of the recorded Qwen protocol."""
import json
from pathlib import Path


def instrument(agent, flow):
    runtime = Path(__file__).with_name("rsi_flow_runtime.py").read_text(encoding="utf-8-sig")
    runtime += "\nFLOW_SPEC = json.loads(" + repr(json.dumps(flow, ensure_ascii=False)) + ")\n"
    replacements = {
        'print(json.dumps({"type":"skill_context","skills":skills}),flush=True)':
            'flow = SkillFlow(FLOW_SPEC)\n    skills = []',
        'response=request(compact(messages),tools)':
            'if flow.active:\n'
            '                messages[0]["content"] = base_prompt + "\\n" + flow.guidance()\n'
            '            else:\n'
            '                messages[0]["content"] = base_prompt\n'
            '            response=request(compact(messages), tools + ([ADVANCE_TOOL] if flow.active else []))',
        '    completed=False':
            '    base_prompt = messages[0]["content"]\n    completed=False',
        '            if not calls:\n                completed=True':
            '            if not calls and flow.active:\n'
            '                flow.log("premature_final")\n'
            '                messages[-1]["content"] = (msg.get("content") or "") + '
            '"\\n[Flow is still active. Next turn, continue this stage or call advance_skill.]"\n'
            '                continue\n'
            '            if not calls:\n                completed=True',
        '                    if call["function"]["name"]!="shell":':
            '                    name = call["function"]["name"]\n'
            '                    if name == "advance_skill" and flow.active:\n'
            '                        reason = json.loads(call["function"]["arguments"]).get("skip_reason", "").strip()\n'
            '                        if reason:\n'
            '                            flow.log("skip")\n'
            '                            flow.failed = False\n'
            '                        result = flow.advance()\n'
            '                        print(json.dumps({"type":"tool","tool_call_id":call["id"],"result":result}),flush=True)\n'
            '                        messages.append({"role":"tool","tool_call_id":call["id"],"content":json.dumps(result)})\n'
            '                        continue\n'
            '                    if name!="shell":',
        '                print(json.dumps({"type":"tool","tool_call_id":call["id"],"result":result}),flush=True)':
            '                if flow.active:\n'
            '                    flow.accept_shell_result(result)\n'
            '                print(json.dumps({"type":"tool","tool_call_id":call["id"],"result":result}),flush=True)',
    }
    # Apply anchors in reverse so inserted tool branches do not affect subsequent matches.
    for before, after in reversed(list(replacements.items())):
        if agent.count(before) != 1:
            raise ValueError(f"Unsupported agent source near {before!r}")
        agent = agent.replace(before, after, 1)
    source = runtime + "\n" + agent
    compile(source, "<flow-agent>", "exec")
    return source
