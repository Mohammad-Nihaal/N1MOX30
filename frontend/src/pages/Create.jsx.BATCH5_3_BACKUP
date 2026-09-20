import { useState } from "react";
import api from "../api/client";

export default function Create() {
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState("youtube");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  async function createWorkflow(event) {
    event.preventDefault();
    if (!topic.trim()) return;
    setBusy(true);
    setResult(null);
    try {
      const response = await api.post("/central-workflow/prepare", {
        command: `Create a ${platform} video about ${topic}`,
        platform,
        topic,
      });
      setResult(response.data);
    } catch (error) {
      setResult({ error: error.response?.data?.detail || error.message });
    } finally {
      setBusy(false);
    }
  }

  return <section className="page-section">
    <div className="page-heading"><div><p className="eyebrow">AUTOMATION</p><h2>Create with N1MOX</h2><p>Give one idea. N1MOX prepares the complete creator workflow.</p></div></div>
    <form className="glass-card create-form" onSubmit={createWorkflow}>
      <label>What should N1MOX create?</label>
      <textarea value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Example: AI replacing traditional jobs" rows={6} />
      <div className="form-row"><select value={platform} onChange={(e) => setPlatform(e.target.value)}><option value="youtube">YouTube</option><option value="instagram">Instagram</option><option value="tiktok">TikTok</option></select><button disabled={busy}>{busy ? "Preparing…" : "Start full workflow"}</button></div>
      {result && <pre className="result-box">{JSON.stringify(result, null, 2)}</pre>}
    </form>
  </section>;
}
