import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/app", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);

    try {
      await login(email.trim(), password);
      navigate("/app", { replace: true });
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to sign in. Check your credentials."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="nm-login-page">
      <div className="nm-login-grid" aria-hidden="true" />
      <div className="nm-login-noise" aria-hidden="true" />

      {/* LEFT — N1MOX SYSTEM */}
      <section className="nm-login-showcase">
        <Link to="/" className="nm-login-brand">
          <span className="nm-login-brand-mark">N</span>

          <span className="nm-login-brand-name">
            N1MOX30
          </span>

          <span className="nm-login-brand-divider" />

          <span className="nm-login-brand-type">
            CREATOR OS
          </span>
        </Link>

        <div className="nm-login-showcase-content">
          <div className="nm-login-eyebrow">
            <span className="nm-live-dot" />
            INTELLIGENCE / CREATION / AUTOMATION
          </div>

          <h1>
            Your ideas
            <br />
            <span>have a system.</span>
          </h1>

          <p className="nm-login-description">
            Research what matters. Build what works.
            Automate the repetitive. Publish with intent.
          </p>

          {/* AI CORE */}
          <div className="nm-login-core">
            <div className="nm-core-ring nm-core-ring-one" />
            <div className="nm-core-ring nm-core-ring-two" />
            <div className="nm-core-ring nm-core-ring-three" />

            <div className="nm-core-orbit nm-orbit-one">
              <span />
            </div>

            <div className="nm-core-orbit nm-orbit-two">
              <span />
            </div>

            <div className="nm-core-center">
              <span className="nm-core-n">N</span>
              <span className="nm-core-status">AI</span>
            </div>

            <div className="nm-core-label nm-core-label-top">
              <span>01</span>
              RESEARCH
            </div>

            <div className="nm-core-label nm-core-label-right">
              <span>02</span>
              CREATE
            </div>

            <div className="nm-core-label nm-core-label-bottom">
              <span>03</span>
              AUTOMATE
            </div>

            <div className="nm-core-label nm-core-label-left">
              <span>04</span>
              PUBLISH
            </div>
          </div>

          {/* WORKFLOW */}
          <div className="nm-login-workflow">
            <div className="nm-workflow-line" />

            <div className="nm-workflow-item active">
              <span className="nm-workflow-number">01</span>
              <div>
                <strong>Research</strong>
                <small>Find the signal</small>
              </div>
            </div>

            <div className="nm-workflow-item">
              <span className="nm-workflow-number">02</span>
              <div>
                <strong>Create</strong>
                <small>Turn ideas into assets</small>
              </div>
            </div>

            <div className="nm-workflow-item">
              <span className="nm-workflow-number">03</span>
              <div>
                <strong>Automate</strong>
                <small>Let the system execute</small>
              </div>
            </div>

            <div className="nm-workflow-item">
              <span className="nm-workflow-number">04</span>
              <div>
                <strong>Publish</strong>
                <small>Ship everywhere</small>
              </div>
            </div>
          </div>
        </div>

        <div className="nm-login-showcase-footer">
          <span>N1MOX30 / 01</span>
          <span>CREATOR OPERATING SYSTEM</span>
          <span>BUILD · AUTOMATE · GROW</span>
        </div>
      </section>

      {/* RIGHT — AUTH */}
      <section className="nm-login-auth">
        <div className="nm-login-auth-top">
          <span className="nm-auth-system">
            <span className="nm-live-dot" />
            SYSTEM ONLINE
          </span>

          <Link to="/" className="nm-auth-back">
            Back to N1MOX30
            <span>↗</span>
          </Link>
        </div>

        <div className="nm-login-card">
          <div className="nm-login-card-index">
            ACCESS / 01
          </div>

          <div className="nm-login-card-heading">
            <span className="nm-login-kicker">
              WELCOME BACK
            </span>

            <h2>
              Enter your
              <br />
              <em>workspace.</em>
            </h2>

            <p>
              Continue where your creator system left off.
            </p>
          </div>

          {location.state?.message && (
            <div className="nm-login-success">
              <span>✓</span>
              {location.state.message}
            </div>
          )}

          {error && (
            <div className="nm-login-error">
              <span>!</span>
              {error}
            </div>
          )}

          <form
            onSubmit={submit}
            className="nm-login-form"
          >
            <label className="nm-field">
              <span className="nm-field-label">
                <span>01</span>
                Email
              </span>

              <input
                type="email"
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </label>

            <label className="nm-field">
              <span className="nm-field-label">
                <span>02</span>
                Password
              </span>

              <div className="nm-password-field">
                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  value={password}
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }
                  placeholder="Your password"
                  autoComplete="current-password"
                  required
                />

                <button
                  type="button"
                  className="nm-password-toggle"
                  onClick={() =>
                    setShowPassword(
                      (value) => !value
                    )
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                  aria-pressed={showPassword}
                >
                  {showPassword ? "HIDE" : "SHOW"}
                </button>
              </div>
            </label>

            <button
              type="submit"
              className="nm-login-submit"
              disabled={busy}
            >
              <span>
                {busy
                  ? "AUTHENTICATING..."
                  : "ENTER WORKSPACE"}
              </span>

              <span className="nm-submit-arrow">
                →
              </span>
            </button>
          </form>

          <div className="nm-login-meta">
            <p>
              New to N1MOX30?
              {" "}
              <Link to="/register">
                Create an account
              </Link>
            </p>

            <small>
              By continuing, you agree to our{" "}
              <Link to="/terms">Terms</Link>{" "}
              and{" "}
              <Link to="/privacy">
                Privacy Policy
              </Link>
              .
            </small>
          </div>
        </div>

        <div className="nm-auth-footer">
          <span>SECURE ACCESS</span>

          <span className="nm-footer-line" />

          <span>N1MOX30</span>

          <span className="nm-footer-line" />

          <span>2026</span>
        </div>
      </section>
    </main>
  );
}