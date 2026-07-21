import api from "../api/axios";

export const alertService = {
  getAlerts: async () => {
    const response = await api.get("/alerts/");
    return response.data;
  },

  acknowledge: async (alertId) => {
    const response = await api.post(
      `/alerts/acknowledge/${alertId}`
    );
    return response.data;
  },

  resolve: async (alertId) => {
    const response = await api.post(
      `/alerts/resolve/${alertId}`
    );
    return response.data;
  },

  escalate: async (alertId) => {
    const response = await api.post(
      `/alerts/escalate/${alertId}`
    );
    return response.data;
  },
};