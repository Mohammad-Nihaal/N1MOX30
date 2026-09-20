import api from "./client";


// =================================================
// SEND ASSISTANT MESSAGE
// =================================================

export async function sendAssistantMessage(
  data
) {
  const response = await api.post(
    "/assistant/chat",
    {
      message: data.message,
      conversation_type:
        data.conversation_type || "chat",
    }
  );

  return response.data;
}


// =================================================
// GET ASSISTANT HISTORY
// =================================================

export async function getAssistantHistory(
  limit = 50,
  offset = 0
) {
  const response = await api.get(
    "/assistant/history",
    {
      params: {
        limit,
        offset,
      },
    }
  );

  return response.data;
}


// =================================================
// DELETE ASSISTANT CONVERSATION
// =================================================

export async function deleteAssistantConversation(
  conversationId
) {
  const response = await api.delete(
    `/assistant/history/${conversationId}`
  );

  return response.data;
}