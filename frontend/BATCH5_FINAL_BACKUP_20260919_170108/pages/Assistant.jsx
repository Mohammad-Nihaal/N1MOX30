import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  deleteAssistantConversation,
  getAssistantHistory,
  sendAssistantMessage,
} from "../api/assistant";


function Assistant() {
  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([]);

  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(false);

  const [historyLoading, setHistoryLoading] =
    useState(true);

  const [error, setError] = useState("");

  const messagesEndRef = useRef(null);


  // =================================================
  // LOAD HISTORY
  // =================================================

  const loadHistory = useCallback(
    async () => {
      try {
        setHistoryLoading(true);

        const data =
          await getAssistantHistory();

        const conversations =
          Array.isArray(
            data?.conversations
          )
            ? data.conversations
            : [];

        setHistory(conversations);

      } catch (loadError) {
        console.error(
          "Failed to load assistant history:",
          loadError
        );

        setHistory([]);

      } finally {
        setHistoryLoading(false);
      }
    },
    []
  );


  // =================================================
  // INITIAL HISTORY LOAD
  // =================================================

  useEffect(() => {
    const timer = window.setTimeout(
      () => {
        loadHistory();
      },
      0
    );

    return () => {
      window.clearTimeout(timer);
    };
  }, [loadHistory]);


  // =================================================
  // AUTO SCROLL
  // =================================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);


  // =================================================
  // START NEW CONVERSATION
  // =================================================

  function startNewConversation() {
    setMessages([]);
    setMessage("");
    setError("");
  }


  // =================================================
  // SAFE ERROR MESSAGE
  // =================================================

  function getErrorMessage(requestError) {
    const detail =
      requestError?.response?.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (typeof item === "string") {
            return item;
          }

          if (
            item &&
            typeof item === "object"
          ) {
            if (
              typeof item.msg === "string"
            ) {
              return item.msg;
            }

            if (
              typeof item.message === "string"
            ) {
              return item.message;
            }
          }

          return "Validation error";
        })
        .join(", ");
    }

    if (
      detail &&
      typeof detail === "object"
    ) {
      if (
        typeof detail.msg === "string"
      ) {
        return detail.msg;
      }

      if (
        typeof detail.message === "string"
      ) {
        return detail.message;
      }

      return "Request validation failed.";
    }

    if (
      typeof requestError?.message === "string" &&
      requestError.message
    ) {
      return requestError.message;
    }

    return (
      "N1MOX30 could not process your message. " +
      "Please try again."
    );
  }


  // =================================================
  // SEND MESSAGE
  // =================================================

  async function handleSendMessage(event) {
    event.preventDefault();

    const trimmedMessage =
      message.trim();

    if (
      !trimmedMessage ||
      loading
    ) {
      return;
    }


    // ===============================================
    // ADD USER MESSAGE IMMEDIATELY
    // ===============================================

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      message: trimmedMessage,
      created_at:
        new Date().toISOString(),
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setMessage("");
    setError("");
    setLoading(true);


    try {
      const data =
        await sendAssistantMessage({
          message: trimmedMessage,
          conversation_type: "chat",
        });


      // =============================================
      // VALIDATE RESPONSE
      // =============================================

      const responseText =
        typeof data?.response === "string"
          ? data.response.trim()
          : "";

      if (!responseText) {
        throw new Error(
          "N1MOX30 did not return a valid response."
        );
      }


      // =============================================
      // ADD ASSISTANT RESPONSE
      // =============================================

      const assistantMessage = {
        id:
          data?.conversation_id ||
          `assistant-${Date.now()}`,

        role: "assistant",

        message: responseText,

        provider:
          typeof data?.provider === "string"
            ? data.provider
            : "unknown",

        action_type:
          typeof data?.action_type === "string"
            ? data.action_type
            : null,

        action_status:
          typeof data?.action_status === "string"
            ? data.action_status
            : null,

        created_at:
          data?.created_at ||
          new Date().toISOString(),
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);


      // =============================================
      // UPDATE HISTORY WITHOUT BLOCKING CHAT
      // =============================================

      loadHistory();

    } catch (sendError) {
      console.error(
        "Failed to send assistant message:",
        sendError
      );

      const errorMessage =
        getErrorMessage(sendError);

      setError(errorMessage);

    } finally {
      setLoading(false);
    }
  }


  // =================================================
  // OPEN HISTORY CONVERSATION
  // =================================================

  function openConversation(conversation) {
    if (!conversation) {
      return;
    }

    const userText =
      typeof conversation.message === "string"
        ? conversation.message
        : "";

    const assistantText =
      typeof conversation.response === "string"
        ? conversation.response
        : "No response available.";

    setMessages([
      {
        id:
          `history-user-${conversation.id}`,

        role: "user",

        message: userText,

        created_at:
          conversation.created_at ||
          new Date().toISOString(),
      },

      {
        id:
          `history-assistant-${conversation.id}`,

        role: "assistant",

        message: assistantText,

        action_type:
          typeof conversation.action_type === "string"
            ? conversation.action_type
            : null,

        action_status:
          typeof conversation.action_status === "string"
            ? conversation.action_status
            : null,

        created_at:
          conversation.created_at ||
          new Date().toISOString(),
      },
    ]);

    setError("");
  }


  // =================================================
  // DELETE CONVERSATION
  // =================================================

  async function handleDeleteConversation(
    event,
    conversationId
  ) {
    event.stopPropagation();

    if (!conversationId) {
      return;
    }

    const confirmed =
      window.confirm(
        "Delete this assistant conversation?"
      );

    if (!confirmed) {
      return;
    }


    try {
      await deleteAssistantConversation(
        conversationId
      );

      setHistory((currentHistory) =>
        currentHistory.filter(
          (conversation) =>
            conversation.id !== conversationId
        )
      );

      setMessages((currentMessages) =>
        currentMessages.filter(
          (chatMessage) =>
            !String(chatMessage.id).includes(
              conversationId
            )
        )
      );

    } catch (deleteError) {
      console.error(
        "Failed to delete conversation:",
        deleteError
      );

      setError(
        getErrorMessage(deleteError)
      );
    }
  }


  // =================================================
  // USE SUGGESTION
  // =================================================

  function useSuggestion(text) {
    setMessage(text);
    setError("");
  }


  // =================================================
  // RENDER
  // =================================================

  return (
    <div className="assistant-page">

      {/* ============================================= */}
      {/* HEADER */}
      {/* ============================================= */}

      <div className="assistant-page-header">

        <div>
          <div className="assistant-eyebrow">
            PERSONAL CREATOR AI
          </div>

          <h1>
            N1MOX30 Assistant
          </h1>

          <p>
            Your intelligent creator assistant for
            content, planning, ideas, workflow,
            research, and creator decisions.
          </p>
        </div>


        <button
          type="button"
          className="assistant-new-chat-button"
          onClick={startNewConversation}
        >
          + New Conversation
        </button>

      </div>


      {/* ============================================= */}
      {/* MAIN LAYOUT */}
      {/* ============================================= */}

      <div className="assistant-layout">


        {/* =========================================== */}
        {/* HISTORY */}
        {/* =========================================== */}

        <aside className="assistant-history-panel">

          <div className="assistant-history-header">

            <div>

              <span className="assistant-history-label">
                CONVERSATIONS
              </span>

              <h2>
                Recent Activity
              </h2>

            </div>

          </div>


          <div className="assistant-history-list">

            {historyLoading ? (

              <div className="assistant-history-empty">
                Loading conversations...
              </div>

            ) : history.length === 0 ? (

              <div className="assistant-history-empty">

                No conversations yet.

                <span>
                  Start talking with N1MOX30.
                </span>

              </div>

            ) : (

              history.map((conversation) => (

                <div
                  key={conversation.id}
                  className="assistant-history-item"
                >

                  <button
                    type="button"
                    className="assistant-history-content"
                    onClick={() =>
                      openConversation(
                        conversation
                      )
                    }
                  >

                    <span>
                      {typeof conversation.message ===
                      "string"
                        ? conversation.message
                        : "Untitled conversation"}
                    </span>

                    <small>
                      {typeof conversation.conversation_type ===
                      "string"
                        ? conversation.conversation_type
                        : "chat"}
                    </small>

                  </button>


                  <button
                    type="button"
                    className="assistant-history-delete"
                    onClick={(event) =>
                      handleDeleteConversation(
                        event,
                        conversation.id
                      )
                    }
                    title="Delete conversation"
                    aria-label="Delete conversation"
                  >
                    ×
                  </button>

                </div>

              ))

            )}

          </div>

        </aside>


        {/* =========================================== */}
        {/* CHAT */}
        {/* =========================================== */}

        <section className="assistant-chat-panel">


          {/* ========================================= */}
          {/* WELCOME */}
          {/* ========================================= */}

          {messages.length === 0 && (

            <div className="assistant-welcome">

              <div className="assistant-orb">
                N
              </div>

              <span className="assistant-status">
                N1MOX30 ONLINE
              </span>

              <h2>
                What can we create today?
              </h2>

              <p>
                Ask me to plan content, generate ideas,
                improve your workflow, analyze creator
                decisions, or organize your next move.
              </p>


              <div className="assistant-suggestions">

                <button
                  type="button"
                  onClick={() =>
                    useSuggestion(
                      "Help me plan my content for this week"
                    )
                  }
                >
                  Plan my week
                </button>


                <button
                  type="button"
                  onClick={() =>
                    useSuggestion(
                      "Give me 5 content ideas for my niche"
                    )
                  }
                >
                  Generate ideas
                </button>


                <button
                  type="button"
                  onClick={() =>
                    useSuggestion(
                      "What should I focus on today?"
                    )
                  }
                >
                  What should I do today?
                </button>

              </div>

            </div>

          )}


          {/* ========================================= */}
          {/* MESSAGES */}
          {/* ========================================= */}

          {messages.length > 0 && (

            <div className="assistant-messages">

              {messages.map((chatMessage) => (

                <div
                  key={chatMessage.id}
                  className={
                    "assistant-message " +
                    (
                      chatMessage.role === "user"
                        ? "assistant-message-user"
                        : "assistant-message-ai"
                    )
                  }
                >

                  <div className="assistant-message-role">

                    {chatMessage.role === "user"
                      ? "YOU"
                      : "N1MOX30"}

                  </div>


                  <div className="assistant-message-content">

                    {typeof chatMessage.message ===
                    "string"
                      ? chatMessage.message
                      : "Unable to display message."}

                  </div>


                  {chatMessage.action_type && (

                    <div className="assistant-action-badge">

                      Action:{" "}
                      {chatMessage.action_type}

                      {chatMessage.action_status && (
                        <>
                          {" · "}
                          {chatMessage.action_status}
                        </>
                      )}

                    </div>

                  )}

                </div>

              ))}


              {loading && (

                <div className="assistant-message assistant-message-ai">

                  <div className="assistant-message-role">
                    N1MOX30
                  </div>

                  <div className="assistant-typing">
                    <span />
                    <span />
                    <span />
                  </div>

                </div>

              )}


              <div ref={messagesEndRef} />

            </div>

          )}


          {/* ========================================= */}
          {/* ERROR */}
          {/* ========================================= */}

          {error && (

            <div className="assistant-error">

              {typeof error === "string"
                ? error
                : "An unexpected error occurred."}

            </div>

          )}


          {/* ========================================= */}
          {/* INPUT */}
          {/* ========================================= */}

          <form
            className="assistant-input-form"
            onSubmit={handleSendMessage}
          >

            <textarea
              value={message}

              onChange={(event) =>
                setMessage(
                  event.target.value
                )
              }

              placeholder={
                "Ask N1MOX30 anything about your creator workflow..."
              }

              rows="1"

              disabled={loading}

              onKeyDown={(event) => {

                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {
                  event.preventDefault();

                  event.currentTarget
                    .form
                    ?.requestSubmit();
                }

              }}
            />


            <button
              type="submit"

              disabled={
                loading ||
                !message.trim()
              }
            >

              {loading
                ? "Thinking..."
                : "Send"}

            </button>

          </form>


          {/* ========================================= */}
          {/* FOOTER */}
          {/* ========================================= */}

          <div className="assistant-input-footer">

            N1MOX30 uses your creator profile,
            memory, and platform intelligence to
            provide contextual assistance.

          </div>

        </section>

      </div>

    </div>
  );
}


export default Assistant;