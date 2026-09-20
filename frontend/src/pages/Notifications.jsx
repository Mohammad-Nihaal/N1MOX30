import { useEffect, useState } from "react";
import api from "../api/client";

export default function Notifications() {
  const [items, setItems] = useState([]);
  async function load(){ try { setItems((await api.get("/notifications")).data); } catch { setItems([]); } }
  useEffect(() => { load(); }, []);
  async function read(id){ await api.post(`/notifications/${id}/read`); load(); }
  return <section className="page-section"><div className="page-heading"><div><p className="eyebrow">ACTIVITY</p><h2>Notifications</h2><p>Publishing, workflow and creator intelligence events.</p></div><button onClick={async()=>{await api.post("/notifications/read-all");load();}}>Mark all read</button></div><div className="feature-grid">{items.length ? items.map(n=><button className={`glass-card notification ${n.is_read ? "read" : ""}`} key={n.id} onClick={()=>read(n.id)}><strong>{n.title}</strong><p>{n.message}</p><small>{new Date(n.created_at).toLocaleString()}</small></button>) : <div className="glass-card"><strong>All clear</strong><p>No notifications are waiting.</p></div>}</div></section>;
}
