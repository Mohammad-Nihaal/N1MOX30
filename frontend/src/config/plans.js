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