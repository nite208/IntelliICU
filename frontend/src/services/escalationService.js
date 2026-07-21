import config from "../config";

export const escalationService = {
  checkEscalation: (alert, now, addAuditEvent) => {
    if (alert.status !== "ACTIVE" || alert.severity !== "CRITICAL") {
      return null;
    }

    const ageSec = (now - (alert.createdAtMs || now)) / 1000;
    let newEsc = alert.escalationLevel || null;

    if (ageSec > config.ESCALATION_L3_SECONDS && alert.escalationLevel !== "L3") {
      newEsc = "L3";
    } else if (ageSec > config.ESCALATION_L2_SECONDS && !alert.escalationLevel) {
      newEsc = "L2";
    }

    if (newEsc !== alert.escalationLevel) {
      const prevLvl = alert.escalationLevel || "L1";
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

      const timeline = [...(alert.timeline || [])];
      timeline.push({
        action: `Escalated to ${newEsc}`,
        time: timeStr,
        by: "System",
      });

      addAuditEvent(
        alert.id,
        "Escalated",
        `Alert escalated from ${prevLvl} to ${newEsc} due to no response.`,
        timeStr
      );

      return {
        ...alert,
        escalationLevel: newEsc,
        timeline,
      };
    }

    return null;
  }
};
