import { useState } from "react";
import { Mail, ShieldCheck, Sparkles } from "lucide-react";
import api from "../api/client";

export default function EmailCenter() {
  const [provider, setProvider] = useState("gmail");
  const [recipient, setRecipient] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [status, setStatus] = useState("");

  async function saveDraft() {
    try {
      await api.post("/communications/draft", { provider, recipient, subject, body, category: "general" });
      setStatus("Email draft saved. Review and authorize sending through the connected provider.");
    } catch (error) { setStatus(error.response?.data?.detail?.message || error.response?.data?.detail || "Unable to save email draft."); }
  }

  return <section className="launch-page">
    <header className="launch-hero"><div><span className="launch-kicker">COMMUNICATION</span><h1>Email Center</h1><p>Draft professional Gmail and Outlook/Microsoft replies with creator approval before external sending.</p></div><div className="launch-badge"><ShieldCheck size={16}/> Authorized send only</div></header>
    <article className="launch-card launch-email-card">
      <div className="launch-card-title"><Sparkles size={18}/><strong>Natural-language email assistant</strong></div>
      <div className="launch-suggestions"><button onClick={()=>setBody("Create a professional reply to this.")}>Create a professional reply</button><button onClick={()=>setBody("Write a collaboration proposal with clear next steps and a professional tone.")}>Draft collaboration email</button><button onClick={()=>setBody("Draft a concise follow-up for this sponsor.")}>Sponsor follow-up</button></div>
      <div className="launch-form-grid"><label>Provider<select value={provider} onChange={e=>setProvider(e.target.value)}><option value="gmail">Gmail</option><option value="outlook">Outlook / Microsoft</option></select></label><label>Recipient<input value={recipient} onChange={e=>setRecipient(e.target.value)} placeholder="brand@example.com"/></label></div>
      <label>Subject<input value={subject} onChange={e=>setSubject(e.target.value)} placeholder="Collaboration proposal"/></label>
      <label>Email<textarea rows="12" value={body} onChange={e=>setBody(e.target.value)} placeholder="Draft the email here..."/></label>
      <button className="launch-primary" onClick={saveDraft}><Mail size={16}/> Save draft</button>
      {status && <p className="launch-note">{status}</p>}
    </article>
  </section>;
}
