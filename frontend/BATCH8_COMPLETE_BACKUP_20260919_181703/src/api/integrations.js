export const INTEGRATION_STATUS = {
  CONNECTED: "connected",
  AVAILABLE: "available",
  CONFIGURATION_REQUIRED: "configuration_required",
  FUTURE: "future",
  ERROR: "error",
};

export const INTEGRATION_CAPABILITIES = {
  YOUTUBE: [
    "oauth",
    "channel_data",
    "analytics",
    "video_upload",
    "publishing",
    "scheduling",
  ],

  OPENCLAW: [
    "ai_routing",
    "agent_execution",
    "automation",
  ],

  OMNIROUTE: [
    "provider_routing",
    "model_routing",
    "failover",
  ],

  GROQ: [
    "text_generation",
  ],

  INSTAGRAM: [
    "oauth",
    "publishing",
    "analytics",
  ],

  TIKTOK: [
    "oauth",
    "publishing",
    "analytics",
  ],

  X: [
    "oauth",
    "publishing",
    "analytics",
  ],
};

export const INTEGRATION_REGISTRY = [
  {
    id: "youtube",
    name: "YouTube",
    category: "publishing",
    status: INTEGRATION_STATUS.CONNECTED,
    description:
      "YouTube OAuth, channel intelligence, analytics, scheduling and publishing.",
    capabilities:
      INTEGRATION_CAPABILITIES.YOUTUBE,
    existing: true,
    requiresOAuth: true,
  },

  {
    id: "openclaw",
    name: "OpenClaw",
    category: "ai",
    status: INTEGRATION_STATUS.CONNECTED,
    description:
      "Agent orchestration and AI execution layer.",
    capabilities:
      INTEGRATION_CAPABILITIES.OPENCLAW,
    existing: true,
    requiresOAuth: false,
  },

  {
    id: "omniroute",
    name: "OmniRoute",
    category: "ai",
    status: INTEGRATION_STATUS.CONNECTED,
    description:
      "Unified AI provider and model routing layer.",
    capabilities:
      INTEGRATION_CAPABILITIES.OMNIROUTE,
    existing: true,
    requiresOAuth: false,
  },

  {
    id: "groq",
    name: "Groq",
    category: "ai",
    status: INTEGRATION_STATUS.CONNECTED,
    description:
      "Configured AI generation provider.",
    capabilities:
      INTEGRATION_CAPABILITIES.GROQ,
    existing: true,
    requiresOAuth: false,
  },

  {
    id: "instagram",
    name: "Instagram",
    category: "social",
    status: INTEGRATION_STATUS.FUTURE,
    description:
      "Future social publishing and analytics integration.",
    capabilities:
      INTEGRATION_CAPABILITIES.INSTAGRAM,
    existing: false,
    requiresOAuth: true,
  },

  {
    id: "tiktok",
    name: "TikTok",
    category: "social",
    status: INTEGRATION_STATUS.FUTURE,
    description:
      "Future short-form publishing and analytics integration.",
    capabilities:
      INTEGRATION_CAPABILITIES.TIKTOK,
    existing: false,
    requiresOAuth: true,
  },

  {
    id: "x",
    name: "X",
    category: "social",
    status: INTEGRATION_STATUS.FUTURE,
    description:
      "Future social publishing and analytics integration.",
    capabilities:
      INTEGRATION_CAPABILITIES.X,
    existing: false,
    requiresOAuth: true,
  },
];

export function getIntegration(id) {
  return INTEGRATION_REGISTRY.find(
    (integration) =>
      integration.id === id
  ) || null;
}

export function getIntegrationsByCategory(
  category
) {
  return INTEGRATION_REGISTRY.filter(
    (integration) =>
      integration.category === category
  );
}

export function getConnectedIntegrations() {
  return INTEGRATION_REGISTRY.filter(
    (integration) =>
      integration.status ===
      INTEGRATION_STATUS.CONNECTED
  );
}

export function getIntegrationSummary() {
  const connected =
    getConnectedIntegrations().length;

  const total =
    INTEGRATION_REGISTRY.length;

  const future =
    INTEGRATION_REGISTRY.filter(
      (integration) =>
        integration.status ===
        INTEGRATION_STATUS.FUTURE
    ).length;

  return {
    connected,
    total,
    future,
  };
}
