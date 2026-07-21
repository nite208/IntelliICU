import api from "../api/axios";

export const aiService = {
  async analyzePatient(payload) {
    const response = await api.post("/clinical-ai/", payload);
    return response.data;
  },

  async getProviders() {
    const res = await api.get("/ai/providers");
    return res.data;
  },

  async getModels() {
    const res = await api.get("/ai/models");
    return res.data;
  },

  async getConfig() {
    const res = await api.get("/ai/config");
    return res.data;
  },

  async updateConfig(config) {
    const res = await api.put("/ai/config", config);
    return res.data;
  },

  async getHealth() {
    const res = await api.get("/ai/health");
    return res.data;
  },
};