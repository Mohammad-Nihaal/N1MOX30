import { useEffect, useState } from "react";
import { CheckCircle2, Flame, Target, ListChecks, RefreshCw } from "lucide-react";
import api from "../api/client";

export default function DailyWorkspace(){
 const [data,setData]=useState(null);
 const [loading,setLoading]=useState(true);
 const load=async()=>{setLoading(true);try{setData((await api.get("/workspace/daily")).data)}finally{setLoading(false)}};
 useEffect(()=>{load()},[]);
 if(loading) return <div className="page-loading"><RefreshCw className="spin" size={30}/><p>Loading daily workspace...</p></div>;
 const goals=data?.goals||{};
 return <div className="page-content">
  <div className="page-header"><div><span className="page-eyebrow">CREATOR WORKSPACE</span><h1>Daily Command Center</h1><p>Tasks, goals and momentum for today's creator work.</p></div><button className="secondary-button" onClick={load}><RefreshCw size={17}/> Refresh</button></div>
  <div className="stats-grid">
   <div className="stat-card"><div className="stat-icon"><Flame size={22}/></div><div><p>Creator streak</p><h3>{data?.streak_days||0} days</h3><span>Recent output momentum</span></div></div>
   <div className="stat-card"><div className="stat-icon"><Target size={22}/></div><div><p>Weekly goal</p><h3>{goals.completion_percent||0}%</h3><span>{goals.weekly_content_completed||0} / {goals.weekly_content_target||3} pieces</span></div></div>
  </div>
  <section className="panel" style={{padding:22,marginTop:18}}>
   <div className="n1-section-heading"><div><ListChecks size={18}/><span>Today's action list</span></div></div>
   <div className="n1-check-list">{(data?.tasks||[]).map(t=><div key={t.id}><CheckCircle2 size={17}/><span><strong>{t.title}</strong> — {t.status==="clear"?"Clear":`${t.count} item(s)`}</span></div>)}</div>
  </section>
 </div>
}
