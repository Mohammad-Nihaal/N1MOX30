import { useEffect, useState } from "react";
import { Bot, Check, MessageSquare, Send, ShieldCheck } from "lucide-react";
import api from "../api/client";

const PROVIDERS = ["instagram", "x", "tiktok"];
const CATEGORIES = ["general", "customer enquiry", "collaboration", "sponsorship", "partnership", "support", "pricing", "sales", "complaint", "spam"];

export default function Messages() {
  const [items, setItems] = useState([]);
  const [body, setBody] = useState("");
  const [provider, setProvider] = useState("instagram");
  const [category, setCategory] = useState("general");
  const [status, setStatus] = useState("");

  async function load() {
    try { setItems((await api.get("/communications/messages")).data); } catch { setStatus("Connect a social account to load live messages."); }
  }
  useEffect(() => { load(); }, []);

  async function draft() {
    if (!body.trim()) return;
    try {
      await api.post("/communications/draft", { provider, category, body, auto_reply_enabled: false });
      setBody(""); setStatus("Draft saved. Review before sending."); await load();
    } catch (error) { setStatus(error.response?.data?.detail?.message || error.response?.data?.detail || "Unable to save draft."); }
  }

  return <section className="launch-page">
    <header className="launch-hero"><div><span className="launch-kicker">COMMUNICATION</span><h1>Messages / Inbox</h1><p>One workspace for creator conversations with AI-assisted context, drafting and approval.</p></div><div className="launch-badge"><ShieldCheck size={16}/> Approval-first sending</div></header>
    <div className="launch-grid two">
      <article className="launch-card">
        <div className="launch-card-title"><MessageSquare size={18}/><strong>AI Draft → Review → Send</strong></div>
        <label>Channel<select value={provider} onChange={e=>setProvider(e.target.value)}>{PROVIDERS.map(p=><option key={p}>{p}</option>)}</select></label>
        <label>Category<select value={category} onChange={e=>setCategory(e.target.value)}>{CATEGORIES.map(p=><option key={p}>{p}</option>)}</select></label>
        <label>Message<textarea rows="9" value={body} onChange={e=>setBody(e.target.value)} placeholder="Describe the reply N1MOX30 should prepare..."/></label>
        <button className="launch-primary" onClick={draft}><Bot size={16}/> Save AI draft</button>
        {status && <p className="launch-note">{status}</p>}
      </article>
      <article className="launch-card">
        <div className="launch-card-title"><Send size={18}/><strong>Inbox</strong></div>
        {!items.length && <div className="launch-empty">No messages yet. Connect Instagram, X or TikTok in Accounts.</div>}
        {items.map(item=><div className="launch-list-row" key={item.id}><div><strong>{item.provider} · {item.category}</strong><p>{item.body}</p></div><span>{item.status}</span></div>)}
      </article>
    </div>
  </section>;
}
