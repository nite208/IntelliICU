import api from "../api/axios";

export const clinicalCopilotService = {
  askQuestion: async (patientId, question) => {
    const response = await api.post(
      "/clinical-copilot/chat",
      {
        patient_id: patientId,
        question,
      },
      {
        timeout: 180000,
      }
    );

    return response.data;
  },

  askQuestionStream: async (
    patientId,
    question,
    onToken,
    onFinal
  ) => {
    const baseURL = api.defaults.baseURL || "/api";
    const accessToken = localStorage.getItem("access_token");

    const headers = {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    };

    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`;
    }

    const response = await fetch(
      `${baseURL}/clinical-copilot/chat?stream=true`,
      {
        method: "POST",
        headers,
        body: JSON.stringify({
          patient_id: patientId,
          question,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(
        `Inference stream connection failed: HTTP ${response.status}`
      );
    }

    if (!response.body) {
      throw new Error(
        "Streaming response body is unavailable."
      );
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, {
          stream: true,
        });

        const lines = buffer.split("\n");

        // Preserve incomplete SSE line for next chunk
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();

          if (!trimmed.startsWith("data: ")) {
            continue;
          }

          try {
            const data = JSON.parse(
              trimmed.substring(6)
            );

            if (data.type === "token") {
              onToken?.(data.content);
            } else if (data.type === "final") {
              onFinal?.(data.content);
            }
          } catch (error) {
            console.warn(
              "Failed to parse SSE JSON chunk:",
              trimmed,
              error
            );
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};