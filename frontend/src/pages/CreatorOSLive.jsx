import { useState, useEffect, useMemo } from "react";
import {
  getCreatorOSStages,
  createCreatorOSJob,
  getCreatorOSProgress,
  getCreatorAccounts,
  getPublishingQueue,
} from "../api/creatorOSLive";

export default function CreatorOSLive() {
  const [topic, setTopic] = useState("");
  const [job, setJob] = useState(null);
  const [stages, setStages] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const userId =
    localStorage.getItem("user_id") ||
    localStorage.getItem("userId") ||
    "1";

  useEffect(() => {
    loadInitial();
  }, []);

  async function loadInitial() {
    try {
      const [stageData, accountData, queueData] = await Promise.all([
        getCreatorOSStages(),
        getCreatorAccounts(userId),
        getPublishingQueue(userId),
      ]);

      setStages(stageData.stages || []);
      setAccounts(accountData.accounts || []);
      setQueue(queueData.items || []);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function startProduction() {
    if (!topic.trim()) {
      setMessage("Enter a content topic first.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const created = await createCreatorOSJob(userId, topic.trim());
      setJob(created);
      setMessage("Creator OS job created.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshProgress() {
    if (!job?.job_id) return;

    try {
      const data = await getCreatorOSProgress(job.job_id);
      setJob((current) => ({ ...(current || {}), ...data }));
    } catch (error) {
      setMessage(error.message);
    }
  }

  const completed = job?.completed_stages || [];
  const progress =
    Number(job?.progress_percent ?? job?.progress ?? 0) || 0;

  const accountStatus = useMemo(() => {
    return accounts.length ? "Connected" : "Not connected";
  }, [accounts]);

  return (
    <div className="nimox-creator-os-page">
      <div className="nimox-creator-os-hero">
        <div>
          <div className="nimox-eyebrow">N1MOX30 CREATOR OS</div>
          <h1>One command. Thirteen production stages.</h1>
          <p>
            Research, strategy, scripting, production, publishing and
            intelligence in one creator workflow.
          </p>
        </div>

        <div className="nimox-os-status">
          <span>Account</span>
          <strong>{accountStatus}</strong>
        </div>
      </div>

      <div className="nimox-os-create">
        <input
          value={topic}
          onChange={(event) => setTopic(event.target.value)}
          placeholder="What should N1MOX30 create?"
        />
        <button onClick={startProduction} disabled={loading}>
          {loading ? "Starting..." : "Start Creator OS"}
        </button>
        <button onClick={refreshProgress} disabled={!job}>
          Refresh
        </button>
      </div>

      {message && <div className="nimox-os-message">{message}</div>}

      <section className="nimox-os-progress">
        <div className="nimox-os-progress-head">
          <span>Pipeline Progress</span>
          <strong>{progress}%</strong>
        </div>

        <div className="nimox-os-progress-track">
          <div
            className="nimox-os-progress-fill"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>
      </section>

      <section className="nimox-os-grid">
        {stages.map((stage, index) => {
          const done = completed.includes(stage);
          const active =
            !done &&
            completed.length === index;

          return (
            <div
              key={stage}
              className={`nimox-os-stage ${done ? "done" : ""} ${
                active ? "active" : ""
              }`}
            >
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{stage.replaceAll("_", " ")}</strong>
              <small>
                {done ? "Completed" : active ? "Current" : "Waiting"}
              </small>
            </div>
          );
        })}
      </section>

      <section className="nimox-os-panels">
        <div className="nimox-os-panel">
          <h2>Connected Creator Accounts</h2>
          {accounts.length ? (
            accounts.map((account, index) => (
              <div className="nimox-os-row" key={account.id || index}>
                <strong>{account.platform || "Creator account"}</strong>
                <span>{account.channel_name || account.status || "Connected"}</span>
              </div>
            ))
          ) : (
            <p>No creator account is connected yet.</p>
          )}
        </div>

        <div className="nimox-os-panel">
          <h2>Publishing Queue</h2>
          {queue.length ? (
            queue.map((item, index) => (
              <div className="nimox-os-row" key={item.id || index}>
                <strong>{item.title || "Queued content"}</strong>
                <span>{item.status || "queued"}</span>
              </div>
            ))
          ) : (
            <p>No publishing items waiting.</p>
          )}
        </div>
      </section>
    </div>
  );
}