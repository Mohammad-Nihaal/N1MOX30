import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  executeCreatorCommand,
} from "../api/commandExecutor";

type SpeechRecognitionEventLike = Event & {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
        confidence: number;
      };
    };
  };
};

type SpeechRecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;

  start: () => void;
  stop: () => void;

  onresult: (
    event: SpeechRecognitionEventLike
  ) => void;

  onerror: (
    event: Event
  ) => void;

  onend: () => void;
};

type SpeechRecognitionConstructor =
  new () => SpeechRecognitionLike;

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

type CreatorCommandResult = {
  parsed?: {
    command?: string;
    platform?: string;
    topic?: string;
    contentType?: string;
  };

  workflow?: {
    id?: string;
    workflow_id?: string;
    status?: string;
    current_stage?: string;
    progress?: number;
    message?: string;
  };
};

function speak(text: string) {
  if (!text) {
    return;
  }

  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();

    const utterance =
      new SpeechSynthesisUtterance(text);

    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    window.speechSynthesis.speak(
      utterance
    );
  }
}

function getWorkflowId(
  result: CreatorCommandResult
): string {
  return (
    result.workflow?.id ||
    result.workflow?.workflow_id ||
    ""
  );
}

function buildVoiceResponse(
  result: CreatorCommandResult
): string {
  const workflowId =
    getWorkflowId(result);

  const platform =
    result.parsed?.platform ||
    "your platform";

  const topic =
    result.parsed?.topic ||
    "your content";

  if (workflowId) {
    return (
      `Done. I started your ${platform} ` +
      `workflow for "${topic}". ` +
      `Creator OS is now processing it.`
    );
  }

  return (
    "Done. Your N1MOX creator workflow has been started."
  );
}

export default function N1MOXVoice() {
  const recognitionRef =
    useRef<SpeechRecognitionLike | null>(null);

  const [listening, setListening] =
    useState(false);

  const [processing, setProcessing] =
    useState(false);

  const [transcript, setTranscript] =
    useState("");

  const [response, setResponse] =
    useState("");

  const [error, setError] =
    useState("");

  const [supported, setSupported] =
    useState(true);

  const executeVoiceCommand = async (
    text: string
  ) => {
    const cleaned =
      String(text || "").trim();

    if (!cleaned) {
      return;
    }

    setProcessing(true);
    setError("");
    setResponse(
      "N1MOX is processing your command..."
    );

    try {
      /*
       * IMPORTANT:
       *
       * Voice uses the EXACT SAME command executor
       * as the typed Assistant.
       *
       * Voice does NOT create a second automation
       * system and does NOT call a separate workflow
       * endpoint.
       */
      const result =
        (await executeCreatorCommand(
          cleaned
        )) as CreatorCommandResult;

      const workflowId =
        getWorkflowId(result);

      const message =
        buildVoiceResponse(result);

      if (workflowId) {
        setResponse(
          `${message} Workflow ID: ${workflowId}`
        );
      } else {
        setResponse(message);
      }

      speak(message);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "N1MOX could not execute that command.";

      setError(message);
      setResponse("");

      speak(
        "I couldn't complete that command."
      );
    } finally {
      setProcessing(false);
    }
  };

  const startListening = () => {
    setError("");
    setResponse("");

    const Recognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!Recognition) {
      setSupported(false);

      setError(
        "Speech recognition is not supported in this browser."
      );

      return;
    }

    const recognition =
      new Recognition();

    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = async (
      event
    ) => {
      const text =
        event.results[0][0].transcript;

      setTranscript(text);
      setListening(false);

      await executeVoiceCommand(text);
    };

    recognition.onerror = () => {
      setListening(false);
      setProcessing(false);

      setError(
        "I couldn't understand the microphone input."
      );
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognitionRef.current =
      recognition;

    try {
      recognition.start();
      setListening(true);
    } catch (err) {
      setListening(false);

      setError(
        err instanceof Error
          ? err.message
          : "Could not start microphone."
      );
    }
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setListening(false);
  };

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop();

      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return (
    <section
      style={{
        padding: 24,
        borderRadius: 20,
        border:
          "1px solid rgba(255,255,255,.12)",
        background:
          "rgba(255,255,255,.04)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
        }}
      >
        <button
          type="button"
          onClick={
            listening
              ? stopListening
              : startListening
          }
          disabled={
            !supported ||
            processing
          }
          aria-label={
            listening
              ? "Stop listening"
              : "Talk to N1MOX"
          }
          style={{
            width: 64,
            height: 64,
            borderRadius: "50%",
            border: "none",
            cursor:
              processing
                ? "wait"
                : "pointer",
            fontSize: 24,
          }}
        >
          {processing
            ? "◌"
            : listening
              ? "■"
              : "🎙️"}
        </button>

        <div>
          <strong>
            {processing
              ? "N1MOX is executing..."
              : listening
                ? "N1MOX is listening..."
                : "Hey N1MOX"}
          </strong>

          <div
            style={{
              marginTop: 6,
              opacity: 0.7,
            }}
          >
            Say: "Hey N1MOX, create a
            video about AI."
          </div>
        </div>
      </div>

      {transcript && (
        <div
          style={{
            marginTop: 20,
          }}
        >
          <strong>You:</strong>

          <div>
            {transcript}
          </div>
        </div>
      )}

      {response && (
        <div
          style={{
            marginTop: 16,
          }}
        >
          <strong>N1MOX:</strong>

          <div>
            {response}
          </div>
        </div>
      )}

      {error && (
        <div
          style={{
            marginTop: 16,
          }}
        >
          <strong>N1MOX:</strong>

          <div>
            {error}
          </div>
        </div>
      )}
    </section>
  );
}
