import { useState } from "react";
import { motion } from "framer-motion";
import {
  TrendingUp,
  LineChart as LineIcon,
  Calendar,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

// 7-day historical aggregated data across all ICU wards
const historicalRiskData = [
  { day: "Mon", avgRisk: 24, admissions: 8, discharges: 6 },
  { day: "Tue", avgRisk: 28, admissions: 10, discharges: 7 },
  { day: "Wed", avgRisk: 35, admissions: 12, discharges: 9 },
  { day: "Thu", avgRisk: 42, admissions: 9, discharges: 11 },
  { day: "Fri", avgRisk: 38, admissions: 14, discharges: 8 },
  { day: "Sat", avgRisk: 31, admissions: 7, discharges: 10 },
  { day: "Sun", avgRisk: 29, admissions: 6, discharges: 8 },
];

export default function AnalyticsAggregateSection() {
  const [timeframe, setTimeframe] = useState("7d");

  return (
    <section className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">
            ICU Aggregate Analytics & Longitudinal Trends
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Historical population risk averages, admission velocities, and clinical AI predictive accuracy
          </p>
        </div>

        <div className="flex gap-1.5 bg-slate-100 p-1 rounded-xl">
          {["24h", "7d", "30d"].map((t) => (
            <button
              key={t}
              onClick={() => setTimeframe(t)}
              className={`px-3 py-1 text-xs font-bold rounded-lg transition ${
                timeframe === t
                  ? "bg-slate-900 text-white shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {t.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Main Historical Risk Trend Chart */}
      <motion.div
        whileHover={{ y: -2 }}
        className="clinical-card p-6"
      >
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-2.5">
            <LineIcon className="text-cyan-600" size={20} />
            <div>
              <h3 className="text-base font-bold text-slate-800">
                Mean ICU Patient Risk Progression ({timeframe.toUpperCase()})
              </h3>
              <p className="text-[11px] text-slate-400 font-medium">
                Calculated population sepsis probability average across all admitted cases
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs font-bold">
            <span className="flex items-center gap-1 text-emerald-600">
              <ArrowDownRight size={16} /> -4.2% vs previous period
            </span>
          </div>
        </div>

        <div className="mt-6 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={historicalRiskData}>
              <defs>
                <linearGradient id="analyticsRiskGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#0284c7" stopOpacity={0.25} />
                  <stop offset="100%" stopColor="#0284c7" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" fontSize={11} unit="%" />
              <Tooltip
                contentStyle={{
                  background: "#0f172a",
                  borderRadius: "12px",
                  border: "none",
                  color: "#fff",
                  fontSize: "11px",
                  fontWeight: "bold",
                }}
              />
              <Area
                type="monotone"
                dataKey="avgRisk"
                name="Avg Risk Score (%)"
                stroke="#0284c7"
                strokeWidth={3}
                fill="url(#analyticsRiskGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Admissions vs Discharges Trend & Performance Stat Cards */}
      <div className="grid grid-cols-12 gap-6">
        <motion.div
          whileHover={{ y: -2 }}
          className="col-span-12 xl:col-span-8 clinical-card p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Layers className="text-indigo-600" size={18} />
              <h3 className="text-base font-bold text-slate-800">
                ICU Patient Flow (Admissions vs Discharges)
              </h3>
            </div>
            <div className="flex items-center gap-3 text-xs font-semibold">
              <span className="flex items-center gap-1.5 text-indigo-600">
                <span className="h-2.5 w-2.5 rounded-full bg-indigo-600" /> Admissions
              </span>
              <span className="flex items-center gap-1.5 text-cyan-500">
                <span className="h-2.5 w-2.5 rounded-full bg-cyan-500" /> Discharges
              </span>
            </div>
          </div>

          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={historicalRiskData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    borderRadius: "12px",
                    border: "none",
                    color: "#fff",
                    fontSize: "11px",
                    fontWeight: "bold",
                  }}
                />
                <Bar dataKey="admissions" name="Admissions" fill="#6366f1" radius={[6, 6, 0, 0]} />
                <Bar dataKey="discharges" name="Discharges" fill="#06b6d4" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* AI Model Analytics Summary */}
        <div className="col-span-12 xl:col-span-4 space-y-4">
          <div className="clinical-card p-5">
            <span className="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider">
              AI Sepsis Early Detection Accuracy
            </span>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="text-3xl font-black text-slate-800">94.8%</span>
              <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                +1.2% AUROC
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400 leading-relaxed">
              Validated on 6-hour lead time prior to clinical septic shock onset.
            </p>
          </div>

          <div className="clinical-card p-5">
            <span className="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider">
              Mean Time to Intervention
            </span>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="text-3xl font-black text-slate-800">18.4 min</span>
              <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                -6.2 min faster
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400 leading-relaxed">
              Average clinician response time following high-priority AI risk notifications.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
