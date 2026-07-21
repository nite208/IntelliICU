import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

import { timelineService } from "../services/timelineService";

const TimelineContext = createContext(null);

export function TimelineProvider({ children }) {
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadTimeline = useCallback(async (patientId) => {
    try {
      setLoading(true);

      const data = await timelineService.getTimeline(patientId);

      setTimelineEvents(data || []);
    } catch (err) {
      console.error("Timeline loading failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const addTimelineEvent = useCallback((event) => {
    setTimelineEvents((prev) => [event, ...prev]);
  }, []);

  const clearTimeline = useCallback(() => {
    setTimelineEvents([]);
  }, []);

  const value = useMemo(
    () => ({
      timelineEvents,
      loading,

      loadTimeline,
      addTimelineEvent,
      clearTimeline,

      setTimelineEvents,
    }),
    [timelineEvents, loading, loadTimeline, addTimelineEvent, clearTimeline]
  );

  return (
    <TimelineContext.Provider value={value}>
      {children}
    </TimelineContext.Provider>
  );
}

export function useTimeline() {
  const context = useContext(TimelineContext);

  if (!context) {
    throw new Error("useTimeline must be used inside TimelineProvider.");
  }

  return context;
}