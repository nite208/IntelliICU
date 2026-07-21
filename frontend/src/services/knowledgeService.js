import api from "../api/axios";

export const knowledgeService = {
  uploadDocument: async (formData) => {
    const response = await api.post("/rag/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  searchGuidelines: async (query, category = null) => {
    const params = { query };
    if (category) {
      params.category = category;
    }
    const response = await api.get("/rag/search", { params });
    return response.data;
  },

  listDocuments: async () => {
    const response = await api.get("/rag/documents");
    return response.data;
  },

  deleteDocument: async (identifier) => {
    const response = await api.delete(`/rag/documents/${encodeURIComponent(identifier)}`);
    return response.data;
  },
};
