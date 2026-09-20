const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";

async function request(path, options = {}) {
  const token =
    localStorage.getItem("access_token") ||
    localStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";

  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof data === "object" && data?.detail
        ? data.detail
        : typeof data === "string"
          ? data
          : `Research request failed (${response.status})`;

    throw new Error(message);
  }

  return data;
}

export async function getResearch(params = {}) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, value);
    }
  });

  const suffix = query.toString() ? `?${query}` : "";

  return request(`/research${suffix}`);
}

export async function runResearch(payload = {}) {
  return request("/research", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function selectResearchOpportunity(opportunity) {
  return request("/research/select", {
    method: "POST",
    body: JSON.stringify({ opportunity }),
  });
}

export async function generateResearchContent(payload = {}) {
  return request("/research/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getResearchHistory() {
  return request("/research/history");
}

export default {
  getResearch,
  runResearch,
  selectResearchOpportunity,
  generateResearchContent,
  getResearchHistory,
};
/*
 * Batch 19 compatibility exports.
 * These names are consumed by the existing Research.jsx page.
 */

export async function createResearch(payload = {}) {
  return request("/research", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function deleteResearch(id) {
  return request(`/research/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
}

export async function generateContentFromResearch(payload = {}) {
  return request("/research/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
/*
 * Batch 20
 * Research -> N1MOX30 AI Pipeline
 */

export async function generateResearchPipelineContent(payload = {}) {
  const opportunity = payload.opportunity || payload;

  const topic =
    payload.topic ||
    opportunity?.topic ||
    opportunity?.title ||
    opportunity?.name ||
    "";

  const prompt =
    payload.prompt ||
    `Create creator-ready content from this research opportunity:

Topic: ${topic}

Research opportunity:
${JSON.stringify(opportunity, null, 2)}

Return structured creator content including:
- hook
- title options
- short-form script
- caption
- hashtags
- call to action`;

  const response = await request("/platform/v5/ai/generate", {
    method: "POST",
    body: JSON.stringify({
      prompt,
      task: "creator_content",
      topic,
      context: {
        source: "research",
        opportunity,
      },
    }),
  });

  return response;
}