export const INTEGRATION_STATUS = {
  CONNECTED: "connected",
  AVAILABLE: "available",
  CONFIGURATION_REQUIRED: "configuration_required",
  FUTURE: "future",
  ERROR: "error",
};

export const INTEGRATION_CATEGORY = {
  PUBLISHING: "publishing",
  SOCIAL: "social",
  AI: "ai",
  PAYMENTS: "payments",
  COMMUNICATION: "communication",
};

export const INTEGRATION_REGISTRY = [
  {
    id: "youtube",
    name: "YouTube",
    category: INTEGRATION_CATEGORY.PUBLISHING,
    status: INTEGRATION_STATUS.CONNECTED,
    description:
      "OAuth, channel analytics, publishing, scheduling and creator intelligence.",
    capabilities: [
      "oauth",
      "channel",
      "analytics",
      "upload",
      "publishing",
      "scheduling",
    ],
    existing: true,
    oauth: true,
  },

  {
    id: "openclaw",
    name: "OpenClaw",
    category: INTEGRATION_CATEGORY.AI,
    status: INTEGRATION_STATUS.CONNECTED,
    description:
      "Agent execution and orchestration layer.",
    capabilities: [
      "agents",
      "orchestration",
      "execution",
    ],
    existing: true,
    oauth: false,
  },

  {
    id: "omniroute",
    name: "OmniRoute",
    category: INTEGRATION_CATEGORY.AI,
    status: INTEGRATION_STATUS.CONNECTED,
    description:
      "Unified model and provider routing layer.",
    capabilities: [
      "routing",
      "model_selection",
      "failover",
    ],
    existing: true,
    oauth: false,
  },

  {
    id: "groq",
    name: "Groq",
    category: INTEGRATION_CATEGORY.AI,
    status: INTEGRATION_STATUS.CONNECTED,
    description:
      "Configured high-speed text generation provider.",
    capabilities: [
      "text_generation",
    ],
    existing: true,
    oauth: false,
  },

  {
    id: "instagram",
    name: "Instagram",
    category: INTEGRATION_CATEGORY.SOCIAL,
    status: INTEGRATION_STATUS.FUTURE,
    description:
      "Instagram publishing and analytics adapter.",
    capabilities: [
      "oauth",
      "publishing",
      "analytics",
    ],
    existing: false,
    oauth: true,
  },

  {
    id: "tiktok",
    name: "TikTok",
    category: INTEGRATION_CATEGORY.SOCIAL,
    status: INTEGRATION_STATUS.FUTURE,
    description:
      "TikTok publishing and performance adapter.",
    capabilities: [
      "oauth",
      "publishing",
      "analytics",
    ],
    existing: false,
    oauth: true,
  },

  {
    id: "x",
    name: "X",
    category: INTEGRATION_CATEGORY.SOCIAL,
    status: INTEGRATION_STATUS.FUTURE,
    description:
      "X publishing and analytics adapter.",
    capabilities: [
      "oauth",
      "publishing",
      "analytics",
    ],
    existing: false,
    oauth: true,
  },

  {
    id: "payments",
    name: "Payment Providers",
    category: INTEGRATION_CATEGORY.PAYMENTS,
    status: INTEGRATION_STATUS.AVAILABLE,
    description:
      "Provider abstraction for future subscriptions and billing.",
    capabilities: [
      "checkout",
      "subscriptions",
      "webhooks",
      "refunds",
    ],
    existing: false,
    oauth: false,
  },

  {
    id: "email",
    name: "Email",
    category: INTEGRATION_CATEGORY.COMMUNICATION,
    status: INTEGRATION_STATUS.AVAILABLE,
    description:
      "Transactional email and creator notifications adapter.",
    capabilities: [
      "transactional_email",
      "notifications",
    ],
    existing: false,
    oauth: false,
  },
];

export function getIntegration(id) {
  return (
    INTEGRATION_REGISTRY.find(
      (item) => item.id === id
    ) || null
  );
}

export function getConnectedIntegrations() {
  return INTEGRATION_REGISTRY.filter(
    (item) =>
      item.status ===
      INTEGRATION_STATUS.CONNECTED
  );
}

export function getIntegrationsByCategory(category) {
  return INTEGRATION_REGISTRY.filter(
    (item) =>
      item.category === category
  );
}

export function getIntegrationSummary() {
  return {
    total: INTEGRATION_REGISTRY.length,

    connected:
      INTEGRATION_REGISTRY.filter(
        (item) =>
          item.status ===
          INTEGRATION_STATUS.CONNECTED
      ).length,

    available:
      INTEGRATION_REGISTRY.filter(
        (item) =>
          item.status ===
          INTEGRATION_STATUS.AVAILABLE
      ).length,

    future:
      INTEGRATION_REGISTRY.filter(
        (item) =>
          item.status ===
          INTEGRATION_STATUS.FUTURE
      ).length,

    errors:
      INTEGRATION_REGISTRY.filter(
        (item) =>
          item.status ===
          INTEGRATION_STATUS.ERROR
      ).length,
  };
}
