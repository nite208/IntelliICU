import api from "../api/axios";

export const timelineService = {
  getTimeline: async (patientId, type = "", search = "") => {
    const params = {};
    if (type && type.toLowerCase() !== "all") params.type = type;
    if (search) params.search = search;
    const response = await api.get(`/timeline/${patientId}`, { params });
    return response.data;
  },

  logEvent: async (patientId, event) => {
    const response = await api.post(`/timeline/${patientId}`, event);
    return response.data;
  },

  downloadExport: async (patientId, format = "json", type = "", search = "") => {
    const params = { format };
    if (type && type.toLowerCase() !== "all") params.type = type;
    if (search) params.search = search;

    const response = await api.get(`/timeline/${patientId}/export`, {
      params,
      responseType: "blob"
    });

    const blob = new Blob([response.data], { type: response.headers["content-type"] });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    
    let filename = `timeline_${patientId}.${format}`;
    const disposition = response.headers["content-disposition"];
    if (disposition && disposition.indexOf("filename=") !== -1) {
      filename = disposition.split("filename=")[1].replace(/["']/g, "");
    }
    
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  }
};
