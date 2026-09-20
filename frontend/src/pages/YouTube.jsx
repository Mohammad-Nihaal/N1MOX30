import { useEffect, useState } from "react";
import {
  AlertCircle,
  BarChart3,
  BrainCircuit,
  Eye,
  Heart,
  Lightbulb,
  LoaderCircle,
  MessageCircle,
  RefreshCw,
  TrendingUp,
  Trophy,
  Users,
  Video,
} from "lucide-react";

import api from "../api/client";


function YouTube() {
  const [dashboard, setDashboard] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [insights, setInsights] = useState(null);
  const [growthScore, setGrowthScore] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  async function loadYouTubeData() {
    try {
      setLoading(true);
      setError("");

      const [
        dashboardResponse,
        performanceResponse,
        insightsResponse,
        growthResponse,
      ] = await Promise.all([
        api.get("/youtube/dashboard"),
        api.get("/youtube/performance"),
        api.get("/youtube/insights"),
        api.get("/youtube/growth-score"),
      ]);

      setDashboard(dashboardResponse.data);
      setPerformance(performanceResponse.data);
      setInsights(insightsResponse.data);
      setGrowthScore(growthResponse.data);

    } catch (error) {
      console.error(
        "YouTube loading error:",
        error
      );

      setError(
        error?.response?.data?.detail ||
        "Unable to load YouTube intelligence."
      );

    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadYouTubeData();
  }, []);


  function formatNumber(value) {
    const number = Number(value || 0);

    return new Intl.NumberFormat().format(number);
  }


  function getVideoPerformanceLabel(index) {
    if (index === 0) {
      return "Top Performer";
    }

    if (index === 1) {
      return "Strong Performance";
    }

    if (index === 2) {
      return "Above Average";
    }

    return "Recent Video";
  }


  if (loading) {
    return (
      <div className="page-content">
        <div className="page-loading">
          <LoaderCircle
            size={34}
            className="spin"
          />

          Loading YouTube intelligence...
        </div>
      </div>
    );
  }


  if (error) {
    return (
      <div className="page-content">

        <div className="page-header">
          <div>
            <span className="page-eyebrow">
              YouTube INTELLIGENCE
            </span>

            <h1>
              YouTube Dashboard
            </h1>

            <p>
              Analyze your YouTube channel performance.
            </p>
          </div>
        </div>


        <div className="auth-error">
          <AlertCircle size={20} />

          <div>
            <strong>
              Unable to load YouTube data
            </strong>

            <span>
              {error}
            </span>
          </div>
        </div>


        <button
          className="auth-submit"
          onClick={loadYouTubeData}
        >
          <RefreshCw size={19} />

          Try Again
        </button>

      </div>
    );
  }


  const channel = dashboard?.channel || {};

  const videos = dashboard?.recent_videos || [];

  const rankedVideos = performance?.videos || [];

  const channelName =
    channel.channel_name ||
    performance?.channel_name ||
    "YouTube Channel";


  return (
    <div className="page-content">

      <div className="page-header">

        <div>

          <span className="page-eyebrow">
            YouTube INTELLIGENCE
          </span>

          <h1>
            {channelName}
          </h1>

          <p>
            Monitor performance, discover insights,
            and understand your creator growth.
          </p>

        </div>


        <button
          className="secondary-button"
          onClick={loadYouTubeData}
        >
          <RefreshCw size={18} />

          Refresh
        </button>

      </div>


      <section className="YouTube-overview">

        <div className="panel YouTube-channel-card">

          <div className="YouTube-channel-header">

            <div className="YouTube-channel-avatar">

              {channel.thumbnail ? (

                <img
                  src={channel.thumbnail}
                  alt={channelName}
                />

              ) : (

                <Video size={34} />

              )}

            </div>


            <div>

              <span>
                CONNECTED CHANNEL
              </span>

              <h2>
                {channelName}
              </h2>

              <p>
                YouTube creator intelligence is active.
              </p>

            </div>

          </div>

        </div>


        <div className="stats-grid YouTube-stats">

          <div className="stat-card">

            <div className="stat-icon">
              <Users size={22} />
            </div>

            <div>

              <p>
                Subscribers
              </p>

              <h3>
                {formatNumber(
                  channel.subscriber_count
                )}
              </h3>

              <span>
                Channel audience
              </span>

            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              <Eye size={22} />
            </div>

            <div>

              <p>
                Total Views
              </p>

              <h3>
                {formatNumber(
                  channel.view_count
                )}
              </h3>

              <span>
                Lifetime views
              </span>

            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              <Video size={22} />
            </div>

            <div>

              <p>
                Videos
              </p>

              <h3>
                {formatNumber(
                  channel.video_count
                )}
              </h3>

              <span>
                Published videos
              </span>

            </div>

          </div>

        </div>

      </section>


      <section className="dashboard-grid">

        <div className="panel growth-score-card">

          <div className="panel-header">

            <div>

              <h3>
                Growth Score
              </h3>

              <p>
                Overall recent creator performance.
              </p>

            </div>

            <TrendingUp size={26} />

          </div>


          <div className="growth-score-value">

            <h2>
              {growthScore?.growth_score ?? "--"}
            </h2>

            <span>
              / 100
            </span>

          </div>


          <p className="growth-summary">
            {growthScore?.summary ||
              "Growth data is being analyzed."}
          </p>

        </div>


        <div className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Videos Analyzed
              </h3>

              <p>
                Recent videos used for intelligence.
              </p>

            </div>

            <BarChart3 size={26} />

          </div>


          <div className="big-metric">
            {performance?.total_videos_analyzed ||
              videos.length}
          </div>


          <p className="metric-description">
            N1MOX30 analyzes recent YouTube videos to
            identify performance patterns.
          </p>

        </div>

      </section>


      <section className="panel">

        <div className="panel-header">

          <div>

            <h3>
              Video Performance
            </h3>

            <p>
              Your recent videos ranked by performance.
            </p>

          </div>

          <Trophy size={25} />

        </div>


        {rankedVideos.length === 0 ? (

          <div className="empty-state">

            <Video size={42} />

            <h3>
              No videos found
            </h3>

            <p>
              Upload videos to your connected YouTube
              channel to analyze performance.
            </p>

          </div>

        ) : (

          <div className="video-performance-list">

            {rankedVideos.map(
              (video, index) => (

                <div
                  className="video-performance-item"
                  key={
                    video.video_id ||
                    index
                  }
                >

                  <div className="video-rank">
                    #{index + 1}
                  </div>


                  {video.thumbnail ? (

                    <img
                      className="video-thumbnail"
                      src={video.thumbnail}
                      alt={video.title}
                    />

                  ) : (

                    <div className="video-thumbnail-placeholder">
                      <Video size={24} />
                    </div>

                  )}


                  <div className="video-main-info">

                    <strong>
                      {video.title ||
                        "Untitled Video"}
                    </strong>

                    <span>
                      {getVideoPerformanceLabel(
                        index
                      )}
                    </span>

                  </div>


                  <div className="video-metrics">

                    <div>
                      <Eye size={16} />

                      {formatNumber(
                        video.views
                      )}
                    </div>


                    <div>
                      <Heart size={16} />

                      {formatNumber(
                        video.likes
                      )}
                    </div>


                    <div>
                      <MessageCircle size={16} />

                      {formatNumber(
                        video.comments
                      )}
                    </div>

                  </div>

                </div>

              )
            )}

          </div>

        )}

      </section>


      <section className="panel">

        <div className="panel-header">

          <div>

            <h3>
              Performance Insights
            </h3>

            <p>
              AI-driven observations from your recent
              YouTube performance.
            </p>

          </div>

          <BrainCircuit size={25} />

        </div>


        <div className="insights-grid">

          {insights?.insights &&
          Array.isArray(insights.insights) ? (

            insights.insights.map(
              (insight, index) => (

                <div
                  className="insight-card"
                  key={index}
                >

                  <Lightbulb size={21} />

                  <p>
                    {typeof insight === "string"
                      ? insight
                      : insight.message ||
                        JSON.stringify(
                          insight
                        )}
                  </p>

                </div>

              )
            )

          ) : (

            <div className="empty-state">

              <BrainCircuit size={40} />

              <h3>
                No insights available
              </h3>

              <p>
                More video performance data is needed to
                generate insights.
              </p>

            </div>

          )}

        </div>

      </section>


      <section className="panel">

        <div className="panel-header">

          <div>

            <h3>
              Recent Videos
            </h3>

            <p>
              Latest videos from your YouTube channel.
            </p>

          </div>

          <Video size={25} />

        </div>


        {videos.length === 0 ? (

          <div className="empty-state">

            <Video size={42} />

            <h3>
              No recent videos
            </h3>

            <p>
              No recent videos were returned from your
              connected YouTube channel.
            </p>

          </div>

        ) : (

          <div className="recent-video-grid">

            {videos.map(
              (video, index) => (

                <div
                  className="recent-video-card"
                  key={
                    video.video_id ||
                    index
                  }
                >

                  {video.thumbnail ? (

                    <img
                      src={video.thumbnail}
                      alt={video.title}
                    />

                  ) : (

                    <div className="recent-video-placeholder">
                      <Video size={30} />
                    </div>

                  )}


                  <div className="recent-video-content">

                    <strong>
                      {video.title ||
                        "Untitled Video"}
                    </strong>


                    <div className="recent-video-stats">

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

                    </div>

                  </div>

                </div>

              )
            )}

          </div>

        )}

      </section>

    </div>
  );
}


export default YouTube;






