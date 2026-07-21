/**
 * useTelemetry.js
 *
 * Custom React hook for consuming telemetry trend data from the EXISTING
 * patient WebSocket channel.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import websocketService from "../../services/websocketService";
import config from "../../config";
import { useAuth } from "../../context/AuthContext";

const CHANNEL = "dashboard";
const WS_URL  = `${config.WS_BASE_URL}/dashboard`;

export default function useTelemetry() {
  const { user } = useAuth();
  // Map of patient_id -> telemetry_trends payload
  const [allTrends, setAllTrends] = useState({});
  const [connected, setConnected]   = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const allTrendsRef = useRef({});

  // Track last seen data from patients_update (all patients bulk payload)
  const handleMessage = useCallback((msg) => {
    if (!msg || !msg.type) return;

    if (msg.type === "patients_update" && Array.isArray(msg.data)) {
      let changed = false;
      const next = { ...allTrendsRef.current };

      msg.data.forEach((patient) => {
        if (patient.telemetry_trends && patient.id) {
          next[patient.id] = {
            patient_id:   patient.id,
            patient_name: patient.name || "",
            trends:       patient.telemetry_trends,
          };
          changed = true;
        }
      });

      if (changed) {
        allTrendsRef.current = next;
        setAllTrends(next);
        setLastUpdated(new Date());
      }
    }
  }, []);

  const handleConnected    = useCallback(() => setConnected(true), []);
  const handleDisconnected = useCallback(() => setConnected(false), []);

  useEffect(() => {
    if (!user) {
      setConnected(false);
      return;
    }

    // Connect using the shared singleton service.
    websocketService.connect(CHANNEL, WS_URL);

    websocketService.on(CHANNEL, "connected",    handleConnected);
    websocketService.on(CHANNEL, "disconnected", handleDisconnected);
    websocketService.on(CHANNEL, "message",      handleMessage);

    // Check current state
    setConnected(websocketService.isConnected(CHANNEL));

    return () => {
      websocketService.off(CHANNEL, "connected",    handleConnected);
      websocketService.off(CHANNEL, "disconnected", handleDisconnected);
      websocketService.off(CHANNEL, "message",      handleMessage);
    };
  }, [user, handleConnected, handleDisconnected, handleMessage]);

  const getPatientTrend = useCallback(
    (patientId) => allTrendsRef.current[patientId] || null,
    [],
  );

  const getAllPatientIds = useCallback(
    () => Object.keys(allTrendsRef.current),
    [],
  );

  return {
    allTrends,
    getPatientTrend,
    getAllPatientIds,
    connected,
    lastUpdated,
  };
}
