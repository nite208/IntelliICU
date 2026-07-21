import api from "../api/axios";

export const clinicalAIService = {
  analyzePatient: async (patientData) => {
    const response = await api.post(
      "/clinical-ai/",
      patientData
    );

    return response.data;
  },
};