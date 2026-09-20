import api from "./client";


export async function generateAIContent(data) {
  const response = await api.post(
    "/ai/generate",
    data
  );

  return response.data;
}


export async function getAIGenerationHistory(
  limit = 50,
  offset = 0
) {
  const response = await api.get(
    "/ai/history",
    {
      params: {
        limit,
        offset,
      },
    }
  );

  return response.data;
}


export async function getAIGeneration(
  generationId
) {
  const response = await api.get(
    `/ai/history/${generationId}`
  );

  return response.data;
}


export async function reuseAIGeneration(
  generationId,
  data = {}
) {
  const response = await api.post(
    `/ai/history/${generationId}/reuse`,
    data
  );

  return response.data;
}


export async function deleteAIGeneration(
  generationId
) {
  await api.delete(
    `/ai/history/${generationId}`
  );
}