import {
  getIntegration,
  INTEGRATION_STATUS,
} from "./integrations";

export function canUseIntegration(
  integrationId
) {
  const integration =
    getIntegration(integrationId);

  if (!integration) {
    return false;
  }

  return (
    integration.status ===
    INTEGRATION_STATUS.CONNECTED
  );
}

export function getIntegrationCapabilities(
  integrationId
) {
  const integration =
    getIntegration(integrationId);

  return integration?.capabilities || [];
}

export function getIntegrationState(
  integrationId
) {
  const integration =
    getIntegration(integrationId);

  if (!integration) {
    return {
      exists: false,
      status: "unknown",
      capabilities: [],
    };
  }

  return {
    exists: true,
    id: integration.id,
    name: integration.name,
    status: integration.status,
    capabilities:
      integration.capabilities,
    oauth:
      Boolean(integration.oauth),
  };
}

export function getPublishingTargets() {
  return [
    getIntegration("youtube"),
    getIntegration("instagram"),
    getIntegration("tiktok"),
    getIntegration("x"),
  ].filter(Boolean);
}

export function getAiProviders() {
  return [
    getIntegration("openclaw"),
    getIntegration("omniroute"),
    getIntegration("groq"),
  ].filter(Boolean);
}

export function getCommunicationProviders() {
  return [
    getIntegration("email"),
  ].filter(Boolean);
}

export function getPaymentProviders() {
  return [
    getIntegration("payments"),
  ].filter(Boolean);
}
