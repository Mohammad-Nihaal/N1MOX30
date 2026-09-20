import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  AlertCircle,
  BrainCircuit,
  Eye,
  EyeOff,
  Lock,
  Mail,
  User,
  UserPlus,
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
      await register(name.trim(), email.trim(), password);

      navigate("/login", {
        state: {
          message: "Account created successfully. Please sign in.",
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
    <div className="auth-page">
      <div className="auth-background" />

      <div className="auth-container">
        <section className="auth-hero">
          <div className="auth-brand">
            <div className="auth-logo">N</div>

            <div>
              <h1>N1MOX30</h1>
              <span>Creator Intelligence</span>
            </div>
          </div>

          <div className="auth-hero-content">
            <div className="auth-icon-large">
              <BrainCircuit size={72} />
            </div>

            <span className="welcome-label">
              START YOUR CREATOR JOURNEY
            </span>

            <h2>
              Turn content data
              <br />
              into better decisions.
            </h2>

            <p>
              Connect your creator platforms, understand your performance,
              and use AI-powered intelligence to improve your strategy.
            </p>
          </div>

          <div className="auth-features">
            <span>✓ Performance Analytics</span>
            <span>✓ AI Recommendations</span>
            <span>✓ Growth Tracking</span>
          </div>
        </section>

        <section className="auth-card-wrapper">
          <div className="auth-card">
            <div className="auth-card-header">
              <span className="auth-eyebrow">
                CREATE ACCOUNT
              </span>

              <h2>Join N1MOX30</h2>

              <p>
                Create your creator intelligence account.
              </p>
            </div>

            {error && (
              <div className="auth-error">
                <AlertCircle size={18} />
                <span>{error}</span>
              </div>
            )}

            <form
              onSubmit={handleSubmit}
              className="auth-form"
            >
              <label>
                <span>Full name</span>

                <div className="input-wrapper">
                  <User size={19} />

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

              <label>
                <span>Email address</span>

                <div className="input-wrapper">
                  <Mail size={19} />

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

              <label>
                <span>Password</span>

                <div className="input-wrapper">
                  <Lock size={19} />

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
                    className="password-toggle"
                    onClick={() =>
                      setShowPassword(!showPassword)
                    }
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff size={19} />
                    ) : (
                      <Eye size={19} />
                    )}
                  </button>
                </div>
              </label>

              <label>
                <span>Confirm password</span>

                <div className="input-wrapper">
                  <Lock size={19} />

                  <input
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    value={confirmPassword}
                    onChange={(event) =>
                      setConfirmPassword(event.target.value)
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
                className="auth-submit"
                disabled={loading}
              >
                <UserPlus size={19} />

                {loading
                  ? "Creating account..."
                  : "Create Account"}
              </button>
            </form>

            <div className="auth-footer">
              <p>Already have an account?</p>

              <Link to="/login">
                Sign in
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Register;