import { useEffect, useMemo, useState } from "react";

import api from "../api/client";



const WORKFLOW_STAGES = [
  "research",
  "strategy",
  "hooks",
  "script",
  "voice",
  "visuals",
  "video",
  "captions",
  "thumbnail",
  "metadata",
  "quality_check",
  "scheduling",
  "publishing",
];

async function createWorkflow(payload) {
  return api.post("/automation/workflows", payload);
}

async function listWorkflows() {
  return api.get("/automation/workflows");
}

async function getWorkflow(workflowId) {
  return api.get(`/automation/workflows/${workflowId}`);
}

async function runWorkflow(workflowId) {
  return api.post(`/automation/workflows/${workflowId}/run`);
}

async function retryWorkflow(workflowId, stage) {
  return api.post(
    `/automation/workflows/${workflowId}/retry/${stage}`
  );
}
const STAGE_LABELS = {
  research: "Research",
  strategy: "Strategy",
  hooks: "Hooks",
  script: "Script",
  voice: "Voice",
  visuals: "Visuals",
  video: "Video",
  captions: "Captions",
  thumbnail: "Thumbnail",
  metadata: "Metadata",
  quality_check: "Quality Check",
  scheduling: "Scheduling",
  publishing: "Publishing",
};

const STAGE_SYMBOLS = [
  "01",
  "02",
  "03",
  "04",
  "05",
  "06",
  "07",
  "08",
  "09",
  "10",
  "11",
  "12",
  "13",
];

function formatStage(stage) {
  if (!stage) return "Waiting";

  return (
    STAGE_LABELS[String(stage).toLowerCase()] ||
    String(stage)
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase())
  );
}

function formatDate(value) {
  if (!value) return "—";

  try {
    return new Date(value).toLocaleString();
  } catch {
    return String(value);
  }
}

function statusClass(status) {
  const value = String(status || "").toLowerCase();

  if (value === "completed") return "completed";
  if (value === "failed") return "failed";
  if (value === "running") return "running";
  if (value === "pending") return "pending";

  return "idle";
}

function WorkflowStageList({ workflow }) {
  const steps = workflow?.steps || [];

  const stepMap = new Map(
    steps.map((step) => [
      String(step.stage || "").toLowerCase(),
      step,
    ])
  );

  return (
    <div className="nm-workflow-stages">
      {WORKFLOW_STAGES.map((stage, index) => {
        const key =
          typeof stage === "string"
            ? stage
            : stage?.id || stage?.stage || "";

        const step = stepMap.get(String(key).toLowerCase());

        const status = step?.status || "pending";

        return (
          <div
            className={`nm-workflow-stage ${statusClass(status)}`}
            key={key || index}
          >
            <div className="nm-workflow-stage-number">
              {STAGE_SYMBOLS[index] || String(index + 1).padStart(2, "0")}
            </div>

            <div className="nm-workflow-stage-main">
              <strong>{formatStage(key)}</strong>

              <span>
                {status === "completed"
                  ? "Complete"
                  : status === "running"
                    ? "Running"
                    : status === "failed"
                      ? "Failed"
                      : "Queued"}
              </span>
            </div>

            <div className="nm-workflow-stage-status">
              {status === "completed"
                ? "✓"
                : status === "failed"
                  ? "!"
                  : status === "running"
                    ? "●"
                    : "○"}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function Workflows() {
  const [command, setCommand] = useState("");
  const [platform, setPlatform] = useState("youtube");
  const [topic, setTopic] = useState("");

  const [workflows, setWorkflows] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);

  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const selectedSummary = useMemo(
    () =>
      workflows.find(
        (workflow) => String(workflow.id) === String(selectedId)
      ) || null,
    [workflows, selectedId]
  );

  async function loadWorkflows() {
    try {
      setRefreshing(true);
      setError("");

      const response = await listWorkflows();
      const data = response?.data ?? response ?? [];

      const items = Array.isArray(data)
        ? data
        : Array.isArray(data?.workflows)
          ? data.workflows
          : [];

      setWorkflows(items);

      if (
        selectedId &&
        !items.some(
          (workflow) =>
            String(workflow.id) === String(selectedId)
        )
      ) {
        setSelectedId(null);
        setSelectedWorkflow(null);
      }
    } catch (err) {
      console.error("Workflow list error:", err);

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to load workflows."
      );
    } finally {
      setRefreshing(false);
    }
  }

  async function loadWorkflow(id) {
    if (!id) return;

    try {
      setError("");

      const response = await getWorkflow(id);
      const data = response?.data ?? response;

      setSelectedWorkflow(data);
    } catch (err) {
      console.error("Workflow detail error:", err);

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to load workflow."
      );
    }
  }

  useEffect(() => {
    loadWorkflows();
  }, []);

  useEffect(() => {
    if (!selectedId) return;

    loadWorkflow(selectedId);
  }, [selectedId]);

  useEffect(() => {
    const active = workflows.some((workflow) => {
      const status = String(workflow.status || "").toLowerCase();

      return (
        status === "pending" ||
        status === "running"
      );
    });

    if (!active) return;

    const timer = setInterval(() => {
      loadWorkflows();

      if (selectedId) {
        loadWorkflow(selectedId);
      }
    }, 3000);

    return () => clearInterval(timer);
  }, [workflows, selectedId]);

  async function handleCreate() {
    const cleanCommand = command.trim();
    const cleanTopic = topic.trim();

    if (!cleanCommand) {
      setError("Tell N1MOX what you want to create.");
      return;
    }

    if (!cleanTopic) {
      setError("Enter a topic.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await createWorkflow({
        command: cleanCommand,
        platform,
        topic: cleanTopic,
      });

      const created = response?.data ?? response;

      await loadWorkflows();

      if (created?.id) {
        setSelectedId(created.id);
        await loadWorkflow(created.id);
      }

      setCommand("");
    } catch (err) {
      console.error("Workflow creation error:", err);

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to create workflow."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleRun(id) {
    if (!id) return;

    try {
      setLoading(true);
      setError("");

      await runWorkflow(id);

      await loadWorkflows();
      await loadWorkflow(id);
    } catch (err) {
      console.error("Workflow run error:", err);

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to run workflow."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleRetry(id, stage) {
    if (!id || !stage) return;

    try {
      setLoading(true);
      setError("");

      await retryWorkflow(id, stage);

      await loadWorkflows();
      await loadWorkflow(id);
    } catch (err) {
      console.error("Workflow retry error:", err);

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to retry workflow stage."
      );
    } finally {
      setLoading(false);
    }
  }

  const activeWorkflow =
    selectedWorkflow || selectedSummary;

  return (
    <main className="nm-page nm-workflows-page">
      <section className="nm-page-header">
        <div>
          <span className="nm-small-label">
            CREATOR OPERATING SYSTEM
          </span>

          <h1>Workflows</h1>

          <p>
            Turn one command into a complete N1MOX30
            production pipeline.
          </p>
        </div>

        <button
          type="button"
          className="nm-panel-action"
          onClick={loadWorkflows}
          disabled={refreshing}
        >
          {refreshing ? "Refreshing..." : "↻ Refresh"}
        </button>
      </section>

      <section className="nm-command-panel nm-workflow-command">
        <div className="nm-panel-heading">
          <div>
            <span>CREATE AUTOMATION</span>
            <h3>Start a production workflow</h3>
          </div>
        </div>

        <div className="nm-workflow-form">
          <input
            value={command}
            onChange={(event) =>
              setCommand(event.target.value)
            }
            placeholder="Tell N1MOX what you want to create..."
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                handleCreate();
              }
            }}
          />

          <select
            value={platform}
            onChange={(event) =>
              setPlatform(event.target.value)
            }
          >
            <option value="youtube">YouTube</option>
            <option value="instagram">Instagram</option>
            <option value="tiktok">TikTok</option>
          </select>

          <input
            value={topic}
            onChange={(event) =>
              setTopic(event.target.value)
            }
            placeholder="Topic"
          />

          <button
            type="button"
            className="nm-workflow-create"
            onClick={handleCreate}
            disabled={loading}
          >
            {loading ? "Starting..." : "▷ Start workflow"}
          </button>
        </div>
      </section>

      {error && (
        <div className="nm-error-panel">
          {error}
        </div>
      )}

      <section className="nm-workflow-layout">
        <div className="nm-command-panel">
          <div className="nm-panel-heading">
            <div>
              <span>PRODUCTION PIPELINE</span>
              <h3>Select a workflow</h3>
            </div>

            <span>
              {workflows.length} workflow
              {workflows.length === 1 ? "" : "s"}
            </span>
          </div>

          {!activeWorkflow && (
            <div className="nm-workflow-empty">
              Create or select a workflow to inspect
              the full production pipeline.
            </div>
          )}

          {activeWorkflow && (
            <div className="nm-workflow-detail">
              <div className="nm-workflow-detail-header">
                <div>
                  <span className="nm-small-label">
                    {String(
                      activeWorkflow.platform || ""
                    ).toUpperCase()}
                  </span>

                  <h3>
                    {activeWorkflow.topic ||
                      activeWorkflow.command ||
                      "Workflow"}
                  </h3>

                  <p>
                    {activeWorkflow.command || ""}
                  </p>
                </div>

                <div>
                  <strong>
                    {activeWorkflow.progress ?? 0}%
                  </strong>

                  <span
                    className={`nm-status ${statusClass(
                      activeWorkflow.status
                    )}`}
                  >
                    {activeWorkflow.status || "pending"}
                  </span>
                </div>
              </div>

              <WorkflowStageList
                workflow={activeWorkflow}
              />

              <div className="nm-workflow-actions">
                <button
                  type="button"
                  className="nm-workflow-create"
                  onClick={() =>
                    handleRun(activeWorkflow.id)
                  }
                  disabled={
                    loading ||
                    activeWorkflow.status === "running"
                  }
                >
                  {activeWorkflow.status === "running"
                    ? "Running..."
                    : "▷ Run workflow"}
                </button>

                {activeWorkflow.current_stage &&
                  activeWorkflow.status ===
                    "failed" && (
                    <button
                      type="button"
                      className="nm-panel-action"
                      onClick={() =>
                        handleRetry(
                          activeWorkflow.id,
                          activeWorkflow.current_stage
                        )
                      }
                      disabled={loading}
                    >
                      Retry{" "}
                      {formatStage(
                        activeWorkflow.current_stage
                      )}
                    </button>
                  )}
              </div>
            </div>
          )}
        </div>

        <aside className="nm-command-panel">
          <div className="nm-panel-heading">
            <div>
              <span>WORKFLOW HISTORY</span>
              <h3>Recent runs</h3>
            </div>
          </div>

          {workflows.length === 0 ? (
            <div className="nm-workflow-empty">
              No workflows yet.
            </div>
          ) : (
            <div className="nm-workflow-history">
              {workflows.map((workflow) => (
                <button
                  type="button"
                  key={workflow.id}
                  className={`nm-workflow-history-item ${
                    String(workflow.id) ===
                    String(selectedId)
                      ? "active"
                      : ""
                  }`}
                  onClick={() =>
                    setSelectedId(workflow.id)
                  }
                >
                  <div>
                    <strong>
                      {workflow.topic ||
                        workflow.command ||
                        "Untitled workflow"}
                    </strong>

                    <span>
                      {workflow.status || "pending"} ·{" "}
                      {workflow.progress ?? 0}%
                    </span>
                  </div>

                  <small>
                    {formatDate(workflow.created_at)}
                  </small>
                </button>
              ))}
            </div>
          )}
        </aside>
      </section>
    </main>
  );
}

