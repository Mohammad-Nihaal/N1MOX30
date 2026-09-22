import { useEffect, useState } from "react";
import { CheckCircle2, KeyRound, Trash2 } from "lucide-react";
import api from "../api/client";

const PROVIDERS = [
  ["openai", "OpenAI"],
  ["anthropic", "Anthropic"],
  ["gemini", "Google Gemini"],
  ["groq", "Groq"],
  ["openrouter", "OpenRouter"],
  ["xai", "xAI"],
  ["elevenlabs", "ElevenLabs"],
];

export default function BYOK() {
  const [providers, setProviders] = useState([]);
  const [provider, setProvider] = useState("openai");
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/byok/providers");
      setProviders(
        Array.isArray(response.data)
          ? response.data
          : []
      );
    } catch (e) {
      setError(
        e?.response?.data?.detail ||
          "Unable to load BYOK providers."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function save() {
    if (!apiKey.trim()) {
      setError("Enter an API key first.");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await api.put("/byok/credentials", {
        provider,
        api_key: apiKey.trim(),
      });

      setApiKey("");
      setMessage(
        "API key saved securely. The full key is never displayed."
      );

      await load();
    } catch (e) {
      setError(
        e?.response?.data?.detail ||
          "Unable to save API key."
      );
    } finally {
      setSaving(false);
    }
  }

  async function remove(providerId) {
    if (!window.confirm("Remove this provider API key?")) {
      return;
    }

    setError("");
    setMessage("");

    try {
      await api.delete(
        `/byok/credentials/${providerId}`
      );

      setMessage("Provider key removed.");
      await load();
    } catch (e) {
      setError(
        e?.response?.data?.detail ||
          "Unable to remove provider key."
      );
    }
  }

  return (
    <section className="page-section">
      <div className="page-heading">
        <div>
          <p className="eyebrow">AI PROVIDER CONTROL</p>
          <h2>Bring Your Own API</h2>
          <p>
            Connect your own AI provider keys and use them
            through N1MOX30's provider routing layer.
          </p>
        </div>
      </div>

      {error && (
        <div className="auth-error">
          {error}
        </div>
      )}

      {message && (
        <div
          className="save-note"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <CheckCircle2 size={17} />
          {message}
        </div>
      )}

      <div className="settings-grid">
        <div className="glass-card">
          <h3>
            <KeyRound size={18} /> Connect provider
          </h3>

          <label>
            Provider
            <select
              value={provider}
              onChange={(e) =>
                setProvider(e.target.value)
              }
            >
              {PROVIDERS.map(([id, name]) => (
                <option key={id} value={id}>
                  {name}
                </option>
              ))}
            </select>
          </label>

          <label>
            API key
            <input
              type="password"
              value={apiKey}
              onChange={(e) =>
                setApiKey(e.target.value)
              }
              placeholder="Paste your provider API key"
              autoComplete="off"
            />
          </label>

          <button
            className="primary-button"
            onClick={save}
            disabled={saving || loading}
          >
            <KeyRound size={16} />
            {saving ? "Saving..." : "Save API key"}
          </button>

          <p className="muted">
            N1MOX30 stores an encrypted representation and
            only exposes a masked key hint to your account.
          </p>
        </div>

        <div className="glass-card">
          <h3>Connected providers</h3>

          {loading ? (
            <p className="muted">Loading...</p>
          ) : (
            <div
              style={{
                display: "grid",
                gap: 10,
              }}
            >
              {PROVIDERS.map(([id, name]) => {
                const item = providers.find(
                  (x) => x.provider === id
                );

                return (
                  <div
                    key={id}
                    className="connected-account-info"
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: 12,
                    }}
                  >
                    <div>
                      <strong>{name}</strong>
                      <span
                        style={{
                          display: "block",
                          marginTop: 3,
                        }}
                      >
                        {item?.configured
                          ? item.key_hint || "Configured"
                          : "Not configured"}
                      </span>
                    </div>

                    {item?.configured && (
                      <button
                        className="danger-button"
                        onClick={() => remove(id)}
                      >
                        <Trash2 size={15} />
                        Remove
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
