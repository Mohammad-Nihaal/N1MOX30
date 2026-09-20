import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (isAuthenticated) navigate("/app", { replace: true });
  }, [isAuthenticated, navigate]);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email.trim(), password);
      navigate("/app", { replace: true });
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Unable to sign in. Check your credentials.");
    } finally {
      setBusy(false);
    }
  }

  return <main className="auth-page">
    <section className="auth-brand-panel">
      <Link to="/" className="landing-brand"><span className="landing-mark">N</span><span>N1MOX30</span></Link>
      <div className="auth-brand-copy"><span>CREATOR OPERATING SYSTEM</span><h1>Make the work<br /><em>move.</em></h1><p>Research. Create. Automate. Publish. Learn.</p></div>
      <div className="auth-mini-flow"><span>IDEA</span><i>→</i><span>PRODUCTION</span><i>→</i><span>PUBLISH</span></div>
    </section>
    <section className="auth-form-panel">
      <div className="auth-form-wrap">
        <Link to="/" className="auth-mobile-brand">N1MOX30</Link>
        <span className="auth-kicker">WELCOME BACK</span>
        <h2>Sign in to your workspace.</h2>
        <p className="auth-subtitle">Continue where your creator system left off.</p>
        {location.state?.message && <div className="auth-success">{location.state.message}</div>}
        {error && <div className="auth-error">{error}</div>}
        <form onSubmit={submit} className="auth-form">
          <label>Email<input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" autoComplete="email" required /></label>
          <label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Your password" autoComplete="current-password" required /></label>
          <button disabled={busy}>{busy ? "Signing in…" : "Sign in"}<span>→</span></button>
        </form>
        <p className="auth-switch">New to N1MOX30? <Link to="/register">Create an account</Link></p>
        <small className="auth-legal-note">By continuing, you agree to our <Link to="/terms">Terms</Link> and <Link to="/privacy">Privacy Policy</Link>.</small>
      </div>
    </section>
  </main>;
}
