"""Exercise each numeric Skill node via a bounded Qwen structured code turn."""
import hashlib,json,subprocess,time,uuid
from pathlib import Path
from network_build import preload_verifier_uv
from run_rsi_retests import OUTPUT, baseline_image
import urllib.request, urllib.error

def docker(*a,**kw): return subprocess.run(['docker',*map(str,a)],timeout=900,**kw)
def api(server,key,rule,instruction,state,source,layout,*,python_source=False):
 prompt=json.dumps({'task':instruction,'previous_checkpoint':state,'files':layout,'sources':source},ensure_ascii=False)
 payload={'model':'qwen3.5-plus','temperature':0,'max_tokens':4096,'enable_thinking':False,
          'messages':[{'role':'system','content':rule+(' Return only runnable Python source, no JSON wrapper.'
                      if python_source else ' Return only one JSON object, no markdown.')},{'role':'user','content':prompt}]}
 req=urllib.request.Request(f'http://127.0.0.1:{server.server_port}/chat/completions',json.dumps(payload).encode(),
                            {'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 for attempt in range(2):
  try:
   with urllib.request.urlopen(req,timeout=145) as rsp: res=json.load(rsp)
   break
  except urllib.error.HTTPError as err:
   if attempt or err.code not in (500,502,503,504):raise
   time.sleep(3)
 content=res['choices'][0]['message']['content'].strip()
 if content.startswith('```'): content=content.split('\n',1)[1].rsplit('```',1)[0]
 return ({'python':content} if python_source else json.loads(content)),res['usage']
GUIDES={
 'financial-analysis':{
  'identify':'Generate Python that reads each COVERPAGE.tsv and INFOTABLE.tsv from the original data, finds the named fund accession by case-insensitive fuzzy matching among rows with actual holdings, excludes explicit amendments but allows blank flags, and prints a JSON object mapping each requested fund to the actual quarter-specific accession. No answer values yet.',
  'calculate':'Generate Python that reads the prior accession checkpoint and original TSVs. Import title_class_of_stocks from /tmp/one_fund_analysis.py and filter exact case-insensitive membership before counting stock rows or aggregating positive dollar change by CUSIP. Compute AUM from all rows. Find CUSIPs by stock name in original stock-classified Q2 records and sum Q3 value by manager accession. Write /tmp/candidate-answers.json in task schema and print the actual calculated JSON checkpoint. Do not hardcode output values or guess accessions.',
  'verify':'Generate Python that loads /tmp/candidate-answers.json, validates all requested keys, types, lengths and uniqueness where applicable, then writes /root/answers.json and prints a JSON checkpoint with verified path. Do not invent or recompute values.'}}

def run(family,i,server,key,platform):
 task=f'{family}-{i}'
 dataset=Path('tasks')/family/task
 tests=dataset/'tests'
 pin='726e1f79b96b0cb3d729d0e55a1c847e0b5353ae';output=OUTPUT;mode='qwen3.5-plus'
 subprocess.run(['git','-c','core.safecrlf=false','diff','--quiet',pin,'--',tests.as_posix()],check=True)
 rid=time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]
 root=output/rid
 agent=root/'trials/agent';agent.mkdir(parents=True)
 (root/'artifacts').mkdir()
 spec=json.loads((platform/f'{task}.json').read_bytes())
 graph=root/'flow.json'
 graph.write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf8')
 image=baseline_image(family,i)
 final='answers.json'
 metadata={'task':family,'instance':i,'model':mode,'protocol':'budget-v3-structured-code','upstream_commit':pin,
           'baseline_image':image,'flow_sha256':hashlib.sha256(graph.read_bytes()).hexdigest(),'platform_run_id':platform.name}
 (root/'config.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
 container=f'week4-qwen-numeric-{i}-{rid}'
 previous={}; tokens=0; verifier_exit=None; reward=None; failure=None
 instructions=(dataset/'instruction.md').read_text(encoding='utf8')
 docker('run','-d','--name',container,'--mount',f'type=bind,source={root}/trials,target=/logs',image,'sleep',1200,check=True,stdout=subprocess.DEVNULL)
 try:
  skill,=Path('skills/human_authored/financial-analysis').rglob('one_fund_analysis.py')
  docker('cp',skill,container+':/tmp/one_fund_analysis.py',check=True)
  with (agent/'qwen.txt').open('w',encoding='utf8') as log:
   for node in spec['nodes']:
    stage=node['id']
    attempt_limit=1+spec['retry']['limitPerNode']
    for attempt in range(attempt_limit):
     try:
      rule='Current Skill\n'+node['text']+'\n'+node.get('guidance','')+'\nCurrent stage task\n'+GUIDES[family][stage]
      if family=='financial-analysis':
       rule+='\nThe filesystem is case-sensitive. Real filenames are COVERPAGE.tsv and INFOTABLE.tsv, with headers FILINGMANAGER_NAME, ISAMENDMENT, ACCESSION_NUMBER, TITLEOFCLASS, NAMEOFISSUER, CUSIP, VALUE. Use pandas.read_csv(path, sep=chr(9), dtype=str); do not use manual split or uppercase .TSV. Your task is the current node only.'
       if stage=='identify': rule+='\nReturn {"accessions":{...}} only on stdout, keyed by lowercase underscore fund name plus quarter. The real manager labels are RENAISSANCE TECHNOLOGIES LLC, Berkshire Hathaway Inc, SOROS FUND MANAGEMENT LLC, and Pershing Square Capital Management, L.P. Match these legal names case-insensitively and exactly when present, then fuzzy match only if absent. Keep rows with ISAMENDMENT N or blank; match holdings by accession. Do not compute any final answers.'
       if stage=='calculate': rule+='\nRead the actual accessions from /tmp/previous-checkpoint.json. Do not redo identification. Inserting /tmp into sys.path permits importing title_class_of_stocks from one_fund_analysis. Use pandas exactly via frame["TITLEOFCLASS"].str.lower().isin(title_class_of_stocks), not substring matching, broadening categories, or providing fallback class sets. Determine the target stock CUSIP from stock-classified Q2 rows, then group its Q3 raw holdings by ACCESSION_NUMBER (not by manager name) and map each ranked accession to the manager name. Apply stock-class filtering only for count, holdings changes and Q2 issuer lookup. For Q3 top managers follow original holding_analysis.py: filter the full unclassified INFOTABLE solely by the selected CUSIP; aggregate VALUE by accession, then map FILINGMANAGER_NAME from Q3 COVERPAGE.tsv. INFOTABLE has no FILINGMANAGER_NAME. TSVs are directly under /root/2025-q2 and /root/2025-q3, with no accession subdirectories. Aggregate each quarter by CUSIP before taking an outer-aligned Q3 minus Q2 difference, treating a missing value as zero. Output CUSIP lists and manager name lists as arrays of strings, not objects. Print exactly the required answer keys in JSON, after writing the candidate file.'
       if stage=='verify': rule+='\nOpen the exact candidate JSON path /tmp/candidate-answers.json and write its checked contents to the required output. Do not generate alternative values.'
      rule+='\nReturn {"python":"complete runnable source"} only. Keep the code concise enough to fit a single response. Correct any retry_feedback from the previous attempt instead of repeating it. Your script must print a single JSON object on stdout; execution is in the benchmark container. Do not access official tests. Before this call the previous checkpoint was saved at /tmp/previous-checkpoint.json.'
      state=root/'state.json'
      state.write_text(json.dumps(previous,ensure_ascii=False),encoding='utf8')
      docker('cp',state,container+':/tmp/previous-checkpoint.json',check=True)
      stage_input=instructions
      if family=='financial-analysis':
       select = ('Find Renaissance Technologies Q3 accession, and Berkshire Hathaway Q2 and Q3 accessions.' if i==1 else 'Find Soros Fund Management Q3 accession, and Pershing Square Capital Management Q2 and Q3 accessions.')
       calc = ('q1_answer numeric Renaissance Q3 AUM. q2_answer numeric Renaissance Q3 stock row count. q3_answer list of five CUSIP strings for Berkshire positive value increases. q4_answer list of three manager name strings for Palantir Q3 holders.' if i==1 else 'q1_answer numeric Soros Q3 AUM. q2_answer list of three CUSIP strings for Pershing positive value increases. q3_answer list of five manager name strings for NVIDIA Q3 holders.')
       stage_input={'identify':select,'calculate':calc,
                    'verify':'Validate candidate answers and save /root/answers.json with the same numeric and list fields.'}[stage]
       rule+='\nUse rapidfuzz, which is installed; fuzzywuzzy is unavailable. Your user input is deliberately scoped to this node.'
      source={}
      if stage=='calculate':
       source['original_holding_skill']=next(Path('skills/human_authored/financial-analysis').rglob('holding_analysis.py')).read_text(encoding='utf8')
       rule+='\nUse the exact accession keys provided in the checkpoint. Follow original holding_skill for the manager ranking; do not aggregate FILINGMANAGER_NAME in an INFOTABLE dataframe. Read the original input files at the documented paths. Keep source under 90 lines and omit long commentary.'
      if stage=='calculate' and i==1:
       rule+='\nFor Berkshire purchases, first build filtered Q2 and Q3 stock dataframes using the imported title_class_of_stocks exactly as in the original one_fund_analysis.py. Use those two filtered frames for both accession selections and CUSIP sums. Do not calculate the Berkshire ranking from the raw, unfiltered holdings.'
      if stage=='calculate' and i==3:
       rule+='\nCorrect the narrow NVIDIA search in the earlier draft. Search NAMEOFISSUER across the entire Q2 stock-classified dataframe for NVIDIA, independently of Pershing and uc. Pick the most common CUSIP among matching issuer rows of this common stock; do not restrict to a single fund portfolio. Preserve the working Soros AUM and Pershing outer alignment.'
      response,usage=api(server,key,rule,stage_input,previous,source, {'input_files':['/root/2025-q2','/root/2025-q3','/tmp/one_fund_analysis.py']})
      tokens+=usage['total_tokens']
      code=root/f'{stage}-{attempt+1}.py'
      code.write_text(response['python'],encoding='utf8')
      compile(response['python'],str(code),'exec')
      docker('cp',code,container+':/tmp/current-stage.py',check=True)
      # The official tests are attached only after all stages have executed.
      proc=subprocess.run(['docker','exec',container,'python3','/tmp/current-stage.py'],timeout=100,capture_output=True)
      if proc.returncode:raise ValueError(proc.stderr.decode('utf8',errors='replace')[-1400:])
      emitted=json.loads(proc.stdout)
      if not isinstance(emitted,dict) or not emitted: raise ValueError('Missing runtime checkpoint')
      if family=='financial-analysis' and stage=='identify':
       filings=emitted.get('accessions')
       if not isinstance(filings,dict) or len(filings)<3 or any(not isinstance(v,str) or '-' not in v for v in filings.values()):
        raise ValueError('Expected accessions mapping with at least three real accession strings; do not report final answers from identify')
      if family=='financial-analysis' and stage=='calculate':
       if float(emitted.get('q1_answer',0))<=0 or not emitted.get('q2_answer') or not emitted.get('q3_answer') or (i==1 and not emitted.get('q4_answer')):
        raise ValueError('Calculated answers are missing or empty. Check actual case-sensitive filenames and use the prior accession checkpoint')
       docker('exec',container,'test','-s','/tmp/candidate-answers.json',check=True,capture_output=True)
       required_lists={'q3_answer':5,'q4_answer':3} if i==1 else {'q2_answer':3,'q3_answer':5}
       if any(not isinstance(emitted.get(k),list) or len(emitted[k])!=n or any(not isinstance(v,str) for v in emitted[k]) for k,n in required_lists.items()):
        raise ValueError('Output arrays must contain exactly the requested number of strings, never dicts')
      if stage=='verify':
       docker('cp',f'{container}:/root/{final}',root/'artifacts'/final,check=True,capture_output=True)
      print(json.dumps({'type':'checkpoint','stage':stage,'output':emitted},ensure_ascii=False),file=log,flush=True)
      previous=emitted
      break
     except (ValueError,KeyError,TypeError,SyntaxError,subprocess.SubprocessError) as exc:
      previous={**previous,'retry_feedback':str(exc)[-1000:],'prior_stage_code':response.get('python','') if 'response' in locals() else ''}
      print(json.dumps({'type':'flow','event':'retry','node':stage,'reason':str(exc)[-1000:]}),file=log,flush=True)
      if attempt+1==attempt_limit:raise
  preload_verifier_uv(container,Path('qwen/uv-cache'))
  docker('cp',tests,f'{container}:/tests',check=True)
  with (root/'verifier.stdout.log').open('wb') as out:
   verifier_exit=docker('exec','-e','UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/','-e','UV_DOWNLOAD_URL=file:///tmp/slb-uv-cache',
                        container,'bash','/tests/test.sh',stdout=out,stderr=subprocess.STDOUT).returncode
  reward=int((root/'trials/verifier/reward.txt').read_text().strip())
 except Exception as exc:
  failure=str(exc)
 finally:
  docker('rm','-f',container,check=False,stdout=subprocess.DEVNULL)
 (root/'result.json').write_text(json.dumps(dict(model=mode,verifier_exit=verifier_exit,reward=reward,
   passed=verifier_exit==0 and reward==1,error=failure,token_usage={'total_tokens':tokens}),ensure_ascii=False,indent=2),encoding='utf8')
 print(task,rid,'reward',reward,'error',failure,flush=True)
 return root
