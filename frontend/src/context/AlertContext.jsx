import {
  createContext,
  useContext,
  useMemo,
  useState,
  useCallback,
} from "react";

const AlertContext = createContext(null);

export function AlertProvider({ children }) {
  const [alerts, setAlerts] = useState([]);

  const addAlert = useCallback((alert) => {
    setAlerts((prev) => [alert, ...prev]);
  }, []);

  const removeAlert = useCallback((alertId) => {
    setAlerts((prev) =>
      prev.filter((alert) => alert.id !== alertId)
    );
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  const alertCount = alerts.length;

  const criticalAlerts = useMemo(() => {
    return alerts.filter(
      (alert) =>
        alert.severity === "critical" ||
        alert.priority === "critical"
    );
  }, [alerts]);

  const value = useMemo(
    () => ({
      alerts,
      setAlerts,

      addAlert,
      removeAlert,
      clearAlerts,

      alertCount,
      criticalAlerts,
    }),
    [
      alerts,
      addAlert,
      removeAlert,
      clearAlerts,
      criticalAlerts,
    ]
  );

  return (
    <AlertContext.Provider value={value}>
      {children}
    </AlertContext.Provider>
  );
}

export function useAlert() {
  const context = useContext(AlertContext);

  if (!context) {
    throw new Error(
      "useAlert must be used inside AlertProvider."
    );
  }

  return context;
}