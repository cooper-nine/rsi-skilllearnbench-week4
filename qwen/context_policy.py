"""Deterministic context policy candidate; offline-only until a new protocol is validated."""
import copy,json

def compact(messages,keep_exchanges=3):
    if keep_exchanges<1:raise ValueError('keep_exchanges must be positive')
    prefix=[];groups=[]
    for original in messages:
        item=copy.deepcopy(original)
        if item['role'] in ('system','user') and not groups:prefix.append(item)
        elif item['role']=='assistant':groups.append([item])
        elif item['role']=='tool' and groups:groups[-1].append(item)
        else:raise ValueError('Unexpected message order')
    if len(groups)<=keep_exchanges:return prefix+[m for g in groups for m in g]
    old=groups[:-keep_exchanges];recent=groups[-keep_exchanges:]
    notes=[]
    for group in old:
        assistant=group[0]
        for call in assistant.get('tool_calls',[]):
            notes.append('command: '+call.get('function',{}).get('arguments','')[:400])
        for message in group[1:]:
            notes.append('result: '+str(message.get('content',''))[:200])
    # A deterministic excerpt, not a model-generated factual summary. Full logs stay on disk.
    summary='Older execution excerpts (incomplete; inspect saved files when needed):\n'+'\n'.join(notes)[-3000:]
    return prefix+[{'role':'user','content':summary}]+[m for g in recent for m in g]

def projected_charge_bound(messages,spent_tokens,output_limit=2048,case_limit=150000):
    # UTF-8 byte count is a conservative proxy, NOT an exact Qwen tokenizer count.
    estimate=len(json.dumps(messages,ensure_ascii=False).encode('utf-8'))+2048+output_limit
    return {'allow':spent_tokens+estimate<=case_limit,'estimated_next_token_upper_proxy':estimate,'case_limit':case_limit}
