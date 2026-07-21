import { useEffect, useState } from "react";
import websocketService from "../services/websocketService";
import config from "../config";

export default function useWebSocket() {
  const [dashboardData, setDashboardData] = useState(null);
  const [patientsData, setPatientsData] = useState([]);
  const [alertsData, setAlertsData] = useState([]);

  useEffect(() => {
    const dashboardUrl = `${config.WS_BASE_URL}/dashboard`;

    const handleMessage = (message) => {
      if (!message || !message.type) return;
      switch (message.type) {
        case "dashboard_update":
          setDashboardData(message.data);
          break;

        case "patients_update":
          setPatientsData(message.data);
          break;

        case "alerts_update":
          setAlertsData(message.data);
          break;

        default:
          break;
      }
    };

    websocketService.on("dashboard", "message", handleMessage);

    // Ensure the dashboard channel is connected — connect() is idempotent
    // (it returns immediately if the socket is already OPEN or CONNECTING).
    websocketService.connect("dashboard", dashboardUrl);

    return () => {
      websocketService.off("dashboard", "message", handleMessage);
      // Do NOT call disconnect() here — ClinicalAIContext also subscribes to
      // this same "dashboard" channel. Disconnecting from this hook would kill
      // the socket for all other subscribers too.
    };
  }, []);

  return {
    dashboardData,
    patientsData,
    alertsData,
  };
}