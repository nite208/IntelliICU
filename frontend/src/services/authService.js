import api from "../api/axios";

export const authService = {
  login: async (username, password) => {
    const response = await api.post("/auth/login", { username, password });
    const { access_token, refresh_token, role, username: responseUsername } = response.data;
    
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    
    return { role, username: responseUsername };
  },

  logout: async () => {
    try {
      await api.post("/auth/logout");
    } catch (err) {
      console.warn("Logout request failed, clearing client state anyway:", err);
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },

  getCurrentUser: async () => {
    const response = await api.get("/auth/me");
    return response.data;
  },

  hasSession: () => {
    return !!localStorage.getItem("access_token") || !!localStorage.getItem("refresh_token");
  }
};
