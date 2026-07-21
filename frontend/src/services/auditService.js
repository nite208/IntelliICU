export const auditService = {
  createEvent: (alertId, action, detail, time) => {
    return {
      alertId,
      action,
      detail,
      time: time || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    };
  }
};
