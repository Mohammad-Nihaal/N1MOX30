import { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertCircle, Camera, CheckCircle2, Plus, RefreshCw, Unplug, Video } from "lucide-react";
import api from "../api/client";

const PLATFORM_LIMITS = {
  youtube: 2,
  instagram: 2,
  x: 2,
};

const PLATFORMS = [
  {
    id: "youtube",
    name: "YouTube",
    icon: Video,
    description:
      "Channel analytics, publishing, scheduling and creator growth intelligence.",
  },
  {
    id: "instagram",
    name: "Instagram",
    icon: Camera,
    description:
      "Professional creator publishing, content distribution and audience intelligence.",
  },
  {
    id: "x",
    name: "X",
    icon: Video,
    description:
      "Posts, distribution, account metrics and unified publishing.",
  },
];

function normalizePlatform(platform) {
  const value = String(platform || "").toLowerCase();

  if (value === "video" || value === "youtube") {
    return "youtube";
  }

  if (value === "music2" || value === "instagram") {
    return "instagram";
  }

  return value;
}

export default function Accounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState("");
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
    load();
  }, [load]);

  const groupedAccounts = useMemo(() => {
    const groups = {
      youtube: [],
      instagram: [],
      x: [],
    };

    for (const account of accounts) {
      const platform = normalizePlatform(account.platform);

      if (
        Object.prototype.hasOwnProperty.call(groups, platform) &&
        account.is_active
      ) {
        groups[platform].push(account);
      }
    }

    return groups;
  }, [accounts]);

  async function connect(platform) {
    const current = groupedAccounts[platform] || [];
    const limit = PLATFORM_LIMITS[platform] || 2;

    if (current.length >= limit) {
      setError(
        `${platform} account limit reached. You can connect up to ${limit} accounts.`
      );
      return;
    }

    setConnecting(platform);
    setError("");

    try {
      const response = await api.get(
        `/oauth/${platform}/connect`
      );

      const authorizationUrl =
        response.data?.authorization_url;

      if (!authorizationUrl) {
        setError(
          `${platform} OAuth did not return an authorization URL.`
        );
        return;
      }

      window.location.assign(authorizationUrl);
    } catch (e) {
      setError(
        e?.response?.data?.detail ||
          `${platform} OAuth is not configured yet.`
      );
    } finally {
      setConnecting("");
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
            Connect multiple creator accounts and manage them
            from one N1MOX30 workspace.
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
          const connected =
            groupedAccounts[platform.id] || [];
          const limit = PLATFORM_LIMITS[platform.id];

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

                <span className="account-status">
                  {connected.length}/{limit} slots
                </span>
              </div>

              <div className="account-card-content">
                <h2>{platform.name}</h2>
                <p>{platform.description}</p>
              </div>

              <div
                style={{
                  display: "grid",
                  gap: 10,
                  marginTop: 14,
                }}
              >
                {Array.from({ length: limit }).map(
                  (_, index) => {
                    const account = connected[index];

                    if (!account) {
                      return (
                        <div
                          key={`${platform.id}-empty-${index}`}
                          className="connected-account-info"
                          style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            gap: 12,
                          }}
                        >
                          <span>
                            Account {index + 1} — Available
                          </span>

                          <button
                            className="primary-button"
                            onClick={() =>
                              connect(platform.id)
                            }
                            disabled={
                              loading ||
                              connecting === platform.id ||
                              connected.length >= limit
                            }
                          >
                            <Plus size={16} />
                            {connecting === platform.id
                              ? "Connecting..."
                              : "Connect"}
                          </button>
                        </div>
                      );
                    }

                    return (
                      <div
                        key={account.id}
                        className="connected-account-info"
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          gap: 12,
                        }}
                      >
                        <div>
                          <strong>
                            {account.account_name ||
                              `${platform.name} Account ${index + 1}`}
                          </strong>

                          <span
                            style={{
                              display: "block",
                              marginTop: 3,
                            }}
                          >
                            {account.platform_account_id ||
                              "Connected account"}
                          </span>
                        </div>

                        <span
                          className="account-status connected"
                          style={{ whiteSpace: "nowrap" }}
                        >
                          <CheckCircle2 size={15} />
                          Connected
                        </span>

                        <button
                          className="danger-button"
                          onClick={() =>
                            disconnect(account.id)
                          }
                        >
                          <Unplug size={16} />
                          Disconnect
                        </button>
                      </div>
                    );
                  }
                )}
              </div>
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
            <span>Owner account allowance</span>
          </div>
        </div>

        <p className="muted">
          N1MOX30 supports up to two connected YouTube,
          Instagram and X accounts per workspace. N1MOX30
          does not charge a separate connection fee for these
          owner slots. Platform API quotas, developer approval,
          OAuth availability and any external platform charges
          remain controlled by the respective platforms.
        </p>
      </div>
    </div>
  );
}


