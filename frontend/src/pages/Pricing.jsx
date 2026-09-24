import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Check, ArrowUpRight, ShieldCheck } from "lucide-react";
import {
  PLANS,
  formatPlanPrice,
  YEARLY_SAVINGS,
} from "../config/plans";

const CURRENCIES = [
  ["USD", "US Dollar"],
  ["EUR", "Euro"],
  ["GBP", "British Pound"],
  ["INR", "Indian Rupee"],
  ["AUD", "Australian Dollar"],
  ["CAD", "Canadian Dollar"],
  ["SGD", "Singapore Dollar"],
  ["AED", "UAE Dirham"],
];

export default function Pricing() {
  const [yearly, setYearly] = useState(false);
  const [currency, setCurrency] = useState("USD");
  const [coupon, setCoupon] = useState("");

  const rates = {
    USD: 1,
    EUR: null,
    GBP: null,
    INR: null,
    AUD: null,
    CAD: null,
    SGD: null,
    AED: null,
  };

  const selectedRate = rates[currency];

  const couponPreview = useMemo(() => {
    if (!coupon.trim()) return null;

    return "Coupon will be validated securely during checkout.";
  }, [coupon]);

  return (
    <main className="nm-commercial-page">
      <div className="nm-commercial-shell">

        <header className="nm-commercial-header">
          <Link to="/" className="nm-commercial-brand">
            N1MOX30
          </Link>

          <Link to="/login" className="nm-commercial-login">
            Sign in <ArrowUpRight size={15} />
          </Link>
        </header>

        <section className="nm-commercial-hero">
          <span className="nm-commercial-eyebrow">N1MOX30 · CREATOR OS</span>

          <h1>
            Choose the system
            <br />
            behind your content.
          </h1>

          <p>
            USD is the reference price. Your final checkout currency,
            payment method and applicable taxes depend on the payment
            provider and your country.
          </p>

          <div className="nm-commercial-controls">

            <div className="nm-billing-toggle">
              <button
                className={!yearly ? "active" : ""}
                onClick={() => setYearly(false)}
              >
                Monthly
              </button>

              <button
                className={yearly ? "active" : ""}
                onClick={() => setYearly(true)}
              >
                Yearly
                <span>Save</span>
              </button>
            </div>

            <label className="nm-currency-select">
              <span>Currency</span>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
              >
                {CURRENCIES.map(([code, name]) => (
                  <option key={code} value={code}>
                    {code} — {name}
                  </option>
                ))}
              </select>
            </label>

          </div>

          {currency !== "USD" && !selectedRate && (
            <div className="nm-commercial-note">
              Local-currency display will use a live provider rate when
              regional checkout is enabled. USD remains the authoritative
              catalog price.
            </div>
          )}
        </section>

        <section className="nm-plan-grid">

          {PLANS.map((plan) => {

            const displayCurrency =
              currency !== "USD" && selectedRate ? currency : "USD";

            const displayRate =
              currency !== "USD" && selectedRate ? selectedRate : 1;

            return (
              <article
                className={`nm-plan-card ${
                  plan.popular ? "featured" : ""
                }`}
                key={plan.id}
              >

                {plan.popular && (
                  <div className="nm-plan-badge">
                    MOST POPULAR
                  </div>
                )}

                <div className="nm-plan-top">
                  <div>
                    <span className="nm-plan-kicker">
                      {plan.id.toUpperCase()}
                    </span>
                    <h2>{plan.name}</h2>
                  </div>

                  <span className="nm-plan-videos">
                    {plan.monthlyVideos}+ videos
                  </span>
                </div>

                <p className="nm-plan-description">
                  {plan.description}
                </p>

                <div className="nm-plan-price">
                  {formatPlanPrice(
                    plan,
                    displayCurrency,
                    displayRate,
                    yearly
                  )}

                  <small>
                    {yearly ? "/year" : "/month"}
                  </small>
                </div>

                {yearly && (
                  <div className="nm-yearly-saving">
                    Save ${YEARLY_SAVINGS[plan.id]} / year
                  </div>
                )}

                <ul className="nm-plan-features">
                  {plan.features.map((feature) => (
                    <li key={feature}>
                      <Check size={16} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  to={`/register?plan=${plan.id}`}
                  className="nm-plan-cta"
                >
                  Start {plan.name}
                  <ArrowUpRight size={16} />
                </Link>

              </article>
            );
          })}

        </section>

        <section className="nm-commercial-bottom">

          <div className="nm-coupon-card">
            <div>
              <span className="nm-commercial-eyebrow">
                COUPON
              </span>

              <h3>Have a launch code?</h3>

              <p>
                Enter your coupon during checkout. The server validates
                the code before applying any discount.
              </p>
            </div>

            <div className="nm-coupon-input">
              <input
                value={coupon}
                onChange={(e) => setCoupon(e.target.value)}
                placeholder="Enter coupon code"
                maxLength={64}
              />

              {couponPreview && (
                <span>{couponPreview}</span>
              )}
            </div>
          </div>

          <div className="nm-trust-row">
            <ShieldCheck size={18} />

            <span>
              Secure provider-hosted checkout · server-side verification ·
              no card details stored by the frontend
            </span>
          </div>

        </section>

      </div>
    </main>
  );
}
