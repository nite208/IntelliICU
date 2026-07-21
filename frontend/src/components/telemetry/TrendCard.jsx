/**
 * TrendCard.jsx
 *
 * Enterprise vital-sign trend card.
 *
 * Displays for one parameter:
 *  - Parameter label + unit
 *  - Current value  (large, color-coded)
 *  - Previous value + rate of change badge
 *  - TrendIndicator (direction arrow + classification)
 *  - Mini sparkline (last 8 points via Recharts)
 *  - Rolling average, min, max stats footer
 *  - Color border by alert level
 *
 * Props:
 *   trend        {object}  Full parameter TrendResult (from telemetry_trends.parameters[key])
 *   onClick      {fn}      Optional — called with the parameter key when clicked
 *   isSelected   {boolean} Highlight the card
 */

import { motion } from "framer-motion";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Tooltip,
} from "recharts";
import TrendIndicator from "./TrendIndicator";

// Color maps keyed by alert level
const BORDER_MAP = {
  NORMAL:   "border-slate-200",
  WATCH:    "border-yellow-300",
  WARNING:  "border-orange-400",
  CRITICAL: "border-red-500",
};

const VALUE_COLOR_MAP = {
  NORMAL:   "text-slate-800",
  WATCH:    "text-yellow-700",
  WARNING:  "text-orange-600",
  CRITICAL: "text-red-600",
};

const STROKE_MAP = {
  NORMAL:   "#10b981",
  WATCH:    "#f59e0b",
  WARNING:  "#f97316",
  CRITICAL: "#ef4444",
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl bg-slate-900 px-3 py-2 text-[10px] text-white font-semibold shadow-xl">
      <p>{payload[0]?.payload?.t}</p>
      <p className="text-cyan-300 font-black">{payload[0]?.value}</p>
    </div>
  );
};

export default function TrendCard({ trend, onClick, isSelected = false }) {
  if (!trend) return null;

  const {
    label,
    unit,
    current,
    previous,
    average,
    minimum,
    maximum,
    rate_of_change,
    pct_change,
    direction,
    classification,
    alert_level,
    interpretation,
    history = [],
  } = trend;

  const alertLevel  = alert_level  || "NORMAL";
  const stroke      = STROKE_MAP[alertLevel]    || STROKE_MAP.NORMAL;
  const borderClass = BORDER_MAP[alertLevel]    || BORDER_MAP.NORMAL;
  const valColor    = VALUE_COLOR_MAP[alertLevel]|| VALUE_COLOR_MAP.NORMAL;

  const changePositive = rate_of_change > 0;
  const changeSign     = changePositive ? "+" : "";

  return (
    <motion.button
      whileHover={{ y: -3, scale: 1.01 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onClick && onClick(trend)}
      className={`
        clinical-card border-2 p-4 text-left w-full transition-all duration-200
        ${borderClass}
        ${isSelected ? "ring-2 ring-offset-1 ring-cyan-500 shadow-md" : ""}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-[9px] font-black uppercase tracking-widest text-slate-400">
            {label}
          </p>
          <p className={`text-2xl font-black tracking-tight mt-0.5 ${valColor}`}>
            {current != null ? current : "—"}
            <span className="text-xs font-bold text-slate-400 ml-1">{unit}</span>
          </p>
        </div>
        <TrendIndicator
          direction={direction}
          alertLevel={alertLevel}
          classification={classification}
          size="sm"
        />
      </div>

      {/* Sparkline */}
      {history.length >= 2 && (
        <div className="mt-3 h-14">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id={`tg-${label}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={stroke} stopOpacity={0.25} />
                  <stop offset="100%" stopColor={stroke} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="v"
                stroke={stroke}
                strokeWidth={2}
                fill={`url(#tg-${label})`}
                dot={false}
                isAnimationActive={false}
              />
              <Tooltip content={<CustomTooltip />} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Rate of change badge */}
      <div className="mt-2 flex items-center justify-between">
        <span
          className={`text-[10px] font-bold ${
            changePositive ? "text-red-500" : rate_of_change < 0 ? "text-emerald-600" : "text-slate-400"
          }`}
        >
          {changeSign}{rate_of_change != null ? rate_of_change.toFixed(1) : "0"} {unit}
          <span className="text-slate-350 ml-1">
            ({changeSign}{pct_change != null ? pct_change.toFixed(1) : "0"}%)
          </span>
        </span>
        {previous != null && (
          <span className="text-[9px] text-slate-400 font-semibold">
            prev {previous}
          </span>
        )}
      </div>

      {/* Stats footer */}
      <div className="mt-3 grid grid-cols-3 gap-1 border-t border-slate-100 pt-2">
        {[
          { label: "Avg",  value: average != null  ? average.toFixed(1)  : "—" },
          { label: "Min",  value: minimum != null  ? minimum.toFixed(1)  : "—" },
          { label: "Max",  value: maximum != null  ? maximum.toFixed(1)  : "—" },
        ].map(({ label: statLabel, value }) => (
          <div key={statLabel} className="text-center">
            <p className="text-[8px] font-black uppercase tracking-widest text-slate-350">{statLabel}</p>
            <p className="text-[11px] font-extrabold text-slate-600">{value}</p>
          </div>
        ))}
      </div>

      {/* Interpretation tooltip line */}
      {interpretation && (
        <p className="mt-2 text-[9px] text-slate-450 font-medium leading-relaxed line-clamp-2">
          {interpretation}
        </p>
      )}
    </motion.button>
  );
}
