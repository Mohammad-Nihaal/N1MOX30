const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function headers() {
  const token =
    localStorage.getItem("access_token") ||
    localStorage.getItem("token");

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...headers(),
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || `HTTP ${response.status}`);
  }

  return data;
}

export const getCreatorOSStages = () =>
  request("/platform/v16/creator-os/stages");

export const createCreatorOSJob = (userId, topic) =>
  request(
    `/platform/v16/creator-os/jobs?user_id=${encodeURIComponent(userId)}&topic=${encodeURIComponent(topic)}`,
    { method: "POST" }
  );

export const getCreatorOSProgress = (jobId) =>
  request(`/platform/v16/creator-os/jobs/${encodeURIComponent(jobId)}/progress`);

export const getCreatorAccounts = (userId) =>
  request(`/platform/v17/creator/${encodeURIComponent(userId)}/accounts`);

export const getPublishingQueue = (userId) =>
  request(`/platform/v17/creator/${encodeURIComponent(userId)}/publishing-queue`);