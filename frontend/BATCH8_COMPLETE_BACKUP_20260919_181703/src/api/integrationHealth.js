import {
  INTEGRATION_REGISTRY,
  INTEGRATION_STATUS,
} from "./integrations";

export function getIntegrationHealth() {
  return INTEGRATION_REGISTRY.map(
    (integration) => ({
      id: integration.id,
      name: integration.name,
      category: integration.category,
      status: integration.status,
      healthy:
        integration.status ===
        INTEGRATION_STATUS.CONNECTED,
      capabilities:
        integration.capabilities,
      requiresOAuth:
        integration.requiresOAuth,
    })
  );
}

export function getIntegrationHealthSummary() {
  const health =
    getIntegrationHealth();

  return {
    total: health.length,

    healthy:
      health.filter(
        (item) => item.healthy
      ).length,

    future:
      health.filter(
        (item) =>
          item.status ===
          INTEGRATION_STATUS.FUTURE
      ).length,

    configurationRequired:
      health.filter(
        (item) =>
          item.status ===
          INTEGRATION_STATUS.CONFIGURATION_REQUIRED
      ).length,

    error:
      health.filter(
        (item) =>
          item.status ===
          INTEGRATION_STATUS.ERROR
      ).length,
  };
}
