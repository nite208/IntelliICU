/**
 * TrendTimeline.jsx
 *
 * Chronological ICU trend event timeline.
 *
 * Displays sorted timeline events from the telemetry summary.
 * Events are grouped by alert level severity and time-stamped.
 * CRITICAL events pulsate red.
 *
 * Props:
 *   timeline     {array}   Array of timeline event objects from TrendSummary
 *   maxItems     {number}  Max events to show (default 12)
 */

import { AlertTriangle, Activity, CheckCircle, Eye } from "lucide-react";
import TrendIndicator from "./TrendIndicator";

const LEVEL_ICON = {
  CRITICAL: AlertTriangle,
  WARNING:  AlertTriangle,
  WATCH:    Eye,
  NORMAL:   CheckCircle,
};

const LEVEL_ICON_COLOR = {
  CRITICAL: "text-red-500",
  WARNING:  "text-orange-500",
  WATCH:    "text-yellow-500",
  NORMAL:   "text-emerald-500",
};

const LEVEL_LINE_COLOR = {
  CRITICAL: "bg-red-400",
  WARNING:  "bg-orange-400",
  WATCH:    "bg-yellow-400",
  NORMAL:   "bg-emerald-400",
};

const LEVEL_BG = {
  CRITICAL: "bg-red-50/80 border-red-200",
  WARNING:  "bg-orange-50/80 border-orange-200",
  WATCH:    "bg-yellow-50/50 border-yellow-200",
  NORMAL:   "bg-slate-50/70 border-slate-200",
};

export default function TrendTimeline({ timeline = [], maxItems = 12 }) {
  const items = timeline.slice(0, maxItems);

  if (!items.length) {
    return (
      <div className="clinical-card p-6 flex flex-col items-center justify-center h-40 text-slate-400">
        <Activity size={24} className="mb-2 animate-pulse" />
        <p className="text-xs font-bold">Collecting telemetry — timeline pending.</p>
      </div>
    );
  }

  return (
    <div className="clinical-card p-5 space-y-1">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-black text-slate-800">Trend Timeline</h3>
        <span className="text-[9px] text-slate-400 font-extrabold uppercase tracking-widest">
          {items.length} events
        </span>
      </div>

      <div className="relative space-y-2">
        {/* Vertical connector line */}
        <div className="absolute left-3.5 top-0 bottom-0 w-0.5 bg-slate-100" />

        {items.map((event, idx) => {
          const al    = event.alert_level || "NORMAL";
          const Icon  = LEVEL_ICON[al]       || Activity;
          const iconC = LEVEL_ICON_COLOR[al]  || "text-slate-400";
          const dotC  = LEVEL_LINE_COLOR[al]  || "bg-slate-400";
          const bg    = LEVEL_BG[al]          || LEVEL_BG.NORMAL;
          const isCritical = al === "CRITICAL";

          return (
            <div key={idx} className="relative flex items-start gap-3 pl-7">
              {/* Dot on the timeline */}
              <div
                className={`absolute left-2.5 top-2 h-2 w-2 rounded-full ${dotC} ${isCritical ? "animate-pulse" : ""}`}
              />

              <div className={`flex-1 rounded-xl border p-2.5 ${bg}`}>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    <Icon size={11} className={`${iconC} shrink-0 ${isCritical ? "animate-pulse" : ""}`} />
                    <span className="text-[10px] font-black text-slate-700">
                      {event.label || event.parameter}
                    </span>
                    <span className="text-[9px] text-slate-400 font-semibold">
                      {event.value != null ? `${event.value} ${event.unit || ""}` : ""}
                    </span>
                  </div>
                  <TrendIndicator
                    direction={event.direction}
                    alertLevel={al}
                    classification={event.classification}
                    size="sm"
                    showLabel={false}
                  />
                </div>
                {event.time && (
                  <p className="text-[8px] text-slate-400 font-semibold mt-1">{event.time}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
