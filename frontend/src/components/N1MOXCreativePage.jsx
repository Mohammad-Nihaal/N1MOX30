import React from "react";

const pageMap = {
  "/app/ai-studio": {
    eyebrow: "AI STUDIO",
    title: "Create at the speed of thought.",
    description:
      "Turn ideas into titles, hooks, scripts, captions and production-ready content.",
    accent: "#8d68ff",
  },
  "/app/analytics": {
    eyebrow: "ANALYTICS",
    title: "See what is actually moving.",
    description:
      "Understand views, engagement, content performance and creator momentum.",
    accent: "#ff7568",
  },
  "/app/growth": {
    eyebrow: "GROWTH INTELLIGENCE",
    title: "Turn performance into your next move.",
    description:
      "N1MOX connects content signals with practical growth opportunities.",
    accent: "#71dfaa",
  },
  "/app/research": {
    eyebrow: "RESEARCH INTELLIGENCE",
    title: "Find the opportunity before you create.",
    description:
      "Discover trends, topics and content opportunities before production begins.",
    accent: "#ff9b62",
  },
  "/app/schedules": {
    eyebrow: "AUTOMATION",
    title: "Your content calendar, thinking ahead.",
    description:
      "Coordinate production, scheduling and publishing without losing visibility.",
    accent: "#b26cff",
  },
  "/app/publishing": {
    eyebrow: "PUBLISHING CENTER",
    title: "From finished asset to published content.",
    description:
      "Manage publishing readiness, connected channels and publishing activity.",
    accent: "#ff7568",
  },
};

export default function N1MOXCreativePage({ children, path }) {
  const data = pageMap[path] || {
    eyebrow: "N1MOX30",
    title: "Your creator workspace.",
    description:
      "Everything you need to create, automate, understand and grow.",
    accent: "#ff7568",
  };

  return (
    <div className="nx-visual-page" style={{ minHeight: "100%" }}>
      <div
        className="nx-panel"
        style={{
          margin: "20px 24px 0",
          padding: "22px 24px",
          background: `
            radial-gradient(circle at 90% 30%, ${data.accent}22, transparent 28%),
            linear-gradient(135deg, #321923, #1b1118)
          `,
        }}
      >
        <div className="nx-eyebrow">
          <span
            className="nx-dot"
            style={{ background: data.accent }}
          />
          {data.eyebrow}
        </div>

        <div
          style={{
            marginTop: 12,
            fontSize: "clamp(25px,3vw,42px)",
            lineHeight: 1,
            fontWeight: 900,
            letterSpacing: "-.045em",
          }}
        >
          {data.title}
        </div>

        <div
          style={{
            marginTop: 8,
            maxWidth: 720,
            color: "var(--nx-muted)",
            fontSize: 12,
            lineHeight: 1.6,
          }}
        >
          {data.description}
        </div>
      </div>

      {children}

      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          right: 22,
          bottom: 22,
          width: 54,
          height: 54,
          borderRadius: 18,
          background:
            "linear-gradient(145deg,#ff7568,#8d68ff)",
          boxShadow: "0 14px 45px rgba(255,117,104,.25)",
          opacity: .92,
          zIndex: 20,
          pointerEvents: "none",
        }}
      />
    </div>
  );
}