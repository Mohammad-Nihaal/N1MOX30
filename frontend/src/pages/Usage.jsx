import { useEffect, useState } from "react";
import client from "../api/client";

const LABELS = { youtube: "YouTube long videos", clips: "Clips", messages: "Messages", email: "Gmail / Email", outlook: "Outlook", instagram: "Instagram", x: "X", tiktok: "TikTok" };

export default function Usage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    client.get("/usage/").then((response) => { if (active) setData(response.data); })
      .catch(() => { if (active) setError("Usage information is currently unavailable."); });
    return () => { active = false; };
  }, []);
  if (error) return <section className="page-section"><h1>Usage</h1><p>{error}</p></section>;
  if (!data) return <section className="page-section"><h1>Usage</h1><p>Loading usage…</p></section>;
  return (
    <section className="page-section">
      <div className="page-header"><div><p className="eyebrow">N1MOX30</p><h1>Usage</h1><p>Monthly allowances are enforced by the backend and reset with the billing period.</p></div></div>
      <div className="usage-grid">
        {Object.entries(data.metrics).map(([key, metric]) => (
          <article className="card" key={key}>
            <div className="card-header"><strong>{LABELS[key] || key}</strong><span>{metric.unlimited ? "Unlimited" : `${metric.used} / ${metric.limit}`}</span></div>
            {!metric.unlimited && <div className="usage-track"><div className="usage-fill" style={{ width: `${Math.min(100, (metric.used / metric.limit) * 100)}%` }} /></div>}
            {!metric.unlimited && metric.remaining === 0 && <p className="usage-limit">Monthly limit reached. Resets at the end of the billing period.</p>}
          </article>
        ))}
      </div>
      <p>Plan: <strong>{data.plan}</strong> · Reset: <strong>{new Date(data.period_end).toLocaleDateString()}</strong></p>
    </section>
  );
}
