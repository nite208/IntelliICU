/**
 * TelemetryDashboard.jsx
 *
 * Enterprise ICU Telemetry Trend Dashboard.
 *
 * Layout:
 * ┌────────────────────────────────────────────────────────────┐
 * │  Header banner (LIVE indicator + connection status)        │
 * ├─────────────────────┬──────────────────────────────────────┤
 * │  Patient Selector   │  TrendAlerts (active alerts panel)   │
 * ├─────────────────────┴──────────────────────────────────────┤
 * │  TrendCard × 7  (HR, MAP, SpO2, RR, Temp, SBP, DBP)       │
 * │  Mini sparklines + rate-of-change + stats footer           │
 * ├────────────────────────────────────────────────────────────┤
 * │  TrendChart  (full detail view for selected parameter)      │
 * ├──────────────────────────┬─────────────────────────────────┤
 * │  TrendTimeline           │  TrendSummary                   │
 * └──────────────────────────┴─────────────────────────────────┘
 *
 * All data flows from useTelemetry — zero extra WebSocket connections.
 */

import { useState, useMemo, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Radio, Wifi, WifiOff } from "lucide-react";

import useTelemetry         from "./useTelemetry";
import TrendCard            from "./TrendCard";
import TrendChart           from "./TrendChart";
import TrendTimeline        from "./TrendTimeline";
import TrendAlerts          from "./TrendAlerts";
import TrendSummary         from "./TrendSummary";

// Canonical parameter display order
const PARAM_ORDER = [
  "heart_rate",
  "map",
  "spo2",
  "respiratory_rate",
  "temperature",
  "systolic_bp",
  "diastolic_bp",
];

export default function TelemetryDashboard() {
  const { allTrends, connected, lastUpdated } = useTelemetry();

  // Selected patient
  const [selectedPatientId, setSelectedPatientId] = useState(null);

  // Selected parameter for the full chart view
  const [selectedParam, setSelectedParam] = useState(null);

  // All patient IDs seen so far
  const patientIds = useMemo(() => Object.keys(allTrends), [allTrends]);

  // Auto-select first patient when data arrives
  const currentPatientId = selectedPatientId || patientIds[0] || null;

  const currentPatientData = currentPatientId ? allTrends[currentPatientId] : null;
  const currentTrends      = currentPatientData?.trends;
  const currentParams      = currentTrends?.parameters || {};
  const patientName        = currentPatientData?.patient_name || currentPatientId || "";

  // Timeline from the summary
  const timeline = currentTrends?.timeline || [];

  // Parameter list in display order
  const orderedParams = useMemo(
    () =>
      PARAM_ORDER
        .filter((k) => currentParams[k])
        .map((k) => ({ key: k, trend: currentParams[k] })),
    [currentParams],
  );

  const handleSelectParam = useCallback((key, trend) => {
    setSelectedParam({ key, trend });
  }, []);

  const handleSelectPatient = useCallback((id) => {
    setSelectedPatientId(id);
    setSelectedParam(null);
  }, []);

  const lastUpdatedStr = lastUpdated
    ? lastUpdated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
    : null;

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-[#0B2942] to-cyan-950 p-6 text-white shadow-md">
        <div className="flex items-center gap-4">
          <div className="rounded-xl bg-white/10 p-3">
            <Radio size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-black">Enterprise Telemetry Monitor</h1>
            <p className="mt-1 text-xs text-slate-350">
              Continuous ICU vital sign trend analysis · 7 parameters · Rolling window
            </p>
          </div>
          <div className="ml-auto flex items-center gap-3">
            {lastUpdatedStr && (
              <span className="text-[10px] font-semibold text-slate-400">
                Updated {lastUpdatedStr}
              </span>
            )}
            <div
              className={`flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-semibold ${
                connected
                  ? "bg-emerald-500/20 text-emerald-300"
                  : "bg-red-500/20 text-red-300"
              }`}
            >
              {connected ? <Wifi size={12} /> : <WifiOff size={12} />}
              {connected ? "Stream Active" : "Reconnecting…"}
            </div>
          </div>
        </div>
      </div>

      {/* ── Patient Selector + Alerts ── */}
      <div className="grid grid-cols-12 gap-6">
        {/* Patient selector */}
        <div className="col-span-12 lg:col-span-3">
          <div className="clinical-card p-4">
            <p className="text-[9px] font-black uppercase tracking-widest text-slate-400 mb-3">
              ICU Patients
            </p>
            {patientIds.length === 0 ? (
              <div className="flex items-center gap-2 text-xs text-slate-400 font-semibold py-4">
                <Activity size={14} className="animate-pulse" />
                Waiting for telemetry…
              </div>
            ) : (
              <div className="space-y-1.5">
                {patientIds.map((pid) => {
                  const pData   = allTrends[pid];
                  const pTrends = pData?.trends;
                  const al      = pTrends?.overall_alert_level || "NORMAL";
                  const isSelected = pid === currentPatientId;
                  const dotColor =
                    al === "CRITICAL" ? "bg-red-500 animate-pulse" :
                    al === "WARNING"  ? "bg-orange-500" :
                    al === "WATCH"    ? "bg-yellow-400" : "bg-emerald-400";

                  return (
                    <button
                      key={pid}
                      onClick={() => handleSelectPatient(pid)}
                      className={`w-full flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-left transition
                        ${isSelected ? "bg-slate-900 text-white" : "hover:bg-slate-50 text-slate-700"}`}
                    >
                      <span className={`h-2 w-2 rounded-full shrink-0 ${dotColor}`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-[11px] font-black truncate">
                          {pData?.patient_name || pid}
                        </p>
                        <p className={`text-[9px] font-semibold ${isSelected ? "text-slate-400" : "text-slate-400"}`}>
                          {pid}
                        </p>
                      </div>
                      <span
                        className={`text-[8px] font-black uppercase rounded-full px-1.5 py-0.5 ${
                          al === "CRITICAL" ? "bg-red-100 text-red-700" :
                          al === "WARNING"  ? "bg-orange-100 text-orange-700" :
                          al === "WATCH"    ? "bg-yellow-100 text-yellow-700" :
                          isSelected        ? "bg-white/20 text-white" : "bg-emerald-100 text-emerald-700"
                        }`}
                      >
                        {al}
                      </span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Active Alerts */}
        <div className="col-span-12 lg:col-span-9">
          <TrendAlerts allTrends={allTrends} />
        </div>
      </div>

      {/* ── Parameter Trend Cards ── */}
      {currentPatientId && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-black text-slate-800">
              {patientName} — Live Parameter Trends
            </h2>
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
              Click a card for detail
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4">
            {orderedParams.length === 0 ? (
              <div className="col-span-full clinical-card p-6 text-center text-slate-400 text-xs font-bold">
                <Activity size={20} className="mx-auto mb-2 animate-pulse" />
                Collecting baseline — first trend data arriving…
              </div>
            ) : (
              orderedParams.map(({ key, trend }) => (
                <TrendCard
                  key={key}
                  trend={trend}
                  onClick={handleSelectParam.bind(null, key, trend)}
                  isSelected={selectedParam?.key === key}
                />
              ))
            )}
          </div>
        </div>
      )}

      {/* ── Full Trend Chart (selected parameter) ── */}
      <AnimatePresence mode="wait">
        {selectedParam && (
          <motion.div
            key={selectedParam.key}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.25 }}
          >
            <TrendChart
              trend={selectedParam.trend}
              patientName={patientName}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Timeline + Summary ── */}
      {currentPatientId && (
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 lg:col-span-7">
            <TrendTimeline timeline={timeline} />
          </div>
          <div className="col-span-12 lg:col-span-5">
            <TrendSummary
              patientId={currentPatientId}
              patientName={patientName}
              trends={currentTrends}
              onSelectParam={(key, trend) => handleSelectParam(key, trend)}
            />
          </div>
        </div>
      )}

      {/* Empty state */}
      {!currentPatientId && (
        <div className="clinical-card p-12 flex flex-col items-center justify-center text-slate-400 text-center">
          <Radio size={32} className="mb-4 opacity-30" />
          <h3 className="text-lg font-black text-slate-600 mb-2">Awaiting Telemetry Stream</h3>
          <p className="text-sm font-semibold max-w-sm">
            The simulator is broadcasting live patient data every 2 seconds.
            Trend analysis begins after the first 2 readings are collected.
          </p>
        </div>
      )}
    </div>
  );
}
