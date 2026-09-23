import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowUpRight,
  BarChart3,
  CalendarDays,
  CheckCircle2,
  CreditCard,
  KeyRound,
  Play,
  Sparkles,
  Users,
  Video,
} from "lucide-react";
import api from "../api/client";

function formatNumber(value) {
  const n = Number(value || 0);
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n.toLocaleString();
}

export default function Dashboard() {
  const navigate = useNavigate();

  const [dashboard, setDashboard] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [insights, setInsights] = useState(null);
  const [growth, setGrowth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const [d, p, i, g] = await Promise.allSettled([
          api.get("/youtube/dashboard"),
          api.get("/youtube/performance"),
          api.get("/youtube/insights"),
          api.get("/youtube/growth-score"),
        ]);

        if (!active) return;

        setDashboard(d.status === "fulfilled" ? d.value?.data : null);
        setPerformance(p.status === "fulfilled" ? p.value?.data : null);
        setInsights(i.status === "fulfilled" ? i.value?.data : null);
        setGrowth(g.status === "fulfilled" ? g.value?.data : null);
      } finally {
        if (active) setLoading(false);
      }
    }

    load();

    return () => {
      active = false;
    };
  }, []);

  const channel = dashboard?.channel || {};
  const videos = dashboard?.recent_videos || performance?.videos || [];

  const stats = [
    {
      label: "Subscribers",
      value: formatNumber(channel.subscriber_count),
      note: "Current channel",
      icon: Users,
    },
    {
      label: "Views",
      value: formatNumber(channel.view_count),
      note: "Channel total",
      icon: Play,
    },
    {
      label: "Videos",
      value: formatNumber(channel.video_count || videos.length),
      note: "Published content",
      icon: Video,
    },
    {
      label: "Growth score",
      value: growth?.score != null ? `${growth.score}/100` : "—",
      note: "Creator signal",
      icon: BarChart3,
    },
  ];

  return (
    <div className="nm-clean-dashboard">

      <section className="nm-dash-hero">
        <div>
          <p className="nm-eyebrow">CREATOR OPERATING SYSTEM</p>

          <h1>
            Make content.
            <br />
            Let N1MOX30 handle the rest.
          </h1>

          <p className="nm-hero-copy">
            One calm workspace for research, creation, publishing and growth.
          </p>
        </div>

        <button
          className="nm-primary-button"
          onClick={() => navigate("/app/create")}
        >
          <Sparkles size={17} />
          Create content
        </button>
      </section>

      <section className="nm-stat-grid">
        {stats.map(({ label, value, note, icon: Icon }) => (
          <article className="nm-stat-card" key={label}>
            <div className="nm-stat-icon">
              <Icon size={18} />
            </div>

            <span>{label}</span>
            <strong>{loading ? "..." : value}</strong>
            <small>{note}</small>
          </article>
        ))}
      </section>

      <section className="nm-dashboard-grid">

        <article className="nm-panel nm-main-panel">

          <div className="nm-panel-head">
            <div>
              <p className="nm-eyebrow">TODAY</p>
              <h2>Your creator workspace</h2>
            </div>

            <button
              className="nm-text-button"
              onClick={() => navigate("/app/analytics")}
            >
              View analytics
              <ArrowUpRight size={15} />
            </button>
          </div>

          <div className="nm-action-grid">

            <button onClick={() => navigate("/app/create")}>
              <Sparkles size={19} />
              <span>
                <b>Create</b>
                <small>Turn an idea into content</small>
              </span>
            </button>

            <button onClick={() => navigate("/app/research")}>
              <BarChart3 size={19} />
              <span>
                <b>Research</b>
                <small>Find topics worth making</small>
              </span>
            </button>

            <button onClick={() => navigate("/app/schedules")}>
              <CalendarDays size={19} />
              <span>
                <b>Schedule</b>
                <small>Plan your publishing</small>
              </span>
            </button>

            <button onClick={() => navigate("/app/accounts")}>
              <Youtube size={19} />
              <span>
                <b>Connect accounts</b>
                <small>Manage creator platforms</small>
              </span>
            </button>

          </div>
        </article>

        <article className="nm-panel nm-side-panel">

          <p className="nm-eyebrow">SYSTEM STATUS</p>
          <h2>Ready when you are.</h2>

          <div className="nm-status-row">
            <CheckCircle2 size={17} />
            <span>Creator workflow</span>
            <b>Ready</b>
          </div>

          <div className="nm-status-row">
            <CheckCircle2 size={17} />
            <span>AI Studio</span>
            <b>Ready</b>
          </div>

          <div className="nm-status-row">
            <CheckCircle2 size={17} />
            <span>Scheduling</span>
            <b>Ready</b>
          </div>

          <div className="nm-mini-links">

            <button onClick={() => navigate("/app/byok")}>
              <KeyRound size={16} />
              Bring Your Own API
            </button>

            <button onClick={() => navigate("/app/billing")}>
              <CreditCard size={16} />
              Billing & Plans
            </button>

          </div>

        </article>

      </section>

      <section className="nm-panel nm-insight-panel">

        <div>
          <p className="nm-eyebrow">LATEST SIGNAL</p>

          <h2>
            {insights?.headline || "Your next move starts here."}
          </h2>

          <p>
            {insights?.summary ||
              "Connect your creator accounts and let N1MOX30 turn performance data into practical next steps."}
          </p>
        </div>

        <button
          className="nm-secondary-button"
          onClick={() => navigate("/app/creator-os-live")}
        >
          Open Creator OS
          <ArrowUpRight size={15} />
        </button>

      </section>

    </div>
  );
}

