import { useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, ArrowUpRight, Mail, ShieldCheck, LifeBuoy, UserRound, LockKeyhole, Video} from "lucide-react";

export function Seo({ title, description, canonical }) {
  useEffect(() => {
    document.title = title;
    const setMeta = (name, content) => {
      let el = document.querySelector(`meta[name="${name}"]`);
      if (!el) { el = document.createElement("meta"); el.setAttribute("name", name); document.head.appendChild(el); }
      el.setAttribute("content", content);
    };
    const setProp = (property, content) => {
      let el = document.querySelector(`meta[property="${property}"]`);
      if (!el) { el = document.createElement("meta"); el.setAttribute("property", property); document.head.appendChild(el); }
      el.setAttribute("content", content);
    };
    setMeta("description", description);
    setMeta("robots", "index,follow");
    setProp("og:title", title);
    setProp("og:description", description);
    setProp("og:type", "website");
    if (canonical) {
      let link = document.querySelector('link[rel="canonical"]');
      if (!link) { link = document.createElement("link"); link.rel = "canonical"; document.head.appendChild(link); }
      link.href = canonical;
    }
  }, [title, description, canonical]);
  return null;
}

const shell = (title, eyebrow, children, description) => (
  <main className="nm-public-shell">
    <Seo title={`${title} Ã¢â‚¬â€ N1MOX30`} description={description || `Official ${title} information for N1MOX30.`} />
    <div className="nm-public-top">
      <Link to="/" className="nm-public-back"><ArrowLeft size={16}/> N1MOX30</Link>
      <Link to="/app" className="nm-public-app">Open app <ArrowUpRight size={15}/></Link>
    </div>
    <section className="nm-public-content">
      <div className="nm-public-eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      {children}
    </section>
  </main>
);

export function NotFoundPage() {
  return shell("Page not found", "404", <>
    <p className="nm-public-lead">The page you requested doesn't exist or may have moved.</p>
    <div className="nm-public-actions"><Link className="nm-public-button" to="/">Back to N1MOX30</Link><Link className="nm-public-link" to="/help">Visit Help Center</Link></div>
  </>, "The requested N1MOX30 page could not be found.");
}

export function HelpPage() {
  return shell("Creator Help Center", "SUPPORT", <>
    <p className="nm-public-lead">Find your way through the creator workflow, from research and scripting to publishing and analytics.</p>
    <div className="nm-public-grid">
      {[
        ["Getting started","Account, workspace, AI Studio and your first workflow."],
        ["Content creation","Research, strategy, hooks, scripts, voice, visuals and video."],
        ["Publishing","Scheduling, YouTube connection, OAuth and publishing troubleshooting."],
        ["Analytics","Performance, growth, insights and content decisions."],
        ["Account & security","Login, sessions, connected accounts, privacy and deletion."],
        ["Troubleshooting","Loading, errors, integrations and production issues."]
      ].map(([a,b]) => <article className="nm-public-card" key={a}><h2>{a}</h2><p>{b}</p><Link to="/contact">Get support <ArrowUpRight size={14}/></Link></article>)}
    </div>
  </>, "N1MOX30 creator help center for product, publishing, account and troubleshooting support.");
}

export function ContactPage() {
  return shell("Contact N1MOX30", "CONTACT", <>
    <p className="nm-public-lead">For creator support, technical issues, partnerships, privacy requests or security reports, use the appropriate channel below.</p>
    <div className="nm-public-grid">
      <article className="nm-public-card"><Mail/><h2>Creator support</h2><p>Use the support channel configured for your deployment. A verified support email should be published before launch.</p><Link to="/help">Open Help Center <ArrowUpRight size={14}/></Link></article>
      <article className="nm-public-card"><ShieldCheck/><h2>Security</h2><p>Report suspected vulnerabilities privately. Do not include passwords, API keys or access tokens in a report.</p><a href="#security">Security reporting <ArrowUpRight size={14}/></a></article>
      <article className="nm-public-card"><LockKeyhole/><h2>Privacy & data</h2><p>Request access, correction, deletion or withdrawal of applicable consent through the privacy process.</p><Link to="/privacy">Privacy information <ArrowUpRight size={14}/></Link></article>
      <article className="nm-public-card"><UserRound/><h2>Founder & team</h2><p><strong>Mohammad Nihaal</strong><br/>Founder & CEO, N1MOX30</p><p>Only verified business/team contact details will be published here. No personal contact details are exposed by default.</p></article>
    </div>
    <div id="security" className="nm-public-callout"><strong>Before production:</strong> replace deployment placeholders with verified support, privacy and security email addresses and the legal business identity.</div>
  </>, "Contact N1MOX30 for creator support, business inquiries, privacy and security matters.");
}

export function PrivacyPage() {
  return shell("Privacy Policy", "LEGAL Ã‚Â· PRIVACY", <>
    <p className="nm-public-lead">This page is the implementation-ready privacy framework for N1MOX30. Final legal text must match the deployed company, data flows, processors and countries served.</p>
    <h2>What we may process</h2><p>Account information, creator workspace content, connected-platform identifiers and tokens, generated content, usage events, diagnostics and information you voluntarily provide to support.</p>
    <h2>Why we process it</h2><p>To provide the service, authenticate users, operate creator workflows, connect supported platforms, improve reliability, protect accounts, respond to requests and meet applicable legal obligations.</p>
    <h2>Connected platforms</h2><p>When you connect a service such as YouTube, N1MOX30 processes information required to provide the requested integration. Permissions and Google/YouTube data use must be disclosed accurately for the scopes actually requested.</p>
    <h2>Your choices</h2><p>Depending on applicable law and circumstances, you may have rights concerning access, correction, deletion, portability, objection or consent withdrawal. Contact the deployed privacy channel for requests.</p>
    <h2>Retention & security</h2><p>Keep data only for as long as needed for the stated purpose or applicable legal requirements, with appropriate technical and organizational safeguards.</p>
    <h2>International users</h2><p>N1MOX30 should apply jurisdiction-aware privacy controls where required, including appropriate notices, consent mechanisms, processor disclosures and rights handling. This page is not a claim of universal legal compliance.</p>
    <div className="nm-public-callout">Last updated: September 2026 Ã‚Â· Final policy owner and legal entity details must be verified before public launch.</div>
  </>, "N1MOX30 privacy framework covering account, creator, integration and support data.");
}

export function TermsPage() {
  return shell("Terms & Conditions", "LEGAL Ã‚Â· TERMS", <>
    <p className="nm-public-lead">These implementation terms establish the product framework. They must be reviewed and finalized for the operating company and markets before launch.</p>
    <h2>Use of the service</h2><p>You are responsible for your account, connected platforms, content you provide and actions taken through your workspace.</p>
    <h2>AI-generated output</h2><p>AI output can contain errors. Review generated scripts, metadata, media and publishing actions before relying on them.</p>
    <h2>Third-party platforms</h2><p>Connected services have their own terms, policies, API rules and availability. N1MOX30 does not override those requirements.</p>
    <h2>Publishing responsibility</h2><p>You remain responsible for content rights, claims, disclosures, copyright, platform policies and the destination account.</p>
    <h2>Prohibited use</h2><p>Do not use the service for unlawful activity, abuse of third-party systems, credential theft, malware, or attempts to bypass platform security or access controls.</p>
    <h2>Changes and availability</h2><p>Features, integrations and pricing may change. Operational limitations and maintenance may temporarily affect availability.</p>
    <div className="nm-public-callout">Final governing law, limitation-of-liability, dispute-resolution, billing/refund and company-identification clauses require legal review before launch.</div>
  </>, "N1MOX30 terms and conditions framework for creators and connected platform users.");
}

export function CookiePage() {
  return shell("Cookie Policy", "LEGAL Ã‚Â· COOKIES", <>
    <p className="nm-public-lead">N1MOX30 should distinguish strictly necessary storage from optional analytics, advertising and preference technologies.</p>
    <h2>Necessary</h2><p>Authentication, security, session and essential application functionality may require storage technologies.</p>
    <h2>Preferences</h2><p>Theme and other convenience preferences may be stored where enabled.</p>
    <h2>Analytics</h2><p>Optional measurement should only activate where legally required consent has been obtained.</p>
    <h2>Your controls</h2><p>Use Cookie Preferences to review or change optional categories. Browser controls may also provide additional choices.</p>
    <Link className="nm-public-button" to="/">Cookie Preferences</Link>
  </>, "N1MOX30 cookie policy and controls for necessary, preference and optional analytics technologies.");
}

export function DataRequestPage() {
  return shell("Privacy & Data Request", "DATA RIGHTS", <>
    <p className="nm-public-lead">Use this route for applicable requests concerning personal data.</p>
    <div className="nm-public-card"><h2>Request types</h2><ul><li>Access / copy of applicable personal data</li><li>Correction</li><li>Deletion</li><li>Consent withdrawal where applicable</li><li>Other rights provided by applicable law</li></ul><p>Final identity-verification and response procedures must be configured with the deployed privacy contact.</p></div>
  </>, "N1MOX30 personal data request and privacy rights information.");
}

export function AboutPage() {
  return shell("About N1MOX30", "COMPANY", <>
    <p className="nm-public-lead">N1MOX30 is being built as an AI-powered creator operating system: research, strategy, creation, automation, analytics and publishing in one workspace.</p>
    <div className="nm-public-card"><h2>Founder</h2><p><strong>Mohammad Nihaal</strong><br/>Founder & CEO</p><p>The public site will publish verified business and team information as the company structure is finalized.</p></div>
  </>, "About N1MOX30 and its creator operating system vision.");
}

