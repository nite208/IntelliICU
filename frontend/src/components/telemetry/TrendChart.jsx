/**
 * TrendChart.jsx
 *
 * Full-width live area chart for a single telemetry parameter.
 *
 * Features:
 *  - Recharts ResponsiveContainer + AreaChart
 *  - Dynamic gradient fill color by alert level
 *  - Reference lines for normal range upper/lower bounds
 *  - Animated dot on the latest data point
 *  - Custom dark-theme tooltip
 *  - Rolling statistics summary bar
 *
 * Props:
 *   trend         {object}  Full TrendResult for one parameter
 *   patientName   {string}  Optional patient display name
 */

import { useMemo } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
} from "recharts";
import TrendIndicator from "./TrendIndicator";

// Stroke and fill by alert level
const STROKE_MAP = {
  NORMAL:   "#10b981",
  WATCH:    "#f59e0b",
  WARNING:  "#f97316",
  CRITICAL: "#ef4444",
};

const LABEL_BG = {
  NORMAL:   "bg-emerald-50 text-emerald-700 border-emerald-200",
  WATCH:    "bg-yellow-50 text-yellow-700 border-yellow-200",
  WARNING:  "bg-orange-50 text-orange-700 border-orange-200",
  CRITICAL: "bg-red-50 text-red-700 border-red-200",
};

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const { t, v } = payload[0]?.payload || {};
  return (
    <div className="rounded-xl bg-slate-900 px-4 py-2.5 shadow-2xl text-xs text-white">
      <p className="text-slate-400 mb-0.5">{t}</p>
      <p className="text-xl font-black text-cyan-300">{v}</p>
    </div>
  );
}

export default function TrendChart({ trend, patientName = "" }) {
  if (!trend) {
    return (
      <div className="clinical-card p-6 flex items-center justify-center h-64 text-slate-400 text-xs font-bold">
        Select a parameter to view the trend chart.
      </div>
    );
  }

  const {
    label,
    unit,
    current,
    previous,
    average,
    minimum,
    maximum,
    std_dev,
    slope,
    pct_change,
    direction,
    classification,
    alert_level,
    interpretation,
    possible_causes,
    normal_range,
    history = [],
    sample_count,
    time_window_seconds,
    confidence,
    deterioration_score,
  } = trend;

  const alertLevel = alert_level || "NORMAL";
  const stroke     = STROKE_MAP[alertLevel] || STROKE_MAP.NORMAL;
  const labelBg    = LABEL_BG[alertLevel]   || LABEL_BG.NORMAL;
  const isCritical = alertLevel === "CRITICAL";
  const gradId     = `tcg-${label?.replace(/\s/g, "")}`;

  // Use the last 30 history points for the chart
  const chartData = useMemo(() => (history || []).slice(-30), [history]);
  const hasData   = chartData.length >= 2;

  // Dynamic Y-axis domain with 10% padding
  const allVals   = chartData.map((d) => d.v).filter(Boolean);
  const yMin      = allVals.length ? Math.min(...allVals) * 0.95 : 0;
  const yMax      = allVals.length ? Math.max(...allVals) * 1.05 : 100;

  return (
    <div className={`clinical-card overflow-hidden border-2 ${isCritical ? "border-red-400" : "border-slate-200"}`}>
      {/* Header */}
      <div className="flex items-start justify-between p-5 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-black text-slate-800">{label}</h3>
            {patientName && (
              <span className="text-[10px] font-bold text-slate-400">— {patientName}</span>
            )}
          </div>
          <p className="text-[10px] text-slate-400 font-semibold mt-0.5">
            Live ICU telemetry · {time_window_seconds}s window · {sample_count} samples
          </p>
        </div>
        <div className="flex items-center gap-2">
          <TrendIndicator
            direction={direction}
            alertLevel={alertLevel}
            classification={classification}
            size="md"
          />
          <span className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase border ${labelBg}`}>
            {alertLevel}
          </span>
        </div>
      </div>

      {/* Current value hero */}
      <div className="flex items-center gap-8 px-5 pt-4">
        <div>
          <p className="text-[9px] font-black uppercase tracking-widest text-slate-400">Current</p>
          <p className={`text-4xl font-black tracking-tight ${isCritical ? "text-red-600" : "text-slate-800"} ${isCritical ? "animate-pulse" : ""}`}>
            {current != null ? current : "—"}
            <span className="text-sm font-bold text-slate-400 ml-1">{unit}</span>
          </p>
        </div>
        <div className="h-10 w-px bg-slate-100" />
        <div>
          <p className="text-[9px] font-black uppercase tracking-widest text-slate-400">Previous</p>
          <p className="text-xl font-black text-slate-500">
            {previous != null ? previous : "—"}
            <span className="text-xs text-slate-400 ml-1">{unit}</span>
          </p>
        </div>
        <div className="h-10 w-px bg-slate-100" />
        <div>
          <p className="text-[9px] font-black uppercase tracking-widest text-slate-400">Change</p>
          <p className={`text-xl font-black ${pct_change > 0 ? "text-red-500" : pct_change < 0 ? "text-emerald-600" : "text-slate-400"}`}>
            {pct_change != null ? `${pct_change > 0 ? "+" : ""}${pct_change.toFixed(1)}%` : "—"}
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="px-5 pt-4 pb-2">
        {!hasData ? (
          <div className="flex h-48 items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50/50">
            <p className="text-xs text-slate-400 font-bold">Collecting telemetry samples…</p>
          </div>
        ) : (
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stopColor={stroke} stopOpacity={0.20} />
                    <stop offset="100%" stopColor={stroke} stopOpacity={0}    />
                  </linearGradient>
                </defs>

                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis
                  dataKey="t"
                  stroke="#94a3b8"
                  fontSize={9}
                  tickLine={false}
                  interval="preserveStartEnd"
                />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={9}
                  tickLine={false}
                  domain={[yMin, yMax]}
                />
                <Tooltip content={<CustomTooltip />} />

                {/* Normal range reference lines */}
                {normal_range?.low != null && (
                  <ReferenceLine
                    y={normal_range.low}
                    stroke="#94a3b8"
                    strokeDasharray="4 4"
                    label={{ value: `Low ${normal_range.low}`, fontSize: 8, fill: "#94a3b8", position: "insideBottomLeft" }}
                  />
                )}
                {normal_range?.high != null && (
                  <ReferenceLine
                    y={normal_range.high}
                    stroke="#94a3b8"
                    strokeDasharray="4 4"
                    label={{ value: `High ${normal_range.high}`, fontSize: 8, fill: "#94a3b8", position: "insideTopLeft" }}
                  />
                )}

                <Area
                  type="monotone"
                  dataKey="v"
                  stroke={stroke}
                  strokeWidth={2.5}
                  fill={`url(#${gradId})`}
                  dot={false}
                  activeDot={{ r: 5, strokeWidth: 2, fill: stroke, stroke: "#fff" }}
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Rolling statistics bar */}
      <div className="mx-5 mb-4 grid grid-cols-4 gap-3 rounded-xl bg-slate-50/70 border border-slate-100 p-3">
        {[
          { label: "Average",   value: average != null  ? `${average.toFixed(1)} ${unit}`  : "—" },
          { label: "Std Dev",   value: std_dev != null  ? std_dev.toFixed(2)    : "—" },
          { label: "Slope",     value: slope != null    ? `${slope > 0 ? "+" : ""}${slope.toFixed(3)}`  : "—" },
          { label: "Confidence",value: confidence != null ? `${(confidence * 100).toFixed(0)}%` : "—" },
        ].map(({ label: sl, value }) => (
          <div key={sl} className="text-center">
            <p className="text-[8px] font-black uppercase tracking-widest text-slate-400">{sl}</p>
            <p className="text-[12px] font-extrabold text-slate-700 mt-0.5">{value}</p>
          </div>
        ))}
      </div>

      {/* Interpretation */}
      {interpretation && (
        <div className="mx-5 mb-4 rounded-xl border border-slate-100 bg-slate-50/50 p-3">
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">Clinical Interpretation</p>
          <p className="text-xs text-slate-700 font-medium leading-relaxed">{interpretation}</p>
          {possible_causes && possible_causes.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {possible_causes.map((c, i) => (
                <span key={i} className="px-2 py-0.5 rounded-lg bg-slate-200/60 text-[9px] font-bold text-slate-600">
                  {c}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
