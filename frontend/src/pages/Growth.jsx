import { useEffect, useState } from "react";

import {
  AlertCircle,
  BrainCircuit,
  Lightbulb,
  LoaderCircle,
  RefreshCw,
  Target,
  TrendingUp,
  Trophy,
  Zap, Video} from "lucide-react";

import api from "../api/client";


function Growth() {
  const [growthScore, setGrowthScore] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [insights, setInsights] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  async function loadGrowthData() {
    try {
      setLoading(true);
      setError("");

      const [
        growthResponse,
        insightsResponse,
        recommendationsResponse,
      ] = await Promise.all([
        api.get("/youtube/growth-score"),
        api.get("/youtube/insights"),
        api.get("/youtube/recommendations"),
      ]);

      setGrowthScore(growthResponse.data);

      setInsights(insightsResponse.data);

      const recommendationData =
        recommendationsResponse.data?.recommendations ||
        recommendationsResponse.data?.data?.recommendations ||
        [];

      setRecommendations(
        Array.isArray(recommendationData)
          ? recommendationData
          : []
      );

    } catch (error) {
      console.error(
        "Growth loading error:",
        error
      );

      setError(
        error?.response?.data?.detail ||
        "Unable to load growth intelligence."
      );

    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadGrowthData();
  }, []);


  if (loading) {
    return (
      <div className="page-content">

        <div className="page-loading">

          <LoaderCircle
            size={32}
            className="spin"
          />

          <span>
            Loading growth intelligence...
          </span>

        </div>

      </div>
    );
  }


  const score =
    growthScore?.growth_score ??
    growthScore?.score ??
    growthScore?.data?.growth_score ??
    0;


  const channelName =
    growthScore?.channel_name ||
    insights?.channel_name ||
    "Your YouTube Channel";


  const scoreLabel =
    score >= 80
      ? "Excellent growth potential"
      : score >= 60
        ? "Strong growth potential"
        : score >= 40
          ? "Developing growth potential"
          : "Growth opportunity available";


  return (
    <div className="page-content">

      <div className="page-header">

        <div>

          <span className="page-eyebrow">
            GROWTH INTELLIGENCE
          </span>

          <h1>
            Channel Growth
          </h1>

          <p>
            Understand your current growth performance
            and discover opportunities to improve your
            YouTube channel.
          </p>

        </div>


        <button
          className="secondary-button"
          onClick={loadGrowthData}
          disabled={loading}
        >

          <RefreshCw
            size={18}
            className={
              loading ? "spin" : ""
            }
          />

          Refresh

        </button>

      </div>


      {error && (

        <div className="auth-error">

          <AlertCircle size={18} />

          <span>
            {error}
          </span>

        </div>

      )}


      <section className="growth-hero-card">

        <div className="growth-score-content">

          <span className="page-eyebrow">
            N1MOX30 GROWTH SCORE
          </span>

          <h2>
            {channelName}
          </h2>

          <h3 className="growth-score-label">
            {scoreLabel}
          </h3>

          <p>
            N1MOX30 analyzes channel performance,
            content activity, engagement, and video
            performance to identify opportunities for
            sustainable creator growth.
          </p>

        </div>


        <div className="growth-score-circle">

          <span>
            {Number(score).toFixed(0)}
          </span>

          <small>
            / 100
          </small>

        </div>

      </section>


      <section className="growth-grid">

        <div className="panel growth-panel">

          <div className="panel-header">

            <div>

              <h3>
                Growth Opportunities
              </h3>

              <p>
                Important areas that can help improve
                your channel performance.
              </p>

            </div>

            <TrendingUp size={24} />

          </div>


          <div className="growth-opportunities">

            <div className="growth-item">

              <div className="growth-icon">

                <Target size={20} />

              </div>

              <div>

                <h4>
                  Content Consistency
                </h4>

                <p>
                  Maintain a reliable publishing schedule
                  so your audience knows when to expect
                  new content.
                </p>

              </div>

            </div>


            <div className="growth-item">

              <div className="growth-icon">

                <Lightbulb size={20} />

              </div>

              <div>

                <h4>
                  Content Optimization
                </h4>

                <p>
                  Use your best-performing videos to
                  identify successful topics and formats.
                </p>

              </div>

            </div>


            <div className="growth-item">

              <div className="growth-icon">

                <Zap size={20} />

              </div>

              <div>

                <h4>
                  Audience Engagement
                </h4>

                <p>
                  Monitor likes, comments, and viewer
                  interaction to understand what connects
                  with your audience.
                </p>

              </div>

            </div>

          </div>

        </div>


        <div className="panel growth-panel">

          <div className="panel-header">

            <div>

              <h3>
                AI Recommendations
              </h3>

              <p>
                Personalized recommendations generated
                from your YouTube channel data.
              </p>

            </div>

            <BrainCircuit size={24} />

          </div>


          {recommendations.length > 0 ? (

            <div className="recommendations-list">

              {recommendations.map(
                (recommendation, index) => (

                  <div
                    className="recommendation-item"
                    key={index}
                  >

                    <Lightbulb size={18} />

                    <span>

                      {typeof recommendation === "string"
                        ? recommendation
                        : recommendation?.message ||
                          recommendation?.text ||
                          recommendation?.recommendation ||
                          "Growth recommendation available."
                      }

                    </span>

                  </div>

                )
              )}

            </div>

          ) : (

            <div className="empty-growth-state">

              <Trophy size={38} />

              <h4>
                More channel data will improve insights
              </h4>

              <p>
                Publish and analyze more videos to help
                N1MOX30 generate increasingly personalized
                growth recommendations.
              </p>

            </div>

          )}

        </div>

      </section>


      <section className="panel growth-action-panel">

        <div>

          <span className="page-eyebrow">
            NEXT STEP
          </span>

          <h3>
            Build a stronger content strategy
          </h3>

          <p>
            Use N1MOX30 AI Studio to transform your
            channel intelligence into content ideas,
            strategies, and actionable plans.
          </p>

        </div>

        <BrainCircuit size={42} />

      </section>

    </div>
  );
}


export default Growth;

