import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  ArrowUp,
  Bot,
  CheckCircle2,
  CircleAlert,
  Loader2,
  Mic,
  Workflow,
  Zap, Video} from "lucide-react";

import {
  executeCreatorCommand,
} from "../api/commandExecutor";

import {
  stageLabel,
  workflowStatusLabel,
} from "../api/creatorOS";

const suggestions = [
  "Create a YouTube video about AI agents",
  "Create an Instagram video about creator automation",
  "Create a TikTok video about OpenClaw",
];

function statusIcon(status) {
  if (status === "completed") {
    return <CheckCircle2 size={17} />;
  }

  if (status === "failed") {
    return <CircleAlert size={17} />;
  }

  if (
    status === "running" ||
    status === "pending"
  ) {
    return (
      <Loader2
        size={17}
        className="nm-spin"
      />
    );
  }

  return <Workflow size={17} />;
}

export default function Assistant() {
  const [command, setCommand] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [workflow, setWorkflow] =
    useState(null);

  const textareaRef = useRef(null);

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  async function handleSubmit(event) {
    event?.preventDefault();

    const value = command.trim();

    if (!value || busy) return;

    try {
      setBusy(true);
      setError("");
      setWorkflow(null);

      const result =
        await executeCreatorCommand(value);

      setWorkflow(result.workflow);
      setCommand("");
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "N1MOX could not execute that command."
      );
    } finally {
      setBusy(false);
    }
  }

  const steps =
    workflow?.steps || [];

  return (
    <div className="nm-assistant-page page-enter">
      <div className="page-header">
        <div>
          <div className="section-kicker">
            N1MOX INTELLIGENCE
          </div>

          <h1>
            Command N1MOX.
          </h1>

          <p>
            Describe what you want created.
            N1MOX can turn the command into a
            complete production workflow.
          </p>
        </div>

        <div className="nm-assistant-status">
          <span className="nm-system-status-dot" />
          ENGINE READY
        </div>
      </div>

      <section className="nm-assistant-command-card">
        <div className="nm-assistant-orb">
          <Bot size={30} />
        </div>

        <div className="nm-assistant-command-copy">
          <span className="section-kicker">
            CREATOR COMMAND
          </span>

          <h2>
            What should N1MOX create?
          </h2>

          <p>
            You can type naturally. Platform
            and topic are detected automatically.
          </p>
        </div>

        <form
          className="nm-assistant-form"
          onSubmit={handleSubmit}
        >
          <textarea
            ref={textareaRef}
            value={command}
            onChange={(event) =>
              setCommand(event.target.value)
            }
            placeholder="Example: Create a YouTube video about AI agents"
            rows={3}
            disabled={busy}
          />

          <div className="nm-assistant-form-footer">
            <div className="nm-assistant-tools">
              <button
                type="button"
                className="nm-btn nm-btn-secondary"
                title="Voice command"
                disabled
              >
                <Mic size={15} />
                Voice
              </button>

              <span>
                N1MOX Creator OS
              </span>
            </div>

            <button
              type="submit"
              className="nm-btn nm-btn-primary"
              disabled={
                busy ||
                command.trim().length < 2
              }
            >
              {busy ? (
                <>
                  <Loader2
                    size={15}
                    className="nm-spin"
                  />
                  Launching...
                </>
              ) : (
                <>
                  <ArrowUp size={15} />
                  Run command
                </>
              )}
            </button>
          </div>
        </form>

        <div className="nm-assistant-suggestions">
          {suggestions.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => {
                setCommand(item);
                textareaRef.current?.focus();
              }}
              disabled={busy}
            >
              {item}
            </button>
          ))}
        </div>
      </section>

      {error && (
        <div className="nm-alert nm-alert-error">
          <CircleAlert size={16} />
          {error}
        </div>
      )}

      {workflow && (
        <section className="nm-assistant-result">
          <div className="nm-assistant-result-header">
            <div>
              <span className="section-kicker">
                CREATOR OS
              </span>

              <h2>
                {workflow.topic}
              </h2>

              <p>
                {workflow.command}
              </p>
            </div>

            <div
              className={`nm-os-status status-${workflow.status}`}
            >
              {statusIcon(workflow.status)}
              {workflowStatusLabel(
                workflow.status
              )}
            </div>
          </div>

          <div className="nm-assistant-progress">
            <div>
              <span>
                {workflow.current_stage
                  ? stageLabel(
                      workflow.current_stage
                    )
                  : "Preparing workflow"}
              </span>

              <strong>
                {workflow.progress || 0}%
              </strong>
            </div>

            <div className="nm-os-progress">
              <span
                style={{
                  width: `${Math.max(
                    0,
                    Math.min(
                      100,
                      workflow.progress || 0
                    )
                  )}%`,
                }}
              />
            </div>
          </div>

          {steps.length > 0 && (
            <div className="nm-assistant-stage-grid">
              {steps.map((step) => (
                <div
                  key={
                    step.id ||
                    step.stage
                  }
                  className={`nm-assistant-stage is-${step.status}`}
                >
                  <div>
                    {statusIcon(step.status)}
                  </div>

                  <div>
                    <strong>
                      {stageLabel(
                        step.stage
                      )}
                    </strong>

                    <span>
                      {step.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="nm-assistant-result-footer">
            <Zap size={15} />
            Workflow ID:
            <code>{workflow.id}</code>
          </div>
        </section>
      )}

      {!workflow && !busy && !error && (
        <section className="nm-assistant-info-grid">
          <article>
            <Workflow size={20} />
            <strong>One command</strong>
            <span>
              Describe the result you want.
            </span>
          </article>

          <article>
            <Zap size={20} />
            <strong>13 production stages</strong>
            <span>
              Research through publishing.
            </span>
          </article>

          <article>
            <CheckCircle2 size={20} />
            <strong>Persistent execution</strong>
            <span>
              Workflow state is stored by N1MOX30.
            </span>
          </article>
        </section>
      )}
    </div>
  );
}


