import { useEffect } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  ArrowUpRight,
  Mail,
  ShieldCheck,
  LockKeyhole,
  UserRound,
} from "lucide-react";

export function Seo({ title, description, canonical }) {
  useEffect(() => {
    document.title = title;

    const setMeta = (name, content) => {
      let el = document.querySelector(`meta[name="${name}"]`);

      if (!el) {
        el = document.createElement("meta");
        el.setAttribute("name", name);
        document.head.appendChild(el);
      }

      el.setAttribute("content", content);
    };

    setMeta("description", description);
    setMeta("robots", "index,follow");

    if (canonical) {
      let link = document.querySelector(
        'link[rel="canonical"]'
      );

      if (!link) {
        link = document.createElement("link");
        link.rel = "canonical";
        document.head.appendChild(link);
      }

      link.href = canonical;
    }
  }, [title, description, canonical]);

  return null;
}

function shell(title, eyebrow, children, description) {
  return (
    <main className="nm-public-shell">
      <Seo
        title={`${title} — N1MOX30`}
        description={
          description ||
          `Official ${title} information for N1MOX30.`
        }
      />

      <div className="nm-public-top">
        <Link
          to="/"
          className="nm-public-back"
        >
          <ArrowLeft size={16} />
          N1MOX30
        </Link>

        <Link
          to="/app"
          className="nm-public-app"
        >
          Open app <ArrowUpRight size={15} />
        </Link>
      </div>

      <section className="nm-public-content">
        <div className="nm-public-eyebrow">
          {eyebrow}
        </div>

        <h1>{title}</h1>

        {children}
      </section>
    </main>
  );
}

export function NotFoundPage() {
  return shell(
    "Page not found",
    "404",
    <>
      <p className="nm-public-lead">
        The page you requested doesn't exist or may have moved.
      </p>

      <div className="nm-public-actions">
        <Link
          className="nm-public-button"
          to="/"
        >
          Back to N1MOX30
        </Link>

        <Link
          className="nm-public-link"
          to="/help"
        >
          Visit Help Center
        </Link>
      </div>
    </>,
    "The requested N1MOX30 page could not be found."
  );
}

export function HelpPage() {
  return shell(
    "Creator Help Center",
    "SUPPORT",
    <>
      <p className="nm-public-lead">
        Find your way through the creator workflow, from research
        and scripting to publishing and analytics.
      </p>

      <div className="nm-public-grid">
        {[
          [
            "Getting started",
            "Account, workspace, AI Studio and your first workflow.",
          ],
          [
            "Content creation",
            "Research, strategy, hooks, scripts, voice, visuals and video.",
          ],
          [
            "Publishing",
            "Scheduling, YouTube connection, OAuth and publishing troubleshooting.",
          ],
          [
            "Analytics",
            "Performance, growth, insights and content decisions.",
          ],
          [
            "Account & security",
            "Login, sessions, connected accounts, privacy and deletion.",
          ],
          [
            "Troubleshooting",
            "Loading, errors, integrations and production issues.",
          ],
        ].map(([title, text]) => (
          <article
            className="nm-public-card"
            key={title}
          >
            <h2>{title}</h2>
            <p>{text}</p>
            <Link to="/contact">
              Get support <ArrowUpRight size={14} />
            </Link>
          </article>
        ))}
      </div>
    </>,
    "N1MOX30 creator help center for product, publishing, account and troubleshooting support."
  );
}

export function ContactPage() {
  return shell(
    "Contact N1MOX30",
    "CONTACT",
    <>
      <p className="nm-public-lead">
        N1MOX30 is currently operated from India by Mohammad
        Nihaal. Use the channel that matches your request.
      </p>

      <div className="nm-public-grid">

        <article className="nm-public-card">
          <Mail size={22} />
          <h2>Creator support</h2>
          <p>
            Product help, account problems, workflows and
            general support.
          </p>
          <a href="mailto:spartamacrey@gmail.com">
            spartamacrey@gmail.com{" "}
            <ArrowUpRight size={14} />
          </a>
        </article>

        <article className="nm-public-card">
          <ShieldCheck size={22} />
          <h2>Security & privacy</h2>
          <p>
            Security reports, privacy requests and data-rights
            questions.
          </p>
          <a href="mailto:teamnimoxglobal@gmail.com">
            teamnimoxglobal@gmail.com{" "}
            <ArrowUpRight size={14} />
          </a>
        </article>

        <article className="nm-public-card">
          <LockKeyhole size={22} />
          <h2>Billing</h2>
          <p>
            Payment, subscription and billing-related requests.
          </p>
          <a href="mailto:mohammadnihaal0707@gmail.com">
            mohammadnihaal0707@gmail.com{" "}
            <ArrowUpRight size={14} />
          </a>
        </article>

        <article className="nm-public-card">
          <UserRound size={22} />
          <h2>Operator</h2>
          <p>
            <strong>Mohammad Nihaal</strong>
            <br />
            N1MOX30 operator
            <br />
            India
          </p>
          <p>
            N1MOX30 is not being presented here as a registered
            company or legal entity.
          </p>
        </article>

      </div>

      <div className="nm-public-callout">
        For account-security reports, never send passwords,
        API keys, OAuth secrets or access tokens by email.
      </div>
    </>,
    "Contact N1MOX30 for creator support, billing, privacy and security matters."
  );
}

export function PrivacyPage() {
  return shell(
    "Privacy Policy",
    "LEGAL · PRIVACY",
    <>
      <p className="nm-public-lead">
        This policy describes the intended privacy framework for
        N1MOX30. The final deployed policy must match the actual
        data flows, processors, integrations and jurisdictions
        served.
      </p>

      <h2>1. Information we may process</h2>
      <p>
        Depending on the features you use, N1MOX30 may process
        account information, creator content, workflow data,
        analytics, connected-platform identifiers, integration
        data and technical information required to operate the
        service.
      </p>

      <h2>2. How information is used</h2>
      <p>
        Information may be used to authenticate users, execute
        workflows, generate content, provide analytics, schedule
        actions, protect accounts, maintain reliability and
        respond to support requests.
      </p>

      <h2>3. Connected services</h2>
      <p>
        When you connect a third-party platform, N1MOX30 may
        process information made available through the permissions
        you authorize. Third-party services remain subject to
        their own terms and privacy policies.
      </p>

      <h2>4. AI providers</h2>
      <p>
        Depending on configuration, prompts, content or other
        inputs may be processed by an AI provider. The provider,
        retention behavior and applicable terms should be disclosed
        according to the configuration actually deployed.
      </p>

      <h2>5. Security</h2>
      <p>
        N1MOX30 uses authentication and access-control measures
        intended to protect information. No internet service can
        guarantee absolute security.
      </p>

      <h2>6. Retention</h2>
      <p>
        Information should be retained only as long as necessary
        for the stated purpose, operational requirements and
        applicable legal obligations.
      </p>

      <h2>7. Your rights</h2>
      <p>
        Depending on applicable law, users may have rights such
        as access, correction, deletion, portability, objection or
        withdrawal of consent.
      </p>

      <h2>8. International users</h2>
      <p>
        N1MOX30 may serve users in multiple jurisdictions. Privacy
        notices, consent mechanisms, rights procedures, processor
        disclosures and retention practices must be adapted where
        local law requires it.
      </p>

      <div className="nm-public-callout">
        Privacy contact:
        <a href="mailto:teamnimoxglobal@gmail.com">
          {" "}teamnimoxglobal@gmail.com
        </a>
        <br />
        This page is a product/legal draft and should be reviewed
        by qualified counsel before commercial launch.
      </div>
    </>,
    "N1MOX30 privacy information for account, creator, integration and support data."
  );
}

export function TermsPage() {
  return shell(
    "Terms & Conditions",
    "LEGAL · TERMS",
    <>
      <p className="nm-public-lead">
        These terms are a launch framework for N1MOX30 and must
        remain consistent with the actual operator, product,
        payment configuration and applicable law.
      </p>

      <h2>1. Operator</h2>
      <p>
        N1MOX30 is currently operated by Mohammad Nihaal in India.
        No separate registered company is represented on this page
        unless and until that information is formally established.
      </p>

      <h2>2. Use of the service</h2>
      <p>
        You are responsible for your account, connected platforms,
        content you provide and actions taken through your
        workspace.
      </p>

      <h2>3. AI-generated output</h2>
      <p>
        AI output can contain errors or unsuitable material.
        Review generated scripts, metadata, media and publishing
        actions before relying on them.
      </p>

      <h2>4. Third-party platforms</h2>
      <p>
        Connected services have their own terms, policies, API
        rules and availability. N1MOX30 does not override those
        requirements.
      </p>

      <h2>5. Publishing responsibility</h2>
      <p>
        You remain responsible for content rights, copyright,
        claims, disclosures, platform policies and the destination
        account.
      </p>

      <h2>6. Prohibited use</h2>
      <p>
        Do not use N1MOX30 for unlawful activity, credential theft,
        malware, abuse of third-party systems or attempts to bypass
        security and access controls.
      </p>

      <h2>7. Billing</h2>
      <p>
        Pricing is presented with USD as the reference catalog
        currency. Actual payment currency, taxes, fees, renewal
        terms and consumer rights depend on the configured payment
        provider and applicable jurisdiction.
      </p>

      <h2>8. Changes and availability</h2>
      <p>
        Features, integrations, plans and pricing may change.
        Maintenance or third-party outages may temporarily affect
        availability.
      </p>

      <h2>9. Mandatory local rights</h2>
      <p>
        Nothing on this page is intended to remove consumer or
        other mandatory rights that cannot lawfully be excluded
        in the user's jurisdiction.
      </p>

      <div className="nm-public-callout">
        Billing questions:
        <a href="mailto:mohammadnihaal0707@gmail.com">
          {" "}mohammadnihaal0707@gmail.com
        </a>
        <br />
        These terms require legal review before commercial launch,
        particularly for refunds, cancellation, taxation,
        limitation of liability and dispute resolution.
      </div>
    </>,
    "N1MOX30 terms and conditions framework for creators and connected platform users."
  );
}

export function CookiePage() {
  return shell(
    "Cookie Policy",
    "LEGAL · COOKIES",
    <>
      <p className="nm-public-lead">
        N1MOX30 should distinguish essential storage from optional
        analytics, advertising and preference technologies.
      </p>

      <h2>Necessary storage</h2>
      <p>
        Authentication, security, sessions and essential
        application functionality may require storage technologies.
      </p>

      <h2>Preferences</h2>
      <p>
        Theme and convenience preferences may be stored where
        enabled.
      </p>

      <h2>Analytics</h2>
      <p>
        Optional measurement should only activate where the
        applicable consent requirements have been satisfied.
      </p>
    </>,
    "N1MOX30 cookie information for essential and optional technologies."
  );
}

export function DataRequestPage() {
  return shell(
    "Privacy & Data Request",
    "DATA RIGHTS",
    <>
      <p className="nm-public-lead">
        Use this route for requests concerning personal data,
        subject to applicable law and identity verification.
      </p>

      <div className="nm-public-card">
        <h2>Request types</h2>

        <ul>
          <li>Access or copy of applicable personal data</li>
          <li>Correction</li>
          <li>Deletion</li>
          <li>Consent withdrawal where applicable</li>
          <li>Other rights provided by applicable law</li>
        </ul>

        <p>
          Privacy requests:
          <a href="mailto:teamnimoxglobal@gmail.com">
            {" "}teamnimoxglobal@gmail.com
          </a>
        </p>
      </div>
    </>,
    "N1MOX30 personal data request and privacy rights information."
  );
}

export function AboutPage() {
  return shell(
    "About N1MOX30",
    "N1MOX30",
    <>
      <p className="nm-public-lead">
        N1MOX30 is being built as an AI-powered creator operating
        system connecting research, strategy, creation, automation,
        analytics and publishing in one workspace.
      </p>

      <div className="nm-public-card">
        <h2>Operator</h2>

        <p>
          <strong>Mohammad Nihaal</strong>
          <br />
          N1MOX30
          <br />
          India
        </p>

        <p>
          The public site will be updated when a formal business
          structure and verified business information are established.
        </p>
      </div>
    </>,
    "About N1MOX30 and its creator operating system."
  );
}
