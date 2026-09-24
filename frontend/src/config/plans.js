export const PLANS = [
  {
    id: "creator",
    name: "Creator",
    monthlyUsd: 19,
    yearlyUsd: 190,
    monthlyVideos: 27,
    monthlyClips: 12,
    monthlyMessages: 999,
    monthlyEmail: 999,
    monthlyOutlook: 999,
    monthlyInstagram: 60,
    monthlyX: 60,
    monthlyTiktok: 60,
    youtubeMinMinutes: 15,
    youtubeTargetMinutes: 25,
    description: "A focused operating system for creators building consistently.",
    couponDiscount: 50,
    features: [
      "27 YouTube long videos / month",
      "12 clips / month",
      "999 messages / month",
      "999 Gmail / Email / Outlook actions / month",
      "15–25+ minute YouTube videos",
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
    monthlyClips: 39,
    monthlyMessages: 1999,
    monthlyEmail: 1999,
    monthlyOutlook: 1999,
    monthlyInstagram: 180,
    monthlyX: 180,
    monthlyTiktok: 180,
    youtubeMinMinutes: 15,
    youtubeTargetMinutes: 25,
    description: "For creators running a serious automated content operation.",
    couponDiscount: 25,
    popular: true,
    features: [
      "72 YouTube long videos / month",
      "39 clips / month",
      "1,999 messages / month",
      "1,999 Gmail / Email / Outlook actions / month",
      "15–25+ minute YouTube videos",
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
    monthlyVideos: 111,
    monthlyClips: 100,
    monthlyMessages: 4499,
    monthlyEmail: 4499,
    monthlyOutlook: 4499,
    monthlyInstagram: 360,
    monthlyX: 360,
    monthlyTiktok: 360,
    youtubeMinMinutes: 15,
    youtubeTargetMinutes: 25,
    description: "For high-volume creator operations and teams.",
    couponDiscount: 42,
    features: [
      "111 YouTube long videos / month",
      "100 clips / month",
      "4,499 messages / month",
      "4,499 Gmail / Email / Outlook actions / month",
      "15–25+ minute YouTube videos",
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
