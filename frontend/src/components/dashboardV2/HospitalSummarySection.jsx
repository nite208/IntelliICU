import { motion } from "framer-motion";
import {
  Building2,
  Activity,
  AlertCircle,
  CheckCircle2,
  BarChart2,
} from "lucide-react";
import useWebSocket from "../../hooks/useWebSocket";

export default function HospitalSummarySection() {
  const { patientsData } = useWebSocket();

  // Aggregate severity breakdown from live patient list or fallback
  const total = patientsData.length || 48;
  const criticalCount = patientsData.filter(
    (p) => (p.risk_level || "").toUpperCase() === "HIGH" || (p.status || "").toLowerCase() === "critical"
  ).length || 6;
  
  const highRiskCount = patientsData.filter(
    (p) => (p.risk_level || "").toUpperCase() === "MEDIUM" || (p.status || "").toLowerCase() === "serious"
  ).length || 14;

  const lowRiskCount = patientsData.filter(
    (p) => (p.risk_level || "").toUpperCase() === "LOW" || (p.status || "").toLowerCase() === "stable"
  ).length || 28;

  const wardData = [
    { name: "Medical ICU (MICU)", total: 16, occupied: 14, critical: 3, color: "bg-cyan-500" },
    { name: "Surgical ICU (SICU)", total: 12, occupied: 10, critical: 2, color: "bg-indigo-500" },
    { name: "Cardiac Care (CCU)", total: 14, occupied: 12, critical: 1, color: "bg-violet-500" },
    { name: "Trauma ICU (TICU)", total: 14, occupied: 12, critical: 0, color: "bg-emerald-500" },
  ];

  return (
    <section className="space-y-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">
            Hospital-Wide Unit Summary
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            ICU capacity, patient severity distribution, and unit-level operational readiness
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-cyan-50 px-3.5 py-1.5 border border-cyan-100">
          <Building2 size={14} className="text-cyan-600" />
          <span className="text-xs font-bold text-cyan-800">4 Active Wards</span>
        </div>
      </div>

      {/* Patient Severity & Status Distribution Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          whileHover={{ y: -2 }}
          className="clinical-card p-5 border-l-4 border-l-red-500"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Critical Care Cases
            </span>
            <div className="p-2 rounded-lg bg-red-50 text-red-600">
              <AlertCircle size={18} />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-black text-slate-800">{criticalCount}</span>
            <span className="text-xs font-semibold text-red-600">
              ({Math.round((criticalCount / total) * 100)}% of total)
            </span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400 font-medium">
            Requires 1:1 continuous intensive surveillance
          </p>
        </motion.div>

        <motion.div
          whileHover={{ y: -2 }}
          className="clinical-card p-5 border-l-4 border-l-orange-500"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              High Risk / Serious
            </span>
            <div className="p-2 rounded-lg bg-orange-50 text-orange-600">
              <Activity size={18} />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-black text-slate-800">{highRiskCount}</span>
            <span className="text-xs font-semibold text-orange-600">
              ({Math.round((highRiskCount / total) * 100)}% of total)
            </span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400 font-medium">
            Frequent vital updates & AI trend alerts
          </p>
        </motion.div>

        <motion.div
          whileHover={{ y: -2 }}
          className="clinical-card p-5 border-l-4 border-l-emerald-500"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Stable / Step-Down Ready
            </span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <CheckCircle2 size={18} />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-black text-slate-800">{lowRiskCount}</span>
            <span className="text-xs font-semibold text-emerald-600">
              ({Math.round((lowRiskCount / total) * 100)}% of total)
            </span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400 font-medium">
            Candidates for floor transfer evaluation
          </p>
        </motion.div>
      </div>

      {/* Ward Occupancy & Capacity Table */}
      <div className="clinical-card p-6">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2.5">
            <BarChart2 className="text-cyan-600" size={20} />
            <h3 className="text-lg font-bold text-slate-800">
              Departmental Occupancy & Severity Overview
            </h3>
          </div>
          <span className="text-xs font-bold text-slate-400">
            Total Beds: 56
          </span>
        </div>

        <div className="space-y-4">
          {wardData.map((ward) => {
            const pct = Math.round((ward.occupied / ward.total) * 100);
            return (
              <div key={ward.name} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-bold text-slate-700">
                  <div className="flex items-center gap-2">
                    <span className={`h-2.5 w-2.5 rounded-full ${ward.color}`} />
                    <span>{ward.name}</span>
                  </div>
                  <div className="flex items-center gap-4 text-slate-500">
                    <span>
                      {ward.occupied} / {ward.total} Beds ({pct}%)
                    </span>
                    {ward.critical > 0 && (
                      <span className="text-red-600 font-extrabold bg-red-50 px-2 py-0.5 rounded">
                        {ward.critical} Critical
                      </span>
                    )}
                  </div>
                </div>

                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${ward.color}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
