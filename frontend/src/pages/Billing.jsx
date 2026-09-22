import { useEffect, useState } from "react";
import api from "../api/client";

const DEFAULT_PLANS = [
  {
    id: "creator",
    name: "Creator",
    price: 1599,
    currency: "INR",
    videos: "12 videos / month",
  },
  {
    id: "pro",
    name: "Pro",
    price: 4099,
    currency: "INR",
    videos: "33 videos / month",
  },
  {
    id: "studio",
    name: "Studio",
    price: 10999,
    currency: "INR",
    videos: "100 videos / month",
  },
];

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
      existing.addEventListener("load", () => resolve(true), { once: true });
      existing.addEventListener("error", () => resolve(false), { once: true });
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

function formatPrice(plan) {
  const value =
    plan?.price ??
    plan?.amount ??
    plan?.price_inr ??
    plan?.amount_inr ??
    0;

  const currency = plan?.currency || "INR";

  try {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(Number(value));
  } catch {
    return `₹${Number(value).toLocaleString("en-IN")}`;
  }
}

function normalizePlan(plan) {
  return {
    ...plan,
    id: plan?.id || plan?.plan_id || plan?.slug,
    name: plan?.name || plan?.id || "Plan",
    videos:
      plan?.videos ||
      plan?.video_limit
        ? `${plan?.video_limit || plan?.videos || ""} videos / month`
        : "",
  };
}

export default function Billing() {
  const [plans, setPlans] = useState(DEFAULT_PLANS);
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
        setPlans(
          plansResponse.data.plans.map(normalizePlan)
        );
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
      });

      const data = response?.data || {};

      /*
       * Safe development/test mode:
       * The backend deliberately returns a test order while
       * N1MOX_RAZORPAY_LIVE=false. Never open a real payment
       * window for a test order.
       */
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
          "Razorpay Checkout could not be loaded."
        );
      }

      const orderId =
        data.order_id ||
        data.razorpay_order_id;

      const keyId =
        data.key_id ||
        data.razorpay_key_id ||
        data.key;

      if (!orderId) {
        throw new Error(
          "Payment order was not returned by the server."
        );
      }

      if (!keyId) {
        throw new Error(
          "Razorpay public key was not returned by the server."
        );
      }

      const options = {
        key: keyId,
        order_id: orderId,
        name: "N1MOX30",
        description: `${plan.name} Creator Automation Plan`,
        currency: data.currency || plan.currency || "INR",
        amount:
          data.amount ??
          data.amount_paise ??
          Number(plan.price || 0) * 100,

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
          color: "#111111",
        },
      };

      const checkout = new window.Razorpay(options);

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
    <section className="page-section">
      <div className="page-heading">
        <div>
          <p className="eyebrow">N1MOX30 COMMERCE</p>

          <h2>Plans & Billing</h2>

          <p>
            Manage your N1MOX30 subscription and creator
            automation capacity.
          </p>
        </div>
      </div>

      {message && (
        <div
          className="glass-card"
          style={{ marginBottom: 18 }}
        >
          <p>{message}</p>
        </div>
      )}

      {error && (
        <div
          className="glass-card"
          style={{ marginBottom: 18 }}
        >
          <p>{error}</p>
        </div>
      )}

      <div className="settings-grid">
        {plans.map((plan) => {
          const isLoading = loadingPlan === plan.id;

          return (
            <div
              className="glass-card"
              key={plan.id || plan.name}
            >
              <p className="eyebrow">{plan.name}</p>

              <h2>{formatPrice(plan)}</h2>

              <p className="muted">
                {plan.videos ||
                  `${plan.video_limit || ""} videos / month`}
              </p>

              <button
                className="primary-button"
                onClick={() => choosePlan(plan)}
                disabled={Boolean(loadingPlan)}
              >
                {isLoading
                  ? "Opening checkout..."
                  : "Choose plan"}
              </button>
            </div>
          );
        })}
      </div>

      <div
        className="glass-card"
        style={{ marginTop: 18 }}
      >
        <h3>Payment status</h3>

        <p className="muted">
          {status?.checkout_ready
            ? "Checkout is ready."
            : "Payment provider is currently in test/setup mode."}
        </p>

        <small className="muted">
          Provider configured:{" "}
          {status?.provider_configured
            ? "Yes"
            : "No"}
        </small>

        <br />

        <small className="muted">
          Live charging:{" "}
          {status?.live_enabled
            ? "Enabled"
            : "Disabled"}
        </small>
      </div>
    </section>
  );
}
