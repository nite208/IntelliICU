import api from "../api/axios";

export const patientService = {
  getPatients: async () => {
    const response = await api.get("/patients/");
    return response.data;
  },

  getPatient: async (patientId) => {
    const response = await api.get(`/patients/${patientId}`);
    return response.data;
  },

  // Backward compatibility
  // Can be removed once all components use getPatient()
  getPatientById: async (patientId) => {
    return await patientService.getPatient(patientId);
  },
};