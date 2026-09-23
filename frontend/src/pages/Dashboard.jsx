import { useNavigate } from "react-router-dom";
import "./../styles/n30-fast-ui.css";

const stats = [
  ["CONTENT PIPELINE", "12", "active projects"],
  ["AUDIENCE", "24.8K", "tracked followers"],
  ["SYSTEM HEALTH", "100%", "all systems operational"],
];

const actions = [
  ["Create content", "/app/create", "Turn an idea into a production workflow."],
  ["Run research", "/app/research", "Find topics, signals and audience opportunities."],
  ["Open workflows", "/app/workflows", "Manage repeatable creator automations."],
];

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="n30-page">
      <section className="n30-welcome">
        <div>
          <span className="n30-eyebrow">N1MOX30 / COMMAND CENTER</span>
          <h1>Make the system move.</h1>
          <p>
            Your creator operation at a glance — research, production,
            publishing and growth in one workspace.
          </p>
          <div className="n30-actions">
            <button onClick={() => navigate("/app/create")}>
              Start creating <span>→</span>
            </button>
            <button className="secondary" onClick={() => navigate("/app/assistant")}>
              Ask N1MOX
            </button>
          </div>
        </div>

        <div className="n30-note">
          <span className="n30-dot" />
          SYSTEM OPERATIONAL
          <small>Creator OS ready</small>
        </div>
      </section>

      <section className="n30-stats">
        {stats.map(([label, value, detail]) => (
          <article key={label} className="n30-stat">
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{detail}</small>
          </article>
        ))}
      </section>

      <section className="n30-section">
        <div className="n30-section-head">
          <div>
            <span className="n30-eyebrow">QUICK START</span>
            <h2>Move an idea forward.</h2>
          </div>
          <button className="n30-text-button" onClick={() => navigate("/app/workflows")}>
            View workflows →
          </button>
        </div>

        <div className="n30-action-grid">
          {actions.map(([title, path, description], index) => (
            <button key={title} className="n30-action-card" onClick={() => navigate(path)}>
              <span className="n30-card-number">0{index + 1}</span>
              <strong>{title}</strong>
              <p>{description}</p>
              <span className="n30-card-arrow">→</span>
            </button>
          ))}
        </div>
      </section>

      <section className="n30-section n30-system-grid">
        <article className="n30-feature-card">
          <span className="n30-eyebrow">CREATOR OS</span>
          <h2>13 stages. One connected workflow.</h2>
          <p>
            Research → strategy → hooks → script → production → publishing →
            growth, with the automation layer between each stage.
          </p>
          <button onClick={() => navigate("/app/creator-os-live")}>
            Open Creator OS →
          </button>
        </article>

        <article className="n30-feature-card n30-feature-warm">
          <span className="n30-eyebrow">ACCOUNT &amp; AI</span>
          <h2>Connect your tools without losing control.</h2>
          <p>
            Manage connected platforms and bring your own AI provider keys
            from one place.
          </p>
          <div className="n30-dual-actions">
            <button onClick={() => navigate("/app/accounts")}>Accounts</button>
            <button onClick={() => navigate("/app/byok")}>BYOK / API Keys</button>
          </div>
        </article>
      </section>

      <section className="n30-billing">
        <div>
          <span className="n30-eyebrow">PLANS &amp; BILLING</span>
          <h2>Choose the creator capacity you need.</h2>
          <p>Creator, Pro and Studio plans are available. Razorpay charging remains in test mode until production payments are enabled.</p>
        </div>
        <button onClick={() => navigate("/app/billing")}>Open Billing →</button>
      </section>
    </div>
  );
}
