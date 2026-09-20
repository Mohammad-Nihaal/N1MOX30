import { useState } from "react";

import {
  AlertCircle,
  BrainCircuit,
  Check,
  Clipboard,
  Copy,
  FileText,
  Hash,
  Lightbulb,
  LoaderCircle,
  RefreshCw,
  Sparkles,
  WandSparkles,
} from "lucide-react";

import {
  generateAIContent,
  reuseAIGeneration,
} from "../api/ai";


function AIStudio() {
  const [platform, setPlatform] = useState("youtube");
  const [topic, setTopic] = useState("");
  const [contentType, setContentType] = useState("video");
  const [tone, setTone] = useState("professional");

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState("");


  async function generateContent(event) {
    event?.preventDefault();

    const cleanTopic = topic.trim();

    if (!cleanTopic) {
      setError(
        "Please enter a topic for your content."
      );
      return;
    }

    if (cleanTopic.length < 3) {
      setError(
        "Please enter a topic with at least 3 characters."
      );
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResult(null);

      const data = await generateAIContent({
        platform,
        topic: cleanTopic,
        content_type: contentType,
        tone,
      });

      setResult(data);

    } catch (error) {
      console.error(
        "AI generation error:",
        error
      );

      const message =
        error?.response?.data?.detail ||
        "Unable to generate AI content.";

      setError(
        typeof message === "string"
          ? message
          : "Unable to generate AI content."
      );

    } finally {
      setLoading(false);
    }
  }


  async function regenerateContent() {
    if (!result?.generation_id) {
      generateContent();
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data = await reuseAIGeneration(
        result.generation_id,
        {
          topic: topic.trim() || result.topic,
          content_type:
            contentType || result.content_type,
          tone: tone || result.tone,
        }
      );

      setResult(data);

    } catch (error) {
      console.error(
        "AI regeneration error:",
        error
      );

      const message =
        error?.response?.data?.detail ||
        "Unable to regenerate AI content.";

      setError(
        typeof message === "string"
          ? message
          : "Unable to regenerate AI content."
      );

    } finally {
      setLoading(false);
    }
  }


  async function copyText(text, type) {
    if (!text) {
      return;
    }

    try {
      await navigator.clipboard.writeText(text);

      setCopied(type);

      setTimeout(() => {
        setCopied("");
      }, 2000);

    } catch (error) {
      console.error(
        "Copy error:",
        error
      );
    }
  }


  function CopyButton({ text, type }) {
    return (
      <button
        type="button"
        className="copy-button"
        onClick={() =>
          copyText(text, type)
        }
      >
        {copied === type ? (
          <>
            <Check size={16} />
            Copied
          </>
        ) : (
          <>
            <Copy size={16} />
            Copy
          </>
        )}
      </button>
    );
  }


  return (
    <div className="page-content">

      <div className="page-header">
        <div>

          <span className="page-eyebrow">
            AI CONTENT INTELLIGENCE
          </span>

          <h1>
            AI Studio
          </h1>

          <p>
            Generate content ideas, scripts, captions,
            and hashtags using N1MOX30 AI.
          </p>

        </div>
      </div>


      <section className="ai-studio-grid">

        <div className="panel ai-generator-panel">

          <div className="panel-header">

            <div>

              <h3>
                Create Content
              </h3>

              <p>
                Tell N1MOX30 what you want to create.
              </p>

            </div>

            <WandSparkles size={26} />

          </div>


          {error && (

            <div className="auth-error">

              <AlertCircle size={18} />

              <span>
                {error}
              </span>

            </div>

          )}


          <form
            className="ai-form"
            onSubmit={generateContent}
          >

            <label>

              <span>
                Platform
              </span>

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

            </label>


            <label>

              <span>
                Content Topic
              </span>

              <textarea
                value={topic}
                onChange={(event) =>
                  setTopic(
                    event.target.value
                  )
                }
                placeholder="Example: How artificial intelligence is changing content creation"
                rows="5"
                required
              />

            </label>


            <div className="ai-form-row">

              <label>

                <span>
                  Content Type
                </span>

                <select
                  value={contentType}
                  onChange={(event) =>
                    setContentType(
                      event.target.value
                    )
                  }
                >

                  <option value="video">
                    Video
                  </option>

                  <option value="short">
                    Short-form Video
                  </option>

                  <option value="tutorial">
                    Tutorial
                  </option>

                  <option value="review">
                    Review
                  </option>

                  <option value="educational">
                    Educational
                  </option>

                </select>

              </label>


              <label>

                <span>
                  Tone
                </span>

                <select
                  value={tone}
                  onChange={(event) =>
                    setTone(
                      event.target.value
                    )
                  }
                >

                  <option value="professional">
                    Professional
                  </option>

                  <option value="casual">
                    Casual
                  </option>

                  <option value="educational">
                    Educational
                  </option>

                  <option value="energetic">
                    Energetic
                  </option>

                  <option value="friendly">
                    Friendly
                  </option>

                </select>

              </label>

            </div>


            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >

              {loading ? (

                <>
                  <LoaderCircle
                    size={19}
                    className="spin"
                  />

                  Generating...
                </>

              ) : (

                <>
                  <Sparkles size={19} />

                  Generate Content
                </>

              )}

            </button>

          </form>


          {result && (

            <button
              type="button"
              className="secondary-button ai-regenerate-button"
              onClick={regenerateContent}
              disabled={loading}
            >

              <RefreshCw
                size={17}
                className={
                  loading ? "spin" : ""
                }
              />

              Generate Again

            </button>

          )}


          <div className="ai-tips">

            <div>

              <Lightbulb size={19} />

              <span>
                Tip: Be specific about your topic to get
                more useful AI content.
              </span>

            </div>

          </div>

        </div>


        <div className="panel ai-info-panel">

          <div className="panel-header">

            <div>

              <h3>
                N1MOX30 AI
              </h3>

              <p>
                Your creator intelligence assistant.
              </p>

            </div>

            <BrainCircuit size={26} />

          </div>


          <div className="ai-info-hero">

            <BrainCircuit
              size={60}
              strokeWidth={1.3}
            />

            <h3>
              Create smarter content
            </h3>

            <p>
              Turn a simple idea into titles,
              scripts, captions, and hashtags.
            </p>

          </div>


          <div className="ai-feature-list">

            <div>

              <Sparkles size={18} />

              <div>

                <strong>
                  Content Ideas
                </strong>

                <span>
                  Multiple creative titles
                </span>

              </div>

            </div>


            <div>

              <FileText size={18} />

              <div>

                <strong>
                  Full Scripts
                </strong>

                <span>
                  Structured creator content
                </span>

              </div>

            </div>


            <div>

              <Clipboard size={18} />

              <div>

                <strong>
                  Captions
                </strong>

                <span>
                  Platform-ready descriptions
                </span>

              </div>

            </div>


            <div>

              <Hash size={18} />

              <div>

                <strong>
                  Hashtags
                </strong>

                <span>
                  Discoverable content tags
                </span>

              </div>

            </div>

          </div>

        </div>

      </section>


      {result && (

        <section className="ai-results">

          <div className="ai-results-header">

            <div>

              <span className="page-eyebrow">
                AI GENERATED CONTENT
              </span>

              <h2>
                Your Content Strategy
              </h2>

              <p>
                Generated for "
                {result.topic || topic}
                "
              </p>

              {result.provider && (
                <p className="ai-generation-meta">
                  Provider: {result.provider}
                </p>
              )}

              {result.generation_id && (
                <p className="ai-generation-meta">
                  Generation ID: {result.generation_id}
                </p>
              )}

            </div>

            <Sparkles size={30} />

          </div>


          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Title Ideas
                </h3>

                <p>
                  Potential titles for your content.
                </p>

              </div>

              <Lightbulb size={24} />

            </div>


            <div className="title-list">

              {(result.titles || []).map(
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

                    <CopyButton
                      text={title}
                      type={`title-${index}`}
                    />

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

                <p>
                  AI-generated script for your content.
                </p>

              </div>

              <FileText size={24} />

            </div>


            <div className="generated-content">

              <pre>
                {result.script ||
                  "No script was generated."}
              </pre>

            </div>


            <CopyButton
              text={
                result.script || ""
              }
              type="script"
            />

          </div>


          <div className="panel ai-result-panel">

            <div className="panel-header">

              <div>

                <h3>
                  Caption
                </h3>

                <p>
                  Ready to use on your selected platform.
                </p>

              </div>

              <Clipboard size={24} />

            </div>


            <div className="generated-content">

              <pre>
                {result.caption ||
                  "No caption was generated."}
              </pre>

            </div>


            <CopyButton
              text={
                result.caption || ""
              }
              type="caption"
            />

          </div>


          <div className="panel ai-result-panel">

            <div className="panel-header">

              <div>

                <h3>
                  Hashtags
                </h3>

                <p>
                  Suggested hashtags for discoverability.
                </p>

              </div>

              <Hash size={24} />

            </div>


            <div className="hashtag-list">

              {(result.hashtags || []).map(
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


            <CopyButton
              text={
                (result.hashtags || [])
                  .join(" ")
              }
              type="hashtags"
            />

          </div>

        </section>

      )}

    </div>
  );
}


export default AIStudio;