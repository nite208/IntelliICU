/**
 * hospitalAssistantService.js
 *
 * API service for the Hospital AI Assistant (Phase 13.6).
 * Reuses the existing axios instance and SSE streaming pattern from
 * clinicalCopilotService.js.
 */

import api from "../api/axios";

const BASE = "/hospital-assistant";

export const hospitalAssistantService = {
  /** Full hospital snapshot — all patients, alerts, insights */
  getSnapshot: async () => {
    const res = await api.get(`${BASE}/snapshot`, { timeout: 30000 });
    return res.data;
  },

  /** Compact KPI summary */
  getSummary: async () => {
    const res = await api.get(`${BASE}/summary`, { timeout: 15000 });
    return res.data;
  },

  /** Active clinical alerts */
  getAlerts: async () => {
    const res = await api.get(`${BASE}/alerts`, { timeout: 15000 });
    return res.data;
  },

  /** Critical patient ranking */
  getCritical: async () => {
    const res = await api.get(`${BASE}/critical`, { timeout: 15000 });
    return res.data;
  },

  /** AI insights + recommended actions */
  getInsights: async () => {
    const res = await api.get(`${BASE}/insights`, { timeout: 15000 });
    return res.data;
  },

  /** Batch chat — returns full JSON response */
  chat: async (question, sessionId = "hospital") => {
    const res = await api.post(
      `${BASE}/chat`,
      { question, session_id: sessionId },
      { timeout: 180000 },
    );
    return res.data;
  },

  /** Streaming chat — yields SSE tokens, resolves on "final" event */
  chatStream: async (question, onToken, onFinal, sessionId = "hospital") => {
    const baseURL = api.defaults.baseURL || "/api";
    const token   = localStorage.getItem("access_token");

    const res = await fetch(`${baseURL}${BASE}/chat?stream=true`, {
      method:  "POST",
      headers: {
        "Content-Type":  "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ question, session_id: sessionId }),
    });

    if (!res.ok) throw new Error(`Hospital Assistant stream failed: HTTP ${res.status}`);

    const reader  = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer    = "";

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(trimmed.substring(6));
            if (data.type === "token")  onToken(data.content);
            if (data.type === "final")  onFinal(data.content);
          } catch {
            // Silently skip malformed chunks
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};
