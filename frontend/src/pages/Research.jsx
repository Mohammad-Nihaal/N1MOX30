import { generateResearchPipelineContent } from "../api/research";
import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  createResearch,
  deleteResearch,
  generateContentFromResearch,
  getResearchHistory,
} from "../api/research";


function Research() {
  // =================================================
  // FORM STATE
  // =================================================

  const [platform, setPlatform] = useState(
    "youtube"
  );

  const [topic, setTopic] = useState("");

  const [contentType, setContentType] = useState(
    "youtube short"
  );

  const [tone, setTone] = useState(
    "engaging"
  );


  // =================================================
  // RESEARCH STATE
  // =================================================

  const [researchResult, setResearchResult] =
    useState(null);

  const [researchHistory, setResearchHistory] =
    useState([]);


  // =================================================
  // LOADING STATE
  // =================================================

  const [loading, setLoading] = useState(false);

  const [historyLoading, setHistoryLoading] =
    useState(false);

  const [generatingContent, setGeneratingContent] =
    useState(false);


  // =================================================
  // ERROR / SUCCESS STATE
  // =================================================

  const [error, setError] = useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  const [generatedContent, setGeneratedContent] =
    useState(null);


  // =================================================
  // LOAD HISTORY
  // =================================================

  const loadHistory = useCallback(
    async () => {
      try {
        setHistoryLoading(true);

        const response =
          await getResearchHistory({
            limit: 50,
            offset: 0,
          });

        setResearchHistory(
          response?.research || []
        );
      } catch (loadError) {
        console.error(
          "Failed to load research history:",
          loadError
        );
      } finally {
        setHistoryLoading(false);
      }
    },
    []
  );


  // =================================================
  // INITIAL HISTORY LOAD
  // =================================================

  useEffect(() => {
    const timeoutId = window.setTimeout(
      () => {
        loadHistory();
      },
      0
    );

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [loadHistory]);


  // =================================================
  // CREATE RESEARCH
  // =================================================

  const handleResearch = async (
    event
  ) => {
    event.preventDefault();

    const cleanTopic = topic.trim();

    if (!cleanTopic) {
      setError(
        "Please enter a topic to research."
      );

      return;
    }

    try {
      setLoading(true);

      setError("");

      setSuccessMessage("");

      setGeneratedContent(null);

      const result =
        await createResearch({
          platform,
          topic: cleanTopic,
        });

      setResearchResult(result);

      setSuccessMessage(
        "Research completed successfully."
      );

      await loadHistory();
    } catch (researchError) {
      console.error(
        "Research failed:",
        researchError
      );

      const detail =
        researchError?.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Research failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };


  // =================================================
  // SELECT HISTORY ITEM
  // =================================================

  const handleSelectResearch = (
    item
  ) => {
    setResearchResult({
      research_id: item.id,
      platform: item.platform,
      topic: item.topic,
      keywords: item.keywords || [],
      audience_angles:
        item.audience_angles || [],
      content_opportunities:
        item.content_opportunities || [],
      competitor_insights:
        item.competitor_insights || [],
      research_summary:
        item.research_summary || "",
      opportunity_score:
        item.opportunity_score,
      trend_score:
        item.trend_score,
      provider:
        item.provider || "unknown",
      research_status:
        item.research_status || "completed",
      created_at:
        item.created_at,
    });

    setGeneratedContent(null);

    setError("");

    setSuccessMessage("");
  };


  // =================================================
  // DELETE RESEARCH
  // =================================================

  const handleDeleteResearch = async (
    event,
    researchId
  ) => {
    event.stopPropagation();

    try {
      setError("");

      await deleteResearch(
        researchId
      );

      if (
        researchResult?.research_id ===
        researchId
      ) {
        setResearchResult(null);

        setGeneratedContent(null);
      }

      await loadHistory();

      setSuccessMessage(
        "Research record deleted."
      );
    } catch (deleteError) {
      console.error(
        "Failed to delete research:",
        deleteError
      );

      setError(
        "Failed to delete research record."
      );
    }
  };


  // =================================================
  // GENERATE CONTENT
  // =================================================

  const handleGenerateContent =
    async (
      opportunityIndex = 0
    ) => {
      if (
        !researchResult?.research_id
      ) {
        setError(
          "Please select a research result first."
        );

        return;
      }

      try {
        setGeneratingContent(true);

        setError("");

        setSuccessMessage("");

        const result =
          await generateContentFromResearch(
            researchResult.research_id,
            {
              contentType,
              tone,
              opportunityIndex,
            }
          );

        setGeneratedContent(result);

        setSuccessMessage(
          "AI content generated from research."
        );
      } catch (contentError) {
        console.error(
          "Content generation failed:",
          contentError
        );

        const detail =
          contentError?.response?.data?.detail;

        setError(
          typeof detail === "string"
            ? detail
            : "Failed to generate content."
        );
      } finally {
        setGeneratingContent(false);
      }
    };


  // =================================================
  // RENDER HELPERS
  // =================================================

  const renderList = (
    title,
    items
  ) => {
    if (
      !items ||
      items.length === 0
    ) {
      return null;
    }

    return (
      <div className="research-section">
        <h3>
          {title}
        </h3>

        <ul>
          {items.map(
            (item, index) => (
              <li
                key={`${title}-${index}`}
              >
                {item}
              </li>
            )
          )}
        </ul>
      </div>
    );
  };


  // =================================================
  // PAGE
  // =================================================

  return (
    <div className="page-container">

      {/* ============================================= */}
      {/* PAGE HEADER */}
      {/* ============================================= */}

      <div className="page-header">
        <div>
          <h1>
            Research Intelligence
          </h1>

          <p>
            Discover keywords, audience
            opportunities, competitor insights,
            and content ideas for your next
            creator strategy.
          </p>
        </div>
      </div>


      {/* ============================================= */}
      {/* MESSAGES */}
      {/* ============================================= */}

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          {successMessage}
        </div>
      )}


      {/* ============================================= */}
      {/* RESEARCH FORM */}
      {/* ============================================= */}

      <div className="card research-form-card">

        <h2>
          Research a Topic
        </h2>

        <form
          onSubmit={handleResearch}
          className="research-form"
        >

          <div className="form-group">

            <label>
              Platform
            </label>

            <select
              value={platform}
              onChange={(event) =>
                setPlatform(
                  event.target.value
                )
              }
            >
              <option value="youtube">
                YouTube
              </option>

              <option value="instagram">
                Instagram
              </option>
            </select>

          </div>


          <div className="form-group">

            <label>
              Topic
            </label>

            <input
              type="text"
              value={topic}
              onChange={(event) =>
                setTopic(
                  event.target.value
                )
              }
              placeholder="Example: AI tools for content creators"
              maxLength={500}
            />

          </div>


          <button
            type="submit"
            className="primary-button"
            disabled={loading}
          >
            {loading
              ? "Researching..."
              : "Start Research"}
          </button>

        </form>

      </div>


      {/* ============================================= */}
      {/* MAIN CONTENT */}
      {/* ============================================= */}

      <div className="research-layout">


        {/* =========================================== */}
        {/* RESULTS */}
        {/* =========================================== */}

        <div className="research-main">

          {!researchResult && (

            <div className="card empty-state">

              <h2>
                Ready to Research
              </h2>

              <p>
                Enter a topic and let N1MOX30
                analyze content opportunities,
                audience angles, keywords, and
                competitor insights.
              </p>

            </div>

          )}


          {researchResult && (

            <>

              {/* SUMMARY */}

              <div className="card research-result-card">

                <div className="research-result-header">

                  <div>

                    <span className="research-platform">
                      {researchResult.platform}
                    </span>

                    <h2>
                      {researchResult.topic}
                    </h2>

                  </div>

                  <span className="research-status">
                    {
                      researchResult.research_status
                    }
                  </span>

                </div>


                {/* SCORES */}

                <div className="research-scores">

                  <div className="research-score">

                    <span>
                      Opportunity Score
                    </span>

                    <strong>
                      {
                        researchResult
                          .opportunity_score ??
                        "N/A"
                      }
                    </strong>

                  </div>


                  <div className="research-score">

                    <span>
                      Trend Score
                    </span>

                    <strong>
                      {
                        researchResult
                          .trend_score ??
                        "N/A"
                      }
                    </strong>

                  </div>


                  <div className="research-score">

                    <span>
                      Provider
                    </span>

                    <strong>
                      {
                        researchResult.provider ||
                        "Unknown"
                      }
                    </strong>

                  </div>

                </div>


                {/* SUMMARY */}

                {researchResult.research_summary && (

                  <div className="research-summary">

                    <h3>
                      Research Summary
                    </h3>

                    <p>
                      {
                        researchResult
                          .research_summary
                      }
                    </p>

                  </div>

                )}


                {/* LISTS */}

                {renderList(
                  "Keywords",
                  researchResult.keywords
                )}

                {renderList(
                  "Audience Angles",
                  researchResult.audience_angles
                )}

                {renderList(
                  "Content Opportunities",
                  researchResult
                    .content_opportunities
                )}

                {renderList(
                  "Competitor Insights",
                  researchResult
                    .competitor_insights
                )}

              </div>


              {/* ===================================== */}
              {/* GENERATE CONTENT */}
              {/* ===================================== */}

              <div className="card content-generation-card">

                <h2>
                  Generate Content from Research
                </h2>

                <p>
                  Turn your research insights into
                  usable creator content.
                </p>


                <div className="generation-controls">

                  <div className="form-group">

                    <label>
                      Content Type
                    </label>

                    <input
                      type="text"
                      value={contentType}
                      onChange={(event) =>
                        setContentType(
                          event.target.value
                        )
                      }
                      placeholder="youtube short"
                    />

                  </div>


                  <div className="form-group">

                    <label>
                      Tone
                    </label>

                    <input
                      type="text"
                      value={tone}
                      onChange={(event) =>
                        setTone(
                          event.target.value
                        )
                      }
                      placeholder="engaging"
                    />

                  </div>

                </div>


                <button
                  type="button"
                  className="primary-button"
                  disabled={
                    generatingContent
                  }
                  onClick={() =>
                    handleGenerateContent(0)
                  }
                >
                  {generatingContent
                    ? "Generating Content..."
                    : "Generate Content"}
                </button>

              </div>


              {/* ===================================== */}
              {/* GENERATED CONTENT */}
              {/* ===================================== */}

              {generatedContent && (

                <div className="card generated-content-card">

                  <h2>
                    Generated Content
                  </h2>


                  {generatedContent.titles &&
                    generatedContent.titles.length >
                      0 && (

                    <div className="research-section">

                      <h3>
                        Title Ideas
                      </h3>

                      <ol>

                        {generatedContent.titles.map(
                          (title, index) => (

                            <li
                              key={`title-${index}`}
                            >
                              {title}
                            </li>

                          )
                        )}

                      </ol>

                    </div>

                  )}


                  {generatedContent.script && (

                    <div className="research-section">

                      <h3>
                        Script
                      </h3>

                      <p className="generated-text">
                        {
                          generatedContent.script
                        }
                      </p>

                    </div>

                  )}


                  {generatedContent.caption && (

                    <div className="research-section">

                      <h3>
                        Caption
                      </h3>

                      <p className="generated-text">
                        {
                          generatedContent.caption
                        }
                      </p>

                    </div>

                  )}


                  {generatedContent.hashtags &&
                    generatedContent.hashtags.length >
                      0 && (

                    <div className="research-section">

                      <h3>
                        Hashtags
                      </h3>

                      <div className="hashtag-list">

                        {generatedContent.hashtags.map(
                          (hashtag, index) => (

                            <span
                              key={`hashtag-${index}`}
                              className="hashtag"
                            >
                              {hashtag}
                            </span>

                          )
                        )}

                      </div>

                    </div>

                  )}

                </div>

              )}

            </>

          )}

        </div>


        {/* =========================================== */}
        {/* HISTORY */}
        {/* =========================================== */}

        <aside className="research-history">

          <div className="card">

            <div className="history-header">

              <h2>
                Research History
              </h2>

              <button
                type="button"
                className="secondary-button"
                onClick={loadHistory}
                disabled={historyLoading}
              >
                {historyLoading
                  ? "Loading..."
                  : "Refresh"}
              </button>

            </div>


            {historyLoading &&
              researchHistory.length === 0 && (

              <p className="muted-text">
                Loading research history...
              </p>

            )}


            {!historyLoading &&
              researchHistory.length === 0 && (

              <p className="muted-text">
                No research history yet.
              </p>

            )}


            <div className="history-list">

              {researchHistory.map(
                (item) => (

                  <div
                    key={item.id}
                    className={`history-item ${
                      researchResult?.research_id ===
                      item.id
                        ? "active"
                        : ""
                    }`}
                  >

                    <button
                      type="button"
                      className="history-item-main"
                      onClick={() =>
                        handleSelectResearch(item)
                      }
                    >

                      <strong>
                        {item.topic}
                      </strong>

                      <span>
                        {item.platform}
                      </span>

                    </button>


                    <button
                      type="button"
                      className="history-delete-button"
                      onClick={(event) =>
                        handleDeleteResearch(
                          event,
                          item.id
                        )
                      }
                      title="Delete research"
                    >
                      ×
                    </button>

                  </div>

                )
              )}

            </div>

          </div>

        </aside>

      </div>

    </div>
  );
}


export default Research;