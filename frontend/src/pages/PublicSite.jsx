import { useEffect, useState } from "react";

const NAV = [
  ["Features", "/features"],
  ["Pricing", "/pricing"],
  ["Security", "/security"],
  ["Contact", "/contact"],
];

const FOOTER = [
  ["Privacy", "/privacy"],
  ["Terms", "/terms"],
  ["Cookies", "/cookies"],
  ["Security", "/security"],
  ["Contact", "/contact"],
];

const plans = [
  {
    name: "Free",
    price: "$0",
    description: "Explore N1MOX30 with essential creator automation.",
    items: ["3 videos / month", "6 messages / month", "Core creator workspace", "Voice-ready interface"],
  },
  {
    name: "Creator",
    price: "$19",
    description: "For creators building a consistent publishing operation.",
    items: ["27 YouTube long videos / month", "12 clips / month", "999 messages / month", "999 email actions / month"],
  },
  {
    name: "Pro",
    price: "$49",
    description: "For creators running a larger content operation.",
    items: ["72 YouTube long videos / month", "39 clips / month", "1,999 messages / month", "1,999 email actions / month"],
  },
  {
    name: "Studio",
    price: "$129",
    description: "For high-volume creator operations.",
    items: ["111 YouTube long videos / month", "100 clips / month", "4,499 messages / month", "4,499 email actions / month"],
  },
];

function CookieBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    try {
      setVisible(localStorage.getItem("n1mox30_cookie_consent") !== "accepted");
    } catch {
      setVisible(true);
    }
  }, []);

  function accept() {
    try { localStorage.setItem("n1mox30_cookie_consent", "accepted"); } catch {}
    setVisible(false);
  }

  function reject() {
    try { localStorage.setItem("n1mox30_cookie_consent", "rejected"); } catch {}
    setVisible(false);
  }

  if (!visible) return null;

  return (
    <div className="n1mox-public-cookie" role="dialog" aria-label="Cookie preferences">
      <div>
        <strong>Privacy choices</strong>
        <p>
          N1MOX30 uses necessary storage to operate the site. Optional analytics
          should only be enabled after the appropriate consent.
        </p>
      </div>
      <div className="n1mox-public-cookie-actions">
        <button onClick={reject}>Reject optional</button>
        <a href="/cookies">Preferences</a>
        <button className="primary" onClick={accept}>Accept</button>
      </div>
    </div>
  );
}

function Header() {
  return (
    <header className="n1mox-public-header">
      <a className="n1mox-public-brand" href="/">N1MOX30</a>
      <nav aria-label="Public navigation">
        {NAV.map(([label, path]) => <a key={path} href={path}>{label}</a>)}
      </nav>
      <div className="n1mox-public-header-actions">
        <a href="/login">Sign in</a>
        <a className="primary" href="/register">Start free</a>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="n1mox-public-footer">
      <div>
        <strong>N1MOX30</strong>
        <p>Creator Operating System for research, production, publishing and growth.</p>
      </div>
      <div className="n1mox-public-footer-links">
        {FOOTER.map(([label, path]) => <a key={path} href={path}>{label}</a>)}
      </div>
    </footer>
  );
}

function Layout({ eyebrow, title, intro, children }) {
  return (
    <div className="n1mox-public-site">
      <Header />
      <main className="n1mox-public-main">
        <section className="n1mox-public-hero">
          <div className="n1mox-public-eyebrow">{eyebrow}</div>
          <h1>{title}</h1>
          <p>{intro}</p>
        </section>
        {children}
      </main>
      <Footer />
      <CookieBanner />
    </div>
  );
}

function Home() {
  return (
    <Layout
      eyebrow="N1MOX30 / CREATOR OPERATING SYSTEM"
      title="Make the system move."
      intro="Research, create, automate, publish and understand your creator operation from one workspace."
    >
      <section className="n1mox-public-grid">
        {[
          ["Research", "Turn ideas, trends and source material into production-ready direction."],
          ["Create", "Build scripts, visuals, videos, captions and metadata through one workflow."],
          ["Automate", "Orchestrate repeatable creator work with workflows and natural-language commands."],
          ["Publish", "Prepare, schedule and publish across connected creator platforms where their APIs allow it."],
          ["Communicate", "Bring messages and email workflows into the creator operating system."],
          ["Understand", "Track performance, usage and growth signals without fabricated dashboard numbers."],
        ].map(([title, text]) => (
          <article className="n1mox-public-card" key={title}>
            <span>{title}</span>
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </section>
      <section className="n1mox-public-cta">
        <h2>Start with a free creator workspace.</h2>
        <p>No payment is required to create a Free account.</p>
        <a className="primary" href="/register">Create free account</a>
      </section>
    </Layout>
  );
}

function Features() {
  return (
    <Layout eyebrow="N1MOX30 / FEATURES" title="One operating layer for your creator work." intro="N1MOX30 connects research, creation, automation, communication, publishing and analytics into one workspace.">
      <section className="n1mox-public-grid">
        {[
          ["Creator OS", "Natural-language workflows can coordinate multiple creator tasks through the existing orchestration layer."],
          ["AI Studio", "Generate creator-ready titles, scripts, captions, hashtags and production assets."],
          ["Video + Clips", "Move from long-form production into clip selection, formatting, captions, QC and scheduling."],
          ["Social Hub", "Connect YouTube, Instagram, TikTok and X only where their APIs authorize the requested capability."],
          ["Messages + Email", "Work with supported social messages, Gmail and Outlook workflows from the creator workspace."],
          ["Voice", "Use the N1MOX voice interface for hands-free creator commands where browser speech support and microphone permissions allow it."],
        ].map(([title, text]) => (
          <article className="n1mox-public-card" key={title}>
            <span>CAPABILITY</span>
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </section>
    </Layout>
  );
}

function Pricing() {
  return (
    <Layout eyebrow="N1MOX30 / PRICING" title="Start free. Scale when you need more capacity." intro="Transparent monthly creator capacity. Usage is enforced by account entitlement rather than by the interface alone.">
      <section className="n1mox-public-plans">
        {plans.map((plan) => (
          <article className={`n1mox-public-plan ${plan.name === "Pro" ? "featured" : ""}`} key={plan.name}>
            <span>{plan.name}</span>
            <h2>{plan.price}<small>/month</small></h2>
            <p>{plan.description}</p>
            <ul>{plan.items.map((item) => <li key={item}>{item}</li>)}</ul>
            <a className={plan.name === "Pro" ? "primary" : ""} href="/register">
              {plan.name === "Free" ? "Start free" : "Choose plan"}
            </a>
          </article>
        ))}
      </section>
    </Layout>
  );
}

function Security() {
  return (
    <Layout eyebrow="N1MOX30 / SECURITY" title="Security is part of the product." intro="Production security is designed around protected secrets, controlled access, account isolation and verified integrations.">
      <section className="n1mox-public-prose">
        <h2>Application security</h2>
        <p>Production deployments should use protected environment secrets, disabled debug mode, restricted CORS and hosts, HTTPS and secure cookie settings where applicable.</p>
        <h2>Account isolation</h2>
        <p>Creator data, connected accounts, usage and entitlements must remain scoped to the authenticated account.</p>
        <h2>Integrations</h2>
        <p>OAuth secrets and payment credentials belong on the backend. Webhooks must be verified before changing billing or entitlement state.</p>
        <h2>Usage controls</h2>
        <p>Plan limits are enforced server-side so an exhausted allowance cannot be bypassed by changing the frontend.</p>
      </section>
    </Layout>
  );
}

function Privacy() {
  return (
    <Layout eyebrow="N1MOX30 / PRIVACY" title="Privacy information." intro="This page provides the public privacy notice location for N1MOX30.">
      <section className="n1mox-public-prose">
        <h2>Information we process</h2>
        <p>Account information, creator workspace data, connected-service information and usage information may be processed to provide the service.</p>
        <h2>Connected services</h2>
        <p>When you authorize a provider, N1MOX30 processes the information required for the enabled integration and its authorized capabilities.</p>
        <h2>Your controls</h2>
        <p>Users should be able to review account settings, connected services and available privacy choices. Production legal text should be finalized with the applicable business and jurisdictional requirements before launch.</p>
      </section>
    </Layout>
  );
}

function Terms() {
  return (
    <Layout eyebrow="N1MOX30 / TERMS" title="Terms of service." intro="This page provides the public terms location for N1MOX30.">
      <section className="n1mox-public-prose">
        <h2>Service use</h2>
        <p>Use N1MOX30 only with accounts, content and integrations you are authorized to operate.</p>
        <h2>Automated actions</h2>
        <p>Publishing, messaging, email and other external actions require the permissions and provider capabilities applicable to the connected account.</p>
        <h2>Plans and limits</h2>
        <p>Each plan has defined monthly allowances. Exhausted allowances are blocked until the applicable reset or plan change.</p>
        <p className="legal-note">Final production terms should be reviewed and approved for the business jurisdiction before launch.</p>
      </section>
    </Layout>
  );
}

function Cookies() {
  return (
    <Layout eyebrow="N1MOX30 / COOKIES" title="Cookie preferences." intro="Control optional website storage and understand what is necessary for the service.">
      <section className="n1mox-public-prose">
        <h2>Necessary storage</h2>
        <p>Necessary browser storage may be used for preferences, consent state and application operation.</p>
        <h2>Optional technologies</h2>
        <p>Optional analytics or similar technologies should only activate after the appropriate consent where required.</p>
        <h2>Change your choice</h2>
        <button className="n1mox-public-cookie-reset" onClick={() => {
          try { localStorage.removeItem("n1mox30_cookie_consent"); } catch {}
          window.location.reload();
        }}>Reset cookie choice</button>
      </section>
    </Layout>
  );
}

function Contact() {
  return (
    <Layout
      eyebrow="N1MOX30 / CONTACT"
      title="Talk to N1MOX30."
      intro="For support, business enquiries, partnerships and general questions, contact the N1MOX30 team directly."
    >
      <section className="n1mox-public-contact">
        <div className="n1mox-public-card">
          <span>SUPPORT + BUSINESS</span>
          <h2>teamnimoxglobal@gmail.com</h2>
          <p>Use our main team inbox for product support, business enquiries, partnerships and general N1MOX30 questions.</p>
          <div className="n1mox-public-contact-actions">
            <a className="primary" href="mailto:teamnimoxglobal@gmail.com">Email the team</a>
          </div>
        </div>
        <div className="n1mox-public-card">
          <span>ALTERNATIVE CONTACT</span>
          <h2>spartamacrey@gmail.com</h2>
          <p>Alternative contact email for N1MOX30-related communication.</p>
          <div className="n1mox-public-contact-actions">
            <a href="mailto:spartamacrey@gmail.com">Use alternative email</a>
          </div>
        </div>
        <div className="n1mox-public-card">
          <span>OFFICIAL LINKS</span>
          <h2>Connect with N1MOX30</h2>
          <div className="n1mox-public-social-links">
            <a href="https://github.com/Mohammad-Nihaal" target="_blank" rel="noreferrer">GitHub</a>
            <a href="https://www.linkedin.com/in/mohammad-nihaal-1932ba317" target="_blank" rel="noreferrer">LinkedIn</a>
            <a href="https://www.instagram.com/n1mox30?stkn=MTlkOTBxZjMxbDljMQ==" target="_blank" rel="noreferrer">Instagram</a>
          </div>
        </div>
      </section>
    </Layout>
  );
}

export default function PublicSite() {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";
  switch (path) {
    case "/pricing": return <Pricing />;
    case "/features": return <Features />;
    case "/security": return <Security />;
    case "/privacy": return <Privacy />;
    case "/terms": return <Terms />;
    case "/cookies": return <Cookies />;
    case "/contact": return <Contact />;
    default: return <Home />;
  }
}