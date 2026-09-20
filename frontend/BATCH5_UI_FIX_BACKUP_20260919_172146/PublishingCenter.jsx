import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Globe2, Loader2, Send, Sparkles, Music2 } from "lucide-react";
import api from "../api/client";

const PLATFORMS = [
  { id: "Video", name: "Video", icon: "â–¶", tone: "Video" },
  { id: "Camera", name: "Camera", icon: "â—Ž", tone: "Camera" },
  { id: "tiktok", name: "TikTok", icon: "â™ª", tone: "tiktok" },
  { id: "x", name: "X", icon: "ð•", tone: "x" },
];

export default function PublishingCenter() {
  const [accounts, setAccounts] = useState([]);
  const [selected, setSelected] = useState(["Video"]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [videoPath, setVideoPath] = useState("");
  const [mediaUrl, setMediaUrl] = useState("");
  const [status, setStatus] = useState("");
  const [publishing, setPublishing] = useState(false);

  useEffect(() => {
    api.get("/connected-accounts").then((r) => setAccounts(Array.isArray(r.data) ? r.data : [])).catch(() => {});
  }, []);

  const connected = useMemo(() => {
    const map = {};
    accounts.forEach((a) => { if (a.is_active && a.is_authorized) map[a.platform] = a; });
    return map;
  }, [accounts]);

  function toggle(platform) {
    setSelected((current) => current.includes(platform)
      ? current.filter((p) => p !== platform)
      : [...current, platform]);
  }

  async function publish() {
    if (!selected.length) return setStatus("Select at least one platform.");
    setPublishing(true);
    setStatus("");
    try {
      const accountMap = {};
      selected.forEach((p) => { if (connected[p]) accountMap[p] = connected[p].id; });
      const result = await api.post("/multi-publishing/publish", {
        platforms: selected,
        payload: {
          video_path: videoPath,
          media_url: mediaUrl || undefined,
          media_type: "video",
          title,
          description,
          account_id_by_platform: accountMap,
          platform_options_by_platform: Object.fromEntries(
            selected.map((p) => [p, { instagram_account_id: connected[p]?.platform_account_id, is_aigc: true }])
          ),
        },
      });
      const failed = (result.data.results || []).filter((r) => r.status === "failed");
      setStatus(failed.length ? `Completed with ${failed.length} platform failure(s).` : "Publishing workflow completed.");
    } catch (error) {
      setStatus(error?.response?.data?.detail || "Publishing request failed.");
    } finally {
      setPublishing(false);
    }
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <div>
          <span className="page-eyebrow">PUBLISHING OS</span>
          <h1>Publishing Center</h1>
          <p>Prepare once, distribute across your connected creator platforms.</p>
        </div>
        <button className="primary-button" onClick={publish} disabled={publishing}>
          {publishing ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
          {publishing ? "Publishing..." : "Publish everywhere"}
        </button>
      </div>

      <div className="panel" style={{ padding: 22, marginBottom: 18 }}>
        <div className="n1-section-heading">
          <div><Sparkles size={18} /><span>Distribution</span></div>
          <small>{selected.length} platform{selected.length !== 1 ? "s" : ""} selected</small>
        </div>
        <div className="accounts-grid">
          {PLATFORMS.map((p) => {
            const active = selected.includes(p.id);
            const isConnected = Boolean(connected[p.id]);
            return (
              <button key={p.id} className={`platform-select-card ${active ? "selected" : ""}`} onClick={() => toggle(p.id)}>
                <div className={`platform-mark ${p.tone}`}>{p.icon}</div>
                <div>
                  <strong>{p.name}</strong>
                  <span>{isConnected ? "Connected" : "Connect in Accounts"}</span>
                </div>
                {active && <CheckCircle2 size={18} />}
              </button>
            );
          })}
        </div>
      </div>

      <div className="n1-two-column">
        <section className="panel" style={{ padding: 22 }}>
          <div className="n1-section-heading"><div><Globe2 size={18} /><span>Content</span></div></div>
          <label className="n1-field">Title<input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Your high-retention title" /></label>
          <label className="n1-field">Description / caption<textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={8} placeholder="Write the caption, description, hashtags and CTA..." /></label>
          <label className="n1-field">Rendered video path<input value={videoPath} onChange={(e) => setVideoPath(e.target.value)} placeholder="C:\N1MOX30\outputs\video.mp4" /></label>
          <label className="n1-field">Public media URL <span className="n1-help">required for Camera/TikTok URL delivery</span><input value={mediaUrl} onChange={(e) => setMediaUrl(e.target.value)} placeholder="https://media.n1mox.com/videos/video.mp4" /></label>
        </section>

        <section className="panel" style={{ padding: 22 }}>
          <div className="n1-section-heading"><div><Music2 size={18} /><span>Preflight</span></div></div>
          <div className="n1-check-list">
            <div><CheckCircle2 size={17} /> OAuth accounts are resolved server-side.</div>
            <div><CheckCircle2 size={17} /> Platform-specific provider adapters are selected automatically.</div>
            <div><CheckCircle2 size={17} /> Failures are isolated per platform.</div>
            <div><CheckCircle2 size={17} /> Publishing results are returned together.</div>
            <div><CheckCircle2 size={17} /> TikTok/Camera can use the public media URL delivery path.</div>
          </div>
          {status && <div className="auth-error" style={{ marginTop: 18 }}>{status}</div>}
        </section>
      </div>
    </div>
  );
}
