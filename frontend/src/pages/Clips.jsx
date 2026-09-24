import { useEffect, useState } from "react";
import { Film, Play, Scissors, ShieldCheck } from "lucide-react";
import api from "../api/client";

const STEPS = ["Transcription", "Valuable moments", "Hook detection", "Clip selection", "Reframing", "Captions", "Brand styling", "Music / audio", "Vertical formatting", "QC", "Ready to publish"];

export default function Clips() {
  const [source, setSource] = useState("");
  const [title, setTitle] = useState("");
  const [formats, setFormats] = useState(["9:16"]);
  const [jobs, setJobs] = useState([]);
  const [status, setStatus] = useState("");
  useEffect(() => { api.get("/clips/jobs").then(r=>setJobs(r.data)).catch(()=>{}); }, []);
  const toggle = f => setFormats(v => v.includes(f) ? v.filter(x=>x!==f) : [...v,f]);
  async function create() {
    try { const r=await api.post("/clips/jobs",{source_path:source,title,formats}); setStatus(r.data.message); setJobs(v=>[{id:r.data.id,status:r.data.status,title,source_path:source,formats},...v]); }
    catch(error){ setStatus(error.response?.data?.detail?.message || error.response?.data?.detail || "Unable to queue clips."); }
  }
  return <section className="launch-page">
    <header className="launch-hero"><div><span className="launch-kicker">CLIPS</span><h1>Long video → ready-to-publish clips</h1><p>Generate 9:16, 1:1 and 16:9 variants through one production pipeline.</p></div><div className="launch-badge"><ShieldCheck size={16}/> QC before publish</div></header>
    <article className="launch-card"><div className="launch-card-title"><Film size={18}/><strong>Generate → Edit → Preview → Schedule → Publish</strong></div>
      <div className="launch-form-grid"><label>Long-video source<input value={source} onChange={e=>setSource(e.target.value)} placeholder="Path or approved media URL"/></label><label>Project title<input value={title} onChange={e=>setTitle(e.target.value)} placeholder="Episode / topic"/></label></div>
      <div className="format-row">{["9:16","1:1","16:9"].map(f=><button key={f} className={formats.includes(f)?"selected":""} onClick={()=>toggle(f)}>{f}</button>)}</div>
      <button className="launch-primary" onClick={create}><Scissors size={16}/> Generate clips</button>{status&&<p className="launch-note">{status}</p>}
    </article>
    <article className="launch-card"><div className="pipeline">{STEPS.map((s,i)=><div key={s}><span>{i+1}</span>{s}</div>)}</div></article>
    <article className="launch-card"><div className="launch-card-title"><Play size={18}/><strong>Jobs</strong></div>{jobs.map(j=><div className="launch-list-row" key={j.id}><div><strong>{j.title||j.source_path}</strong><p>{(j.formats||[]).join(" · ")}</p></div><span>{j.status}</span></div>)}</article>
  </section>;
}
