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

      oauth:
        Boolean(integration.oauth),
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

    available:
      health.filter(
        (item) =>
          item.status ===
          INTEGRATION_STATUS.AVAILABLE
      ).length,

    errors:
      health.filter(
        (item) =>
          item.status ===
          INTEGRATION_STATUS.ERROR
      ).length,
  };
}
