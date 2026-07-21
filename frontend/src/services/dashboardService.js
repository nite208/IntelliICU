import api from "../api/axios";

export const dashboardService = {
  getDashboard: async () => {
    const response = await api.get("/dashboard/");
    return response.data;
  },
};