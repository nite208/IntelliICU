import { motion } from "framer-motion";
import {
  BrainCircuit,
  AlertTriangle,
  ShieldCheck,
  Loader2,
  Sparkles,
  Zap,
} from "lucide-react";

import { useClinicalAI } from "../../context/ClinicalAIContext";

export default function AIRecommendationPanel() {
  const { recommendation, loading, analyzePatient, selectedPatient } = useClinicalAI();

  async function handleAnalyze() {
    if (!selectedPatient) return;

    const payload = {
      patient: {
        id: selectedPatient.patient?.id,
        name: selectedPatient.patient?.name,
        age: selectedPatient.patient?.age,
        gender: selectedPatient.patient?.gender,
      },
      admission: {
        bed: selectedPatient.admission?.bed,
        diagnosis: selectedPatient.admission?.diagnosis,
      },
      vitals: {
        heart_rate: selectedPatient.vitals?.heart_rate,
        systolic_bp: selectedPatient.vitals?.blood_pressure?.systolic,
        diastolic_bp: selectedPatient.vitals?.blood_pressure?.diastolic,
        respiratory_rate: selectedPatient.vitals?.respiratory_rate,
        spo2: selectedPatient.vitals?.spo2,
        temperature: selectedPatient.vitals?.temperature,
      },
      labs: {
        lactate: parseFloat(selectedPatient.labs?.Lactate),
        wbc: parseFloat(selectedPatient.labs?.WBC),
        creatinine: parseFloat(selectedPatient.labs?.Creatinine),
      },
      prediction: {
        risk_score: selectedPatient.patient?.risk_score,
        risk_level: selectedPatient.patient?.risk_level,
      },
    };

    await analyzePatient(payload);
  }

  if (loading) {
    return (
      <div className="clinical-card p-6">
        <div className="flex items-center gap-3">
          <Loader2 className="animate-spin text-cyan-600" size={24} />
          <div>
            <h2 className="text-base font-bold text-slate-800">AI Command Center Analyzing...</h2>
            <p className="text-[10px] text-slate-500 mt-0.5">
              Processing Telemetry • Evaluating Guidelines • Computing SHAP Weights
            </p>
          </div>
        </div>
        <div className="mt-6 space-y-3">
          <div className="h-6 skeleton-clinical" />
          <div className="h-6 skeleton-clinical" />
          <div className="h-24 skeleton-clinical" />
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className="clinical-card p-8 text-center space-y-4">
        <BrainCircuit size={48} className="mx-auto text-cyan-600 animate-pulse" />
        <div>
          <h2 className="text-base font-bold text-slate-800">AI Clinical Workspace Offline</h2>
          <p className="text-[11px] text-slate-500 mt-1 max-w-[220px] mx-auto leading-relaxed">
            Execute a telemetry review to construct diagnostic decision trees.
          </p>
        </div>
        {selectedPatient && (
          <button
            onClick={handleAnalyze}
            className="btn-clinical-primary w-full"
          >
            <BrainCircuit size={14} />
            Evaluate Patient
          </button>
        )}
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header Banner */}
      <div className="rounded-2xl overflow-hidden border border-slate-950 shadow-md">
        <div className="bg-gradient-to-r from-slate-900 via-[#0B2942] to-cyan-950 p-5 text-white">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-1.5 text-[9px] font-black text-cyan-400 uppercase tracking-widest">
                <BrainCircuit size={13} />
                <span>AI Command Center</span>
              </div>
              <h2 className="mt-2 text-xl font-black tracking-tight">Clinical Decision Suite</h2>
            </div>
            <Sparkles size={26} className="text-cyan-300" />
          </div>
        </div>
      </div>

      {/* Patient Status Summary */}
      <div className="clinical-card p-5">
        <span className="clinical-label text-[9px] text-slate-400">Sepsis Condition Status</span>
        <div className="flex items-center justify-between mt-3">
          <span className={`rounded-xl px-3 py-1.5 text-xs font-black uppercase tracking-wider ${
            recommendation.summary?.overall_condition === "Critical"
              ? "bg-red-50 text-red-750 border border-red-100"
              : recommendation.summary?.overall_condition === "Serious"
              ? "bg-amber-50 text-amber-700 border border-amber-100"
              : "bg-emerald-50 text-emerald-700 border border-emerald-100"
          }`}>
            {recommendation.summary?.overall_condition}
          </span>
          <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider">
            Trend: {recommendation.risk_progress?.trend}
          </div>
        </div>
      </div>

      {/* Risk Metrics */}
      <div className="grid grid-cols-2 gap-4">
        <div className="clinical-card p-4">
          <span className="clinical-label text-[9px] text-slate-400">Risk Score</span>
          <h2 className="text-2xl font-black text-slate-800 mt-2">
            {recommendation.risk_progress?.current_risk ? `${(recommendation.risk_progress.current_risk * 100).toFixed(0)}%` : "-"}
          </h2>
        </div>
        <div className="clinical-card p-4">
          <span className="clinical-label text-[9px] text-slate-400">AI Confidence</span>
          <h2 className="text-2xl font-black text-slate-800 mt-2">
            {recommendation.summary?.confidence ? `${(recommendation.summary.confidence * 100).toFixed(0)}%` : "-"}
          </h2>
        </div>
      </div>

      {/* Immediate Actions Required */}
      {recommendation.summary?.priority_actions?.length > 0 && (
        <div className="clinical-card p-5 border-l-4 border-red-500 bg-red-50/10">
          <div className="flex items-center gap-2 text-red-700">
            <Zap size={14} className="shrink-0" />
            <h3 className="text-[10px] font-black uppercase tracking-widest">Immediate Interventions</h3>
          </div>
          <ul className="mt-3 space-y-1.5 text-xs font-semibold text-slate-700 list-disc list-inside">
            {recommendation.summary.priority_actions.map((act, i) => (
              <li key={i}>{act}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Interventions Protocol */}
      <div className="clinical-card p-5 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-50 pb-2.5">
          <AlertTriangle size={14} className="text-cyan-600 shrink-0" />
          <h3 className="text-[10px] font-black text-slate-800 uppercase tracking-widest">Intervention Protocol</h3>
        </div>
        <div className="space-y-3">
          {recommendation.recommendations?.map((rec, i) => (
            <div key={i} className="rounded-xl border border-slate-100 bg-slate-50/50 p-4">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-slate-800 text-xs">{rec.title}</h4>
                <span className="badge-clinical-danger text-[9px]">{rec.priority}</span>
              </div>
              <p className="mt-1.5 text-xs font-medium text-slate-500 leading-relaxed">{rec.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Feature Contributors */}
      <div className="clinical-card p-5 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-50 pb-2.5">
          <ShieldCheck size={14} className="text-cyan-600 shrink-0" />
          <h3 className="text-[10px] font-black text-slate-800 uppercase tracking-widest">Explainability Summary</h3>
        </div>
        <div className="space-y-2.5">
          {recommendation.explainability?.positive_contributors?.slice(0, 3).map((feat, i) => (
            <div key={i} className="flex items-center justify-between text-xs font-semibold">
              <span className="text-slate-600">{feat.feature}</span>
              <span className="text-red-650">+{Math.round(feat.impact * 100)}% ({feat.reason})</span>
            </div>
          ))}
        </div>
      </div>

      {/* Evidence & Guidelines */}
      <div className="clinical-card p-5 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-50 pb-2.5">
          <Sparkles size={14} className="text-cyan-600 shrink-0" />
          <h3 className="text-[10px] font-black text-slate-800 uppercase tracking-widest">Evidence & Clinical Guidelines</h3>
        </div>
        <div className="space-y-3">
          {recommendation.sources?.map((src, i) => (
            <div key={i} className="rounded-xl border border-slate-100 bg-slate-50/50 p-4 text-xs font-semibold">
              <h4 className="font-bold text-slate-850 text-xs">{src.title}</h4>
              <p className="text-[9px] text-slate-400 mt-1 uppercase font-extrabold tracking-wide">
                {src.organization} • Page {src.page} (Relevance: {Math.round(src.relevance * 100)}%)
              </p>
              <p className="mt-2 text-xs font-medium text-slate-500 leading-relaxed">{src.summary}</p>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
