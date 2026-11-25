'use client';
import React, {useEffect,useRef,useState} from 'react';
import VisualDiagram from '@horsecoder/visual-core';
const catalog = {
 earthquake: ['地震板块','第 5 题',[
  ['prepare','检查输入','题面、地震记录、板块数据','字段清单与测距口径'],
  ['filter','筛选地震','检查输出、原始地震记录','板块代码、事件与坐标'],
  ['measure','计算距离','筛选结果、板块边界','两种边界表示的测距结果'],
  ['verify','组装并检查答案','事件和测距检查点','answer.json']]],
 financial: ['金融分析','第 1、3 题',[
  ['identify','确认基金申报','题面、季度申报表、持仓表','基金及各季度申报编号'],
  ['calculate','计算持仓与变化','申报编号、持仓字段','规模、持仓数和变化排名'],
  ['verify','组装并检查答案','计算结果、题目输出要求','answers.json']]],
 gdp: ['加权 GDP','第 1、4、5 题',[
  ['requirements','确认工作簿要求','题面、原始工作簿','目标单元格和公式契约'],
  ['read','定位数据与年份','工作簿契约、Data 页','数据区域、年份和序列映射'],
  ['calculate','写公式与加权','行列映射、原始工作簿','带公式的 gdp.xlsx'],
  ['verify','重算并检查','候选工作簿','gdp.xlsx 及校验结果']]],
 stock: ['股票可视化','第 1、2、3、4 题',[
  ['prepare','检查数据与依赖','题面、原始股票数据','文件格式、字段、输出契约'],
  ['render','画气泡图和表格','原始数据、输出契约','本地网页、气泡图与表格'],
  ['interact','实现悬停和联动','渲染产物、交互要求','提示框、行与气泡联动'],
  ['verify','浏览器检查','网页、数据和交互结果','通过本地检查的 output/']]]
};
const width=207, height=153, y=112;
function Card({element,pendant}){
 const d=pendant.data.detail;
 return <div style={{boxSizing:'border-box',width,height,border:'1px solid #c8d6e3',borderTop:'4px solid '+element.state.color,borderRadius:10,padding:'13px 12px',background:'#fff'}}>
 <div style={{fontSize:18,fontWeight:700,marginBottom:4}}>{element.state.name}</div>
 <div style={{color:element.state.color,fontSize:12,marginBottom:11}}>{d.official?'独立判分':'Qwen 3.5 Plus · 子 Skill'}</div>
 <div style={{fontSize:13,lineHeight:1.7}}>输入　{d.input}<br/>输出　{d.output}</div>
 </div>;
}
function Link({link}){
 const p=link.state.points;
 return <g><path d={p.map((t,i)=>(i?'L':'M')+t.x+','+t.y).join(' ')} stroke="#577596" strokeWidth="2" fill="none"/><path d={'M'+(p.at(-1).x-8)+','+(p.at(-1).y-5)+' L'+p.at(-1).x+','+p.at(-1).y+' L'+(p.at(-1).x-8)+','+(p.at(-1).y+5)} fill="none" stroke="#577596" strokeWidth="2"/></g>
}
const config={toolbarConfig:[],elementConfig:{components:{stage:{component:Card,minSize:{width,height}}}},linkConfig:{components:{route:{component:Link,hasArrow:true,showName:false}}},globalConfig:{gridSize:25}};
export default function Visual(){
 const ref=useRef(null);
 const [type,setType]=useState('earthquake');
 const [target,setTarget]=useState('');
 const [message,setMessage]=useState('');
 const [busy,setBusy]=useState(false);
 const [family,cases,nodes]=catalog[type];
 const stages=[...nodes,['official','官方验收','容器内的最终产物','原版 test.sh 的 reward']];
 const elements=stages.map(([id,name,input,output],i)=>({
 id,name,type:'stage',x:27+i*(stages.length===4?330:257),y,locked:false,select:false,color:id==='official'?'#188368':'#215aaf',
 pendant:{data:{type:'stage',detail:{input,output,official:id==='official'}}}
}));
const links=elements.slice(1).map((next,i)=>({
 id:'edge-'+i,name:'通过',type:'route',color:'#577596',points:[{x:elements[i].x+width,y:y+58},{x:next.x,y:y+58}],fromElementId:elements[i].id,toElementId:next.id
}));

 const storageKey='week4-canvas-'+type;
 useEffect(()=>{
  const saved=localStorage.getItem(storageKey);
  ref.current?.setView(saved ? JSON.parse(saved) : {id:storageKey,elements,links});
 },[storageKey]);
 function save(){
  const view=ref.current?.getView();
  if(!view)return;
  localStorage.setItem(storageKey,JSON.stringify(view));
  setMessage('已保存 '+family+' 画布');
  return view;
 }
 async function run(mode){
  const view=save();
  if(!view)return;
  const graphs=Object.fromEntries(Object.keys(catalog).map(familyKey=>{
   const stored=localStorage.getItem('week4-canvas-'+familyKey);
   return [familyKey,stored ? JSON.parse(stored) : null];
  }));
  if(Object.values(graphs).some(graph=>!graph)){
   setMessage('请先保存四类画布');
   return;
  }
  setBusy(true);
  try{
   const response=await fetch('/test/week4/launch',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({mode,graphs,target:mode==='fresh' ? target : ''}),
   });
   if(!response.ok)throw new Error('平台启动失败（HTTP '+response.status+'）');
   const result=await response.json();
   const launch=result.data?.value;
   if(!response.ok || !launch?.platformRunId)throw new Error('RSI 后端未返回运行 ID');
   setMessage(launch.launchStatus+' · '+launch.platformRunId);
  }catch(error){setMessage(error.message);}
  finally{setBusy(false);}
 }
 return <main style={{width:1320,margin:'42px auto',zoom:'min(1, calc(100vw / 1380px))'}}>
 <header style={{marginBottom:22}}><div style={{fontSize:14,color:'#295c8a'}}>RSI Flow Platform · 第四周</div><h1 style={{margin:'10px 0',fontSize:34}}>{family} · Qwen 节点编排</h1><div style={{color:'#485f76',fontSize:16}}>{cases} · 原始题目输入 · Docker 官方验收</div></header>
 <div style={{display:'flex',gap:12,marginBottom:16}}>
 <select aria-label="任务类型" value={type} onChange={event=>setType(event.target.value)}>
 {Object.entries(catalog).map(([id,[label]])=><option key={id} value={id}>{label}</option>)}
 </select>
 <button type="button" onClick={save}>保存画布</button>
 <select aria-label="运行题目" value={target} onChange={event=>setTarget(event.target.value)}>
 <option value="">全部十题</option>
 {Object.entries({
 'earthquake-plate-calculation':[5],'financial-analysis':[1,3],
 'weighted-gdp-calculation':[1,4,5],'stock-data-visualization':[1,2,3,4],
 }).flatMap(([familyId,instances])=>instances.map(instance=>{
  const id=familyId+'-'+instance;
  return <option key={id} value={id}>{id}</option>;
 }))}
 </select>
 <button type="button" disabled={busy} onClick={()=>run('fresh')}>从原始输入运行</button>
 <button type="button" disabled={busy} onClick={()=>run('recheck')}>复核已有产物</button>
 {target==='stock-data-visualization-4' &&
 <button type="button" disabled={busy} onClick={()=>run('repair-stock-4')}>续修股票第 4 题</button>}
 <output aria-live="polite">{message}</output>
 </div>
 <section aria-label="可拖动编排画布" style={{height:390,position:'relative',border:'1px solid #c8d6e3',borderRadius:12,overflow:'hidden',background:'#eaf0f6'}}>
 <div style={{position:'absolute',left:27,top:24,zIndex:3,fontSize:15,color:'#485f76',pointerEvents:'none'}}>检查点通过后向右传递</div>
 <VisualDiagram ref={ref} canvasConfig={config}/>
 <aside style={{position:'absolute',left:27,bottom:27,zIndex:4,background:'#fff6e7',border:'1px solid #e8c58b',borderRadius:8,padding:'13px 17px',color:'#713d15',fontSize:14,pointerEvents:'none'}}>补救分支　节点失败 → 留在当前阶段修复 → 再提交检查点。官方判分失败记录为整题未通过。</aside>
 </section>
 <footer style={{marginTop:18,fontSize:14,color:'#526679'}}>从当前 RSI Flow Platform 页面向 Spring Boot 提交十题复测</footer>
 </main>;
}
