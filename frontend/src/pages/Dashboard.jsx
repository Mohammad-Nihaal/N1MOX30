import "../styles/nimox30-dashboard.css";

const navGroups = [
  {
    label: "WORKSPACE",
    items: [
      ["Dashboard", "◆"]
      ["N1MOX Assistant", "◆"]
      ["Create", "◉"]
      ["Workflows", "+"]
    ],
  },
  {
    label: "INTELLIGENCE",
    items: [
      ["Intelligence", "↗"]
      ["Research", "◆"]
      ["Analytics", "◆"]
      ["Growth", "◉"]
    ],
  },
  {
    label: "PUBLISH",
    items: [
      ["YouTube", "▶"]
      ["Publishing Center", "↗"]
    ],
  },
];

function CyberCharacter({ type, className = "" }) {
  return (
    <div className={`nimox-character ${type} ${className}`} aria-hidden="true">
      <div className="character-aura" />
      <div className="character-shadow" />
      <div className="character-head">
        <span className="character-eye eye-left" />
        <span className="character-eye eye-right" />
      </div>
      <div className="character-neck" />
      <div className="character-body">
        <span className="character-core" />
      </div>
      <div className="character-arm arm-left" />
      <div className="character-arm arm-right" />
      <div className="character-leg leg-left" />
      <div className="character-leg leg-right" />
      <div className="character-energy" />
    </div>
  );
}

function MetricCard({ eyebrow, value, label, trend, visual }) {
  return (
    <div className="metric-card">
      <div>
        <span className="metric-eyebrow">{eyebrow}</span>
        <strong>{value}</strong>
        <span className="metric-label">{label}</span>
      </div>

      {visual === "bars" && (
        <div className="metric-bars">
          {[35, 52, 43, 68, 55, 78, 92].map((height, i) => (
            <i key={i} style={{ height: `${height}%` }} />
          ))}
        </div>
      )}

      {visual === "chart" && (
        <div className="mini-chart">
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
      )}

      {visual === "ring" && (
        <div className="health-ring">
          <div>100%</div>
        </div>
      )}

      {trend && <small className="metric-trend">{trend}</small>}
    </div>
  );
}

export default function Dashboard() {
  return (
    <div className="nimox-dashboard">
      <aside className="nimox-sidebar">
        <div className="brand">
          <div className="brand-mark">N</div>
          <div>
            <strong>N1MOX30</strong>
            <span>Creator Operating System</span>
          </div>
        </div>

        <div className="nav-scroll">
          {navGroups.map((group) => (
            <div className="nav-group" key={group.label}>
              <div className="nav-label">{group.label}</div>

              {group.items.map(([name, icon]) => (
                <button
                  className={`nav-item ${name === "Dashboard" ? "active" : ""}`}
                  key={name}
                  onClick={() => {
                    const routes = {
                      Research: "/research",
                      Analytics: "/analytics",
                      Growth: "/growth",
                      YouTube: "/youtube",
                      "Publishing Center": "/publishing",
                      Workflows: "/creator-os",
                    };

                    if (routes[name]) window.location.href = routes[name];
                  }}
                >
                  <span className="nav-icon">{icon}</span>
                  <span>{name}</span>
                  <b>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Âº</b>
                </button>
              ))}
            </div>
          ))}
        </div>

        <div className="sidebar-status">
          <div className="status-avatar">
            <span />
          </div>
          <div>
            <strong>N1MOX AI</strong>
            <small>Systems operational</small>
          </div>
        </div>

        <div className="sidebar-version">v1.0 ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚· Creator Intelligence</div>
      </aside>

      <main className="nimox-main">
        <header className="nimox-topbar">
          <div className="top-brand">N1MOX30</div>

          <div className="search-box">
            <span>ÃƒÆ’Ã‚Â¢Ãƒ…Ã¢â‚¬â„¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢</span>
            <input
              placeholder="Search content, workflows, insights..."
              aria-label="Search"
            />
            <kbd>ÃƒÆ’Ã‚Â¢Ãƒ…Ã¢â‚¬â„¢Ãƒâ€¹Ã…“ K</kbd>
          </div>

          <div className="top-actions">
            <button className="theme-toggle active">ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬”Ãƒâ€šÃ‚Â Dark</button>
            <button className="theme-toggle">ÃƒÆ’Ã‚Â¢Ãƒâ€¹Ã…“Ãƒâ€šÃ‚Â¼ Light</button>
            <button className="icon-button">ÃƒÆ’Ã‚Â¢Ãƒ…“Ãƒâ€šÃ‚Â£</button>
            <button className="icon-button">ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢Ãƒâ€šÃ‚Â§</button>
            <button className="create-button">ÃƒÆ’Ã‚Â¯Ãƒâ€šÃ‚Â¼ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¹ Create</button>

            <div className="user-chip">
              <div>N</div>
              <span>
                <strong>nihaal</strong>
                <small>Creator workspace</small>
              </span>
            </div>
          </div>
        </header>

        <section className="hero">
          <div className="hero-grid" />

          <div className="hero-content">
            <div className="hero-kicker">
              <i /> N1MOX30 / COMMAND CENTER
            </div>

            <h1>
              Make the
              <br />
              <em>system move.</em>
            </h1>

            <p>
              Your creator operation at a glance ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â intelligence,
              production and growth.
            </p>

            <div className="hero-actions">
              <button className="hero-primary">
                <span>
                  <small>START SOMETHING</small>
                  Create with N1MOX
                </span>
                <b>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢</b>
              </button>

              <button className="hero-secondary">ÃƒÆ’Ã‚Â¢Ãƒ…“Ãƒâ€šÃ‚Â¦ Ask N1MOX <b>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Âº</b></button>
              <button className="hero-secondary">ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢Ãƒâ€šÃ‚Â§ Research <b>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Âº</b></button>
              <button className="hero-secondary">ÃƒÆ’Ã‚Â¢Ãƒ…Ã¢â‚¬â„¢Ãƒâ€¹Ã…“ Run workflow <b>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Âº</b></button>
            </div>
          </div>

          <div className="hero-character-zone">
            <div className="floating-hud hud-one">
              <span>LIVE</span>
              CONTENT ENGINE
            </div>

            <div className="floating-hud hud-two">
              <span>AI</span>
              ANALYZING
            </div>

            <CyberCharacter type="cyber-hero" className="hero-main-character" />
            <CyberCharacter type="tactical-agent" className="hero-side-character" />

            <div className="energy-orb orb-one" />
            <div className="energy-orb orb-two" />

            <div className="hero-graffiti graffiti-one">
              CREATE
              <br />
              <span>ANALYZE</span>
              <br />
              GROW
            </div>

            <div className="hero-graffiti graffiti-two">
              DREAM
              <br />
              BIGGER
            </div>
          </div>

          <div className="system-pill">
            <span />
            SYSTEM OPERATIONAL
            <button>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ Ãƒâ€šÃ‚Â»</button>
          </div>
        </section>

        <section className="metrics">
          <MetricCard
            eyebrow="CREATOR SYSTEM"
            value="NK MIX TAPES"
            label="YouTube intelligence active"
            visual="bars"
          />

          <MetricCard
            eyebrow="CONTENT PIPELINE"
            value="12"
            label="Active projects"
            trend="ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ ÃƒÂ¢Ã¢â€šÂ¬Ã‹Å“ +20%"
            visual="bars"
          />

          <MetricCard
            eyebrow="AUDIENCE MOMENTUM"
            value="24.8K"
            label="Total followers"
            trend="ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ ÃƒÂ¢Ã¢â€šÂ¬Ã‹Å“ +12%"
            visual="chart"
          />

          <MetricCard
            eyebrow="SYSTEM HEALTH"
            value="100%"
            label="All systems operational"
            visual="ring"
          />
        </section>

        <section className="character-strip">
          <div className="strip-copy">
            <span>YOUR CREATOR SQUAD</span>
            <strong>Built for creators who move fast.</strong>
          </div>

          <div className="mini-character-stage">
            <CyberCharacter type="runner" />
            <CyberCharacter type="survivor" />
            <CyberCharacter type="neon-agent" />
          </div>

          <div className="strip-badge">N1MOX AI ACTIVE</div>
        </section>

        <section className="activity-section">
          <div className="section-heading">
            <span>RECENT ACTIVITY</span>
            <button>View all activity ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢</button>
          </div>

          <div className="activity-grid">
            <article className="activity-card">
              <div className="activity-icon youtube">ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬“Ãƒâ€šÃ‚Â¶</div>
              <div>
                <strong>Video script generated</strong>
                <small>12 minutes ago</small>
              </div>
              <div className="activity-thumb thumb-one">
                <CyberCharacter type="runner" />
              </div>
              <b>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢</b>
            </article>

            <article className="activity-card">
              <div className="activity-icon purple">ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬”ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¡</div>
              <div>
                <strong>Thumbnail created</strong>
                <small>28 minutes ago</small>
              </div>
              <div className="activity-thumb thumb-two">
                <CyberCharacter type="neon-agent" />
              </div>
              <b>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢</b>
            </article>

            <article className="activity-card">
              <div className="activity-icon green">ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ ÃƒÂ¢Ã¢â€šÂ¬”</div>
              <div>
                <strong>Competitor analysis complete</strong>
                <small>1 hour ago</small>
              </div>
              <div className="activity-thumb thumb-three">
                <CyberCharacter type="tactical-agent" />
              </div>
              <b>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢</b>
            </article>
          </div>
        </section>

        <div className="dashboard-footer">
          <span>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â</span>
          DISCIPLINE CREATES FREEDOM
          <span>ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â</span>
        </div>
      </main>
    </div>
  );
}
