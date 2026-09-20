import { useEffect, useState } from "react";
import api from "../api/client";

export default function Workflows() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  useEffect(() => { api.get("/automation/workflows").then(r => setItems(r.data)).catch(e => setError(e.response?.data?.detail || e.message)); }, []);
  return <section className="page-section"><div className="page-heading"><div><p className="eyebrow">OPERATIONS</p><h2>Workflow Control</h2><p>Monitor, recover and control every N1MOX production run.</p></div></div>{error && <div className="glass-card">{error}</div>}<div className="feature-grid">{items.length ? items.map(w => <div className="glass-card" key={w.id}><strong>{w.topic || w.command || "N1MOX workflow"}</strong><p>{String(w.status || "pending")}</p><small>{w.id}</small></div>) : <div className="glass-card"><strong>No workflows yet</strong><p>Start a creation from the Create page or say “Hey N1MOX”.</p></div>}</div></section>;
}
