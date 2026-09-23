export const PLANS = [
  {
    id: "creator",
    name: "Creator",
    monthlyUsd: 19,
    yearlyUsd: 190,
    monthlyVideos: 27,
    description: "For creators building a consistent publishing system.",
    couponDiscount: 50,
    features: [
      "27 videos / month",
      "AI content studio",
      "Production workflow",
      "Scheduling",
      "Creator analytics",
    ],
  },
  {
    id: "pro",
    name: "Pro",
    monthlyUsd: 49,
    yearlyUsd: 490,
    monthlyVideos: 72,
    description: "For serious creators running an automated content operation.",
    couponDiscount: 25,
    popular: true,
    features: [
      "72 videos / month",
      "Everything in Creator",
      "Automation workflows",
      "Advanced insights",
      "Priority processing",
    ],
  },
  {
    id: "studio",
    name: "Studio",
    monthlyUsd: 129,
    yearlyUsd: 1290,
    monthlyVideos: 100,
    description: "For high-volume creator operations.",
    couponDiscount: 42,
    features: [
      "100+ videos / month",
      "Everything in Pro",
      "High-volume generation",
      "Advanced operations",
      "Priority support",
    ],
  },
];

export const DEFAULT_CURRENCY = "USD";

export const YEARLY_SAVINGS = {
  creator: 38,
  pro: 98,
  studio: 258,
};

export function formatUsd(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatPlanPrice(
  plan,
  currency = "USD",
  rate = 1,
  yearly = false
) {
  const usd = yearly ? plan.yearlyUsd : plan.monthlyUsd;
  const amount = currency === "USD" ? usd : usd * rate;

  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: currency === "USD" ? 0 : 2,
  }).format(amount);
}
