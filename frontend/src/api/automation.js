import api from "./client";

export async function listWorkflows() {
  const response = await api.get("/automation/workflows");
  return response.data;
}

export async function getWorkflow(workflowId) {
  const response = await api.get(
    `/automation/workflows/${workflowId}`
  );

  return response.data;
}

export async function createWorkflow({
  command,
  platform = "youtube",
  topic,
  project_id = null,
}) {
  const response = await api.post(
    "/automation/workflows",
    {
      command,
      platform,
      topic,
      project_id,
    }
  );

  return response.data;
}

export async function runWorkflow(workflowId) {
  const response = await api.post(
    `/automation/workflows/${workflowId}/run`
  );

  return response.data;
}

export async function retryWorkflowStage(
  workflowId,
  stage
) {
  const response = await api.post(
    `/automation/workflows/${workflowId}/retry/${stage}`
  );

  return response.data;
}
