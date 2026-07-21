import {
  createContext,
  useContext,
  useMemo,
  useState,
  useEffect,
  useRef,
} from "react";
import { aiService } from "../services/aiService";
import websocketService from "../services/websocketService";
import config from "../config";
import { patientService } from "../services/patientService";
import { AlertEngine } from "../services/alertEngine";
import { auditService } from "../services/auditService";
import { escalationService } from "../services/escalationService";
import { alertAnalyticsService } from "../services/alertAnalytics";
import { timelineService } from "../services/timelineService";
import { eventEngine } from "../services/eventEngine";
import { useAuth } from "./AuthContext";
import { usePatient } from "./PatientContext";
import { useAlert } from "./AlertContext";
import { useDashboard } from "./DashboardContext";
import { useTimeline } from "./TimelineContext";

const ClinicalAIContext = createContext();

function buildAnalysisPayload(selectedPatient) {
  const patient = selectedPatient?.patient || {};
  const admission = selectedPatient?.admission || {};
  const vitals = selectedPatient?.vitals || {};
  const labs = selectedPatient?.labs || {};

  return {
    patient: {
      id: patient.id,
      name: patient.name,
      age: patient.age,
      gender: patient.gender,
    },
    admission: {
      bed: admission.bed || patient.bed || "-",
      diagnosis: admission.diagnosis || "Septic Shock",
    },
    vitals: {
      heart_rate: vitals.heart_rate ?? 132,
      systolic_bp: vitals.blood_pressure?.systolic ?? vitals.systolic_bp ?? 82,
      diastolic_bp: vitals.blood_pressure?.diastolic ?? vitals.diastolic_bp ?? 48,
      respiratory_rate: vitals.respiratory_rate ?? 31,
      spo2: vitals.spo2 ?? 89,
      temperature: vitals.temperature ?? 39.2,
    },
    labs: {
      lactate: parseFloat(labs.Lactate || labs.lactate) || 4.6,
      wbc: parseFloat(labs.WBC || labs.wbc) || 18.2,
      creatinine: parseFloat(labs.Creatinine || labs.creatinine) || 2.1,
    },
    prediction: {
      risk_score: patient.risk_score,
      risk_level: patient.risk_level,
    },
  };
}

function hasPayloadChanged(p1, p2) {
  if (!p1 || !p2) return true;
  return (
    p1.vitals.heart_rate !== p2.vitals.heart_rate ||
    p1.vitals.systolic_bp !== p2.vitals.systolic_bp ||
    p1.vitals.diastolic_bp !== p2.vitals.diastolic_bp ||
    p1.vitals.spo2 !== p2.vitals.spo2 ||
    p1.vitals.temperature !== p2.vitals.temperature ||
    p1.vitals.respiratory_rate !== p2.vitals.respiratory_rate ||
    p1.labs.lactate !== p2.labs.lactate ||
    p1.prediction.risk_score !== p2.prediction.risk_score
  );
}

export function ClinicalAIProvider({ children }) {
  const { user } = useAuth();
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState(null);
  const [auditTrail, setAuditTrail] = useState([]);
  
  const {
    selectedPatient,
    setSelectedPatient,
    patientsList,
    setPatientsList,
  } = usePatient();
  const {
     alerts,
     setAlerts,
     alertCount,
     criticalAlerts,
     addAlert,
     removeAlert,
     clearAlerts,
    } = useAlert();
    const {
      connected,
      updateConnection,
      lastUpdated,
      updateLastUpdated,
      loading,
      setLoading,
    } = useDashboard();
    const {
      timelineEvents,
      setTimelineEvents,
      addTimelineEvent,
      clearTimeline,
    } = useTimeline();

  const loadTimeline = async (patientId) => {
    try {
      const data = await timelineService.getTimeline(patientId);
      setTimelineEvents(data || []);
    } catch (err) {
      console.error("Failed to load patient timeline:", err);
    }
  };

  const lastAnalyzedRef = useRef(null);
  const recommendationRef = useRef(null);
  const debounceTimerRef = useRef(null);
  const activeRequestRef = useRef(null);

  const addAuditEvent = (alertId, action, detail, time) => {
    const event = auditService.createEvent(alertId, action, detail, time);
    setAuditTrail(prev => [...prev, event]);
  };

  // Subscribe to dashboard updates for live patient list
  useEffect(() => {
    if (!user) return;

    const dashboardUrl = `${config.WS_BASE_URL}/dashboard`;
    websocketService.connect("dashboard", dashboardUrl);

    const handleMessage = (message) => {
      if (message?.type === "patients_update") {
        setPatientsList(message.data || []);
      }
    };

    websocketService.on("dashboard", "message", handleMessage);
    return () => {
      websocketService.off("dashboard", "message", handleMessage);
      websocketService.disconnect("dashboard");
    };
  }, [user]);

  // Real-time evaluation of patient alerts with state history and auto-resolve
  useEffect(() => {
    if (!patientsList || patientsList.length === 0) return;

    let currentLiveAlerts = [];
    patientsList.forEach(patient => {
      const patientAlerts = AlertEngine.evaluatePatient(patient);
      currentLiveAlerts = [...currentLiveAlerts, ...patientAlerts];
    });

    setAlerts(prev => {
      const updated = prev.map(a => ({ ...a }));
      const liveIds = new Set(currentLiveAlerts.map(a => a.id));

      // 1. Auto-resolve
      updated.forEach(alert => {
        if ((alert.status === "ACTIVE" || alert.status === "ACKNOWLEDGED") && !liveIds.has(alert.id)) {
          alert.status = "RESOLVED";
          alert.resolvedAt = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          alert.resolvedAtMs = Date.now();
          alert.timeline = [...(alert.timeline || []), {
            action: "Resolved (Auto)",
            time: alert.resolvedAt,
            by: "System",
          }];

        }
      });

      // 2. Add new
      currentLiveAlerts.forEach(liveAlert => {
        const existingIndex = updated.findIndex(a => a.id === liveAlert.id);
        if (existingIndex === -1) {
          const timestamp = liveAlert.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          updated.push({
            ...liveAlert,
            status: "ACTIVE",
            createdAt: timestamp,
            createdAtMs: Date.now(),
            assignedTo: "Dr. Reyes",
            timeline: [{
              action: "Created",
              time: timestamp,
              by: "System",
            }],
          });

          addAuditEvent(
            liveAlert.id,
            "Created",
            `System generated alert: ${liveAlert.message} for ${liveAlert.patient_name}`,
            timestamp
          );
        }
      });

      return updated;
    });
  }, [patientsList]);

  // Escalation engine effect running in background checking unacknowledged critical alerts
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setAlerts(prev => {
        let changed = false;
        const updated = prev.map(alert => {
          const escalated = escalationService.checkEscalation(alert, now, addAuditEvent);
          if (escalated) {
            changed = true;
            return escalated;
          }
          return alert;
        });

        return changed ? updated : prev;
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const activeAlerts = useMemo(() => alerts.filter(a => a.status === "ACTIVE" || a.status === "ACKNOWLEDGED"), [alerts]);
  const criticalCount = useMemo(() => activeAlerts.filter(a => a.severity === "CRITICAL" && a.status === "ACTIVE").length, [activeAlerts]);
  const escalatedAlerts = useMemo(() => alerts.filter(a => a.escalationLevel && a.status !== "RESOLVED"), [alerts]);

  const alertAnalytics = useMemo(() => {
    return alertAnalyticsService.calculateAnalytics(alerts);
  }, [alerts]);

  const acknowledgeAlert = (alertId, user = "Dr. Reyes") => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const alertItem = alerts.find(a => a.id === alertId);
    if (alertItem) {
      eventEngine.recordAlertAction(alertItem.patient_id, "Acknowledged", alertItem.message, user);
    }
    setAlerts(prev => prev.map(a => {
      if (a.id !== alertId) return a;
      return {
        ...a,
        status: "ACKNOWLEDGED",
        acknowledgedBy: user,
        acknowledgedAtMs: Date.now(),
        timeline: [...(a.timeline || []), {
          action: "Acknowledged",
          time: timeStr,
          by: user,
        }],
      };
    }));

    addAuditEvent(alertId, "Acknowledged", `${user} acknowledged alert ${alertId}`, timeStr);
  };

  const resolveAlert = (alertId, user = "Dr. Reyes") => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const alertItem = alerts.find(a => a.id === alertId);
    if (alertItem) {
      eventEngine.recordAlertAction(alertItem.patient_id, "Resolved", alertItem.message, user);
    }
    setAlerts(prev => prev.map(a => {
      if (a.id !== alertId) return a;
      return {
        ...a,
        status: "RESOLVED",
        resolvedBy: user,
        resolvedAt: timeStr,
        resolvedAtMs: Date.now(),
        timeline: [...(a.timeline || []), {
          action: "Resolved",
          time: timeStr,
          by: user,
        }],
      };
    }));

    addAuditEvent(alertId, "Resolved", `${user} resolved alert ${alertId}`, timeStr);
  };

  const assignAlert = (alertId, assignee, user = "Dr. Reyes") => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const alertItem = alerts.find(a => a.id === alertId);
    if (alertItem) {
      eventEngine.recordAlertAction(alertItem.patient_id, `Assigned to ${assignee}`, alertItem.message, user);
    }
    setAlerts(prev => prev.map(a => {
      if (a.id !== alertId) return a;
      return {
        ...a,
        assignedTo: assignee,
        timeline: [...(a.timeline || []), {
          action: `Assigned to ${assignee}`,
          time: timeStr,
          by: user,
        }],
      };
    }));

    addAuditEvent(alertId, "Assigned", `${user} assigned alert ${alertId} to ${assignee}`, timeStr);
  };

  const escalateAlert = (alertId, user = "Dr. Reyes") => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const alertItem = alerts.find(a => a.id === alertId);
    if (alertItem) {
      const nextLvl = alertItem.escalationLevel === "L2" ? "L3" : "L2";
      eventEngine.recordAlertAction(alertItem.patient_id, `Escalated to ${nextLvl} (Manual)`, alertItem.message, user);
    }
    setAlerts(prev => prev.map(a => {
      if (a.id !== alertId) return a;
      const nextLvl = a.escalationLevel === "L2" ? "L3" : "L2";
      return {
        ...a,
        escalationLevel: nextLvl,
        timeline: [...(a.timeline || []), {
          action: `Escalated to ${nextLvl} (Manual)`,
          time: timeStr,
          by: user,
        }],
      };
    }));

    addAuditEvent(alertId, "Escalated (Manual)", `${user} manually escalated alert ${alertId}`, timeStr);
  };

  const clearResolvedAlerts = () => {
    setAlerts(prev => prev.filter(a => a.status !== "RESOLVED"));
  };

  const patientId = selectedPatient?.patient?.id;
  const channel = useMemo(() => {
    return patientId ? `patient_${patientId}` : "patient";
  }, [patientId]);

  useEffect(() => {
    lastAnalyzedRef.current = null;
    recommendationRef.current = null;
    activeRequestRef.current = null;
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    if (patientId) {
      loadTimeline(patientId);
      const name = selectedPatient?.patient?.name || "Unknown";
      eventEngine.recordPatientSelected(patientId, name).then(() => {
        loadTimeline(patientId);
      });
    } else {
      setTimelineEvents([]);
    }
  }, [patientId]);

  const runAutoAnalysis = async (payload) => {
    const requestId = Math.random().toString(36).substring(7);
    activeRequestRef.current = requestId;

    try {
      setError(null);

      const result = await aiService.analyzePatient(payload);

      if (activeRequestRef.current === requestId) {
        if (JSON.stringify(result) !== JSON.stringify(recommendationRef.current)) {
          recommendationRef.current = result;
          setRecommendation(result);
        }
        lastAnalyzedRef.current = payload;
        eventEngine.recordAIAnalysis(patientId, payload.prediction.risk_score, payload.prediction.risk_level, true).then(() => {
          loadTimeline(patientId);
        });
      }
    } catch (err) {
      if (activeRequestRef.current === requestId) {
        console.error("ClinicalAI auto-analyze error:", err);
      }
    }
  };

  const scheduleAutoAnalysis = (payload) => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    debounceTimerRef.current = setTimeout(() => {
      runAutoAnalysis(payload);
    }, 3000);
  };

  useEffect(() => {
    if (!user || !patientId) {
      updateConnection(false);
      return;
    }

    const wsUrl = `${config.WS_BASE_URL}/patient/${patientId}`;

    const handleConnected = () => {
      updateConnection(true);
    };

    const handleDisconnected = () => {
      updateConnection(false);
    };

    const handlePatientUpdate = (message) => {
      if (message?.type === "timeline_event") {
        setTimelineEvents(prev => {
          if (prev.some(e => e.id === message.data.id)) return prev;
          return [message.data, ...prev];
        });
        return;
      }

      if (!message?.data) return;

      updateLastUpdated(message.timestamp ?? new Date().toLocaleTimeString());

      setSelectedPatient(prev => {
        if (!prev || prev.patient?.id !== message.data.id) return prev;
        
        // Compare only telemetry fields
        const hrChanged = message.data.heart_rate !== undefined && message.data.heart_rate !== prev.vitals?.heart_rate;
        const spo2Changed = message.data.spo2 !== undefined && message.data.spo2 !== prev.vitals?.spo2;
        const tempChanged = message.data.temperature !== undefined && message.data.temperature !== prev.vitals?.temperature;
        const rrChanged = message.data.respiratory_rate !== undefined && message.data.respiratory_rate !== prev.vitals?.respiratory_rate;
        const sysBpChanged = message.data.systolic_bp !== undefined && message.data.systolic_bp !== prev.vitals?.blood_pressure?.systolic;
        const diaBpChanged = message.data.diastolic_bp !== undefined && message.data.diastolic_bp !== prev.vitals?.blood_pressure?.diastolic;
        const lactateChanged = message.data.lactate !== undefined && message.data.lactate !== prev.labs?.lactate;
        
        const scoreChanged = message.data.risk_score !== undefined && message.data.risk_score !== prev.patient?.risk_score;
        const levelChanged = message.data.risk_level !== undefined && message.data.risk_level !== prev.patient?.risk_level;
        const statusChanged = message.data.status !== undefined && message.data.status !== prev.patient?.status;

        const anyChanged = hrChanged || spo2Changed || tempChanged || rrChanged || sysBpChanged || diaBpChanged || lactateChanged || scoreChanged || levelChanged || statusChanged;

        if (!anyChanged) {
          return prev;
        }

        const updated = {
          ...prev,
          patient: {
            ...prev.patient,
            status: message.data.status ?? prev.patient.status,
            risk_score: message.data.risk_score ?? prev.patient.risk_score,
            risk_level: message.data.risk_level ?? prev.patient.risk_level,
          },
          vitals: {
            ...prev.vitals,
            heart_rate: message.data.heart_rate ?? prev.vitals.heart_rate,
            spo2: message.data.spo2 ?? prev.vitals.spo2,
            temperature: message.data.temperature ?? prev.vitals.temperature,
            respiratory_rate: message.data.respiratory_rate ?? prev.vitals.respiratory_rate,
            blood_pressure: {
              ...prev.vitals.blood_pressure,
              systolic: message.data.systolic_bp ?? prev.vitals.blood_pressure?.systolic,
              diastolic: message.data.diastolic_bp ?? prev.vitals.blood_pressure?.diastolic,
            }
          },
          labs: {
            ...prev.labs,
            Lactate: message.data.lactate ? `${message.data.lactate} mmol/L` : prev.labs?.Lactate,
            lactate: message.data.lactate ?? prev.labs?.lactate,
          }
        };

        const payload = buildAnalysisPayload(updated);

        if (hasPayloadChanged(payload, lastAnalyzedRef.current)) {
          scheduleAutoAnalysis(payload);
        }

        return updated;
      });
    };

    updateConnection(websocketService.isConnected(channel));

    websocketService.on(channel, "connected", handleConnected);
    websocketService.on(channel, "disconnected", handleDisconnected);
    websocketService.on(channel, "patient_update", handlePatientUpdate);

    websocketService.connect(channel, wsUrl);

    return () => {
      websocketService.off(channel, "connected", handleConnected);
      websocketService.off(channel, "disconnected", handleDisconnected);
      websocketService.off(channel, "patient_update", handlePatientUpdate);
      websocketService.disconnect(channel);
    };
  }, [user, patientId, channel]);

  async function analyzePatient(payload) {
    try {
      setLoading(true);
      setError(null);

      if (!payload || !payload.patient?.id) {
        throw new Error("Invalid patient analysis payload provided.");
      }

      const requestId = Math.random().toString(36).substring(7);
      activeRequestRef.current = requestId;

      const result = await aiService.analyzePatient(payload);

      if (activeRequestRef.current === requestId) {
        if (JSON.stringify(result) !== JSON.stringify(recommendationRef.current)) {
          recommendationRef.current = result;
          setRecommendation(result);
        }
        lastAnalyzedRef.current = payload;
        eventEngine.recordAIAnalysis(patientId, payload.prediction.risk_score, payload.prediction.risk_level, false).then(() => {
          loadTimeline(patientId);
        });
      }
      return result;
    } catch (err) {
      console.error("ClinicalAI manual analyze error:", err);
      let errMsg = "AI analysis failed.";
      
      if (err.message === "Invalid patient analysis payload provided.") {
        errMsg = err.message;
      } else if (err.response) {
        errMsg = err.response.data?.detail || `Server error (${err.response.status}): Analysis failed.`;
      } else if (err.request) {
        errMsg = "Connection to Clinical AI server timed out or failed. Please check your backend service.";
      } else if (err.message) {
        errMsg = err.message;
      }

      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  function clearAnalysis() {
    recommendationRef.current = null;
    setRecommendation(null);
    setError(null);
  }

  const value = useMemo(
    () => ({
      selectedPatient,
      setSelectedPatient,

      recommendation,
      setRecommendation,

      analyzePatient,
      clearAnalysis,

      loading,
      error,

      patientsList,
      setPatientsList,
      connected,
      lastUpdated,
      activeAlerts,
      alertCount,
      criticalCount,
      alertsHistory: alerts,
      acknowledgeAlert,
      resolveAlert,
      clearResolvedAlerts,
      auditTrail,
      escalatedAlerts,
      alertAnalytics,
      assignAlert,
      escalateAlert,
      timelineEvents,
      loadTimeline,
      setTimelineEvents,
    }),
    [
      selectedPatient,
      recommendation,
      loading,
      error,
      patientsList,
      connected,
      lastUpdated,
      activeAlerts,
      alertCount,
      criticalCount,
      auditTrail,
      escalatedAlerts,
      alertAnalytics,
      timelineEvents,
    ]
  );

  return (
    <ClinicalAIContext.Provider value={value}>
      {children}
    </ClinicalAIContext.Provider>
  );
}

export function useClinicalAI() {
  const context = useContext(ClinicalAIContext);

  if (!context) {
    throw new Error(
      "useClinicalAI must be used inside ClinicalAIProvider."
    );
  }

  return context;
}