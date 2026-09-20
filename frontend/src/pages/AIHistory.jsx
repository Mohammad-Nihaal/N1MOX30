import { useEffect, useState } from "react";

import {
  AlertCircle,
  BrainCircuit,
  Clock3,
  Eye,
  FileText,
  LoaderCircle,
  RefreshCw,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";

import {
  deleteAIGeneration,
  getAIGeneration,
  getAIGenerationHistory,
  reuseAIGeneration,
} from "../api/ai";


function AIHistory() {
  const [generations, setGenerations] = useState([]);
  const [total, setTotal] = useState(0);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");

  const [error, setError] = useState("");

  const [selectedGeneration, setSelectedGeneration] =
    useState(null);


  // =============================================
  // LOAD HISTORY
  // =============================================

  async function loadHistory() {
    try {
      setLoading(true);
      setError("");

      const data = await getAIGenerationHistory(
        100,
        0
      );

      setGenerations(
        data.generations || []
      );

      setTotal(
        data.total || 0
      );

    } catch (error) {

      console.error(
        "AI history error:",
        error
      );

      const message =
        error?.response?.data?.detail ||
        "Unable to load AI generation history.";

      setError(
        typeof message === "string"
          ? message
          : "Unable to load AI generation history."
      );

    } finally {

      setLoading(false);
    }
  }


  // =============================================
  // LOAD SINGLE GENERATION
  // =============================================

  async function viewGeneration(
    generationId
  ) {
    try {
      setActionLoading(generationId);
      setError("");

      const data = await getAIGeneration(
        generationId
      );

      setSelectedGeneration(data);

    } catch (error) {

      console.error(
        "AI generation view error:",
        error
      );

      const message =
        error?.response?.data?.detail ||
        "Unable to load this generation.";

      setError(
        typeof message === "string"
          ? message
          : "Unable to load this generation."
      );

    } finally {

      setActionLoading("");
    }
  }


  // =============================================
  // REUSE GENERATION
  // =============================================

  async function regenerateGeneration(
    generation
  ) {
    try {
      setActionLoading(generation.id);
      setError("");

      const data = await reuseAIGeneration(
        generation.id,
        {}
      );

      await loadHistory();

      setSelectedGeneration(data);

    } catch (error) {

      console.error(
        "AI reuse error:",
        error
      );

      const message =
        error?.response?.data?.detail ||
        "Unable to regenerate this content.";

      setError(
        typeof message === "string"
          ? message
          : "Unable to regenerate this content."
      );

    } finally {

      setActionLoading("");
    }
  }


  // =============================================
  // DELETE GENERATION
  // =============================================

  async function removeGeneration(
    generationId
  ) {
    const confirmed = window.confirm(
      "Delete this AI generation permanently?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setActionLoading(generationId);
      setError("");

      await deleteAIGeneration(
        generationId
      );

      if (
        selectedGeneration?.id ===
        generationId
      ) {
        setSelectedGeneration(null);
      }

      setGenerations((current) =>
        current.filter(
          (generation) =>
            generation.id !== generationId
        )
      );

      setTotal((current) =>
        Math.max(current - 1, 0)
      );

    } catch (error) {

      console.error(
        "AI delete error:",
        error
      );

      const message =
        error?.response?.data?.detail ||
        "Unable to delete this generation.";

      setError(
        typeof message === "string"
          ? message
          : "Unable to delete this generation."
      );

    } finally {

      setActionLoading("");
    }
  }


  // =============================================
  // LOAD ON START
  // =============================================

  useEffect(() => {

    loadHistory();

  }, []);


  // =============================================
  // FORMAT DATE
  // =============================================

  function formatDate(value) {
    if (!value) {
      return "Unknown date";
    }

    try {

      return new Date(
        value
      ).toLocaleString();

    } catch {

      return value;
    }
  }


  // =============================================
  // RENDER
  // =============================================

  return (
    <div className="page-content">

      <div className="page-header">

        <div>

          <span className="page-eyebrow">
            AI CONTENT LIBRARY
          </span>

          <h1>
            AI History
          </h1>

          <p>
            View, reuse, and manage your previous
            AI content generations.
          </p>

        </div>


        <button
          type="button"
          className="secondary-button"
          onClick={loadHistory}
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


      <div className="panel">

        <div className="panel-header">

          <div>

            <h3>
              Your Generations
            </h3>

            <p>
              {total} saved AI generation
              {total === 1 ? "" : "s"}
            </p>

          </div>

          <BrainCircuit size={26} />

        </div>


        {loading ? (

          <div className="empty-state">

            <LoaderCircle
              size={32}
              className="spin"
            />

            <h3>
              Loading AI history...
            </h3>

          </div>

        ) : generations.length === 0 ? (

          <div className="empty-state">

            <Sparkles size={38} />

            <h3>
              No AI generations yet
            </h3>

            <p>
              Go to AI Studio and generate your
              first piece of content.
            </p>

          </div>

        ) : (

          <div className="ai-history-list">

            {generations.map(
              (generation) => (

                <div
                  className="ai-history-item"
                  key={generation.id}
                >

                  <div className="ai-history-main">

                    <div className="ai-history-icon">

                      <BrainCircuit size={22} />

                    </div>


                    <div className="ai-history-content">

                      <div className="ai-history-title-row">

                        <h3>
                          {generation.topic}
                        </h3>

                        <span className="status-badge">
                          {generation.platform}
                        </span>

                      </div>


                      <div className="ai-history-meta">

                        <span>
                          <FileText size={15} />

                          {generation.content_type}
                        </span>

                        <span>
                          {generation.tone}
                        </span>

                        <span>

                          <Clock3 size={15} />

                          {formatDate(
                            generation.created_at
                          )}

                        </span>

                      </div>


                      {generation.provider && (

                        <p className="ai-generation-meta">

                          Provider: {
                            generation.provider
                          }

                        </p>

                      )}

                    </div>

                  </div>


                  <div className="ai-history-actions">

                    <button
                      type="button"
                      className="icon-button"
                      onClick={() =>
                        viewGeneration(
                          generation.id
                        )
                      }
                      disabled={
                        actionLoading ===
                        generation.id
                      }
                      title="View generation"
                    >

                      {actionLoading ===
                      generation.id ? (

                        <LoaderCircle
                          size={18}
                          className="spin"
                        />

                      ) : (

                        <Eye size={18} />

                      )}

                    </button>


                    <button
                      type="button"
                      className="icon-button"
                      onClick={() =>
                        regenerateGeneration(
                          generation
                        )
                      }
                      disabled={
                        actionLoading ===
                        generation.id
                      }
                      title="Generate again"
                    >

                      <RefreshCw size={18} />

                    </button>


                    <button
                      type="button"
                      className="icon-button danger-button"
                      onClick={() =>
                        removeGeneration(
                          generation.id
                        )
                      }
                      disabled={
                        actionLoading ===
                        generation.id
                      }
                      title="Delete generation"
                    >

                      <Trash2 size={18} />

                    </button>

                  </div>

                </div>

              )
            )}

          </div>

        )}

      </div>


      {selectedGeneration && (

        <section className="ai-results">

          <div className="ai-results-header">

            <div>

              <span className="page-eyebrow">
                SELECTED GENERATION
              </span>

              <h2>
                {selectedGeneration.topic}
              </h2>

              <p>
                Generated on {
                  formatDate(
                    selectedGeneration.created_at
                  )
                }
              </p>

            </div>


            <button
              type="button"
              className="icon-button"
              onClick={() =>
                setSelectedGeneration(null)
              }
              title="Close"
            >

              <X size={20} />

            </button>

          </div>


          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Title Ideas
                </h3>

                <p>
                  Generated content titles.
                </p>

              </div>

              <Sparkles size={24} />

            </div>


            <div className="title-list">

              {(
                selectedGeneration.titles || []
              ).map(
                (title, index) => (

                  <div
                    className="title-item"
                    key={`${title}-${index}`}
                  >

                    <span className="title-number">

                      {index + 1}

                    </span>

                    <p>
                      {title}
                    </p>

                  </div>

                )
              )}

            </div>

          </div>


          <div className="panel ai-result-panel">

            <div className="panel-header">

              <div>

                <h3>
                  Content Script
                </h3>

              </div>

              <FileText size={24} />

            </div>


            <div className="generated-content">

              <pre>

                {
                  selectedGeneration.script ||
                  "No script available."
                }

              </pre>

            </div>

          </div>


          <div className="panel ai-result-panel">

            <div className="panel-header">

              <div>

                <h3>
                  Caption
                </h3>

              </div>

              <FileText size={24} />

            </div>


            <div className="generated-content">

              <pre>

                {
                  selectedGeneration.caption ||
                  "No caption available."
                }

              </pre>

            </div>

          </div>


          <div className="panel ai-result-panel">

            <div className="panel-header">

              <div>

                <h3>
                  Hashtags
                </h3>

              </div>

              <Sparkles size={24} />

            </div>


            <div className="hashtag-list">

              {(
                selectedGeneration.hashtags || []
              ).map(
                (hashtag, index) => (

                  <span
                    key={`${hashtag}-${index}`}
                    className="hashtag"
                  >

                    {hashtag}

                  </span>

                )
              )}

            </div>

          </div>

        </section>

      )}

    </div>
  );
}


export default AIHistory;