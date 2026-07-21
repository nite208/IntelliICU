import api from "../api/axios";

export const permissionService = {
  getMyPermissions: async () => {
    const response = await api.get("/rbac/users/me/permissions");
    return response.data; // returns { role: "Doctor", permissions: ["Dashboard", "Patients", ...] }
  },

  getAllRoles: async () => {
    const response = await api.get("/rbac/roles");
    return response.data;
  },

  getAllPermissions: async () => {
    const response = await api.get("/rbac/permissions");
    return response.data;
  }
};
