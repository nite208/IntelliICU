import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Clock3, Download, FileText, Database, ShieldAlert } from "lucide-react";
import { useClinicalAI } from "../../context/ClinicalAIContext";
import { timelineService } from "../../services/timelineService";
import TimelineItem from "./TimelineItem";
import TimelineFilters from "./TimelineFilters";
import TimelineSearch from "./TimelineSearch";
import TimelineDrawer from "./TimelineDrawer";

export default function ClinicalTimeline() {
  const { selectedPatient, timelineEvents } = useClinicalAI();
  const patientId = selectedPatient?.patient?.id;

  const [activeFilter, setActiveFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    if (!patientId) {
      setFilteredEvents([]);
      return;
    }

    const fetchTimeline = async () => {
      try {
        const data = await timelineService.getTimeline(patientId, activeFilter, searchQuery);
        setFilteredEvents(data || []);
      } catch (err) {
        console.error("Failed to load filtered timeline events:", err);
      }
    };

    fetchTimeline();
  }, [patientId, activeFilter, searchQuery, timelineEvents]);

  const handleOpenDetails = (event) => {
    setSelectedEvent(event);
    setDrawerOpen(true);
  };

  const handleExport = async (format) => {
    if (!patientId) return;
    try {
      await timelineService.downloadExport(patientId, format, activeFilter, searchQuery);
    } catch (err) {
      console.error("Failed to export clinical event logs:", err);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-[30px] bg-white border border-slate-200 shadow-xl p-6 flex flex-col h-full"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-50 pb-5">
        <div>
          <h2 className="text-2xl font-black text-slate-800">Clinical Event Log</h2>
          <p className="mt-1 text-xs text-slate-500">Chronological telemetry audit & actions</p>
        </div>
        <Clock3 size={24} className="text-cyan-600 animate-pulse" />
      </div>

      {/* Toolbar - Search, Filters, and Exports */}
      <div className="mt-5 space-y-4">
        <TimelineSearch value={searchQuery} onChange={setSearchQuery} />
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1 border-b border-slate-100 pb-3">
          <TimelineFilters activeFilter={activeFilter} onChangeFilter={setActiveFilter} />
          
          {/* Export Actions Group */}
          <div className="flex gap-1.5 shrink-0 self-end">
            <button
              onClick={() => handleExport("pdf")}
              disabled={!patientId}
              className="flex items-center gap-1 rounded-xl bg-red-50 hover:bg-red-100 disabled:opacity-50 text-red-700 px-3 py-1.5 text-xs font-bold transition"
              title="Export as PDF"
            >
              <FileText size={13} />
              PDF
            </button>
            <button
              onClick={() => handleExport("csv")}
              disabled={!patientId}
              className="flex items-center gap-1 rounded-xl bg-emerald-50 hover:bg-emerald-100 disabled:opacity-50 text-emerald-700 px-3 py-1.5 text-xs font-bold transition"
              title="Export as CSV"
            >
              <Download size={13} />
              CSV
            </button>
            <button
              onClick={() => handleExport("json")}
              disabled={!patientId}
              className="flex items-center gap-1 rounded-xl bg-slate-100 hover:bg-slate-200 disabled:opacity-50 text-slate-700 px-3 py-1.5 text-xs font-bold transition"
              title="Export as JSON"
            >
              <Database size={13} />
              JSON
            </button>
          </div>
        </div>
      </div>

      {/* Events Stream List */}
      <div className="mt-6 flex-1 overflow-y-auto pr-1 space-y-4 max-h-[500px] scrollbar-thin">
        {filteredEvents.length > 0 ? (
          filteredEvents.map((event, index) => (
            <TimelineItem
              key={event.id ?? index}
              event={event}
              isLast={index === filteredEvents.length - 1}
              onOpenDetails={handleOpenDetails}
            />
          ))
        ) : (
          <div className="py-16 text-center">
            <ShieldAlert size={36} className="mx-auto text-slate-300 mb-2" />
            <h4 className="font-bold text-slate-700 text-sm">No Events Found</h4>
            <p className="text-xs text-slate-400 mt-1 max-w-[200px] mx-auto">
              No matching clinical logs recorded under these filters.
            </p>
          </div>
        )}
      </div>

      {/* Event Details Slider Drawer */}
      <TimelineDrawer
        open={drawerOpen}
        event={selectedEvent}
        onClose={() => setDrawerOpen(false)}
      />
    </motion.div>
  );
}