import { timelineService } from "./timelineService";

export const eventEngine = {
  recordEvent: async (patientId, { type, title, description, actor = "Dr. Reyes", metadata = {} }) => {
    if (!patientId) return null;
    try {
      const event = { type, title, description, actor, metadata };
      return await timelineService.logEvent(patientId, event);
    } catch (err) {
      console.error("Failed to record timeline event:", err);
      return null;
    }
  },

  recordPatientSelected: async (patientId, patientName, actor = "Dr. Reyes") => {
    return await eventEngine.recordEvent(patientId, {
      type: "User",
      title: "Patient Selected",
      description: `Patient ${patientName} selected for clinical review.`,
      actor,
      metadata: { patient_id: patientId, name: patientName }
    });
  },

  recordVitalsUpdated: async (patientId, vitals, actor = "System") => {
    const descParts = [];
    if (vitals.heart_rate) descParts.push(`HR: ${vitals.heart_rate} bpm`);
    if (vitals.spo2) descParts.push(`SpO₂: ${vitals.spo2}%`);
    if (vitals.systolic_bp) descParts.push(`BP: ${vitals.systolic_bp}/${vitals.diastolic_bp} mmHg`);
    
    return await eventEngine.recordEvent(patientId, {
      type: "Clinical",
      title: "Vitals Telemetry Update",
      description: `Live vitals updated: ${descParts.join(", ")}.`,
      actor,
      metadata: { vitals }
    });
  },

  recordAIAnalysis: async (patientId, riskScore, riskLevel, isAuto = false, actor = "System") => {
    const mode = isAuto ? "Automatic" : "Manual";
    return await eventEngine.recordEvent(patientId, {
      type: "AI",
      title: `AI Sepsis Analysis (${mode})`,
      description: `${mode} sepsis prediction completed. Sepsis Risk Score: ${(riskScore * 100).toFixed(0)}% (${riskLevel}).`,
      actor,
      metadata: { risk_score: riskScore, risk_level: riskLevel, is_auto: isAuto }
    });
  },

  recordRiskChanged: async (patientId, oldLevel, newLevel, actor = "System") => {
    return await eventEngine.recordEvent(patientId, {
      type: "AI",
      title: "Sepsis Risk Level Changed",
      description: `Sepsis risk level transitioned from ${oldLevel} to ${newLevel}.`,
      actor,
      metadata: { old_level: oldLevel, new_level: newLevel }
    });
  },

  recordRecommendation: async (patientId, action, actor = "System") => {
    return await eventEngine.recordEvent(patientId, {
      type: "Recommendations",
      title: "Priority Recommendation",
      description: `AI recommended priority action: ${action}`,
      actor,
      metadata: { action }
    });
  },

  recordEvidenceRetrieved: async (patientId, query, actor = "System") => {
    return await eventEngine.recordEvent(patientId, {
      type: "AI",
      title: "Clinical Evidence Retrieved",
      description: `RAG search executed for: "${query}". Retaining top relevant sources.`,
      actor,
      metadata: { query }
    });
  },

  recordAlertAction: async (patientId, actionType, alertMessage, actor = "System") => {
    return await eventEngine.recordEvent(patientId, {
      type: "Alerts",
      title: `Alert ${actionType}`,
      description: `Physiological alert [${alertMessage}] has been ${actionType.toLowerCase()}.`,
      actor,
      metadata: { action_type: actionType, alert_message: alertMessage }
    });
  }
};
