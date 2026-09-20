import { useEffect, useState } from "react";
import {
  AlertCircle,
  ArrowUpRight,
  BarChart3,
  BrainCircuit,
  CalendarDays,
  ChevronRight,
  Clapperboard,
  FileText,
  Lightbulb,
  Play,
  RefreshCw,
  Send,
  Sparkles,
  TrendingUp,
  Video,
  WandSparkles,
  Workflow,
} from "lucide-react";

import { useNavigate } from "react-router-dom";
import api from "../api/client";

const pipeline = [
  {
    number: "01",
    title: "Research",
    description: "Discover signals",
    icon: Lightbulb,
  },
  {
    number: "02",
    title: "Strategy",
    description: "Find the angle",
    icon: BrainCircuit,
  },
  {
    number: "03",
    title: "Script",
    description: "Build the story",
    icon: FileText,
  },
  {
    number: "04",
    title: "Production",
    description: "Generate assets",
    icon: Clapperboard,
  },
  {
    number: "05",
    title: "Publish",
    description: "Ship everywhere",
    icon: Send,
  },
];

function Dashboard() {
  const navigate = useNavigate();

  const [dashboard, setDashboard] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [insights, setInsights] = useState(null);
  const [growthScore, setGrowthScore] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboardData() {
    try {
      setLoading(true);
      setError("");

      const results = await Promise.allSettled([
        api.get("/youtube/dashboard"),
        api.get("/youtube/performance"),
        api.get("/youtube/insights"),
        api.get("/youtube/growth-score"),
      ]);

      const [
        dashboardResult,
        performanceResult,
        insightsResult,
        growthResult,
      ] = results;

      const dashboardData =
        dashboardResult.status === "fulfilled"
          ? dashboardResult.value.data
          : null;

      const performanceData =
        performanceResult.status === "fulfilled"
          ? performanceResult.value.data
          : null;

      const insightsData =
        insightsResult.status === "fulfilled"
          ? insightsResult.value.data
          : null;

      const growthData =
        growthResult.status === "fulfilled"
          ? growthResult.value.data
          : null;

      if (!dashboardData) {
        const dashboardError =
          dashboardResult.reason?.response?.data?.detail ||
          "Unable to load your YouTube dashboard.";

        throw new Error(dashboardError);
      }

      setDashboard(dashboardData);
      setPerformance(performanceData);
      setInsights(insightsData);
      setGrowthScore(growthData);
    } catch (loadError) {
      console.error("Dashboard loading error:", loadError);

      setDashboard(null);
      setPerformance(null);
      setInsights(null);
      setGrowthScore(null);

      setError(
        loadError?.message ||
          loadError?.response?.data?.detail ||
          "Unable to load dashboard data."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      loadDashboardData();
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  const channel = dashboard?.channel || {};
  const videos = dashboard?.recent_videos || [];

  const insightList = Array.isArray(insights?.insights)
    ? insights.insights
    : [];

  const channelName =
    channel.channel_name || "YouTube workspace";

  const hasYouTube = Boolean(dashboard);

  const growthValue =
    growthScore?.growth_score ?? "--";

  const videosAnalyzed =
    performance?.total_videos_analyzed ??
    videos.length ??
    0;

  const growthBarWidth =
    typeof growthValue === "number"
      ? Math.min(
          100,
          Math.max(0, growthValue)
        ) + "%"
      : "0%";

  if (loading) {
    return (
      <div className="nm-dashboard">
        <div className="nm-dashboard-loading">
          <div className="nm-loading-core">
            <div />
            <span>N</span>
          </div>

          <span className="nm-dashboard-loading-label">
            INITIALIZING CREATOR OS
          </span>

          <p>
            Loading your intelligence workspace...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="nm-dashboard">
        <section className="nm-dashboard-error">
          <div className="nm-error-icon">
            <AlertCircle size={24} />
          </div>

          <span className="nm-dashboard-kicker">
            SYSTEM / CONNECTION
          </span>

          <h1>
            Your command center
            <br />
            needs a connection.
          </h1>

          <p>{error}</p>

          <div className="nm-error-actions">
            <button
              type="button"
              className="nm-command-button primary"
              onClick={loadDashboardData}
            >
              <RefreshCw size={16} />
              Retry connection
            </button>

            <button
              type="button"
              className="nm-command-button"
              onClick={() =>
                navigate("/app/accounts")
              }
            >
              Connect account
              <ArrowUpRight size={16} />
            </button>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="nm-dashboard">
      <section className="nm-dashboard-header">
        <div>
          <div className="nm-dashboard-kicker">
            <span className="nm-live-dot" />
            N1MOX30 / COMMAND CENTER
          </div>

          <h1>
            Make the
            <br />
            <span>system move.</span>
          </h1>

          <p>
            Your creator operation at a glance —
            intelligence, production and growth.
          </p>
        </div>

        <div className="nm-dashboard-header-actions">
          <div className="nm-system-status">
            <span className="nm-system-status-dot" />
            SYSTEM OPERATIONAL
          </div>

          <button
            type="button"
            className="nm-dashboard-refresh"
            onClick={loadDashboardData}
            aria-label="Refresh dashboard"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </section>

      <section className="nm-command-strip">
        <button
          type="button"
          onClick={() =>
            navigate("/app/create")
          }
          className="nm-command-primary"
        >
          <Sparkles size={17} />

          <span>
            <small>START SOMETHING</small>
            Create with N1MOX
          </span>

          <ArrowUpRight size={16} />
        </button>

        <button
          type="button"
          onClick={() =>
            navigate("/app/assistant")
          }
          className="nm-command-item"
        >
          <WandSparkles size={17} />
          Ask N1MOX
        </button>

        <button
          type="button"
          onClick={() =>
            navigate("/app/research")
          }
          className="nm-command-item"
        >
          <Lightbulb size={17} />
          Research
        </button>

        <button
          type="button"
          onClick={() =>
            navigate("/app/workflows")
          }
          className="nm-command-item"
        >
          <Workflow size={17} />
          Run workflow
        </button>
      </section>

      <section className="nm-dashboard-hero">
        <div className="nm-hero-copy">
          <span className="nm-small-label">
            CREATOR SYSTEM
          </span>

          <div className="nm-channel-line">
            <div className="nm-channel-avatar">
              <Video size={19} />
            </div>

            <div>
              <strong>
                {hasYouTube
                  ? channelName
                  : "No channel connected"}
              </strong>

              <span>
                {hasYouTube
                  ? "YouTube intelligence active"
                  : "Connect a platform to activate intelligence"}
              </span>
            </div>
          </div>

          <div className="nm-hero-actions">
            {hasYouTube ? (
              <button
                type="button"
                className="nm-inline-action"
                onClick={() =>
                  navigate("/app/youtube")
                }
              >
                Open YouTube intelligence
                <ArrowUpRight size={15} />
              </button>
            ) : (
              <button
                type="button"
                className="nm-inline-action"
                onClick={() =>
                  navigate("/app/accounts")
                }
              >
                Connect YouTube
                <ArrowUpRight size={15} />
              </button>
            )}
          </div>
        </div>

        <div className="nm-hero-orbit">
          <div className="nm-dashboard-orbit orbit-1" />
          <div className="nm-dashboard-orbit orbit-2" />
          <div className="nm-dashboard-orbit orbit-3" />

          <div className="nm-dashboard-orbit-core">
            <span>N</span>
            <small>30</small>
          </div>

          <div className="nm-orbit-dot dot-a" />
          <div className="nm-orbit-dot dot-b" />
        </div>

        <div className="nm-hero-index">
          <span>01</span>
          CREATOR
          <br />
          OPERATING
          <br />
          SYSTEM
        </div>
      </section>

      <section className="nm-metric-grid">
        <MetricCard
          label="Growth score"
          value={growthValue}
          suffix={
            growthValue !== "--"
              ? "/100"
              : ""
          }
          description={
            growthScore?.summary ||
            "Performance intelligence"
          }
          icon={TrendingUp}
          accent
        />

        <MetricCard
          label="Videos analyzed"
          value={videosAnalyzed}
          description="Content currently indexed"
          icon={BarChart3}
        />

        <MetricCard
          label="AI insights"
          value={insightList.length}
          description="Recommendations generated"
          icon={BrainCircuit}
        />

        <MetricCard
          label="Platform"
          value={hasYouTube ? "01" : "00"}
          description={
            hasYouTube
              ? "YouTube connected"
              : "Connect your first platform"
          }
          icon={Video}
        />
      </section>

      <section className="nm-dashboard-section">
        <div className="nm-section-heading">
          <div>
            <span className="nm-small-label">
              THE ENGINE
            </span>

            <h2>
              From signal
              <span> to publish.</span>
            </h2>
          </div>

          <button
            type="button"
            className="nm-section-link"
            onClick={() =>
              navigate("/app/workflows")
            }
          >
            Open automation
            <ArrowUpRight size={14} />
          </button>
        </div>

        <div className="nm-pipeline">
          {pipeline.map((stage, index) => {
            const Icon = stage.icon;

            return (
              <div
                className="nm-pipeline-stage"
                key={stage.number}
              >
                <div className="nm-pipeline-number">
                  {stage.number}
                </div>

                <div className="nm-pipeline-icon">
                  <Icon size={18} />
                </div>

                <strong>{stage.title}</strong>

                <span>
                  {stage.description}
                </span>

                {index <
                  pipeline.length - 1 && (
                  <div className="nm-pipeline-connector">
                    <ChevronRight size={13} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      <section className="nm-intelligence-grid">
        <div className="nm-command-panel nm-growth-panel">
          <PanelHeading
            eyebrow="PERFORMANCE"
            title="Growth intelligence"
            icon={TrendingUp}
          />

          <div className="nm-growth-number">
            <strong>{growthValue}</strong>

            {growthValue !== "--" && (
              <span>/ 100</span>
            )}
          </div>

          <div className="nm-growth-bar">
            <span
              style={{
                width: growthBarWidth,
              }}
            />
          </div>

          <p className="nm-panel-description">
            {growthScore?.summary ||
              "Connect your creator platform to generate a personalized growth score."}
          </p>

          <button
            type="button"
            className="nm-panel-action"
            onClick={() =>
              navigate("/app/growth")
            }
          >
            Explore growth
            <ArrowUpRight size={14} />
          </button>
        </div>

        <div className="nm-command-panel">
          <PanelHeading
            eyebrow="AI BRAIN"
            title="Latest intelligence"
            icon={BrainCircuit}
          />

          {insightList.length > 0 ? (
            <div className="nm-insight-list">
              {insightList
                .slice(0, 3)
                .map((insight, index) => {
                  const text =
                    typeof insight ===
                    "string"
                      ? insight
                      : insight?.message ||
                        insight?.title ||
                        JSON.stringify(
                          insight
                        );

                  return (
                    <div
                      className="nm-insight-row"
                      key={index}
                    >
                      <div className="nm-insight-index">
                        0{index + 1}
                      </div>

                      <p>{text}</p>

                      <ArrowUpRight
                        size={14}
                      />
                    </div>
                  );
                })}
            </div>
          ) : (
            <div className="nm-empty-intelligence">
              <BrainCircuit size={28} />

              <strong>
                Intelligence waiting
              </strong>

              <span>
                More performance data will
                unlock deeper recommendations.
              </span>
            </div>
          )}

          <button
            type="button"
            className="nm-panel-action"
            onClick={() =>
              navigate("/app/intelligence")
            }
          >
            Open intelligence
            <ArrowUpRight size={14} />
          </button>
        </div>
      </section>

      <section className="nm-lower-grid">
        <div className="nm-command-panel">
          <PanelHeading
            eyebrow="ACTIVITY"
            title="Recent production"
            icon={Play}
          />

          {videos.length > 0 ? (
            <div className="nm-video-list">
              {videos
                .slice(0, 4)
                .map((video, index) => (
                  <div
                    className="nm-video-row"
                    key={
                      video.id ||
                      video.video_id ||
                      index
                    }
                  >
                    <div className="nm-video-index">
                      0{index + 1}
                    </div>

                    <div className="nm-video-thumb">
                      <Play size={12} />
                    </div>

                    <div className="nm-video-info">
                      <strong>
                        {video.title ||
                          video.name ||
                          "Untitled video"}
                      </strong>

                      <span>
                        {video.views != null
                          ? String(
                              video.views
                            ) + " views"
                          : "Content indexed"}
                      </span>
                    </div>

                    <ChevronRight size={15} />
                  </div>
                ))}
            </div>
          ) : (
            <div className="nm-empty-production">
              <Clapperboard size={28} />

              <strong>
                No production activity
              </strong>

              <span>
                Start your first piece of
                content with N1MOX30.
              </span>

              <button
                type="button"
                onClick={() =>
                  navigate("/app/create")
                }
              >
                Create something
                <ArrowUpRight size={14} />
              </button>
            </div>
          )}
        </div>

        <div className="nm-command-panel nm-schedule-panel">
          <PanelHeading
            eyebrow="OPERATIONS"
            title="Today's workspace"
            icon={CalendarDays}
          />

          <div className="nm-operation-status">
            <div className="nm-operation-ring">
              <span>0</span>
            </div>

            <div>
              <strong>
                No active runs
              </strong>

              <span>
                Your automation queue is clear.
              </span>
            </div>
          </div>

          <div className="nm-operation-actions">
            <button
              type="button"
              onClick={() =>
                navigate("/app/daily")
              }
            >
              Daily workspace
              <ArrowUpRight size={14} />
            </button>

            <button
              type="button"
              onClick={() =>
                navigate("/app/schedules")
              }
            >
              View scheduler
              <ArrowUpRight size={14} />
            </button>
          </div>
        </div>
      </section>

      <section className="nm-dashboard-footer">
        <div>
          <span className="nm-system-status-dot" />
          N1MOX ENGINE OPERATIONAL
        </div>

        <span>
          INTELLIGENCE · AUTOMATION · CREATION
        </span>

        <span>
          N1MOX30 / 2026
        </span>
      </section>
    </div>
  );
}

function MetricCard({
  label,
  value,
  suffix = "",
  description,
  icon: Icon,
  accent = false,
}) {
  return (
    <article
      className={
        "nm-metric-card" +
        (accent ? " accent" : "")
      }
    >
      <div className="nm-metric-top">
        <span>{label}</span>
        <Icon size={16} />
      </div>

      <div className="nm-metric-value">
        <strong>{value}</strong>

        {suffix && (
          <span>{suffix}</span>
        )}
      </div>

      <p>{description}</p>

      <div className="nm-metric-line" />
    </article>
  );
}

function PanelHeading({
  eyebrow,
  title,
  icon: Icon,
}) {
  return (
    <div className="nm-panel-heading">
      <div>
        <span>{eyebrow}</span>
        <h3>{title}</h3>
      </div>

      <Icon size={18} />
    </div>
  );
}

export default Dashboard;