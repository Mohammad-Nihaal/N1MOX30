import { useEffect, useState } from "react";
import { BarChart3, CalendarClock, Link2, Send, ShieldCheck } from "lucide-react";
import api from "../api/client";

export default function SocialHub() {
  const [data,setData]=useState(null); const [error,setError]=useState("");
  useEffect(()=>{api.get("/social-hub/overview").then(r=>setData(r.data)).catch(()=>setError("Connect your social accounts to load the live hub."));},[]);
  return <section className="launch-page">
    <header className="launch-hero"><div><span className="launch-kicker">SOCIAL</span><h1>Social Hub</h1><p>YouTube, Instagram, TikTok and X in one workspace, with provider-authorized capabilities only.</p></div><div className="launch-badge"><ShieldCheck size={16}/> API permissions respected</div></header>
    {error&&<p className="launch-note">{error}</p>}
    <div className="launch-grid four">{["youtube","instagram","tiktok","x"].map(p=><article className="launch-card social-card" key={p}><strong>{p}</strong><span>{data?.accounts?.[p]?.length||0} connected account{(data?.accounts?.[p]?.length||0)===1?"":"s"}</span><div className="social-actions"><span><Link2 size={14}/> Connect</span><span><Send size={14}/> Publish</span><span><CalendarClock size={14}/> Schedule</span><span><BarChart3 size={14}/> Analytics</span></div></article>)}</div>
  </section>;
}
