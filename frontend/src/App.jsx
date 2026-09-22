import N1MOXVoiceAssistant from "./components/N1MOXVoiceAssistant";
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import { useAuth } from "./context/AuthContext";
import DashboardLayout from "./layouts/DashboardLayout";

import Accounts from "./pages/Accounts";
import AIHistory from "./pages/AIHistory";
import AIStudio from "./pages/AIStudio";
import Analytics from "./pages/Analytics";
import Assistant from "./pages/Assistant";
import CreatorProfile from "./pages/CreatorProfile";
import Dashboard from "./pages/Dashboard";
import Growth from "./pages/Growth";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Pricing from "./pages/Pricing";
import Research from "./pages/Research";
import Schedules from "./pages/Schedules";
import YouTube from "./pages/YouTube";
import Create from "./pages/Create";
import Workflows from "./pages/Workflows";
import Intelligence from "./pages/Intelligence";
import Notifications from "./pages/Notifications";
import Settings from "./pages/Settings";
import BYOK from "./pages/BYOK";
import Billing from "./pages/Billing";
import PublishingCenter from "./pages/PublishingCenter";
import DailyWorkspace from "./pages/DailyWorkspace";

import {
  AboutPage,
  ContactPage,
  CookiePage,
  DataRequestPage,
  HelpPage,
  NotFoundPage,
  PrivacyPage,
  TermsPage,
} from "./pages/PublicPages";
import "./App.css";
import "./styles/auth.css";
import CreatorOSLive from "./pages/CreatorOSLive";
import "./styles/nimox30-creator-os.css";
/* =========================================================
   PROTECTED ROUTE
   ========================================================= */

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="app-loader">
        Loading N1MOX30...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}


/* =========================================================
   HOME / LANDING
   ========================================================= */

function HomeRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="landing-loading">N1MOX30</div>;
  }

  if (isAuthenticated) {
    return <Navigate to="/app" replace />;
  }

  return (
    <main className="nx30-home">
      <nav className="nx30-nav">
        <Link to="/" className="nx30-logo">
          <b>N</b>
          <span>N1MOX30</span>
        </Link>

        <div className="nx30-nav-links">
          <a href="#system">System</a>
          <a href="#workflow">Workflow</a>
          <Link to="/pricing">Pricing</Link>
        </div>

        <Link to="/login" className="nx30-login">Log in</Link>
      </nav>

      <section className="nx30-hero">
        <div className="nx30-copy">
          <p className="nx30-eyebrow">THE CREATOR OPERATING SYSTEM</p>

          <h1>
            Stop managing content.
            <br />
            <i>Start making it.</i>
          </h1>

          <p className="nx30-lead">
            Research, hooks, scripts, production, publishing and growth
            connected into one creator workflow.
          </p>

          <div className="nx30-actions">
            <Link to="/register" className="nx30-primary">
              Start creating <span>→</span>
            </Link>
            <Link to="/pricing" className="nx30-secondary">
              Explore N1MOX30
            </Link>
          </div>

          <p className="nx30-note">
            ONE IDEA IN. A COMPLETE PUBLISHING WORKFLOW OUT.
          </p>
        </div>

        <div className="nx30-scene" aria-hidden="true">
          <div className="nx30-window">
            <div className="nx30-sky" />
            <div className="nx30-cloud nx30-cloud-one" />
            <div className="nx30-cloud nx30-cloud-two" />
            <div className="nx30-window-bars" />
            <div className="nx30-leaf nx30-leaf-one" />
            <div className="nx30-leaf nx30-leaf-two" />
            <div className="nx30-leaf nx30-leaf-three" />
          </div>

          <div className="nx30-desk" />

          <div className="nx30-paper">
            <small>N1MOX / WORKFLOW</small>
            <strong>IDEA → AUDIENCE</strong>
            <span>research / create / publish</span>
          </div>

          <div className="nx30-pencil" />
          <div className="nx30-cup" />
        </div>
      </section>

      <section id="system" className="nx30-stats">
        <div>
          <strong>13</strong>
          <span>creator stages</span>
        </div>
        <div>
          <strong>01</strong>
          <span>connected workflow</span>
        </div>
        <div>
          <strong>AI</strong>
          <span>inside production</span>
        </div>
        <div>
          <strong>24/7</strong>
          <span>automation ready</span>
        </div>
      </section>

      <section id="workflow" className="nx30-bottom">
        <p>FROM FIRST THOUGHT TO FINAL POST</p>
        <h2>Your content deserves a system behind it.</h2>
        <Link to="/register">Build your workflow →</Link>
      </section>
    </main>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}




export default App;
