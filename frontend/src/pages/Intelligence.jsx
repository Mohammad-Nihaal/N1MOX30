import { useEffect, useState } from "react";
import api from "../api/client";

export default function Intelligence() {
  const [data, setData] = useState(null);
  useEffect(() => { api.get("/daily-intelligence").then(r => setData(r.data)).catch(() => setData(null)); }, []);
  const summary = data?.summary || {};
  return <section className="page-section"><div className="page-heading"><div><p className="eyebrow">N1MOX INTELLIGENCE</p><h2>Daily Work Intelligence</h2><p>One operating view for what is running, finished, blocked and next.</p></div></div><div className="stat-grid">{[["Active workflows",summary.active_workflows],["Completed today",summary.completed_today],["Failed",summary.failed_workflows],["Upcoming",summary.upcoming_schedules],["Unread",summary.unread_notifications]].map(([a,b]) => <div className="glass-card stat-card" key={a}><span>{a}</span><strong>{b ?? "—"}</strong></div>)}</div><div className="glass-card"><h3>Next actions</h3>{data?.next_actions?.length ? data.next_actions.map((x,i)=><div className="list-row" key={i}><b>{x.priority}</b><span>{x.message}</span></div>) : <p>No urgent actions. N1MOX is ready for the next creator task.</p>}</div></section>;
}
