import {
  AlertCircle,
  BarChart3,
  Eye,
  Heart,
  LoaderCircle,
  MessageCircle,
  RefreshCw,
  TrendingUp,
  Trophy,
  Users,
  Video,
  Globe2,
} from "lucide-react";

import { useEffect, useState } from "react";

import api from "../api/client";


function Analytics() {
  const [dashboard, setDashboard] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [insights, setInsights] = useState(null);
  const [overview, setOverview] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  async function loadAnalytics() {
    try {
      setLoading(true);
      setError("");

      const [dashboardResponse, performanceResponse, insightsResponse, overviewResponse] = await Promise.allSettled([
        api.get("/youtube/dashboard"),
        api.get("/youtube/performance"),
        api.get("/youtube/insights"),
        api.get("/analytics/overview"),
      ]);

      if (dashboardResponse.status === "fulfilled") setDashboard(dashboardResponse.value.data);
      if (performanceResponse.status === "fulfilled") setPerformance(performanceResponse.value.data);
      if (insightsResponse.status === "fulfilled") setInsights(insightsResponse.value.data);
      if (overviewResponse.status === "fulfilled") setOverview(overviewResponse.value.data?.platforms || []);

    } catch (error) {
      console.error(
        "Analytics loading error:",
        error
      );

      setError(
        error?.response?.data?.detail ||
        "Unable to load YouTube analytics."
      );

    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadAnalytics();
  }, []);


  if (loading) {
    return (
      <div className="page-loading">

        <LoaderCircle
          size={32}
          className="spin"
        />

        <p>
          Loading analytics...
        </p>

      </div>
    );
  }


  const channel =
    dashboard?.channel || {};

  const channelName =
    channel?.channel_name ||
    performance?.channel_name ||
    "Your YouTube Channel";

  const subscribers =
    Number(
      channel?.subscriber_count || 0
    );

  const totalViews =
    Number(
      channel?.view_count || 0
    );

  const totalVideos =
    Number(
      channel?.video_count || 0
    );


  const rankedVideos =
    performance?.videos || [];


  const totalRecentViews =
    rankedVideos.reduce(
      (total, video) =>
        total + Number(video.views || 0),
      0
    );


  const totalLikes =
    rankedVideos.reduce(
      (total, video) =>
        total + Number(video.likes || 0),
      0
    );


  const totalComments =
    rankedVideos.reduce(
      (total, video) =>
        total + Number(video.comments || 0),
      0
    );


  const engagementRate =
    totalRecentViews > 0
      ? (
          (
            (totalLikes + totalComments) /
            totalRecentViews
          ) * 100
        ).toFixed(2)
      : "0.00";


  const topVideo =
    rankedVideos.length > 0
      ? rankedVideos[0]
      : null;


  function formatNumber(value) {
    return Number(
      value || 0
    ).toLocaleString();
  }


  function getInsightItems() {
    if (!insights) {
      return [
        "Connect more YouTube data to unlock performance insights.",
      ];
    }

    const items = [];

    Object.entries(insights).forEach(
      ([key, value]) => {
        if (
          typeof value === "string" &&
          value.trim()
        ) {
          items.push(value);
        }

        if (Array.isArray(value)) {
          value.forEach((item) => {
            if (
              typeof item === "string" &&
              item.trim()
            ) {
              items.push(item);
            }
          });
        }
      }
    );

    return items.slice(0, 5);
  }


  const insightItems =
    getInsightItems();


  return (
    <div className="page-content">

      {/* PAGE HEADER */}

      <div className="page-header">

        <div>

          <span className="page-eyebrow">
            PERFORMANCE INTELLIGENCE
          </span>

          <h1>
            Analytics
          </h1>

          <p>
            Analyze your YouTube performance,
            content results, and audience
            engagement.
          </p>

        </div>


        <button
          className="secondary-button"
          onClick={loadAnalytics}
          disabled={loading}
        >

          <RefreshCw size={18} />

          Refresh

        </button>

      </div>


      {/* ERROR */}

      {error && (

        <div className="auth-error">

          <AlertCircle size={18} />

          <span>
            {error}
          </span>

        </div>

      )}


      {/* CROSS-PLATFORM OVERVIEW */}

      <section className="panel" style={{padding: 22, marginBottom: 18}}>
        <div className="panel-header">
          <div><h3>Cross-platform intelligence</h3><p>Latest connected account metrics across your publishing network.</p></div>
          <BarChart3 size={24} />
        </div>
        <div className="stats-grid">
          {["youtube","instagram","tiktok","x"].map((platform) => {
            const item = overview.find((x) => x.platform === platform);
            const latest = item?.latest;
            return (
              <div className="stat-card" key={platform}>
                <div className="stat-icon"><Globe2 size={22}/></div>
                <div>
                  <p>{platform.toUpperCase()}</p>
                  <h3>{formatNumber(latest?.followers || 0)}</h3>
                  <span>{item?.authorized ? "Connected" : "Connect account"} Â· {formatNumber(latest?.likes || 0)} likes</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* CHANNEL OVERVIEW */}

      <section className="analytics-hero panel">

        <div className="analytics-hero-icon">

          <BarChart3 size={32} />

        </div>


        <div>

          <span className="page-eyebrow">
            CONNECTED CHANNEL
          </span>

          <h2>
            {channelName}
          </h2>

          <p>
            Real-time performance intelligence
            from your connected YouTube channel.
          </p>

        </div>

      </section>


      {/* PRIMARY STATS */}

      <section className="stats-grid">

        <div className="stat-card">

          <div className="stat-icon">

            <Users size={23} />

          </div>

          <div>

            <p>
              Subscribers
            </p>

            <h3>
              {formatNumber(subscribers)}
            </h3>

            <span>
              Current audience
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">

            <Eye size={23} />

          </div>

          <div>

            <p>
              Total Views
            </p>

            <h3>
              {formatNumber(totalViews)}
            </h3>

            <span>
              Lifetime reach
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">

            <Video size={23} />

          </div>

          <div>

            <p>
              Videos
            </p>

            <h3>
              {formatNumber(totalVideos)}
            </h3>

            <span>
              Published content
            </span>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">

            <Heart size={23} />

          </div>

          <div>

            <p>
              Engagement
            </p>

            <h3>
              {engagementRate}%
            </h3>

            <span>
              Recent video interaction
            </span>

          </div>

        </div>

      </section>


      {/* RECENT PERFORMANCE */}

      <section className="dashboard-grid">

        <div className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Recent Content Performance
              </h3>

              <p>
                Your highest performing videos
                ranked by views and engagement.
              </p>

            </div>

            <TrendingUp size={24} />

          </div>


          {rankedVideos.length > 0 ? (

            <div className="analytics-video-list">

              {rankedVideos
                .slice(0, 5)
                .map((video, index) => (

                  <div
                    className="analytics-video-item"
                    key={
                      video.video_id ||
                      index
                    }
                  >

                    <div className="video-rank">

                      #{index + 1}

                    </div>


                    <div className="analytics-video-info">

                      <strong>

                        {video.title ||
                          "Untitled Video"}

                      </strong>


                      <div className="analytics-video-metrics">

                        <span>

                          <Eye size={15} />

                          {formatNumber(
                            video.views
                          )}

                        </span>


                        <span>

                          <Heart size={15} />

                          {formatNumber(
                            video.likes
                          )}

                        </span>


                        <span>

                          <MessageCircle
                            size={15}
                          />

                          {formatNumber(
                            video.comments
                          )}

                        </span>

                      </div>

                    </div>

                  </div>

                ))}

            </div>

          ) : (

            <div className="empty-state">

              <Video size={32} />

              <p>
                No recent videos were found.
              </p>

            </div>

          )}

        </div>


        {/* PERFORMANCE SUMMARY */}

        <div className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Performance Summary
              </h3>

              <p>
                Key signals calculated from
                your recent YouTube videos.
              </p>

            </div>

            <BarChart3 size={24} />

          </div>


          <div className="analytics-summary">

            <div>

              <span>
                Recent Video Views
              </span>

              <strong>
                {formatNumber(
                  totalRecentViews
                )}
              </strong>

            </div>


            <div>

              <span>
                Recent Likes
              </span>

              <strong>
                {formatNumber(
                  totalLikes
                )}
              </strong>

            </div>


            <div>

              <span>
                Recent Comments
              </span>

              <strong>
                {formatNumber(
                  totalComments
                )}
              </strong>

            </div>


            <div>

              <span>
                Engagement Rate
              </span>

              <strong>
                {engagementRate}%
              </strong>

            </div>

          </div>


          {topVideo && (

            <div className="top-video-highlight">

              <div className="top-video-icon">

                <Trophy size={20} />

              </div>


              <div>

                <span>
                  TOP PERFORMING VIDEO
                </span>

                <strong>
                  {topVideo.title}
                </strong>

                <p>
                  {formatNumber(
                    topVideo.views
                  )} views
                </p>

              </div>

            </div>

          )}

        </div>

      </section>


      {/* AI INSIGHTS */}

      <section className="panel analytics-insights-panel">

        <div className="panel-header">

          <div>

            <h3>
              N1MOX30 Performance Insights
            </h3>

            <p>
              Intelligence generated from your
              YouTube content performance.
            </p>

          </div>

          <TrendingUp size={24} />

        </div>


        <div className="analytics-insight-list">

          {insightItems.length > 0 ? (

            insightItems.map(
              (insight, index) => (

                <div
                  key={index}
                  className="analytics-insight-item"
                >

                  <div className="insight-number">

                    {index + 1}

                  </div>

                  <span>
                    {insight}
                  </span>

                </div>

              )
            )

          ) : (

            <div className="empty-state">

              <BarChart3 size={32} />

              <p>
                Performance insights will
                appear here as more channel
                data is analyzed.
              </p>

            </div>

          )}

        </div>

      </section>

    </div>
  );
}


export default Analytics;

