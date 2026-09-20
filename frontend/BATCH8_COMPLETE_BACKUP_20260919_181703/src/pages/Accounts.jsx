import { useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  ExternalLink,
  RefreshCw,
  Unplug,
  Video,
  Music2,
  AtSign,
} from "lucide-react";
import api from "../api/client";

const PLATFORMS = [
  {
    id: "youtube",
    name: "YouTube",
    icon: Video,
    description:
      "Channel analytics, uploads, scheduling and growth intelligence.",
  },
  {
    id: "instagram",
    name: "Instagram",
    icon: AtSign,
    description:
      "Professional account publishing, creator analytics and audience growth.",
  },
  {
    id: "tiktok",
    name: "TikTok",
    icon: Music2,
    description:
      "Short-form video publishing and creator performance intelligence.",
  },
  {
    id: "x",
    name: "X",
    icon: AtSign,
    description:
      "Posts, account metrics and unified distribution.",
  },
];

export default function Accounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/connected-accounts");
      setAccounts(Array.isArray(response.data) ? response.data : []);
    } catch (e) {
      setError(
        e?.response?.data?.detail ||
          "Unable to load connected accounts."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function initialLoad() {
      setLoading(true);
      setError("");

      try {
        const response = await api.get("/connected-accounts");

        if (!cancelled) {
          setAccounts(
            Array.isArray(response.data) ? response.data : []
          );
        }
      } catch (e) {
        if (!cancelled) {
          setError(
            e?.response?.data?.detail ||
              "Unable to load connected accounts."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    initialLoad();

    return () => {
      cancelled = true;
    };
  }, []);

  async function connect(platform) {
    setError("");

    try {
      const response = await api.get(
        `/oauth/${platform}/connect`
      );

      const authorizationUrl =
        response.data?.authorization_url;

      if (authorizationUrl) {
        window.open(
          authorizationUrl,
          "_self",
          "noopener,noreferrer"
        );
        return;
      }

      setError("Authorization URL was not returned.");
    } catch (e) {
      setError(
        e?.response?.data?.detail ||
          `${platform} OAuth is not configured.`
      );
    }
  }

  async function disconnect(id) {
    if (!window.confirm("Disconnect this account?")) {
      return;
    }

    setError("");

    try {
      await api.delete(`/connected-accounts/${id}`);
      await load();
    } catch (e) {
      setError(
        e?.response?.data?.detail ||
          "Unable to disconnect account."
      );
    }
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <div>
          <span className="page-eyebrow">PLATFORM HUB</span>
          <h1>Connected Accounts</h1>
          <p>
            One identity layer for every creator platform in N1MOX30.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={load}
          disabled={loading}
        >
          <RefreshCw
            size={17}
            className={loading ? "spin" : ""}
          />
          Refresh
        </button>
      </div>

      {error && (
        <div className="auth-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="accounts-grid">
        {PLATFORMS.map((platform) => {
          const Icon = platform.icon;

          const account = accounts.find(
            (item) =>
              item.platform === platform.id &&
              item.is_active
          );

          const connected = Boolean(account?.is_authorized);

          return (
            <div
              className="panel account-card"
              key={platform.id}
            >
              <div className="account-card-header">
                <div
                  className={`platform-icon platform-${platform.id}`}
                >
                  <Icon size={25} />
                </div>

                {connected ? (
                  <span className="account-status connected">
                    <CheckCircle2 size={15} />
                    Connected
                  </span>
                ) : (
                  <span className="account-status">
                    Not connected
                  </span>
                )}
              </div>

              <div className="account-card-content">
                <h2>{platform.name}</h2>
                <p>{platform.description}</p>
              </div>

              {connected ? (
                <>
                  <div className="connected-account-info">
                    <strong>
                      {account.account_name || platform.name}
                    </strong>

                    <span>
                      {account.platform_account_id}
                    </span>
                  </div>

                  <button
                    className="danger-button"
                    onClick={() => disconnect(account.id)}
                  >
                    <Unplug size={16} />
                    Disconnect
                  </button>
                </>
              ) : (
                <button
                  className="primary-button"
                  onClick={() => connect(platform.id)}
                  disabled={loading}
                >
                  <ExternalLink size={16} />
                  Connect {platform.name}
                </button>
              )}
            </div>
          );
        })}
      </div>

      <div
        className="panel"
        style={{
          padding: 22,
          marginTop: 18,
        }}
      >
        <div className="n1-section-heading">
          <div>
            <CheckCircle2 size={18} />
            <span>Unified publishing</span>
          </div>
        </div>

        <p className="muted">
          After connecting accounts, use Publishing Center to
          send one finished asset through the platform adapters.
          Platform approval, developer credentials, verified
          domains and app-store signing remain external account
          requirements.
        </p>
      </div>
    </div>
  );
}
