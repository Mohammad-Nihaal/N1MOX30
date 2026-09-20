import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
  User,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";

function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      await register(
        name.trim(),
        email.trim(),
        password
      );

      navigate("/login", {
        state: {
          message:
            "Account created successfully. Please sign in.",
        },
      });
    } catch (error) {
      const message =
        error?.response?.data?.detail ||
        error?.message ||
        "Unable to create your account.";

      setError(
        typeof message === "string"
          ? message
          : "Unable to create your account."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="nm-register-page">
      <div className="nm-register-grid" aria-hidden="true" />
      <div className="nm-register-noise" aria-hidden="true" />

      {/* LEFT SIDE */}
      <section className="nm-register-showcase">
        <Link
          to="/"
          className="nm-login-brand"
        >
          <span className="nm-login-brand-mark">
            N
          </span>

          <span className="nm-login-brand-name">
            N1MOX30
          </span>

          <span className="nm-login-brand-divider" />

          <span className="nm-login-brand-type">
            CREATOR OS
          </span>
        </Link>

        <div className="nm-register-content">
          <div className="nm-login-eyebrow">
            <span className="nm-live-dot" />
            INITIALIZE YOUR CREATOR SYSTEM
          </div>

          <h1>
            Build your
            <br />
            <span>operating system.</span>
          </h1>

          <p className="nm-login-description">
            One workspace for research, creation,
            automation, publishing and intelligence.
          </p>

          <div className="nm-register-visual">
            <div className="nm-register-orbit orbit-a">
              <span />
            </div>

            <div className="nm-register-orbit orbit-b">
              <span />
            </div>

            <div className="nm-register-orbit orbit-c">
              <span />
            </div>

            <div className="nm-register-core">
              <div className="nm-register-core-inner">
                <span>N</span>
                <small>30</small>
              </div>
            </div>

            <div className="nm-register-node node-one">
              <span>01</span>
              IDEA
            </div>

            <div className="nm-register-node node-two">
              <span>02</span>
              INTELLIGENCE
            </div>

            <div className="nm-register-node node-three">
              <span>03</span>
              CREATION
            </div>

            <div className="nm-register-node node-four">
              <span>04</span>
              AUTOMATION
            </div>
          </div>

          <div className="nm-register-features">
            <div>
              <span>01</span>
              <strong>Research</strong>
              <small>Find the signal.</small>
            </div>

            <div>
              <span>02</span>
              <strong>Create</strong>
              <small>Build the asset.</small>
            </div>

            <div>
              <span>03</span>
              <strong>Automate</strong>
              <small>Execute the workflow.</small>
            </div>
          </div>
        </div>

        <div className="nm-login-showcase-footer">
          <span>N1MOX30 / 02</span>
          <span>CREATOR OPERATING SYSTEM</span>
          <span>BUILD · AUTOMATE · GROW</span>
        </div>
      </section>

      {/* RIGHT SIDE */}
      <section className="nm-register-auth">
        <div className="nm-login-auth-top">
          <span className="nm-auth-system">
            <span className="nm-live-dot" />
            SYSTEM ONLINE
          </span>

          <Link
            to="/login"
            className="nm-auth-back"
          >
            Already have an account
            <span>→</span>
          </Link>
        </div>

        <div className="nm-register-card">
          <div className="nm-login-card-index">
            INITIALIZE / 02
          </div>

          <div className="nm-login-card-heading">
            <span className="nm-login-kicker">
              CREATE YOUR SYSTEM
            </span>

            <h2>
              Start building
              <br />
              <em>your workspace.</em>
            </h2>

            <p>
              Create your N1MOX30 identity and
              enter your creator operating system.
            </p>
          </div>

          {error && (
            <div className="nm-login-error">
              <span>!</span>
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="nm-register-form"
          >
            <label className="nm-field">
              <span className="nm-field-label">
                <span>01</span>
                Full name
              </span>

              <div className="nm-register-input">
                <User size={15} />

                <input
                  type="text"
                  value={name}
                  onChange={(event) =>
                    setName(event.target.value)
                  }
                  placeholder="Your name"
                  required
                  autoComplete="name"
                />
              </div>
            </label>

            <label className="nm-field">
              <span className="nm-field-label">
                <span>02</span>
                Email address
              </span>

              <div className="nm-register-input">
                <Mail size={15} />

                <input
                  type="email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  placeholder="you@example.com"
                  required
                  autoComplete="email"
                />
              </div>
            </label>

            <label className="nm-field">
              <span className="nm-field-label">
                <span>03</span>
                Password
              </span>

              <div className="nm-register-input">
                <Lock size={15} />

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  placeholder="At least 6 characters"
                  required
                  minLength={6}
                  autoComplete="new-password"
                />

                <button
                  type="button"
                  className="nm-register-eye"
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
                >
                  {showPassword ? (
                    <EyeOff size={15} />
                  ) : (
                    <Eye size={15} />
                  )}
                </button>
              </div>
            </label>

            <label className="nm-field">
              <span className="nm-field-label">
                <span>04</span>
                Confirm password
              </span>

              <div className="nm-register-input">
                <Lock size={15} />

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(
                      event.target.value
                    )
                  }
                  placeholder="Repeat your password"
                  required
                  minLength={6}
                  autoComplete="new-password"
                />
              </div>
            </label>

            <button
              type="submit"
              className="nm-login-submit"
              disabled={loading}
            >
              <span>
                {loading
                  ? "INITIALIZING..."
                  : "CREATE WORKSPACE"}
              </span>

              <span className="nm-submit-arrow">
                →
              </span>
            </button>
          </form>

          <div className="nm-register-meta">
            <p>
              Already have a N1MOX30 account?{" "}
              <Link to="/login">
                Sign in
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

export default Register;