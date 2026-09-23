import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowUpRight,
  CheckCircle2,
  CreditCard,
  ShieldCheck,
} from "lucide-react";
import api from "../api/client";
import { PLANS } from "../config/plans";

const FALLBACK_PLANS = PLANS.map((plan) => ({
  id: plan.id,
  name: plan.name,
  monthly_usd: plan.monthlyUsd,
  yearly_usd: plan.yearlyUsd,
  monthly_videos: plan.monthlyVideos,
}));

function loadRazorpayScript() {
  return new Promise((resolve) => {
    if (window.Razorpay) {
      resolve(true);
      return;
    }

    const existing = document.querySelector(
      'script[src="https://checkout.razorpay.com/v1/checkout.js"]'
    );

    if (existing) {
      existing.addEventListener("load", () => resolve(true), {
        once: true,
      });
      existing.addEventListener("error", () => resolve(false), {
        once: true,
      });
      return;
    }

    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;

    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);

    document.body.appendChild(script);
  });
}

function normalizePlan(plan) {
  const source = plan || {};

  const fallback = FALLBACK_PLANS.find(
    (item) => item.id === source.id
  );

  return {
    ...source,
    id: source.id || source.plan_id || source.slug,
    name: source.name || fallback?.name || source.id || "Plan",
    monthly_usd:
      source.monthly_usd ??
      source.price_usd ??
      fallback?.monthly_usd ??
      0,
    yearly_usd:
      source.yearly_usd ??
      fallback?.yearly_usd ??
      0,
    monthly_videos:
      source.monthly_videos ??
      source.video_limit ??
      fallback?.monthly_videos ??
      0,
  };
}

function usd(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

export default function Billing() {
  const [plans, setPlans] = useState(FALLBACK_PLANS);
  const [yearly, setYearly] = useState(false);
  const [coupon, setCoupon] = useState("");
  const [status, setStatus] = useState(null);
  const [loadingPlan, setLoadingPlan] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    Promise.all([
      api.get("/billing/plans").catch(() => null),
      api.get("/billing/overview").catch(() => null),
      api.get("/billing/providers").catch(() => null),
    ]).then(([plansResponse, overviewResponse, providersResponse]) => {
      if (!mounted) return;

      if (Array.isArray(plansResponse?.data?.plans)) {
        setPlans(plansResponse.data.plans.map(normalizePlan));
      }

      const overview = overviewResponse?.data || {};
      const providers = providersResponse?.data || {};

      setStatus({
        ...overview,
        ...providers,
        checkout_ready:
          overview.checkout_ready ??
          providers.checkout_ready ??
          false,
        provider_configured:
          overview.provider_configured ??
          providers.provider_configured ??
          false,
        live_enabled:
          overview.live_enabled ??
          providers.live_enabled ??
          false,
      });
    });

    return () => {
      mounted = false;
    };
  }, []);

  async function choosePlan(plan) {
    setLoadingPlan(plan.id);
    setMessage("");
    setError("");

    try {
      const response = await api.post("/billing/checkout", {
        plan_id: plan.id,
        billing_cycle: yearly ? "yearly" : "monthly",
        coupon_code: coupon.trim() || undefined,
        currency: "USD",
      });

      const data = response?.data || {};

      const testMode =
        data.test_mode === true ||
        data.mode === "test" ||
        String(data.order_id || "").startsWith("order_test_");

      if (testMode) {
        setMessage(
          `Test checkout created for ${plan.name}. No real payment was charged.`
        );
        return;
      }

      const scriptReady = await loadRazorpayScript();

      if (!scriptReady || !window.Razorpay) {
        throw new Error(
          "Payment checkout could not be loaded."
        );
      }

      const orderId =
        data.order_id ||
        data.razorpay_order_id;

      const keyId =
        data.key_id ||
        data.razorpay_key_id ||
        data.key;

      if (!orderId || !keyId) {
        throw new Error(
          "The payment provider did not return a usable checkout order."
        );
      }

      const checkout = new window.Razorpay({
        key: keyId,
        order_id: orderId,
        name: "N1MOX30",
        description: `${plan.name} Creator Operating System`,
        currency: data.currency || "USD",
        amount:
          data.amount ??
          data.amount_paise,

        handler: async (paymentResponse) => {
          try {
            setMessage("Verifying payment...");

            const verifyResponse = await api.post(
              "/billing/verify",
              {
                plan_id: plan.id,
                order_id:
                  paymentResponse.razorpay_order_id ||
                  orderId,
                payment_id:
                  paymentResponse.razorpay_payment_id,
                signature:
                  paymentResponse.razorpay_signature,
              }
            );

            if (
              verifyResponse?.data?.verified === false ||
              verifyResponse?.data?.success === false
            ) {
              throw new Error(
                verifyResponse?.data?.message ||
                "Payment verification failed."
              );
            }

            setMessage(
              `${plan.name} payment verified successfully.`
            );

            const overview = await api
              .get("/billing/overview")
              .catch(() => null);

            if (overview?.data) {
              setStatus((current) => ({
                ...current,
                ...overview.data,
              }));
            }
          } catch (verificationError) {
            setError(
              verificationError?.response?.data?.detail ||
              verificationError?.message ||
              "Payment verification failed."
            );
          }
        },

        modal: {
          ondismiss: () => {
            setMessage("Checkout closed.");
          },
        },

        theme: {
          color: "#171714",
        },
      });

      checkout.on("payment.failed", (paymentError) => {
        setError(
          paymentError?.error?.description ||
          "Payment failed. Please try again."
        );
      });

      checkout.open();
    } catch (checkoutError) {
      setError(
        checkoutError?.response?.data?.detail ||
        checkoutError?.message ||
        "Unable to start checkout."
      );
    } finally {
      setLoadingPlan(null);
    }
  }

  return (
    <main className="nm-billing-page">
      <div className="nm-billing-shell">

        <header className="nm-billing-header">
          <div>
            <span className="nm-commercial-eyebrow">
              N1MOX30 · COMMERCE
            </span>

            <h1>Plans & billing.</h1>

            <p>
              Choose your creator capacity, manage checkout and keep
              your subscription information in one place.
            </p>
          </div>

          <Link
            to="/pricing"
            className="nm-billing-secondary"
          >
            View pricing <ArrowUpRight size={15} />
          </Link>
        </header>

        <section className="nm-billing-toolbar">

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
            </button>
          </div>

          <div className="nm-billing-base">
            <span>Reference currency</span>
            <strong>USD</strong>
          </div>

        </section>

        {message && (
          <div className="nm-billing-message success">
            <CheckCircle2 size={18} />
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="nm-billing-message error">
            <span>{error}</span>
          </div>
        )}

        <section className="nm-billing-grid">

          {plans.map((rawPlan) => {
            const plan = normalizePlan(rawPlan);

            const price = yearly
              ? plan.yearly_usd
              : plan.monthly_usd;

            const loading = loadingPlan === plan.id;

            return (
              <article
                className={`nm-billing-card ${
                  plan.id === "pro" ? "featured" : ""
                }`}
                key={plan.id}
              >
                {plan.id === "pro" && (
                  <span className="nm-billing-popular">
                    MOST POPULAR
                  </span>
                )}

                <span className="nm-commercial-eyebrow">
                  {plan.id}
                </span>

                <h2>{plan.name}</h2>

                <div className="nm-billing-price">
                  {usd(price)}
                  <small>
                    {yearly ? "/year" : "/month"}
                  </small>
                </div>

                <p className="nm-billing-capacity">
                  {plan.monthly_videos >= 100
                    ? "100+ videos / month"
                    : `${plan.monthly_videos} videos / month`}
                </p>

                <button
                  className="nm-billing-primary"
                  onClick={() => choosePlan(plan)}
                  disabled={Boolean(loadingPlan)}
                >
                  {loading
                    ? "Preparing..."
                    : `Choose ${plan.name}`}
                  <ArrowUpRight size={15} />
                </button>
              </article>
            );
          })}

        </section>

        <section className="nm-billing-lower">

          <article className="nm-billing-panel">
            <div className="nm-panel-icon">
              <CreditCard size={19} />
            </div>

            <div>
              <span className="nm-commercial-eyebrow">
                COUPON
              </span>

              <h3>Have a launch code?</h3>

              <p>
                Enter your coupon before checkout. The server must
                validate the code before applying a discount.
              </p>

              <input
                className="nm-billing-input"
                value={coupon}
                onChange={(event) =>
                  setCoupon(event.target.value)
                }
                placeholder="Coupon code"
                maxLength={64}
                autoComplete="off"
              />
            </div>
          </article>

          <article className="nm-billing-panel">
            <div className="nm-panel-icon">
              <ShieldCheck size={19} />
            </div>

            <div>
              <span className="nm-commercial-eyebrow">
                PAYMENT STATUS
              </span>

              <h3>
                {status?.checkout_ready
                  ? "Checkout ready"
                  : "Test / setup mode"}
              </h3>

              <p>
                Provider configured:{" "}
                <strong>
                  {status?.provider_configured
                    ? "Yes"
                    : "No"}
                </strong>
              </p>

              <p>
                Live charging:{" "}
                <strong>
                  {status?.live_enabled
                    ? "Enabled"
                    : "Disabled"}
                </strong>
              </p>

              {!status?.live_enabled && (
                <small>
                  No real payment is charged while live
                  payment mode is disabled.
                </small>
              )}
            </div>
          </article>

        </section>

        <section className="nm-billing-footnote">
          <ShieldCheck size={17} />

          <span>
            USD is the reference catalog price. Final payment
            currency, taxes, payment methods and applicable
            consumer rights depend on the configured payment
            provider and the customer's jurisdiction.
          </span>
        </section>

      </div>
    </main>
  );
}
