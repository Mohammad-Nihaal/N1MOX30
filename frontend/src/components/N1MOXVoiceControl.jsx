import { useEffect, useRef, useState } from "react";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE ||
  "http://127.0.0.1:8000";

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition || null;

function normalize(text) {
  return String(text || "").trim().replace(/\s+/g, " ");
}

async function sendToCreatorOS(command) {
  const paths = [
    "/creator-os/command",
    "/creator-os/execute",
    "/creator-operations/command",
    "/creator-os-live/command",
  ];

  let lastError = null;

  for (const path of paths) {
    try {
      const response = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          command,
          text: command,
          input: command,
          source: "voice",
          wake_word: "Hey N1MOX",
        }),
      });

      if (response.status === 404) continue;

      const raw = await response.text();
      let data = {};
      try { data = raw ? JSON.parse(raw) : {}; } catch {}

      if (!response.ok) {
        throw new Error(data.detail || data.message || `Command failed (${response.status})`);
      }

      return { ok: true, data };
    } catch (error) {
      lastError = error;
    }
  }

  return {
    ok: false,
    error:
      lastError?.message ||
      "Creator OS command endpoint was not available.",
  };
}

export default function N1MOXVoiceControl() {
  const recognitionRef = useRef(null);
  const listeningRef = useRef(false);
  const armedRef = useRef(false);
  const [supported, setSupported] = useState(Boolean(SpeechRecognition));
  const [enabled, setEnabled] = useState(false);
  const [armed, setArmed] = useState(false);
  const [status, setStatus] = useState("Voice ready");
  const [lastCommand, setLastCommand] = useState("");

  useEffect(() => {
    if (!SpeechRecognition) {
      setSupported(false);
      return undefined;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      listeningRef.current = true;
      setStatus(armedRef.current ? "Listening for Hey N1MOX..." : "Voice listening");
    };

    recognition.onerror = (event) => {
      const code = event?.error || "unknown";
      if (code === "not-allowed" || code === "service-not-allowed") {
        setStatus("Microphone permission required");
        setEnabled(false);
      } else {
        setStatus(`Voice error: ${code}`);
      }
    };

    recognition.onend = () => {
      listeningRef.current = false;
      if (enabled && recognitionRef.current) {
        try { recognition.start(); } catch {}
      }
    };

    recognition.onresult = async (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += ` ${event.results[i][0].transcript}`;
      }

      const text = normalize(transcript);
      if (!text) return;

      const lower = text.toLowerCase();
      const wakeIndex = lower.indexOf("hey nimox");

      if (!armedRef.current && wakeIndex >= 0) {
        armedRef.current = true;
        setArmed(true);
        setStatus("N1MOX awake -- listening for your command");
        const after = normalize(text.slice(wakeIndex + "hey nimox".length));
        if (!after) return;
        await execute(after);
        return;
      }

      if (armedRef.current && event.results[event.results.length - 1]?.isFinal) {
        await execute(text);
      }
    };

    recognitionRef.current = recognition;

    return () => {
      recognitionRef.current = null;
      try { recognition.stop(); } catch {}
    };
  }, [enabled]);

  async function execute(command) {
    const clean = normalize(command);
    if (!clean) return;

    setLastCommand(clean);
    setStatus("N1MOX is executing...");

    const result = await sendToCreatorOS(clean);

    if (result.ok) {
      setStatus("Command sent to Creator OS");
      window.dispatchEvent(
        new CustomEvent("n1mox:voice-command", { detail: { command: clean, result: result.data } })
      );
    } else {
      setStatus(result.error);
    }

    armedRef.current = false;
    setArmed(false);
  }

  function start() {
    if (!recognitionRef.current) {
      setStatus("Speech recognition is not supported in this browser");
      return;
    }

    setEnabled(true);
    armedRef.current = false;
    setArmed(false);

    try {
      recognitionRef.current.start();
    } catch {}

    setStatus('Listening -- say "Hey N1MOX"');
  }

  function stop() {
    setEnabled(false);
    armedRef.current = false;
    setArmed(false);
    try { recognitionRef.current?.stop(); } catch {}
    setStatus("Voice paused");
  }

  function wakeNow() {
    if (!enabled) start();
    armedRef.current = true;
    setArmed(true);
    setStatus("N1MOX awake -- speak your command");
  }

  return (
    <div className="n1mox-voice-control" role="region" aria-label="N1MOX voice control">
      <div className="n1mox-voice-status">
        <span className={`n1mox-voice-dot ${enabled ? "is-live" : ""}`} />
        <span>{status}</span>
      </div>

      {lastCommand ? (
        <div className="n1mox-voice-command" title={lastCommand}>
          "{lastCommand}"
        </div>
      ) : null}

      <div className="n1mox-voice-actions">
        <button type="button" className="n1mox-voice-button" onClick={enabled ? stop : start}>
          {enabled ? "Stop voice" : "Start voice"}
        </button>
        <button type="button" className="n1mox-voice-wake" onClick={wakeNow} disabled={!supported}>
          Hey N1MOX
        </button>
      </div>
    </div>
  );
}