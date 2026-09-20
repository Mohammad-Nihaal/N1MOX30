import {
  useEffect,
  useRef,
  useState,
} from "react";

type VoiceResult = {
  wake_word_detected?: boolean;
  transcript?: string;

  response?: {
    text?: string;
    provider?: string;
  };

  action?: {
    executed?: boolean;
    action?: string | null;
    workflow_id?: string;
    message?: string;
  };
};

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

function getToken(): string {
  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("token") ||
    ""
  );
}

export default function N1MOXVoice() {
  const recognitionRef =
    useRef<SpeechRecognitionLike | null>(null);

  const [listening, setListening] =
    useState(false);

  const [transcript, setTranscript] =
    useState("");

  const [response, setResponse] =
    useState("");

  const [error, setError] =
    useState("");

  const [supported, setSupported] =
    useState(true);

  const speak = (text: string) => {
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
  };

  const sendToN1MOX = async (
    text: string
  ) => {
    const token = getToken();

    const result = await fetch(
      "/voice/command",
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",

          ...(token
            ? {
                Authorization:
                  `Bearer ${token}`,
              }
            : {}),
        },

        body: JSON.stringify({
          transcript: text,
        }),
      }
    );

    if (!result.ok) {
      throw new Error(
        `Voice request failed (${result.status})`
      );
    }

    const data: VoiceResult =
      await result.json();

    const reply =
      data.response?.text ||
      data.action?.message ||
      "I have processed your request.";

    setResponse(reply);

    speak(reply);
  };

  const startListening = () => {
    setError("");

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

      try {
        await sendToN1MOX(text);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Voice request failed."
        );
      }
    };

    recognition.onerror = () => {
      setListening(false);

      setError(
        "I couldn't understand the microphone input."
      );
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognitionRef.current =
      recognition;

    recognition.start();

    setListening(true);
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
          disabled={!supported}
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
            cursor: "pointer",
            fontSize: 24,
          }}
        >
          {listening ? "■" : "🎙️"}
        </button>

        <div>
          <strong>
            {listening
              ? "N1MOX is listening..."
              : "Talk to N1MOX"}
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
          {error}
        </div>
      )}
    </section>
  );
}
