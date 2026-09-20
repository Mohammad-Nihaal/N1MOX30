import { useEffect, useState } from "react";
import api from "../api/client";

export default function Settings() {
  const [data, setData] = useState({});
  const [saved, setSaved] = useState(false);
  useEffect(()=>{api.get("/creator-preferences").then(r=>setData(r.data)).catch(()=>{});},[]);
  function change(k,v){setData(x=>({...x,[k]:v}));setSaved(false);}
  async function save(){await api.patch("/creator-preferences", data);setSaved(true);}
  return <section className="page-section"><div className="page-heading"><div><p className="eyebrow">CONTROL CENTER</p><h2>N1MOX Settings</h2><p>Configure creator, AI, voice, workflow, scheduling and approval behavior.</p></div><button onClick={save}>Save settings</button></div><div className="settings-grid"><div className="glass-card"><h3>Creator</h3><label>Topics<input value={data.preferred_topics||""} onChange={e=>change("preferred_topics",e.target.value)}/></label><label>Audience<input value={data.target_audience||""} onChange={e=>change("target_audience",e.target.value)}/></label><label>Brand voice<textarea value={data.brand_voice||""} onChange={e=>change("brand_voice",e.target.value)}/></label></div><div className="glass-card"><h3>AI & automation</h3>{[["creativity_level","Creativity"],["research_depth","Research depth"],["personalization_level","Personalization"],["automation_level","Automation"]].map(([k,l])=><label key={k}>{l}<input type="range" min="0" max="100" value={data[k]??70} onChange={e=>change(k,Number(e.target.value))}/></label>)}<label className="check"><input type="checkbox" checked={data.require_publish_approval??true} onChange={e=>change("require_publish_approval",e.target.checked)}/> Require publishing approval</label></div></div>{saved&&<p className="save-note">Saved.</p>}</section>;
}
