import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  Link,
} from "react-router-dom";

import { useAuth } from "./context/AuthContext";

import DashboardLayout from "./layouts/DashboardLayout";

import Dashboard from "./pages/Dashboard";
import Assistant from "./pages/Assistant";
import Create from "./pages/Create";
import Workflows from "./pages/Workflows";
import Intelligence from "./pages/Intelligence";
import Notifications from "./pages/Notifications";
import Settings from "./pages/Settings";
import PublishingCenter from "./pages/PublishingCenter";
import DailyWorkspace from "./pages/DailyWorkspace";
import YouTube from "./pages/YouTube";
import Analytics from "./pages/Analytics";
import Growth from "./pages/Growth";
import AIStudio from "./pages/AIStudio";
import Research from "./pages/Research";
import AIHistory from "./pages/AIHistory";
import Schedules from "./pages/Schedules";
import Accounts from "./pages/Accounts";

import Login from "./pages/Login";
import Register from "./pages/Register";

import "./App.css";
import "./design-system.css";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="app-loader">Loading N1MOX30...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function LandingPage() {
  return (
    <main className="nm-landing">
      <nav className="nm-nav">
        <Link to="/" className="nm-brand">
          <span className="nm-brand-mark">N</span>
          <span>N1MOX30</span>
        </Link>

        <div className="nm-nav-links">
          <a href="#platform">Platform</a>
          <a href="#workflow">How it works</a>
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
        </div>

        <div className="nm-nav-actions">
          <Link to="/login" className="nm-login-link">
            Log in
          </Link>
          <Link to="/register" className="nm-nav-cta">
            Start creating
            <span>↗</span>
          </Link>
        </div>
      </nav>

      <section className="nm-hero">
        <div className="nm-hero-copy">
          <div className="nm-eyebrow">
            <span className="nm-eyebrow-dot" />
            THE CREATOR OPERATING SYSTEM
          </div>

          <h1>
            Turn ideas into
            <br />
            <em>content that moves.</em>
          </h1>

          <p className="nm-hero-description">
            N1MOX30 brings research, strategy, creation, analytics and
            publishing into one intelligent workspace built for modern
            creators.
          </p>

          <div className="nm-hero-actions">
            <Link to="/register" className="nm-primary-button">
              Build your first workflow
              <span>→</span>
            </Link>

            <a href="#platform" className="nm-secondary-button">
              Explore N1MOX30
            </a>
          </div>

          <div className="nm-proof">
            <div className="nm-proof-avatars">
              <span>1</span>
              <span>2</span>
              <span>3</span>
              <span>+</span>
            </div>
            <div>
              <strong>One workspace.</strong>
              <small>From first idea to published content.</small>
            </div>
          </div>
        </div>

        <div className="nm-hero-product">
          <div className="nm-window">
            <div className="nm-window-top">
              <div className="nm-window-dots">
                <i />
                <i />
                <i />
              </div>
              <span>N1MOX30 / Command Center</span>
              <span className="nm-live">
                <b />
                LIVE
              </span>
            </div>

            <div className="nm-product-body">
              <aside className="nm-product-sidebar">
                <div className="nm-mini-logo">N</div>
                <span className="nm-mini-active">⌂</span>
                <span>✦</span>
                <span>◈</span>
                <span>◌</span>
                <span>▣</span>
                <span>⚙</span>
              </aside>

              <div className="nm-product-main">
                <div className="nm-product-heading">
                  <div>
                    <small>MONDAY · CREATOR COMMAND</small>
                    <h3>Good morning, Nihaal.</h3>
                  </div>
                  <span className="nm-date">Sep 18, 2026</span>
                </div>

                <div className="nm-metric-row">
                  <div>
                    <small>CONTENT VELOCITY</small>
                    <strong>+38.4%</strong>
                    <span>↗ this month</span>
                  </div>
                  <div>
                    <small>WORKFLOWS</small>
                    <strong>12</strong>
                    <span>4 running</span>
                  </div>
                  <div>
                    <small>REACH</small>
                    <strong>2.8M</strong>
                    <span>across platforms</span>
                  </div>
                </div>

                <div className="nm-workspace-grid">
                  <div className="nm-workflow-card">
                    <div className="nm-card-label">
                      <span>ACTIVE WORKFLOW</span>
                      <b>RUNNING</b>
                    </div>

                    <h4>AI is changing content creation</h4>

                    <div className="nm-progress">
                      <span />
                    </div>

                    <div className="nm-pipeline">
                      <div className="done">
                        <b>01</b>
                        Research
                      </div>
                      <div className="done">
                        <b>02</b>
                        Strategy
                      </div>
                      <div className="done">
                        <b>03</b>
                        Script
                      </div>
                      <div className="active">
                        <b>04</b>
                        Visuals
                      </div>
                      <div>
                        <b>05</b>
                        Publish
                      </div>
                    </div>
                  </div>

                  <div className="nm-insight-card">
                    <span>AI INSIGHT</span>
                    <div className="nm-insight-line" />
                    <h4>
                      Your audience is responding to
                      <strong> practical AI workflows.</strong>
                    </h4>
                    <small>
                      Recommendation generated 8 min ago
                    </small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="nm-product-glow" />
        </div>
      </section>

      <section className="nm-platform-strip" id="platform">
        <span>BUILT AROUND YOUR ENTIRE CREATOR LOOP</span>
        <div>
          <b>Research</b>
          <i>→</i>
          <b>Strategy</b>
          <i>→</i>
          <b>Create</b>
          <i>→</i>
          <b>Optimize</b>
          <i>→</i>
          <b>Publish</b>
          <i>→</i>
          <b>Learn</b>
        </div>
      </section>

      <section className="nm-section nm-story" id="workflow">
        <div className="nm-section-intro">
          <span className="nm-section-number">01 / WORKFLOW</span>
          <h2>
            Your entire content operation,
            <br />
            <em>connected.</em>
          </h2>
          <p>
            Stop jumping between disconnected tools. N1MOX30 turns the
            complete creator workflow into one continuous system.
          </p>
        </div>

        <div className="nm-flow">
          <div className="nm-flow-item">
            <span>01</span>
            <div className="nm-flow-icon">⌁</div>
            <h3>Discover</h3>
            <p>Research trends, audiences and opportunities.</p>
          </div>
          <div className="nm-flow-line" />
          <div className="nm-flow-item">
            <span>02</span>
            <div className="nm-flow-icon">✦</div>
            <h3>Think</h3>
            <p>Turn signals into strategies and strong ideas.</p>
          </div>
          <div className="nm-flow-line" />
          <div className="nm-flow-item">
            <span>03</span>
            <div className="nm-flow-icon">◈</div>
            <h3>Create</h3>
            <p>Generate scripts, voice, visuals and assets.</p>
          </div>
          <div className="nm-flow-line" />
          <div className="nm-flow-item">
            <span>04</span>
            <div className="nm-flow-icon">↗</div>
            <h3>Distribute</h3>
            <p>Schedule and publish across your channels.</p>
          </div>
        </div>
      </section>

      <section className="nm-section nm-features" id="features">
        <div className="nm-feature-heading">
          <span className="nm-section-number">02 / PLATFORM</span>
          <h2>
            Less tool switching.
            <br />
            <em>More creating.</em>
          </h2>
        </div>

        <div className="nm-feature-grid">
          <article className="nm-feature feature-wide">
            <div className="nm-feature-copy">
              <span>CREATOR INTELLIGENCE</span>
              <h3>Know what to create before you create it.</h3>
              <p>
                Combine research, trends, audience signals and performance
                data to find the next opportunity.
              </p>
            </div>
            <div className="nm-feature-visual nm-research-visual">
              <div className="nm-signal signal-one">
                <b>AI TOOLS</b>
                <span>↑ 84%</span>
              </div>
              <div className="nm-signal signal-two">
                <b>CREATOR WORKFLOWS</b>
                <span>↑ 67%</span>
              </div>
              <div className="nm-signal signal-three">
                <b>FACeless VIDEO</b>
                <span>↑ 52%</span>
              </div>
            </div>
          </article>

          <article className="nm-feature">
            <span>AI STUDIO</span>
            <h3>From prompt to production.</h3>
            <p>
              Generate the building blocks of a finished piece without
              losing creative control.
            </p>
            <div className="nm-code-preview">
              <small>N1MOX30 / GENERATION</small>
              <div>
                <span>idea</span> → <b>strategy</b> → <b>script</b>
              </div>
              <div>
                <span>voice</span> → <b>visuals</b> → <b>video</b>
              </div>
              <div>
                <span>metadata</span> → <b>publish</b>
              </div>
            </div>
          </article>

          <article className="nm-feature">
            <span>AUTOMATION</span>
            <h3>Build once. Let the system run.</h3>
            <p>
              Connect repeatable workflows and let N1MOX30 handle the
              operational work.
            </p>
            <div className="nm-automation-lines">
              <span>● Research</span>
              <span>● Script</span>
              <span>● Voice</span>
              <span>● Video</span>
              <span>● Publish</span>
            </div>
          </article>
        </div>
      </section>

      <section className="nm-section nm-quote-section">
        <div className="nm-quote-mark">“</div>
        <blockquote>
          The best creator workflow is the one that disappears behind
          <em> your ideas.</em>
        </blockquote>
        <span>N1MOX30 / CREATOR OPERATING SYSTEM</span>
      </section>

      <section className="nm-section nm-pricing" id="pricing">
        <div>
          <span className="nm-section-number">03 / START</span>
          <h2>
            Build your
            <br />
            <em>content engine.</em>
          </h2>
          <p>
            Start with the core workspace. Connect your channels when you're
            ready to scale.
          </p>
        </div>

        <div className="nm-pricing-card">
          <div>
            <span>CREATOR WORKSPACE</span>
            <strong>Build your system.</strong>
          </div>
          <div className="nm-pricing-list">
            <span>✓ AI content workflows</span>
            <span>✓ Research & intelligence</span>
            <span>✓ Content generation</span>
            <span>✓ Analytics workspace</span>
            <span>✓ Publishing workflows</span>
          </div>
          <Link to="/register" className="nm-primary-button">
            Get started
            <span>→</span>
          </Link>
        </div>
      </section>

      <section className="nm-final-cta">
        <div className="nm-final-grid" />
        <span>THE NEXT GENERATION OF CREATOR SOFTWARE</span>
        <h2>
          Make the work
          <br />
          <em>flow.</em>
        </h2>
        <Link to="/register" className="nm-primary-button nm-final-button">
          Enter N1MOX30
          <span>↗</span>
        </Link>
      </section>

      <footer className="nm-footer">
        <div className="nm-footer-main">
          <div className="nm-footer-brand">
            <Link to="/" className="nm-brand">
              <span className="nm-brand-mark">N</span>
              <span>N1MOX30</span>
            </Link>
            <p>
              An intelligent operating system for creators who want to
              build, automate and grow.
            </p>
            <span className="nm-footer-status">
              <b /> SYSTEMS OPERATIONAL
            </span>
          </div>

          <div className="nm-footer-column">
            <span>PRODUCT</span>
            <a href="#platform">Platform</a>
            <a href="#workflow">Workflows</a>
            <a href="#features">AI Studio</a>
            <a href="#pricing">Pricing</a>
          </div>

          <div className="nm-footer-column">
            <span>COMPANY</span>
            <a href="#platform">About</a>
            <a href="#features">Technology</a>
            <a href="#workflow">Changelog</a>
            <a href="#pricing">Contact</a>
          </div>

          <div className="nm-footer-column">
            <span>RESOURCES</span>
            <a href="#workflow">Documentation</a>
            <a href="#features">Creator guide</a>
            <a href="#platform">Updates</a>
            <Link to="/login">Sign in</Link>
          </div>
        </div>

        <div className="nm-footer-bottom">
          <span>© 2026 N1MOX30. All rights reserved.</span>
          <div>
            <a href="#platform">Privacy</a>
            <a href="#platform">Terms</a>
            <a href="#platform">Security</a>
          </div>
        </div>
      </footer>
    </main>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />

      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="assistant" element={<Assistant />} />
        <Route path="create" element={<Create />} />
        <Route path="workflows" element={<Workflows />} />
        <Route path="intelligence" element={<Intelligence />} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="settings" element={<Settings />} />
        <Route path="publishing" element={<PublishingCenter />} />
        <Route path="daily" element={<DailyWorkspace />} />
        <Route path="youtube" element={<YouTube />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="growth" element={<Growth />} />
        <Route path="ai-studio" element={<AIStudio />} />
        <Route path="research" element={<Research />} />
        <Route path="ai-history" element={<AIHistory />} />
        <Route path="schedules" element={<Schedules />} />
        <Route path="accounts" element={<Accounts />} />
      </Route>

      <Route
        path="/dashboard"
        element={<Navigate to="/app" replace />}
      />

      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
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
