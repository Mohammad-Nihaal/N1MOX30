import { useState, useEffect, useRef } from "react";
import {
  executeVoiceCommand,
  getVoiceStatus,
} from "../api/voiceAssistant";

export default function N1MOXVoiceAssistant() {
  const recognitionRef = useRef(null);
  const activeRef = useRef(false);

  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState(
    "Say Ã¢â‚¬Å“Hey N1MOXÃ¢â‚¬Â to control your creator workflow."
  );
  const [error, setError] = useState("");

  useEffect(() => {
    const Recognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!Recognition) {
      setSupported(false);
      return;
    }

    setSupported(true);

    const recognition = new Recognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = async (event) => {
      let finalText = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        const text = event.results[i][0].transcript;

        if (event.results[i].isFinal) {
          finalText += text;
        }
      }

      if (!finalText.trim()) {
        return;
      }

      const cleaned = finalText.trim();

      setTranscript(cleaned);

      const lower = cleaned.toLowerCase();
      const wakeIndex = lower.indexOf("hey nimox");

      if (wakeIndex === -1) {
        return;
      }

      const command = cleaned
        .slice(wakeIndex + "hey nimox".length)
        .trim();

      if (!command) {
        setResponse(
          "I'm listening. What would you like me to do?"
        );
        return;
      }

      try {
        setError("");
        setResponse("N1MOX is processing your command...");

        const result = await executeVoiceCommand({
          text: command,
        });

        const message =
          result?.execution?.message ||
          result?.message ||
          "Command completed.";

        setResponse(message);

        if ("speechSynthesis" in window) {
          window.speechSynthesis.cancel();

          const utterance =
            new SpeechSynthesisUtterance(message);

          utterance.rate = 1;
          utterance.pitch = 1;

          window.speechSynthesis.speak(utterance);
        }
      } catch (err) {
        setError(err.message);
        setResponse(
          "I couldn't complete that command."
        );
      }
    };

    recognition.onerror = (event) => {
      if (event.error !== "aborted") {
        setError(`Voice input error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setListening(false);

      if (activeRef.current) {
        try {
          recognition.start();
          setListening(true);
        } catch {
          // Browser may reject a rapid restart.
        }
      }
    };

    recognitionRef.current = recognition;

    return () => {
      activeRef.current = false;

      try {
        recognition.stop();
      } catch {
        // Already stopped.
      }
    };
  }, []);

  async function startListening() {
    setError("");

    try {
      await getVoiceStatus();

      if (!recognitionRef.current) {
        setError(
          "This browser does not support microphone speech recognition."
        );
        return;
      }

      activeRef.current = true;
      recognitionRef.current.start();
      setListening(true);
      setResponse(
        "Listening for Ã¢â‚¬Å“Hey N1MOXÃ¢â‚¬Â..."
      );
    } catch (err) {
      setError(err.message);
    }
  }

  function stopListening() {
    activeRef.current = false;

    try {
      recognitionRef.current?.stop();
    } catch {
      // Already stopped.
    }

    setListening(false);
    setResponse("Voice control paused.");
  }

  return (
    <section
      style={{
        margin: "20px 0",
        padding: "20px",
        borderRadius: "18px",
        border: "1px solid rgba(0,0,0,.12)",
        background: "#f8f5ee",
        color: "#111",
        maxWidth: "720px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "16px",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "12px",
              letterSpacing: "2px",
              fontWeight: 700,
            }}
          >
            N1MOX VOICE
          </div>

          <h3
            style={{
              margin: "6px 0",
              fontSize: "24px",
            }}
          >
            Hey N1MOX
          </h3>

          <div
            style={{
              opacity: 0.7,
              fontSize: "14px",
            }}
          >
            Hands-free creator workflow control
          </div>
        </div>

        <button
          onClick={
            listening
              ? stopListening
              : startListening
          }
          disabled={!supported}
          style={{
            border: 0,
            borderRadius: "999px",
            padding: "12px 20px",
            cursor: supported
              ? "pointer"
              : "not-allowed",
            fontWeight: 700,
            background: listening
              ? "#111"
              : "#e8dfce",
            color: listening
              ? "#fff"
              : "#111",
          }}
        >
          {listening
            ? "Stop Listening"
            : "Start Voice"}
        </button>
      </div>

      <div
        style={{
          marginTop: "18px",
          padding: "14px",
          borderRadius: "12px",
          background: "#fff",
          fontSize: "14px",
        }}
      >
        <strong>Transcript:</strong>{" "}
        {transcript || "Ã¢â‚¬â€"}
      </div>

      <div
        style={{
          marginTop: "10px",
          padding: "14px",
          borderRadius: "12px",
          background: "#fff",
          fontSize: "14px",
        }}
      >
        <strong>N1MOX:</strong>{" "}
        {response}
      </div>

      {!supported && (
        <div
          style={{
            marginTop: "10px",
            fontSize: "13px",
            opacity: 0.7,
          }}
        >
          Microphone speech recognition is not
          available in this browser.
        </div>
      )}

      {error && (
        <div
          style={{
            marginTop: "10px",
            fontSize: "13px",
            color: "#8b0000",
          }}
        >
          {error}
        </div>
      )}
    </section>
  );
}