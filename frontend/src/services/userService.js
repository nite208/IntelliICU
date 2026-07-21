import api from "../api/axios";

export const userService = {
  getUsers: async (search = "", role = "", department = "", page = 1, size = 10) => {
    const params = { page, size };
    if (search) params.search = search;
    if (role && role.toLowerCase() !== "all") params.role = role;
    if (department && department.toLowerCase() !== "all") params.department = department;
    
    const response = await api.get("/users", { params });
    return response.data; // returns { users: [...], total, page, size }
  },

  createUser: async (userData) => {
    const response = await api.post("/users", userData);
    return response.data;
  },

  updateUser: async (userId, updateData) => {
    const response = await api.put(`/users/${userId}`, updateData);
    return response.data;
  },

  deactivateUser: async (userId) => {
    const response = await api.delete(`/users/${userId}`);
    return response.data;
  },

  resetUserPassword: async (userId, newPassword) => {
    const response = await api.post(`/users/${userId}/reset-password`, { new_password: newPassword });
    return response.data;
  },

  changeMyPassword: async (oldPassword, newPassword) => {
    const response = await api.post("/users/me/change-password", {
      old_password: oldPassword,
      new_password: newPassword
    });
    return response.data;
  },

  getDepartments: async () => {
    const response = await api.get("/departments");
    return response.data;
  }
};
