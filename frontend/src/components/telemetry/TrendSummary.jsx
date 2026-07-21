/**
 * TrendSummary.jsx
 *
 * Patient-level telemetry trend summary card.
 *
 * Displays:
 *  - Patient name + bed
 *  - Overall classification badge + deterioration score
 *  - Clinical narrative text
 *  - Mini parameter grid (7 vitals with arrow + current value)
 *
 * Props:
 *   patientId     {string}
 *   patientName   {string}
 *   trends        {object}  telemetry_trends object from patient broadcast
 *   onSelectParam {fn}      called with (paramKey, paramTrend) when a vital chip is clicked
 */

import { motion } from "framer-motion";
import { Activity, BrainCircuit } from "lucide-react";
import TrendIndicator from "./TrendIndicator";

const ARROWS = {
  RISING:      "↑",
  FALLING:     "↓",
  STABLE:      "→",
  OSCILLATING: "≈",
  SPIKE_UP:    "⇑",
  SPIKE_DOWN:  "⇓",
};

const CLASS_BG = {
  Stable:    "bg-emerald-50 border-emerald-200 text-emerald-800",
  Improving: "bg-cyan-50 border-cyan-200 text-cyan-800",
  Declining: "bg-orange-50 border-orange-200 text-orange-800",
  Critical:  "bg-red-50 border-red-300 text-red-800",
  Unknown:   "bg-slate-50 border-slate-200 text-slate-600",
};

const DET_COLOR = (score) => {
  if (score >= 0.7) return "text-red-600";
  if (score >= 0.4) return "text-orange-500";
  if (score >= 0.2) return "text-yellow-600";
  return "text-emerald-600";
};

export default function TrendSummary({ patientId, patientName, trends, onSelectParam }) {
  if (!trends) {
    return (
      <div className="clinical-card p-5 text-xs text-slate-400 font-bold flex items-center gap-2">
        <Activity size={14} className="animate-pulse" />
        Collecting telemetry data…
      </div>
    );
  }

  const {
    overall_classification,
    overall_alert_level,
    clinical_narrative,
    combined_deterioration_score,
    parameters = {},
  } = trends;

  const classBg       = CLASS_BG[overall_classification] || CLASS_BG.Unknown;
  const detScore      = combined_deterioration_score || 0;
  const detColorClass = DET_COLOR(detScore);
  const isCritical    = overall_alert_level === "CRITICAL";

  // Parameter chip list
  const paramList = Object.entries(parameters).map(([key, p]) => ({
    key,
    label:   p.label  || key,
    abbrev:  p.abbrev || key,
    current: p.current,
    unit:    p.unit || "",
    direction: p.direction || "STABLE",
    alertLevel: p.alert_level || "NORMAL",
    classification: p.classification || "Stable",
  }));

  return (
    <motion.div
      layout
      className={`clinical-card overflow-hidden border-2 ${isCritical ? "border-red-400" : "border-slate-200"}`}
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-100">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-xs font-black text-slate-800 truncate">
              {patientName || patientId}
            </p>
            <p className="text-[9px] text-slate-400 font-semibold mt-0.5">{patientId}</p>
          </div>
          <span className={`px-2.5 py-1 rounded-full border text-[10px] font-black uppercase ${classBg}`}>
            {overall_classification}
          </span>
        </div>
      </div>

      {/* Deterioration score */}
      <div className="flex items-center justify-between px-4 pt-3">
        <div className="flex items-center gap-1.5">
          <BrainCircuit size={11} className="text-slate-400" />
          <span className="text-[9px] font-black uppercase tracking-widest text-slate-400">
            Deterioration Score
          </span>
        </div>
        <span className={`text-sm font-black ${detColorClass}`}>
          {(detScore * 100).toFixed(0)}%
        </span>
      </div>
      <div className="mx-4 mt-1 mb-2 h-1.5 rounded-full bg-slate-100 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${
            detScore >= 0.7 ? "bg-red-500" :
            detScore >= 0.4 ? "bg-orange-500" :
            detScore >= 0.2 ? "bg-yellow-500" : "bg-emerald-500"
          }`}
          style={{ width: `${Math.min(detScore * 100, 100).toFixed(0)}%` }}
        />
      </div>

      {/* Clinical narrative */}
      {clinical_narrative && (
        <p className="px-4 pb-3 text-[10px] text-slate-600 font-medium leading-relaxed border-b border-slate-100">
          {clinical_narrative}
        </p>
      )}

      {/* Parameter chips */}
      <div className="p-3 grid grid-cols-2 gap-1.5">
        {paramList.map(({ key, abbrev, current, unit, direction, alertLevel, classification }) => {
          const arrow = ARROWS[direction] || "→";
          const isAlert = alertLevel === "CRITICAL" || alertLevel === "WARNING";
          return (
            <button
              key={key}
              onClick={() => onSelectParam && onSelectParam(key, parameters[key])}
              className={`
                flex items-center justify-between rounded-lg border px-2 py-1.5 text-left
                transition hover:bg-slate-50 cursor-pointer
                ${isAlert ? "border-orange-200 bg-orange-50/40" : "border-slate-100 bg-slate-50/30"}
              `}
            >
              <span className="text-[9px] font-black uppercase tracking-wide text-slate-500">
                {abbrev}
              </span>
              <div className="flex items-center gap-1">
                <span className="text-[11px] font-black text-slate-800">
                  {current != null ? current : "—"}
                  <span className="text-[8px] text-slate-400 ml-0.5">{unit}</span>
                </span>
                <span className={`text-xs ${isAlert ? "text-red-500" : "text-slate-400"}`}>
                  {arrow}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </motion.div>
  );
}
