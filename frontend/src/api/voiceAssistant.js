const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

function authHeaders() {
  const token =
    localStorage.getItem("access_token") ||
    localStorage.getItem("token");

  return {
    "Content-Type": "application/json",
    ...(token
      ? { Authorization: `Bearer ${token}` }
      : {}),
  };
}

export async function executeVoiceCommand({
  text,
  userId = 1,
  workflowState = {},
}) {
  const response = await fetch(
    `${API_BASE}/platform/v10/voice/execute`,
    {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        user_id: userId,
        text,
        workflow_state: workflowState,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      `N1MOX voice request failed: ${response.status}`
    );
  }

  return response.json();
}

export async function getVoiceStatus() {
  const response = await fetch(
    `${API_BASE}/platform/v10/voice/status`
  );

  if (!response.ok) {
    throw new Error("Unable to reach N1MOX voice service.");
  }

  return response.json();
}