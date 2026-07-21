export const AlertEngine = {
  evaluatePatient: (patient) => {
    const alerts = [];
    const id = patient.id;
    const name = patient.name;
    const bed = patient.bed || "-";
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    if (patient.spo2 !== undefined && patient.spo2 !== null && patient.spo2 < 90) {
      alerts.push({
        id: `${id}-spo2`,
        patient_id: id,
        patient_name: name,
        bed,
        type: "SpO₂",
        message: `Oxygen saturation critically low: ${patient.spo2}%`,
        severity: "CRITICAL",
        value: patient.spo2,
        timestamp,
      });
    }
    if (patient.systolic_bp !== undefined && patient.systolic_bp !== null && patient.systolic_bp < 90) {
      alerts.push({
        id: `${id}-sbp`,
        patient_id: id,
        patient_name: name,
        bed,
        type: "SBP",
        message: `Systolic Blood Pressure critically low: ${patient.systolic_bp} mmHg`,
        severity: "CRITICAL",
        value: patient.systolic_bp,
        timestamp,
      });
    }
    if (patient.heart_rate !== undefined && patient.heart_rate !== null && patient.heart_rate > 130) {
      alerts.push({
        id: `${id}-hr-high`,
        patient_id: id,
        patient_name: name,
        bed,
        type: "HR",
        message: `Severe tachycardia: ${patient.heart_rate} bpm`,
        severity: "HIGH",
        value: patient.heart_rate,
        timestamp,
      });
    }
    if (patient.heart_rate !== undefined && patient.heart_rate !== null && patient.heart_rate < 45) {
      alerts.push({
        id: `${id}-hr-low`,
        patient_id: id,
        patient_name: name,
        bed,
        type: "HR",
        message: `Severe bradycardia: ${patient.heart_rate} bpm`,
        severity: "HIGH",
        value: patient.heart_rate,
        timestamp,
      });
    }
    if (patient.temperature !== undefined && patient.temperature !== null && patient.temperature > 39.0) {
      alerts.push({
        id: `${id}-temp-high`,
        patient_id: id,
        patient_name: name,
        bed,
        type: "Temp",
        message: `Severe hyperthermia: ${patient.temperature}°C`,
        severity: "MEDIUM",
        value: patient.temperature,
        timestamp,
      });
    }
    if (patient.temperature !== undefined && patient.temperature !== null && patient.temperature < 35.0) {
      alerts.push({
        id: `${id}-temp-low`,
        patient_id: id,
        patient_name: name,
        bed,
        type: "Temp",
        message: `Hypothermia detected: ${patient.temperature}°C`,
        severity: "MEDIUM",
        value: patient.temperature,
        timestamp,
      });
    }
    if (patient.lactate !== undefined && patient.lactate !== null && patient.lactate > 4.0) {
      alerts.push({
        id: `${id}-lactate`,
        patient_id: id,
        patient_name: name,
        bed,
        type: "Lactate",
        message: `Critical hyperlactatemia: ${patient.lactate} mmol/L`,
        severity: "CRITICAL",
        value: patient.lactate,
        timestamp,
      });
    }
    if (patient.risk_score !== undefined && patient.risk_score !== null && patient.risk_score > 0.90) {
      alerts.push({
        id: `${id}-risk`,
        patient_id: id,
        patient_name: name,
        bed,
        type: "Risk",
        message: `Critical Sepsis AI Risk Score: ${(patient.risk_score * 100).toFixed(0)}%`,
        severity: "CRITICAL",
        value: patient.risk_score,
        timestamp,
      });
    }

    return alerts;
  }
};
