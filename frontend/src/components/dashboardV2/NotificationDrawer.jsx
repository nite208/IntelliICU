import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Bell,
  ShieldAlert,
  AlertTriangle,
  Activity,
  CheckCircle,
  Eye,
  Trash2,
  User,
  ArrowUpRight,
  Clock,
  History,
} from "lucide-react";
import { useClinicalAI } from "../../context/ClinicalAIContext";

const severityConfig = {
  CRITICAL: {
    icon: ShieldAlert,
    badge: "bg-red-100 text-red-800 border-red-200",
    border: "border-red-500",
  },
  HIGH: {
    icon: AlertTriangle,
    badge: "bg-orange-100 text-orange-800 border-orange-200",
    border: "border-orange-500",
  },
  MEDIUM: {
    icon: Activity,
    badge: "bg-yellow-100 text-yellow-800 border-yellow-200",
    border: "border-yellow-500",
  },
};

export default function NotificationDrawer({ open, onClose }) {
  const {
    alertsHistory = [],
    acknowledgeAlert,
    resolveAlert,
    assignAlert,
    escalateAlert,
    clearResolvedAlerts,
    alertCount,
    alertAnalytics,
  } = useClinicalAI();

  const [activeFilter, setActiveFilter] = useState("all");
  const [showTimelineId, setShowTimelineId] = useState(null);

  const filteredAlerts = useMemo(() => {
    return alertsHistory.filter((alert) => {
      if (activeFilter === "all") return true;
      if (activeFilter === "critical") return alert.severity === "CRITICAL";
      if (activeFilter === "high") return alert.severity === "HIGH";
      if (activeFilter === "medium") return alert.severity === "MEDIUM";
      if (activeFilter === "active") return alert.status === "ACTIVE";
      if (activeFilter === "acknowledged") return alert.status === "ACKNOWLEDGED";
      if (activeFilter === "resolved") return alert.status === "RESOLVED";
      return true;
    }).sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }, [alertsHistory, activeFilter]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.4 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black"
          />

          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 z-50 h-full w-[460px] bg-white shadow-2xl flex flex-col"
          >
            {/* Header */}
            <div className="p-6 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Bell className="text-slate-700" size={24} />
                  {alertCount > 0 && (
                    <span className="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white">
                      {alertCount}
                    </span>
                  )}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-800">Notification Center</h2>
                  <p className="text-xs text-slate-500">ICU Sepsis & Physiological Alerts</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-slate-50 rounded-xl transition text-slate-400 hover:text-slate-600"
              >
                <X size={20} />
              </button>
            </div>

            {/* Analytics Stats Grid */}
            {alertAnalytics && (
              <div className="grid grid-cols-3 border-b border-slate-100 bg-slate-50/50 p-4 text-center">
                <div>
                  <div className="text-sm font-black text-slate-800">{alertAnalytics.ackRate}</div>
                  <div className="text-[9px] font-semibold text-slate-500 uppercase tracking-wider">Ack Rate</div>
                </div>
                <div>
                  <div className="text-sm font-black text-slate-800">{alertAnalytics.avgResponseTime}</div>
                  <div className="text-[9px] font-semibold text-slate-500 uppercase tracking-wider">Avg Response</div>
                </div>
                <div>
                  <div className="text-sm font-black text-slate-800">{alertAnalytics.escalated}</div>
                  <div className="text-[9px] font-semibold text-slate-500 uppercase tracking-wider">Escalated</div>
                </div>
              </div>
            )}

            {/* Filters Slider */}
            <div className="p-4 border-b border-slate-100 overflow-x-auto flex gap-2 scrollbar-none">
              {[
                { id: "all", label: "All" },
                { id: "critical", label: "Critical" },
                { id: "high", label: "High" },
                { id: "medium", label: "Medium" },
                { id: "active", label: "Active" },
                { id: "acknowledged", label: "Acked" },
                { id: "resolved", label: "Resolved" },
              ].map(f => (
                <button
                  key={f.id}
                  onClick={() => setActiveFilter(f.id)}
                  className={`rounded-lg px-2.5 py-1.5 text-xs font-bold transition whitespace-nowrap ${
                    activeFilter === f.id
                      ? "bg-slate-900 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {/* Notifications Timeline List */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              <AnimatePresence initial={false}>
                {filteredAlerts.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    className="h-full flex flex-col items-center justify-center text-center py-20"
                  >
                    <CheckCircle className="text-emerald-500 mb-3 animate-pulse" size={40} />
                    <h3 className="font-bold text-slate-800 text-lg">Clear System</h3>
                    <p className="text-sm text-slate-500 mt-1">No alerts matching active criteria.</p>
                  </motion.div>
                ) : (
                  filteredAlerts.map((alert) => {
                    const sev = severityConfig[alert.severity] || severityConfig.MEDIUM;
                    const Icon = sev.icon;
                    const isExpanded = showTimelineId === alert.id;

                    return (
                      <motion.div
                        key={alert.id}
                        layout
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className={`rounded-2xl border p-4 transition relative flex gap-3 ${
                          alert.status === "RESOLVED"
                            ? "bg-slate-50/50 border-slate-100 opacity-60"
                            : "bg-white border-slate-200 shadow-md hover:shadow-lg"
                        }`}
                      >
                        <div className={`w-1 rounded-full ${
                          alert.severity === "CRITICAL" ? "bg-red-500" :
                          alert.severity === "HIGH" ? "bg-orange-500" : "bg-yellow-500"
                        }`} />

                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <span className={`text-[9px] font-extrabold uppercase px-2 py-0.5 rounded-full ${sev.badge}`}>
                              {alert.severity} {alert.escalationLevel ? `| ${alert.escalationLevel}` : ""}
                            </span>
                            <span className="text-[10px] text-slate-400 font-medium">
                              {alert.createdAt}
                            </span>
                          </div>

                          <h4 className="font-bold text-slate-800 mt-2">
                            {alert.patient_name} <span className="text-slate-500 text-xs font-semibold">({alert.bed})</span>
                          </h4>

                          <p className="text-xs text-slate-600 mt-1">
                            {alert.message}
                          </p>

                          {/* Owner / Escalation Metadata Row */}
                          <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-500 bg-slate-50 p-2 rounded-lg">
                            <div className="flex items-center gap-1.5">
                              <User size={12} className="text-slate-400" />
                              <span>Assignee: <strong>{alert.assignedTo || "Unassigned"}</strong></span>
                            </div>
                            {alert.status === "ACTIVE" && alert.severity === "CRITICAL" && (
                              <button
                                onClick={() => escalateAlert(alert.id)}
                                className="flex items-center gap-1 text-[10px] font-bold text-red-600 hover:text-red-700 bg-red-50 px-1.5 py-0.5 rounded transition"
                              >
                                <ArrowUpRight size={10} /> Escalate
                              </button>
                            )}
                          </div>

                          {/* Action Buttons Row */}
                          <div className="mt-3 flex items-center justify-between gap-3 pt-3 border-t border-slate-50">
                            <div className="flex gap-2">
                              <button
                                onClick={() => setShowTimelineId(isExpanded ? null : alert.id)}
                                className="flex items-center gap-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 text-[10px] font-bold transition"
                              >
                                <History size={11} />
                                Timeline
                              </button>
                              
                              {alert.status === "ACTIVE" && (
                                <button
                                  onClick={() => acknowledgeAlert(alert.id)}
                                  className="flex items-center gap-1 rounded-lg bg-cyan-50 hover:bg-cyan-100 text-cyan-700 px-2 py-1 text-[10px] font-bold transition"
                                >
                                  <Eye size={11} />
                                  Ack
                                </button>
                              )}
                              
                              {alert.status !== "RESOLVED" && (
                                <button
                                  onClick={() => resolveAlert(alert.id)}
                                  className="flex items-center gap-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 px-2 py-1 text-[10px] font-bold transition"
                                >
                                  <CheckCircle size={11} />
                                  Resolve
                                </button>
                              )}
                            </div>

                            {/* Assignee selection */}
                            {alert.status !== "RESOLVED" && (
                              <select
                                value={alert.assignedTo || ""}
                                onChange={(e) => assignAlert(alert.id, e.target.value)}
                                className="text-[10px] font-semibold border rounded px-1 py-0.5 bg-white text-slate-600 outline-none"
                              >
                                <option value="Dr. Reyes">Dr. Reyes</option>
                                <option value="Dr. Miller">Dr. Miller</option>
                                <option value="Nurse Kelly">Nurse Kelly</option>
                              </select>
                            )}
                          </div>

                          {/* Expanded Alert Timeline View */}
                          {isExpanded && alert.timeline && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: "auto" }}
                              exit={{ opacity: 0, height: 0 }}
                              className="mt-3 pt-3 border-t border-dashed border-slate-100 text-[10px] space-y-1.5"
                            >
                              <p className="font-bold text-slate-500 mb-1">Alert Trail Logs:</p>
                              {alert.timeline.map((step, idx) => (
                                <div key={idx} className="flex justify-between text-slate-500 pl-1.5 border-l border-slate-200">
                                  <span>{step.action} by <strong>{step.by}</strong></span>
                                  <span className="text-slate-400">{step.time}</span>
                                </div>
                              ))}
                            </motion.div>
                          )}
                        </div>
                      </motion.div>
                    );
                  })
                )}
              </AnimatePresence>
            </div>

            {alertsHistory.some(a => a.status === "RESOLVED") && (
              <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex justify-end">
                <button
                  onClick={clearResolvedAlerts}
                  className="flex items-center gap-1.5 rounded-xl bg-slate-200 hover:bg-slate-300 text-slate-700 px-4 py-2 text-xs font-extrabold transition"
                >
                  <Trash2 size={14} />
                  Clear Resolved Alerts
                </button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
