import { motion } from "framer-motion";
import { FlaskConical } from "lucide-react";
import { useClinicalAI } from "../../context/ClinicalAIContext";

export default function LabResults() {
  const { selectedPatient } = useClinicalAI();
  const labs = selectedPatient?.labs || {};

  function getLabStatus(name, valueStr) {
    if (!valueStr) return { status: "normal", badge: "Normal", color: "bg-slate-100 text-slate-700 border-slate-200" };
    const val = parseFloat(valueStr);
    if (isNaN(val)) return { status: "normal", badge: "Normal", color: "bg-slate-100 text-slate-700 border-slate-200" };

    const n = name.toLowerCase();
    if (n.includes("lactate")) {
      if (val >= 4.0) return { status: "critical", badge: "Critical", color: "bg-red-100 text-red-700 border-red-200" };
      if (val >= 2.0) return { status: "high", badge: "High", color: "bg-orange-100 text-orange-700 border-orange-200" };
    } else if (n.includes("wbc")) {
      if (val > 11.0 || val < 4.0) return { status: "abnormal", badge: "Abnormal", color: "bg-amber-100 text-amber-700 border-amber-200" };
    } else if (n.includes("creatinine")) {
      if (val > 1.2) return { status: "high", badge: "High", color: "bg-orange-100 text-orange-700 border-orange-200" };
    } else if (n.includes("platelets")) {
      if (val < 150) return { status: "low", badge: "Low", color: "bg-red-100 text-red-700 border-red-200" };
    } else if (n.includes("crp")) {
      if (val >= 5.0) return { status: "high", badge: "High", color: "bg-orange-100 text-orange-700 border-orange-200" };
    } else if (n.includes("procalcitonin")) {
      if (val >= 0.15) return { status: "high", badge: "High", color: "bg-orange-100 text-orange-700 border-orange-200" };
    } else if (n.includes("hemoglobin")) {
      if (val < 12.0) return { status: "low", badge: "Low", color: "bg-amber-100 text-amber-700 border-amber-200" };
    }

    return { status: "normal", badge: "Normal", color: "bg-emerald-100 text-emerald-700 border-emerald-200" };
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-[30px] bg-white border border-slate-200 shadow-xl p-7"
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-black">
            Laboratory Results
          </h2>
          <p className="mt-2 text-slate-500">
            Recent Lab Tests & Biomarkers
          </p>
        </div>
        <FlaskConical
          size={28}
          className="text-cyan-600"
        />
      </div>

      <div className="mt-8 space-y-4">
        {Object.entries(labs).length > 0 ? (
          Object.entries(labs).map(([testName, labValue]) => {
            const valStr = typeof labValue === "object" ? JSON.stringify(labValue) : String(labValue);
            const statusInfo = getLabStatus(testName, valStr);
            return (
              <div
                key={testName}
                className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-slate-100 transition hover:bg-slate-100/50"
              >
                <div>
                  <div className="text-sm font-semibold text-slate-500">
                    {testName}
                  </div>
                  <div className="mt-1 text-xl font-bold text-slate-800">
                    {valStr}
                  </div>
                </div>
                <span className={`rounded-full border px-3 py-1 text-xs font-bold ${statusInfo.color}`}>
                  {statusInfo.badge}
                </span>
              </div>
            );
          })
        ) : (
          <p className="text-center text-slate-500 py-6">
            No lab results available.
          </p>
        )}
      </div>
    </motion.div>
  );
}
