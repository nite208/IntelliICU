/**
 * TrendAlerts.jsx
 *
 * Active Trend Alerts Panel.
 *
 * Shows parameters currently at WARNING or CRITICAL alert level across
 * all tracked patients, pulled from the live useTelemetry hook.
 *
 * Props:
 *   allTrends   {object}  Map of patient_id -> { trends, patient_name } from useTelemetry
 *   maxItems    {number}  Default 20
 */

import { AlertTriangle, AlertCircle, Siren } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import TrendIndicator from "./TrendIndicator";

function AlertRow({ patientId, patientName, param, trend }) {
  const al       = trend.alert_level || "NORMAL";
  const isCrit   = al === "CRITICAL";
  const bgClass  = isCrit ? "bg-red-50/80 border-red-300" : "bg-orange-50/60 border-orange-200";
  const Icon     = isCrit ? Siren : AlertTriangle;
  const iconColor= isCrit ? "text-red-500" : "text-orange-500";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      className={`rounded-xl border p-3 ${bgClass}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2">
          <Icon size={13} className={`${iconColor} mt-0.5 shrink-0 ${isCrit ? "animate-pulse" : ""}`} />
          <div>
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[10px] font-black text-slate-800">{trend.label || param}</span>
              <span className="text-[9px] font-semibold text-slate-400">— {patientName || patientId}</span>
            </div>
            <p className="text-[10px] font-semibold text-slate-600 mt-0.5 leading-relaxed">
              {trend.interpretation}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <span className={`text-base font-black ${isCrit ? "text-red-600" : "text-orange-600"}`}>
            {trend.current} <span className="text-xs font-bold text-slate-400">{trend.unit}</span>
          </span>
          <TrendIndicator
            direction={trend.direction}
            alertLevel={al}
            classification={trend.classification}
            size="sm"
          />
        </div>
      </div>
    </motion.div>
  );
}

export default function TrendAlerts({ allTrends = {}, maxItems = 20 }) {
  // Flatten all patient trends into individual alert rows
  const alertRows = [];

  Object.entries(allTrends).forEach(([patientId, patientData]) => {
    const trends = patientData?.trends?.parameters || {};
    const name   = patientData?.patient_name || patientId;

    Object.entries(trends).forEach(([param, trend]) => {
      const al = trend?.alert_level;
      if (al === "CRITICAL" || al === "WARNING") {
        alertRows.push({ patientId, patientName: name, param, trend, _severity: al === "CRITICAL" ? 2 : 1 });
      }
    });
  });

  // Sort: CRITICAL first, then WARNING, then by patient ID
  alertRows.sort((a, b) => b._severity - a._severity);
  const visible = alertRows.slice(0, maxItems);

  if (!visible.length) {
    return (
      <div className="clinical-card p-6 flex flex-col items-center justify-center h-32">
        <AlertCircle size={20} className="text-emerald-400 mb-2" />
        <p className="text-xs font-bold text-slate-400">No active trend alerts.</p>
      </div>
    );
  }

  const critCount = alertRows.filter((r) => r._severity === 2).length;
  const warnCount = alertRows.filter((r) => r._severity === 1).length;

  return (
    <div className="clinical-card overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Siren size={15} className="text-red-500 animate-pulse" />
          <h3 className="text-sm font-black text-slate-800">Active Trend Alerts</h3>
        </div>
        <div className="flex items-center gap-2">
          {critCount > 0 && (
            <span className="badge-clinical-danger">{critCount} CRITICAL</span>
          )}
          {warnCount > 0 && (
            <span className="badge-clinical-warning">{warnCount} WARNING</span>
          )}
        </div>
      </div>

      {/* Alert list */}
      <div className="p-4 space-y-2 max-h-96 overflow-y-auto">
        <AnimatePresence>
          {visible.map((row, idx) => (
            <AlertRow key={`${row.patientId}-${row.param}-${idx}`} {...row} />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
