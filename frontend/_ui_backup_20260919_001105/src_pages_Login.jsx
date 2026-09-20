import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  AlertCircle,
  BrainCircuit,
  CheckCircle2,
  Eye,
  EyeOff,
  Lock,
  Mail,
  LogIn,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";


function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await login(
        email.trim(),
        password
      );

      navigate("/");
    } catch (error) {
      const message =
        error?.response?.data?.detail ||
        error?.message ||
        "Unable to log in. Please check your credentials.";

      setError(
        typeof message === "string"
          ? message
          : "Unable to log in. Please check your credentials."
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
            <div className="auth-logo">
              N
            </div>

            <div>
              <h1>N1MOX30</h1>

              <span>
                Creator Intelligence
              </span>
            </div>
          </div>


          <div className="auth-hero-content">

            <div className="auth-icon-large">
              <BrainCircuit size={72} />
            </div>

            <span className="welcome-label">
              AI-POWERED CREATOR INTELLIGENCE
            </span>

            <h2>
              Build smarter content.
              <br />
              Grow with intelligence.
            </h2>

            <p>
              N1MOX30 helps creators analyze performance,
              discover opportunities, understand growth,
              and build better content strategies.
            </p>

          </div>


          <div className="auth-features">

            <span>
              <CheckCircle2 size={18} />
              YouTube Analytics
            </span>

            <span>
              <CheckCircle2 size={18} />
              AI Content Studio
            </span>

            <span>
              <CheckCircle2 size={18} />
              Growth Intelligence
            </span>

          </div>

        </section>


        <section className="auth-card-wrapper">

          <div className="auth-card">

            <div className="auth-card-header">

              <span className="auth-eyebrow">
                WELCOME BACK
              </span>

              <h2>
                Sign in to N1MOX30
              </h2>

              <p>
                Continue to your creator intelligence dashboard.
              </p>

            </div>


            {error && (
              <div className="auth-error">

                <AlertCircle size={18} />

                <span>
                  {error}
                </span>

              </div>
            )}


            <form
              onSubmit={handleSubmit}
              className="auth-form"
            >

              <label>

                <span>
                  Email address
                </span>

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

                <span>
                  Password
                </span>

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
                    placeholder="Enter your password"
                    required
                    autoComplete="current-password"
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


              <button
                type="submit"
                className="auth-submit"
                disabled={loading}
              >

                <LogIn size={19} />

                {loading
                  ? "Signing in..."
                  : "Sign In"}

              </button>

            </form>


            <div className="auth-footer">

              <p>
                Don't have an account?
              </p>

              <Link to="/register">
                Create an account
              </Link>

            </div>

          </div>

        </section>

      </div>

    </div>
  );
}


export default Login;