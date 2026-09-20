$ErrorActionPreference = "Stop"

$root = (Get-Location).Path
$src = Join-Path $root "src"
$public = Join-Path $root "public"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = Join-Path $root ".n1mox30-backup-$stamp"
New-Item -ItemType Directory -Force -Path $backup | Out-Null
New-Item -ItemType Directory -Force -Path $public | Out-Null

function Backup-IfExists($path) {
  if (Test-Path $path) {
    $relative = $path.Substring($root.Length).TrimStart("\")
    $dest = Join-Path $backup $relative
    New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
    Copy-Item $path $dest -Force
  }
}

function Write-Utf8($path, $content) {
  $dir = Split-Path $path
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  [System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding($false)))
}

Backup-IfExists (Join-Path $src "App.jsx")
Backup-IfExists (Join-Path $src "index.css")
Backup-IfExists (Join-Path $root "index.html")
Backup-IfExists (Join-Path $public "robots.txt")
Backup-IfExists (Join-Path $public "sitemap.xml")
Backup-IfExists (Join-Path $public "llms.txt")

$publicPages = @'
import { useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, ArrowUpRight, Mail, ShieldCheck, LifeBuoy, UserRound, LockKeyhole } from "lucide-react";

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
    <Seo title={`${title} — N1MOX30`} description={description || `Official ${title} information for N1MOX30.`} />
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
  return shell("Privacy Policy", "LEGAL · PRIVACY", <>
    <p className="nm-public-lead">This page is the implementation-ready privacy framework for N1MOX30. Final legal text must match the deployed company, data flows, processors and countries served.</p>
    <h2>What we may process</h2><p>Account information, creator workspace content, connected-platform identifiers and tokens, generated content, usage events, diagnostics and information you voluntarily provide to support.</p>
    <h2>Why we process it</h2><p>To provide the service, authenticate users, operate creator workflows, connect supported platforms, improve reliability, protect accounts, respond to requests and meet applicable legal obligations.</p>
    <h2>Connected platforms</h2><p>When you connect a service such as YouTube, N1MOX30 processes information required to provide the requested integration. Permissions and Google/YouTube data use must be disclosed accurately for the scopes actually requested.</p>
    <h2>Your choices</h2><p>Depending on applicable law and circumstances, you may have rights concerning access, correction, deletion, portability, objection or consent withdrawal. Contact the deployed privacy channel for requests.</p>
    <h2>Retention & security</h2><p>Keep data only for as long as needed for the stated purpose or applicable legal requirements, with appropriate technical and organizational safeguards.</p>
    <h2>International users</h2><p>N1MOX30 should apply jurisdiction-aware privacy controls where required, including appropriate notices, consent mechanisms, processor disclosures and rights handling. This page is not a claim of universal legal compliance.</p>
    <div className="nm-public-callout">Last updated: September 2026 · Final policy owner and legal entity details must be verified before public launch.</div>
  </>, "N1MOX30 privacy framework covering account, creator, integration and support data.");
}

export function TermsPage() {
  return shell("Terms & Conditions", "LEGAL · TERMS", <>
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
  return shell("Cookie Policy", "LEGAL · COOKIES", <>
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
'@

$controls = @'
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowUp, HelpCircle, X } from "lucide-react";

export function ProductionControls() {
  const [cookies, setCookies] = useState(() => localStorage.getItem("n1mox30_cookie_choice") || "");
  const [top, setTop] = useState(false);

  useEffect(() => {
    const onScroll = () => setTop(window.scrollY > 700);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const choose = (value) => { localStorage.setItem("n1mox30_cookie_choice", value); setCookies(value); };

  return <>
    <a className="nm-skip" href="#main-content">Skip to content</a>
    <Link className="nm-help-float" to="/help" aria-label="Open N1MOX30 Help Center"><HelpCircle size={20}/><span>Help</span></Link>
    {top && <button className="nm-top-button" onClick={() => window.scrollTo({top:0,behavior:"smooth"})} aria-label="Back to top"><ArrowUp size={18}/></button>}
    {!cookies && <div className="nm-cookie" role="dialog" aria-label="Cookie preferences">
      <div><strong>Privacy choices</strong><p>We use essential storage to operate N1MOX30. Optional analytics should only be enabled where applicable consent is provided.</p></div>
      <div className="nm-cookie-actions"><button onClick={() => choose("necessary")}>Necessary only</button><button className="primary" onClick={() => choose("all")}>Allow optional</button><Link to="/cookies">Learn more</Link><button aria-label="Close cookie notice" onClick={() => choose("necessary")}><X size={16}/></button></div>
    </div>}
  </>;
}
'@

Write-Utf8 (Join-Path $src "pages\PublicPages.jsx") $publicPages
Write-Utf8 (Join-Path $src "components\ProductionControls.jsx") $controls

$appPath = Join-Path $src "App.jsx"
$app = Get-Content $appPath -Raw
if ($app -notmatch 'PublicPages') {
  $app = $app -replace 'import Register from "\.\/pages\/Register";', 'import Register from "./pages/Register";`r`nimport { Seo, NotFoundPage, HelpPage, ContactPage, PrivacyPage, TermsPage, CookiePage, DataRequestPage, AboutPage } from "./pages/PublicPages";`r`nimport { ProductionControls } from "./components/ProductionControls";'
}
if ($app -notmatch 'ProductionControls') {
  $app = $app -replace '<BrowserRouter>', '<BrowserRouter>`r`n      <ProductionControls />'
}
if ($app -notmatch 'path="/help"') {
  $needle = '<Route path="/login" element={<Login />} />'
  $replacement = $needle + '`r`n      <Route path="/help" element={<HelpPage />} />`r`n      <Route path="/contact" element={<ContactPage />} />`r`n      <Route path="/about" element={<AboutPage />} />`r`n      <Route path="/privacy" element={<PrivacyPage />} />`r`n      <Route path="/terms" element={<TermsPage />} />`r`n      <Route path="/cookies" element={<CookiePage />} />`r`n      <Route path="/data-request" element={<DataRequestPage />} />'
  $app = $app.Replace($needle, $replacement)
}
$app = $app -replace '<Route path="\*" element=\{<Navigate to="/" replace />\} />', '<Route path="*" element={<NotFoundPage />} />'
$app = $app -replace '<main className="nm-landing">', '<main id="main-content" className="nm-landing">'
Write-Utf8 $appPath $app

$indexPath = Join-Path $root "index.html"
$index = Get-Content $indexPath -Raw
$index = [regex]::Replace($index, '<title>.*?</title>', '<title>N1MOX30 — AI Creator Operating System</title>', 'Singleline')
if ($index -notmatch 'meta name="description"') {
  $index = $index -replace '</title>', '</title>`r`n    <meta name="description" content="N1MOX30 is an AI creator operating system for research, strategy, content creation, automation, analytics and publishing." />`r`n    <meta name="theme-color" content="#0b0d10" />`r`n    <meta name="robots" content="index,follow" />`r`n    <meta property="og:title" content="N1MOX30 — AI Creator Operating System" />`r`n    <meta property="og:description" content="Research, create, automate, analyze and publish from one creator workspace." />`r`n    <meta property="og:type" content="website" />'
}
if ($index -notmatch 'link rel="canonical"') { $index = $index -replace '</head>', '    <link rel="canonical" href="/" />`r`n  </head>' }
Write-Utf8 $indexPath $index

Write-Utf8 (Join-Path $public "robots.txt") @"
User-agent: *
Allow: /
Disallow: /app
Disallow: /login
Disallow: /register
Sitemap: /sitemap.xml
"@

Write-Utf8 (Join-Path $public "sitemap.xml") @"
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>/</loc></url>
  <url><loc>/about</loc></url>
  <url><loc>/help</loc></url>
  <url><loc>/contact</loc></url>
  <url><loc>/privacy</loc></url>
  <url><loc>/terms</loc></url>
  <url><loc>/cookies</loc></url>
  <url><loc>/data-request</loc></url>
</urlset>
"@

Write-Utf8 (Join-Path $public "llms.txt") @"
# N1MOX30
N1MOX30 is an AI-powered creator operating system for research, strategy, content creation, automation, analytics and publishing.

## Public resources
- /: Product overview
- /about: Company and founder
- /help: Creator help center
- /contact: Support and business contact
- /privacy: Privacy information
- /terms: Terms and conditions
- /cookies: Cookie information
- /data-request: Data rights requests

## Important
Do not infer unpublished team members, contact addresses, pricing, legal entity details or product capabilities.
"@

$cssPath = Join-Path $src "index.css"
Backup-IfExists $cssPath
$css = @'
/* N1MOX30 production foundation */
html { scroll-behavior: smooth; }
:focus-visible { outline: 2px solid #9bbcff; outline-offset: 3px; }
button, a, input, textarea, select { font: inherit; }
.nm-skip { position:fixed; left:16px; top:-80px; z-index:10000; padding:10px 14px; border-radius:10px; background:#fff; color:#080a0d; font-weight:700; transition:top .2s ease; }
.nm-skip:focus { top:16px; }
.nm-help-float,.nm-top-button { position:fixed; z-index:900; border:1px solid rgba(255,255,255,.12); background:rgba(14,16,20,.92); color:#fff; box-shadow:0 12px 40px rgba(0,0,0,.24); backdrop-filter:blur(16px); }
.nm-help-float { right:22px; bottom:22px; display:flex; align-items:center; gap:8px; padding:11px 14px; border-radius:999px; text-decoration:none; }
.nm-top-button { right:22px; bottom:76px; width:42px; height:42px; border-radius:50%; display:grid; place-items:center; cursor:pointer; }
.nm-cookie { position:fixed; z-index:9500; left:20px; right:20px; bottom:20px; max-width:1050px; margin:auto; display:flex; justify-content:space-between; gap:24px; padding:18px 20px; border:1px solid rgba(255,255,255,.13); border-radius:18px; background:rgba(15,17,21,.96); color:#fff; box-shadow:0 24px 80px rgba(0,0,0,.4); }
.nm-cookie p { margin:5px 0 0; max-width:700px; color:#b7bcc7; line-height:1.5; font-size:14px; }
.nm-cookie-actions { display:flex; align-items:center; gap:9px; flex-wrap:wrap; }
.nm-cookie button,.nm-cookie a { border:1px solid rgba(255,255,255,.15); background:transparent; color:#fff; padding:9px 12px; border-radius:10px; text-decoration:none; cursor:pointer; }
.nm-cookie button.primary { background:#fff; color:#080a0d; border-color:#fff; font-weight:700; }
.nm-public-shell { min-height:100vh; background:#090b0e; color:#f4f6f8; padding:24px; }
.nm-public-top { max-width:1160px; margin:auto; display:flex; justify-content:space-between; align-items:center; }
.nm-public-back,.nm-public-app { color:#fff; text-decoration:none; display:inline-flex; align-items:center; gap:8px; }
.nm-public-app { opacity:.75; }
.nm-public-content { max-width:900px; margin:90px auto 120px; }
.nm-public-eyebrow { letter-spacing:.12em; text-transform:uppercase; font-size:12px; color:#9aa3b2; font-weight:700; margin-bottom:14px; }
.nm-public-content h1 { font-size:clamp(42px,7vw,76px); line-height:.98; letter-spacing:-.055em; margin:0 0 24px; }
.nm-public-content h2 { font-size:22px; margin:42px 0 10px; letter-spacing:-.02em; }
.nm-public-content p,.nm-public-content li { color:#aeb6c3; line-height:1.7; font-size:17px; }
.nm-public-lead { font-size:21px !important; max-width:760px; }
.nm-public-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; margin-top:38px; }
.nm-public-card { border:1px solid rgba(255,255,255,.1); border-radius:18px; padding:24px; background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.018)); }
.nm-public-card h2 { margin-top:12px; }
.nm-public-card svg { opacity:.7; }
.nm-public-card a { color:#fff; text-decoration:none; display:inline-flex; align-items:center; gap:5px; margin-top:8px; }
.nm-public-actions { display:flex; gap:14px; align-items:center; margin-top:28px; }
.nm-public-button { display:inline-flex; align-items:center; justify-content:center; padding:12px 16px; border-radius:11px; background:#fff; color:#080a0d; text-decoration:none; font-weight:750; }
.nm-public-link { color:#fff; text-decoration:none; }
.nm-public-callout { margin-top:38px; padding:18px 20px; border-left:2px solid #8daeff; background:rgba(141,174,255,.06); color:#c2c9d5; line-height:1.6; }
@media (max-width:700px) {
  .nm-public-shell { padding:18px; }
  .nm-public-content { margin:65px auto 90px; }
  .nm-public-grid { grid-template-columns:1fr; }
  .nm-cookie { left:10px; right:10px; bottom:10px; flex-direction:column; gap:12px; }
  .nm-help-float { right:14px; bottom:14px; }
  .nm-top-button { right:14px; bottom:68px; }
}
@media (prefers-reduced-motion:reduce) { html { scroll-behavior:auto; } *,*::before,*::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; } }
'@
Write-Utf8 $cssPath ($css + "`r`n")

Write-Host "`nN1MOX30 bulk production foundation installed." -ForegroundColor Green
Write-Host "Backup: $backup" -ForegroundColor Cyan
Write-Host "Added: SEO/meta, robots, sitemap, llms, 404, Help, Contact, About/Founder, Privacy, Terms, Cookies, Data Request, cookie UX, skip link, back-to-top, floating Help, accessibility base." -ForegroundColor Yellow

# ================================================================
# N1MOX30 RAPID PRODUCTION EXTENSION
# Security + Billing architecture + Plans + hardening + asset base
# ================================================================

$projectRoot = Split-Path $root -Parent
$backendRoot = Join-Path $projectRoot "backend"
$backendApp = Join-Path $backendRoot "app"

function Add-IfMissing($path, $needle, $content) {
  if (Test-Path $path) {
    $current = Get-Content $path -Raw
    if ($current -notmatch [regex]::Escape($needle)) {
      Write-Utf8 $path ($current + "`r`n" + $content + "`r`n")
    }
  }
}

# ---------- 1) Fix known Lucide export incompatibilities ----------
$lucideFiles = @(
  (Join-Path $src "pages\Dashboard.jsx"),
  (Join-Path $src "pages\Accounts.jsx"),
  (Join-Path $src "pages\PublishingCenter.jsx"),
  (Join-Path $src "components\Sidebar.jsx")
)
foreach ($f in $lucideFiles) {
  if (Test-Path $f) {
    $c = Get-Content $f -Raw
    $c = $c -replace '\bYoutube\b', 'Video'
    $c = $c -replace '\bInstagram\b', 'Camera'
    Write-Utf8 $f $c
  }
}

# ---------- 2) Pricing configuration ----------
New-Item -ItemType Directory -Force -Path (Join-Path $src "config") | Out-Null
Write-Utf8 (Join-Path $src "config\plans.js") @'
export const PLANS = [
  {
    id: "creator",
    name: "Creator",
    monthlyUsd: 19,
    description: "For creators building a consistent publishing system.",
    features: ["AI content studio", "Production workflow", "Scheduling", "Creator analytics"],
  },
  {
    id: "pro",
    name: "Pro",
    monthlyUsd: 49,
    description: "For serious creators running an automated content operation.",
    features: ["Everything in Creator", "Automation workflows", "Advanced insights", "Priority processing"],
    popular: true,
  },
  {
    id: "studio",
    name: "Studio",
    monthlyUsd: 129,
    description: "For teams and high-volume creator operations.",
    features: ["Everything in Pro", "Team workflows", "Higher limits", "Advanced operations"],
  },
];

export const DEFAULT_CURRENCY = "USD";

export function formatPlanPrice(plan, currency = "USD", rate = 1) {
  const amount = currency === "USD" ? plan.monthlyUsd : plan.monthlyUsd * rate;
  return new Intl.NumberFormat(undefined, { style: "currency", currency }).format(amount);
}
'@

Write-Utf8 (Join-Path $src "pages\Pricing.jsx") @'
import { useState } from "react";
import { Link } from "react-router-dom";
import { Check, ChevronDown, ShieldCheck } from "lucide-react";
import { PLANS, formatPlanPrice } from "../config/plans";

const CURRENCIES = [
  ["USD", "US Dollar", 1],
  ["INR", "Indian Rupee", 83.5],
  ["EUR", "Euro", 0.92],
  ["GBP", "British Pound", 0.78],
  ["AUD", "Australian Dollar", 1.53],
  ["CAD", "Canadian Dollar", 1.36],
  ["SGD", "Singapore Dollar", 1.29],
  ["AED", "UAE Dirham", 3.67],
];

export default function Pricing() {
  const [currency, setCurrency] = useState("USD");
  const rate = CURRENCIES.find(([code]) => code === currency)?.[2] || 1;

  return (
    <main className="nm-pricing-page">
      <div className="nm-pricing-top">
        <Link to="/" className="nm-pricing-back">← N1MOX30</Link>
        <label className="nm-currency">
          <span>Currency</span>
          <select value={currency} onChange={(e) => setCurrency(e.target.value)} aria-label="Pricing currency">
            {CURRENCIES.map(([code, name]) => <option value={code} key={code}>{code} — {name}</option>)}
          </select>
        </label>
      </div>

      <header className="nm-pricing-hero">
        <span className="nm-public-eyebrow">PLANS</span>
        <h1>Choose the operating system for your creator workflow.</h1>
        <p>USD is the reference price. Local-currency checkout and payment-method availability are determined by the configured payment provider and country.</p>
      </header>

      <section className="nm-plan-grid" aria-label="N1MOX30 plans">
        {PLANS.map((plan) => (
          <article className={`nm-plan-card ${plan.popular ? "featured" : ""}`} key={plan.id}>
            {plan.popular && <div className="nm-plan-badge">Most selected</div>}
            <h2>{plan.name}</h2>
            <p>{plan.description}</p>
            <div className="nm-plan-price">{formatPlanPrice(plan, currency, rate)}<small>/month</small></div>
            <ul>{plan.features.map((feature) => <li key={feature}><Check size={16} />{feature}</li>)}</ul>
            <Link to="/register" className="nm-plan-cta">Start with {plan.name}</Link>
          </article>
        ))}
      </section>

      <div className="nm-billing-trust">
        <ShieldCheck size={18} />
        <span>Checkout is designed around provider-hosted payment flows, webhook verification and server-side subscription state.</span>
      </div>

      <p className="nm-pricing-note"><ChevronDown size={15}/> Country-specific taxes, payment methods, currency conversion and availability are applied by the final billing configuration.</p>
    </main>
  );
}
'@

# Add pricing route if possible.
if (Test-Path $appPath) {
  $app = Get-Content $appPath -Raw
  if ($app -notmatch 'pages/Pricing|pages\\Pricing') {
    $app = $app -replace 'import Register from "\.\/pages\/Register";', 'import Register from "./pages/Register";`r`nimport Pricing from "./pages/Pricing";'
  }
  if ($app -notmatch 'path="/pricing"') {
    $app = $app -replace '<Route path="/login" element={<Login />} />', '<Route path="/login" element={<Login />} />`r`n      <Route path="/pricing" element={<Pricing />} />'
  }
  Write-Utf8 $appPath $app
}

# Pricing page styling.
Add-IfMissing (Join-Path $src "index.css") "nm-plan-grid" @'
.nm-pricing-page{min-height:100vh;background:#090b0e;color:#f4f6f8;padding:24px}
.nm-pricing-top{max-width:1180px;margin:auto;display:flex;justify-content:space-between;align-items:center}
.nm-pricing-back{color:#fff;text-decoration:none}
.nm-currency{display:flex;align-items:center;gap:10px;color:#aeb6c3;font-size:13px}
.nm-currency select{background:#12151a;color:#fff;border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:9px 11px}
.nm-pricing-hero{max-width:900px;margin:100px auto 45px}
.nm-pricing-hero h1{font-size:clamp(42px,7vw,76px);line-height:.98;letter-spacing:-.055em;margin:12px 0 22px}
.nm-pricing-hero p{color:#aeb6c3;max-width:760px;line-height:1.65;font-size:18px}
.nm-plan-grid{max-width:1180px;margin:auto;display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.nm-plan-card{position:relative;border:1px solid rgba(255,255,255,.1);border-radius:22px;padding:28px;background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.018));transition:transform .25s ease,border-color .25s ease}
.nm-plan-card:hover{transform:translateY(-5px);border-color:rgba(255,255,255,.24)}
.nm-plan-card.featured{border-color:rgba(155,188,255,.55)}
.nm-plan-badge{position:absolute;right:18px;top:18px;font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#bcd0ff}
.nm-plan-card h2{font-size:25px;margin:0 0 10px}
.nm-plan-card p{min-height:52px;color:#9ea7b5;line-height:1.5}
.nm-plan-price{font-size:40px;font-weight:800;letter-spacing:-.04em;margin:25px 0}
.nm-plan-price small{font-size:13px;color:#8f98a7;font-weight:500;margin-left:5px}
.nm-plan-card ul{list-style:none;padding:0;margin:0 0 25px;display:grid;gap:11px}
.nm-plan-card li{display:flex;align-items:center;gap:9px;color:#c1c8d2;font-size:14px}
.nm-plan-cta{display:flex;justify-content:center;padding:12px;border-radius:11px;background:#fff;color:#080a0d;text-decoration:none;font-weight:750}
.nm-billing-trust{max-width:1180px;margin:22px auto 0;display:flex;gap:9px;align-items:center;color:#9ca6b5;font-size:13px}
.nm-pricing-note{max-width:1180px;margin:20px auto 80px;color:#747e8d;font-size:13px;display:flex;align-items:center;gap:5px}
@media(max-width:900px){.nm-plan-grid{grid-template-columns:1fr}.nm-pricing-hero{margin-top:70px}.nm-plan-card p{min-height:0}}
@media(prefers-reduced-motion:reduce){.nm-plan-card{transition:none}.nm-plan-card:hover{transform:none}}
'@

# ---------- 3) Public visual assets ----------
Write-Utf8 (Join-Path $public "favicon.svg") @'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="16" fill="#0b0d10"/>
<path d="M17 46V18h8l14 17V18h8v28h-8L25 29v17z" fill="#f4f6f8"/>
</svg>
'@
Write-Utf8 (Join-Path $public "og-image.svg") @'
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<rect width="1200" height="630" fill="#090b0e"/>
<circle cx="1040" cy="90" r="220" fill="#172235"/>
<text x="80" y="255" fill="#f4f6f8" font-family="Arial, sans-serif" font-size="92" font-weight="800">N1MOX30</text>
<text x="84" y="325" fill="#aeb6c3" font-family="Arial, sans-serif" font-size="32">AI Creator Operating System</text>
<text x="84" y="385" fill="#788291" font-family="Arial, sans-serif" font-size="24">Research · Create · Automate · Analyze · Publish</text>
</svg>
'@

if (Test-Path $indexPath) {
  $index = Get-Content $indexPath -Raw
  if ($index -notmatch 'favicon.svg') { $index = $index -replace '</head>', '    <link rel="icon" href="/favicon.svg" type="image/svg+xml" />`r`n  </head>' }
  if ($index -notmatch 'og-image.svg') { $index = $index -replace '</head>', '    <meta property="og:image" content="/og-image.svg" />`r`n    <meta name="twitter:card" content="summary_large_image" />`r`n  </head>' }
  Write-Utf8 $indexPath $index
}

# ---------- 4) Backend production security middleware ----------
if (Test-Path $backendApp) {
  New-Item -ItemType Directory -Force -Path (Join-Path $backendApp "middleware") | Out-Null
  Write-Utf8 (Join-Path $backendApp "middleware\production_security.py") @'
from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class ProductionSecurityMiddleware(BaseHTTPMiddleware):
    """Baseline production protections.

    Enabled by main.py only when ENVIRONMENT=production.
    Rate limits are intentionally conservative and should move to Redis
    before horizontal scaling.
    """

    def __init__(self, app, requests_per_minute: int = 120, max_body_bytes: int = 8 * 1024 * 1024):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.max_body_bytes = max_body_bytes
        self._hits = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_body_bytes:
                    return JSONResponse({"detail": "Request body too large."}, status_code=413)
            except ValueError:
                return JSONResponse({"detail": "Invalid content length."}, status_code=400)

        host = request.client.host if request.client else "unknown"
        now = time.monotonic()
        bucket = self._hits[host]
        cutoff = now - 60
        while bucket and bucket[0] < cutoff:
            bucket.popleft()

        if len(bucket) >= self.requests_per_minute:
            return JSONResponse({"detail": "Too many requests. Try again later."}, status_code=429)

        bucket.append(now)
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = response.headers.get("Cache-Control", "no-store") if request.url.path.startswith("/auth") else response.headers.get("Cache-Control", "public, max-age=0, must-revalidate")
        return response
'@
  if (-not (Test-Path (Join-Path $backendApp "middleware\__init__.py"))) {
    Write-Utf8 (Join-Path $backendApp "middleware\__init__.py") ""
  }

  # Insert production-only middleware into main.py without changing development behavior.
  $mainPath = Join-Path $backendApp "main.py"
  if (Test-Path $mainPath) {
    $main = Get-Content $mainPath -Raw
    if ($main -notmatch 'ProductionSecurityMiddleware') {
      $main = $main -replace 'from fastapi import FastAPI', 'from fastapi import FastAPI`r`n`r`nfrom app.middleware.production_security import ProductionSecurityMiddleware'
      $needle = 'app.add_middleware(`r`n    CORSMiddleware,'
      $main = $main -replace [regex]::Escape($needle), $needle
      $anchor = 'allow_headers=["*"],`r`n)'
      $insert = $anchor + '`r`n`r`n`r`nif settings.environment.lower() == "production":`r`n    app.add_middleware(ProductionSecurityMiddleware)'
      if ($main.Contains($anchor)) { $main = $main.Replace($anchor, $insert) }
      Write-Utf8 $mainPath $main
    }
  }
}

# ---------- 5) Provider-agnostic billing configuration ----------
if (Test-Path $backendApp) {
  New-Item -ItemType Directory -Force -Path (Join-Path $backendApp "billing") | Out-Null
  Write-Utf8 (Join-Path $backendApp "billing\plans.py") @'
from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    monthly_usd: int
    description: str


PLANS = {
    "creator": Plan("creator", "Creator", 19, "For creators building a consistent publishing system."),
    "pro": Plan("pro", "Pro", 49, "For serious creators running an automated content operation."),
    "studio": Plan("studio", "Studio", 129, "For teams and high-volume creator operations."),
}


def public_plans():
    return [
        {
            "id": plan.id,
            "name": plan.name,
            "monthly_usd": plan.monthly_usd,
            "description": plan.description,
        }
        for plan in PLANS.values()
    ]
'@
  Write-Utf8 (Join-Path $backendApp "billing\__init__.py") ""
  Write-Utf8 (Join-Path $backendApp "billing\provider.py") @'
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CheckoutRequest:
    user_id: str
    plan_id: str
    currency: str = "USD"
    country: str | None = None


class BillingProvider:
    """Provider-neutral billing boundary.

    Implement Stripe, Paddle/MoR, or another approved provider behind this
    interface. Never trust prices, plan ids, currency, or payment status
    from the browser as authoritative values.
    """

    def create_checkout(self, request: CheckoutRequest) -> dict[str, Any]:
        raise NotImplementedError

    def verify_webhook(self, payload: bytes, signature: str | None) -> dict[str, Any]:
        raise NotImplementedError
'@

  Write-Utf8 (Join-Path $backendApp "api\billing.py") @'
from fastapi import APIRouter

from app.billing.plans import public_plans

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans")
def get_public_plans():
    return {"currency": "USD", "plans": public_plans()}


@router.get("/status")
def billing_status():
    return {
        "provider_configured": False,
        "checkout_ready": False,
        "message": "Configure a verified payment provider before accepting live payments.",
    }
'@

  $mainPath = Join-Path $backendApp "main.py"
  if (Test-Path $mainPath) {
    $main = Get-Content $mainPath -Raw
    if ($main -notmatch 'billing_router') {
      $main = $main -replace 'from app.api.automation import router as automation_router', 'from app.api.automation import router as automation_router`r`nfrom app.api.billing import router as billing_router'
      $main = $main -replace 'app.include_router(automation_router)', 'app.include_router(automation_router)`r`napp.include_router(billing_router)'
      Write-Utf8 $mainPath $main
    }
  }
}

# ---------- 6) Production environment template + security documentation ----------
Write-Utf8 (Join-Path $backendRoot ".env.production.example") @'
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/n1mox30
SECRET_KEY=REPLACE_WITH_32_PLUS_BYTE_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=https://YOUR-DOMAIN
REDIS_URL=redis://HOST:6379/0

# AI
AI_PROVIDER=openclaw
OPENCLAW_ENABLED=true
BEDROCK_ENABLED=false

# Billing - keep secrets server-side only
BILLING_PROVIDER=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
PADDLE_API_KEY=
PADDLE_WEBHOOK_SECRET=
'@

New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot "docs\production") | Out-Null
Write-Utf8 (Join-Path $projectRoot "docs\production\SECURITY_AND_BILLING.md") @'
# N1MOX30 Production Security & Billing

## Security baseline
- Server-side validation for every request.
- Argon2/bcrypt password hashing.
- Generic login/reset errors to prevent account enumeration.
- Rate limiting and brute-force protection.
- Secure cookies/tokens in production.
- Strict CORS with the deployed frontend origin.
- CSRF protection where cookie-authenticated state-changing requests are used.
- OAuth state validation and server-side token handling.
- Webhook signature verification before changing billing state.
- Never trust client-supplied plan price, payment status or entitlement.
- Secrets only in environment/secret management, never in source.
- Audit security-sensitive actions.
- PostgreSQL + Redis before horizontal scaling.
- Backups and tested recovery.
- HTTPS/HSTS at the edge.
- Dependency and container security scanning.

## Billing
Plans:
- Creator: $19/month
- Pro: $49/month
- Studio: $129/month

USD is the reference currency. Local currency and payment methods depend on the selected payment provider, country and legal/tax configuration.

Live checkout is intentionally not enabled by this foundation until a payment provider account, business identity, webhook signing secret, refund policy and country availability are configured and verified.

## Compliance
Do not claim universal legal compliance. Configure privacy, tax, consumer, payments, KYC/KYB, AML/fraud and data-transfer requirements for the actual operating entity and countries served.
'@

# ---------- 7) Final build ----------
Write-Host "`nRapid production extension installed. Running final frontend build..." -ForegroundColor Cyan
npm run build

if ($LASTEXITCODE -ne 0) {
  throw "Frontend build failed. Fix the reported build errors before continuing."
}

Write-Host "`nN1MOX30 RAPID FOUNDATION COMPLETE" -ForegroundColor Green
Write-Host "Frontend: SEO/public pages/pricing/accessibility/assets/security UX" -ForegroundColor Yellow
Write-Host "Backend: production security middleware + billing architecture + plans endpoint" -ForegroundColor Yellow
Write-Host "Legal/compliance: implementation framework created; final legal review still required." -ForegroundColor Yellow
Write-Host "Live payment collection remains disabled until provider credentials/webhooks are configured." -ForegroundColor Yellow
