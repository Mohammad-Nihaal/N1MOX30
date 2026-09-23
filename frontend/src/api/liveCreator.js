const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function token() {
  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("token") ||
    ""
  );
}

async function request(path, options = {}) {
  const response = await fetch(
    `${API_BASE}${path}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token()
          ? { Authorization: `Bearer ${token()}` }
          : {}),
        ...(options.headers || {}),
      },
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail ||
      data.error ||
      `Request failed: ${response.status}`
    );
  }

  return data;
}

export function getCreatorAccounts(userId) {
  return request(`/platform/v14/live/accounts/${userId}`);
}

export function getYouTubeChannel(accountId) {
  return request(
    `/platform/v14/live/youtube/${accountId}/channel`
  );
}

export function getYouTubeVideos(accountId, limit = 10) {
  return request(
    `/platform/v14/live/youtube/${accountId}/videos?limit=${limit}`
  );
}

export function getYouTubeAnalytics(accountId, limit = 10) {
  return request(
    `/platform/v14/live/youtube/${accountId}/analytics?limit=${limit}`
  );
}

export function publishToYouTube(payload) {
  return request(
    "/platform/v14/live/youtube/publish",
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}