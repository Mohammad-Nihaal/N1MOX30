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
        <Link to="/" className="nm-pricing-back">â† N1MOX30</Link>
        <label className="nm-currency">
          <span>Currency</span>
          <select value={currency} onChange={(e) => setCurrency(e.target.value)} aria-label="Pricing currency">
            {CURRENCIES.map(([code, name]) => <option value={code} key={code}>{code} â€” {name}</option>)}
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