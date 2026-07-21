export const alertAnalyticsService = {
  calculateAnalytics: (alerts) => {
    const criticalToday = alerts.filter(a => a.severity === "CRITICAL").length;
    const escalated = alerts.filter(a => a.escalationLevel).length;

    const resolvedOrAcked = alerts.filter(a => a.status !== "ACTIVE");
    const acked = alerts.filter(a => a.status === "ACKNOWLEDGED" || a.acknowledgedBy);
    const ackRate = resolvedOrAcked.length > 0 ? (acked.length / resolvedOrAcked.length) * 100 : 100;

    const ackTimes = alerts.filter(a => a.acknowledgedAtMs && a.createdAtMs).map(a => (a.acknowledgedAtMs - a.createdAtMs) / 1000);
    const avgResponseTime = ackTimes.length > 0 ? ackTimes.reduce((s, x) => s + x, 0) / ackTimes.length : 0;

    const resTimes = alerts.filter(a => a.resolvedAtMs && a.createdAtMs).map(a => (a.resolvedAtMs - a.createdAtMs) / 1000);
    const avgResolutionTime = resTimes.length > 0 ? resTimes.reduce((s, x) => s + x, 0) / resTimes.length : 0;

    return {
      avgResponseTime: `${avgResponseTime.toFixed(0)}s`,
      avgResolutionTime: `${avgResolutionTime.toFixed(0)}s`,
      criticalToday,
      escalated,
      ackRate: `${ackRate.toFixed(0)}%`,
    };
  }
};
