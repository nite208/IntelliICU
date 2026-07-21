import {
  createContext,
  useContext,
  useMemo,
  useState,
  useCallback,
} from "react";

const DashboardContext = createContext(null);

export function DashboardProvider({ children }) {
  const [connected, setConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [loading, setLoading] = useState(false);

  const updateConnection = useCallback((status) => {
    setConnected(status);
  }, []);

  const updateLastUpdated = useCallback((time) => {
    setLastUpdated(time);
  }, []);

  const value = useMemo(
    () => ({
      connected,
      lastUpdated,
      loading,
      setLoading,
      updateConnection,
      updateLastUpdated,
    }),
    [
      connected,
      lastUpdated,
      loading,
      updateConnection,
      updateLastUpdated,
    ]
  );

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard() {
  const context = useContext(DashboardContext);

  if (!context) {
    throw new Error(
      "useDashboard must be used inside DashboardProvider."
    );
  }

  return context;
}