import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Check,
  Edit3,
  LoaderCircle,
  Save,
  Sparkles,
  UserRound,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import api from "../api/client";

const EMPTY_PROFILE = {
  creator_name: "",
  niche: "",
  target_audience: "",
  creator_goals: "",
  preferred_platforms: "",
  content_style: "",
  preferred_tone: "",
  posting_preferences: "",
  ai_preferences: "",
};

function CreatorProfile() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState(EMPTY_PROFILE);
  const [user, setUser] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    setLoading(true);
    setError("");

    try {
      const [profileResponse, userResponse] = await Promise.allSettled([
        api.get("/creator-profile/me"),
        api.get("/auth/me"),
      ]);

      if (profileResponse.status === "fulfilled") {
        setProfile({
          ...EMPTY_PROFILE,
          ...(profileResponse.value.data || {}),
        });
      }

      if (userResponse.status === "fulfilled") {
        setUser(userResponse.value.data);
      }

      if (
        profileResponse.status === "rejected" &&
        profileResponse.reason?.response?.status !== 404
      ) {
        throw profileResponse.reason;
      }
    } catch (requestError) {
      setError(
        requestError?.response?.data?.detail ||
          "Unable to load your creator profile."
      );
    } finally {
      setLoading(false);
    }
  }

  function updateField(field, value) {
    setProfile((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function saveProfile(event) {
    event.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    const payload = Object.fromEntries(
      Object.entries(profile).map(([key, value]) => [
        key,
        typeof value === "string" ? value.trim() : value,
      ])
    );

    try {
      let response;

      if (profile.id) {
        response = await api.put("/creator-profile/me", payload);
      } else {
        response = await api.post("/creator-profile", payload);
      }

      setProfile({
        ...EMPTY_PROFILE,
        ...(response.data || payload),
      });

      setEditing(false);
      setSuccess("Creator profile saved successfully.");

      window.setTimeout(() => {
        setSuccess("");
      }, 2500);
    } catch (requestError) {
      setError(
        requestError?.response?.data?.detail ||
          "Unable to save your creator profile."
      );
    } finally {
      setSaving(false);
    }
  }

  const displayName =
    profile.creator_name ||
    user?.full_name ||
    user?.fullName ||
    user?.name ||
    "Creator";

  const initial =
    displayName.trim().charAt(0).toUpperCase() || "N";

  if (loading) {
    return (
      <main className="n1-profile-page">
        <div className="n1-profile-loading">
          <LoaderCircle size={24} className="n1-spin" />
          <span>Loading creator profile</span>
        </div>
      </main>
    );
  }

  return (
    <main className="n1-profile-page">
      <div className="n1-profile-topbar">
        <button
          type="button"
          className="n1-profile-back"
          onClick={() => navigate("/app")}
        >
          <ArrowLeft size={16} />
          Dashboard
        </button>

        <div className="n1-profile-actions">
          {editing ? (
            <>
              <button
                type="button"
                className="n1-profile-secondary"
                onClick={() => {
                  setEditing(false);
                  setError("");
                  setSuccess("");
                }}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                type="submit"
                form="creator-profile-form"
                className="n1-profile-save"
                disabled={saving}
              >
                {saving ? (
                  <LoaderCircle size={15} className="n1-spin" />
                ) : (
                  <Save size={15} />
                )}

                {saving ? "Saving..." : "Save profile"}
              </button>
            </>
          ) : (
            <button
              type="button"
              className="n1-profile-save"
              onClick={() => setEditing(true)}
            >
              <Edit3 size={15} />
              Edit profile
            </button>
          )}
        </div>
      </div>

      <section className="n1-profile-hero">
        <div className="n1-profile-hero-orbit orbit-a" />
        <div className="n1-profile-hero-orbit orbit-b" />

        <div className="n1-profile-avatar">
          {initial}
        </div>

        <div className="n1-profile-identity">
          <div className="n1-profile-kicker">
            <span />
            CREATOR IDENTITY
          </div>

          <h1>{displayName}</h1>

          <p>
            Your creator identity powers N1MOX30&apos;s
            personalization, intelligence and automation.
          </p>
        </div>

        <div className="n1-profile-status">
          <span />
          Profile active
        </div>
      </section>

      {error && (
        <div className="n1-profile-alert n1-profile-alert-error">
          {error}
        </div>
      )}

      {success && (
        <div className="n1-profile-alert n1-profile-alert-success">
          <Check size={15} />
          {success}
        </div>
      )}

      <form
        id="creator-profile-form"
        className="n1-profile-layout"
        onSubmit={saveProfile}
      >
        <section className="n1-profile-main">
          <div className="n1-profile-section">
            <div className="n1-profile-section-heading">
              <div>
                <span className="n1-profile-section-kicker">
                  IDENTITY
                </span>
                <h2>About you</h2>
              </div>

              <UserRound size={19} />
            </div>

            <div className="n1-profile-fields">
              <ProfileField
                label="Creator name"
                value={profile.creator_name}
                field="creator_name"
                editing={editing}
                onChange={updateField}
                placeholder="Your creator or brand name"
              />

              <ProfileField
                label="Niche"
                value={profile.niche}
                field="niche"
                editing={editing}
                onChange={updateField}
                placeholder="AI, technology, mystery, education..."
              />

              <ProfileField
                label="Target audience"
                value={profile.target_audience}
                field="target_audience"
                editing={editing}
                onChange={updateField}
                placeholder="Who you create for"
              />

              <ProfileField
                label="Creator goals"
                value={profile.creator_goals}
                field="creator_goals"
                editing={editing}
                onChange={updateField}
                placeholder="What you want to achieve"
                wide
              />
            </div>
          </div>

          <div className="n1-profile-section">
            <div className="n1-profile-section-heading">
              <div>
                <span className="n1-profile-section-kicker">
                  CONTENT
                </span>
                <h2>Creative direction</h2>
              </div>

              <Sparkles size={19} />
            </div>

            <div className="n1-profile-fields">
              <ProfileField
                label="Preferred platforms"
                value={profile.preferred_platforms}
                field="preferred_platforms"
                editing={editing}
                onChange={updateField}
                placeholder="YouTube, Instagram, TikTok..."
              />

              <ProfileField
                label="Content style"
                value={profile.content_style}
                field="content_style"
                editing={editing}
                onChange={updateField}
                placeholder="Educational, cinematic, storytelling..."
              />

              <ProfileField
                label="Preferred tone"
                value={profile.preferred_tone}
                field="preferred_tone"
                editing={editing}
                onChange={updateField}
                placeholder="Professional, conversational, dramatic..."
              />

              <ProfileField
                label="Posting preferences"
                value={profile.posting_preferences}
                field="posting_preferences"
                editing={editing}
                onChange={updateField}
                placeholder="Your publishing preferences"
                wide
              />

              <ProfileField
                label="AI preferences"
                value={profile.ai_preferences}
                field="ai_preferences"
                editing={editing}
                onChange={updateField}
                placeholder="How N1MOX30 should work with you"
                wide
              />
            </div>
          </div>
        </section>

        <aside className="n1-profile-side">
          <div className="n1-profile-side-card">
            <span className="n1-profile-section-kicker">
              N1MOX30 MEMORY
            </span>

            <h3>
              Your profile becomes
              <br />
              system intelligence.
            </h3>

            <p>
              N1MOX30 uses these preferences to personalize
              research, content generation, recommendations,
              workflows and automation.
            </p>

            <div className="n1-profile-memory-line">
              <span />
              Personalization active
            </div>
          </div>

          <div className="n1-profile-side-card">
            <span className="n1-profile-section-kicker">
              ACCOUNT
            </span>

            <div className="n1-profile-account-row">
              <span>Email</span>
              <strong>
                {user?.email || "Connected account"}
              </strong>
            </div>

            <div className="n1-profile-account-row">
              <span>Workspace</span>
              <strong>N1MOX30 Creator OS</strong>
            </div>

            <div className="n1-profile-account-row">
              <span>Status</span>
              <strong className="n1-profile-active">
                Active
              </strong>
            </div>
          </div>
        </aside>
      </form>
    </main>
  );
}

function ProfileField({
  label,
  value,
  field,
  editing,
  onChange,
  placeholder,
  wide = false,
}) {
  return (
    <label
      className={`n1-profile-field ${
        wide ? "n1-profile-field-wide" : ""
      }`}
    >
      <span>{label}</span>

      {editing ? (
        <textarea
          value={value || ""}
          onChange={(event) =>
            onChange(field, event.target.value)
          }
          placeholder={placeholder}
          rows={wide ? 3 : 2}
        />
      ) : (
        <div className="n1-profile-value">
          {value || (
            <span className="n1-profile-empty">
              Not configured
            </span>
          )}
        </div>
      )}
    </label>
  );
}

export default CreatorProfile;
