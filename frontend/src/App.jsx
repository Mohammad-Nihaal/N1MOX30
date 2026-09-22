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
    return (
      <div className="landing-loading">
        N1MOX30
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/app" replace />;
  }

  return (
    <main className="landing-page">
      <N1MOXVoiceAssistant />

      {/* =====================================================
          NAVIGATION
          ===================================================== */}

      <nav className="landing-nav">
        <Link
          to="/"
          className="landing-brand"
        >
          <span className="landing-mark">
            N
          </span>

          <span>
            N1MOX30
          </span>
        </Link>

        <div className="landing-nav-links">
          <a href="#platform">
            Platform
          </a>

          <a href="#workflow">
            Workflow
          </a>

          <a href="#features">
            Features
          </a>

          <a href="#pricing">
            Pricing
          </a>
        </div>

        <div className="landing-nav-actions">
          <Link
            to="/login"
            className="landing-login"
          >
            Log in
          </Link>

          <Link
            to="/register"
            className="landing-cta"
          >
            Start creating
          </Link>
        </div>
      </nav>


      {/* =====================================================
          HERO
          ===================================================== */}

      <section className="landing-hero">
        <div className="landing-eyebrow">
          THE CREATOR OPERATING SYSTEM
        </div>

        <h1>
          Turn an idea into a
          <br />
          <span>
            published video.
          </span>
        </h1>

        <p>
          N1MOX30 brings research, strategy, scripting,
          voice, visuals, editing, analytics and publishing
          into one intelligent creator workspace.
        </p>

        <div className="landing-hero-actions">
          <Link
            to="/register"
            className="landing-primary-btn"
          >
            Build your first workflow
            <span>ÃƒÂ¢Ã¢â‚¬ Ã¢â‚¬â„¢</span>
          </Link>

          <a
            href="#platform"
            className="landing-secondary-btn"
          >
            See how it works
          </a>
        </div>

        <div className="landing-proof">
          <span>Research</span>
          <i>Ãƒâ€šÃ‚Â·</i>
          <span>Script</span>
          <i>Ãƒâ€šÃ‚Â·</i>
          <span>Voice</span>
          <i>Ãƒâ€šÃ‚Â·</i>
          <span>Visuals</span>
          <i>Ãƒâ€šÃ‚Â·</i>
          <span>Publish</span>
        </div>
      </section>


      {/* =====================================================
          PRODUCT PREVIEW
          ===================================================== */}

      <section
        id="platform"
        className="landing-product"
      >
        <div className="product-frame">

          <div className="product-topbar">
            <span>N1MOX30</span>
            <span>Creator Command Center</span>
            <span>ÃƒÂ¢Ã¢â‚¬â€Ã‚Â Live</span>
          </div>

          <div className="product-grid">

            <aside className="product-sidebar">
              <small>
                WORKSPACE
              </small>

              <b>
                Overview
              </b>

              <span>
                AI Studio
              </span>

              <span>
                Workflows
              </span>

              <span>
                Intelligence
              </span>

              <small>
                CONTENT
              </small>

              <span>
                Create
              </span>

              <span>
                Schedules
              </span>

              <span>
                Publishing
              </span>
            </aside>

            <div className="product-main">

              <div className="product-heading">
                <div>
                  <small>
                    CREATOR OS
                  </small>

                  <h3>
                    Good morning.
                  </h3>
                </div>

                <button type="button">
                  + New workflow
                </button>
              </div>

              <div className="product-stats">

                <div>
                  <small>
                    CONTENT VELOCITY
                  </small>

                  <strong>
                    +38%
                  </strong>

                  <em>
                    vs last 30 days
                  </em>
                </div>

                <div>
                  <small>
                    WORKFLOWS
                  </small>

                  <strong>
                    24
                  </strong>

                  <em>
                    8 running today
                  </em>
                </div>

                <div>
                  <small>
                    CHANNEL HEALTH
                  </small>

                  <strong>
                    92
                  </strong>

                  <em>
                    Strong momentum
                  </em>
                </div>

              </div>

              <div className="product-workflow">

                <div className="workflow-head">
                  <span>
                    Publishing pipeline
                  </span>

                  <small>
                    Today
                  </small>
                </div>

                <div className="workflow-line">

                  <div className="workflow-node done">
                    <b>01</b>
                    <span>Research</span>
                    <small>Complete</small>
                  </div>

                  <div className="workflow-node done">
                    <b>02</b>
                    <span>Strategy</span>
                    <small>Complete</small>
                  </div>

                  <div className="workflow-node active">
                    <b>03</b>
                    <span>Production</span>
                    <small>Rendering</small>
                  </div>

                  <div className="workflow-node">
                    <b>04</b>
                    <span>Quality</span>
                    <small>Queued</small>
                  </div>

                  <div className="workflow-node">
                    <b>05</b>
                    <span>Publish</span>
                    <small>Scheduled</small>
                  </div>

                </div>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* =====================================================
          WORKFLOW
          ===================================================== */}

      <section
        id="workflow"
        className="landing-section"
      >
        <div className="section-kicker">
          ONE CONTINUOUS WORKFLOW
        </div>

        <h2>
          From signal to story
          <br />
          without the busywork.
        </h2>

        <p className="section-lead">
          Every stage connects. Every output becomes useful
          context for the next.
        </p>

        <div className="story-grid">
          {[
            [
              "01",
              "Discover",
              "Find topics, trends and audience signals worth turning into content.",
            ],
            [
              "02",
              "Develop",
              "Generate strategy, hooks, scripts, narration and visual direction.",
            ],
            [
              "03",
              "Produce",
              "Assemble assets, captions, thumbnails and metadata automatically.",
            ],
            [
              "04",
              "Publish",
              "Schedule, distribute and learn from the performance of every release.",
            ],
          ].map(([number, title, description]) => (
            <article
              className="story-card"
              key={number}
            >
              <span>
                {number}
              </span>

              <h3>
                {title}
              </h3>

              <p>
                {description}
              </p>

              <b>
                ÃƒÂ¢Ã¢â‚¬ Ã¢â‚¬â„¢
              </b>
            </article>
          ))}
        </div>
      </section>


      {/* =====================================================
          FEATURES
          ===================================================== */}

      <section
        id="features"
        className="landing-section landing-dark"
      >
        <div className="section-kicker">
          BUILT FOR SERIOUS CREATORS
        </div>

        <h2>
          One system.
          <br />
          Every moving part.
        </h2>

        <div className="feature-grid">
          {[
            [
              "AI Studio",
              "Create titles, scripts, captions and creative direction with a connected context.",
            ],
            [
              "Automation Engine",
              "Build repeatable workflows that move content from idea to production.",
            ],
            [
              "Creator Intelligence",
              "Understand performance, growth signals and what to make next.",
            ],
            [
              "Multi-platform",
              "Prepare content for YouTube and short-form destinations from one workspace.",
            ],
            [
              "Voice + Visuals",
              "Turn structured ideas into narration and production-ready visual assets.",
            ],
            [
              "Publishing Control",
              "Keep approvals, scheduling and connected accounts under your control.",
            ],
          ].map(([title, description]) => (
            <div
              className="feature-card"
              key={title}
            >
              <span>
                ÃƒÂ¢Ã…â€œÃ‚Â¦
              </span>

              <h3>
                {title}
              </h3>

              <p>
                {description}
              </p>
            </div>
          ))}
        </div>
      </section>


      {/* =====================================================
          INTEGRATIONS
          ===================================================== */}

      <section className="landing-section integrations">

        <div className="section-kicker">
          CONNECTED CREATOR STACK
        </div>

        <h2>
          Your tools.
          <br />
          One operating layer.
        </h2>

        <p className="section-lead">
          N1MOX30 is designed to sit above the platforms
          you already use, not replace your audience or ownership.
        </p>

        <div className="integration-row">
          <span>YouTube</span>
          <span>Instagram</span>
          <span>TikTok</span>
          <span>X</span>
          <span>OpenClaw</span>
          <span>OmniRoute</span>
        </div>
      </section>


      {/* =====================================================
          PRICING
          ===================================================== */}

      <section
        id="pricing"
        className="landing-pricing"
      >
        <div className="section-kicker">
          SIMPLE START
        </div>

        <h2>
          Build first.
          <br />
          Scale when ready.
        </h2>

        <div className="price-card">

          <div>
            <small>
              CREATOR WORKSPACE
            </small>

            <h3>
              Start with the core OS
            </h3>

            <p>
              Explore the complete workflow before committing
              to a larger production setup.
            </p>
          </div>

          <Link to="/register">
            Create account ÃƒÂ¢Ã¢â‚¬ Ã¢â‚¬â„¢
          </Link>
        </div>
      </section>


      {/* =====================================================
          FINAL CTA
          ===================================================== */}

      <section className="landing-final">

        <div className="section-kicker">
          YOUR NEXT VIDEO STARTS HERE
        </div>

        <h2>
          Stop managing
          <br />
          the process.{" "}
          <span>
            Run it.
          </span>
        </h2>

        <Link
          to="/register"
          className="landing-primary-btn"
        >
          Enter N1MOX30
          <span>ÃƒÂ¢Ã¢â‚¬ Ã¢â‚¬â„¢</span>
        </Link>
      </section>


      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="landing-footer">

        <div className="footer-main">

          <div>

            <Link
              to="/"
              className="landing-brand"
            >
              <span className="landing-mark">
                N
              </span>

              <span>
                N1MOX30
              </span>
            </Link>

            <p>
              Creator intelligence. Automated production.
              <br />
              One operating system for modern creators.
            </p>

          </div>

          <div className="footer-columns">

            <div>
              <b>Product</b>
              <a href="#platform">Platform</a>
              <a href="#workflow">Workflow</a>
              <a href="#features">Features</a>
            </div>

            <div>
              <b>Company</b>
              <a href="#pricing">Pricing</a>
              <Link to="/about">About</Link>
              <Link to="/contact">Contact</Link>
            </div>

            <div>
              <b>Legal</b>
              <Link to="/terms">
                Terms
              </Link>

              <Link to="/privacy">
                Privacy
              </Link>

              <Link to="/cookies">
                Cookies
              </Link>
            </div>

          </div>
        </div>

        <div className="footer-bottom">
          <span>
            Ãƒâ€šÃ‚Â© 2026 N1MOX30. All rights reserved.
          </span>

          <span>
            Built for creators who ship.
          </span>
        </div>
      </footer>
    </main>
  );
}


/* =========================================================
   APPLICATION ROUTES
   ========================================================= */

function AppRoutes() {
  return (
    <Routes>
        <Route path="/research" element={<Research />} />

      {/* =====================================================
          PUBLIC
          ===================================================== */}

      <Route
        path="/"
        element={<HomeRoute />}
      />

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/register"
        element={<Register />}
      />

      <Route
        path="/pricing"
        element={<Pricing />}
      />

      <Route
        path="/help"
        element={<HelpPage />}
      />

      <Route
        path="/contact"
        element={<ContactPage />}
      />

      <Route
        path="/about"
        element={<AboutPage />}
      />

      <Route
        path="/privacy"
        element={<PrivacyPage />}
      />

      <Route
        path="/terms"
        element={<TermsPage />}
      />

      <Route
        path="/cookies"
        element={<CookiePage />}
      />

      <Route
        path="/data-request"
        element={<DataRequestPage />}
      />


      {/* =====================================================
          PROTECTED APPLICATION
          ===================================================== */}

      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<Dashboard />}
        />

        <Route
          path="assistant"
          element={<Assistant />}
        />

        <Route
          path="create"
          element={<Create />}
        />

        <Route
          path="workflows"
          element={<Workflows />}
        />

        <Route
          path="intelligence"
          element={<Intelligence />}
        />

        <Route
          path="notifications"
          element={<Notifications />}
        />

        <Route
          path="settings"
          element={<Settings />}
        />

        <Route
          path="publishing"
          element={<PublishingCenter />}
        />

        <Route
          path="daily"
          element={<DailyWorkspace />}
        />

        <Route
          path="youtube"
          element={<YouTube />}
        />

        <Route
          path="analytics"
          element={<Analytics />}
        />

        <Route
          path="growth"
          element={<Growth />}
        />

        <Route
          path="ai-studio"
          element={<AIStudio />}
        />

        <Route
          path="research"
          element={<Research />}
        />

        <Route
          path="ai-history"
          element={<AIHistory />}
        />

        <Route
          path="schedules"
          element={<Schedules />}
        />

        <Route
          path="accounts"
          element={<Accounts />}
        />

        {/* =================================================
            CREATOR PROFILE
            ================================================= */}

        <Route
          path="profile"
          element={<CreatorProfile />}
        />
      </Route>


      {/* =====================================================
          LEGACY REDIRECT
          ===================================================== */}

      <Route
        path="/dashboard"
        element={<Dashboard />}
      />


      {/* =====================================================
          404
          ===================================================== */}

      <Route
        path="*"
        element={<NotFoundPage />}
      />

    <Route path="/creator-os" element={<CreatorOSLive />} />
        </Routes>
  );
}


/* =========================================================
   ROOT APP
   ========================================================= */

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}



