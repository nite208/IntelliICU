import { motion } from "framer-motion";
import {
  BrainCircuit,
  AlertTriangle,
  ShieldCheck,
  BookOpen,
  Loader2,
  Sparkles,
} from "lucide-react";

import { useClinicalAI } from "../../context/ClinicalAIContext";

export default function AIRecommendation() {
  const { recommendation, loading } = useClinicalAI();

  if (loading) {
    return (
      <div className="clinical-card p-8">
        <div className="flex items-center gap-3">
          <Loader2
            className="animate-spin text-cyan-600"
            size={30}
          />
          <div>
            <h2 className="text-xl font-bold text-slate-800">
              IntelliAI is analyzing...
            </h2>
            <p className="text-xs text-slate-500">
              Running Prediction • RAG • Clinical Reasoning
            </p>
          </div>
        </div>

        <div className="mt-8 space-y-4">
          <div className="h-6 rounded bg-slate-200 animate-pulse"></div>
          <div className="h-6 rounded bg-slate-200 animate-pulse"></div>
          <div className="h-6 rounded bg-slate-200 animate-pulse"></div>
          <div className="h-48 rounded bg-slate-200 animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className="clinical-card p-10 text-center">
        <BrainCircuit
          size={56}
          className="mx-auto text-cyan-600 animate-pulse"
        />
        <h2 className="mt-6 text-xl font-black text-slate-800">
          IntelliAI Clinical Assistant
        </h2>
        <p className="mt-3 text-xs text-slate-500 leading-relaxed">
          Select a patient from the patient table and click
          <strong> Analyze </strong>
          to generate an evidence-based clinical recommendation.
        </p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="rounded-2xl overflow-hidden border border-slate-900 shadow-md">
        <div className="bg-gradient-to-r from-slate-900 via-[#0B2942] to-cyan-950 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 text-xs font-bold text-cyan-400">
                <BrainCircuit size={16} />
                <span>IntelliAI Recommendation</span>
              </div>
              <h2 className="mt-3 text-2xl font-black tracking-tight">
                Clinical Decision Support
              </h2>
            </div>
            <Sparkles
              size={32}
              className="text-cyan-300"
            />
          </div>
        </div>
      </div>

      {/* Risk */}
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-2xl bg-red-50/50 border border-red-100 p-5">
          <AlertTriangle className="text-red-650" size={20} />
          <p className="mt-3 text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">
            Risk Level
          </p>
          <h2 className="text-3xl font-black text-red-750 mt-1">
            {recommendation.summary?.overall_condition}
          </h2>
        </div>

        <div className="rounded-2xl bg-cyan-50/50 border border-cyan-100 p-5">
          <ShieldCheck className="text-cyan-650" size={20} />
          <p className="mt-3 text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">
            Risk Score
          </p>
          <h2 className="text-3xl font-black text-cyan-750 mt-1">
            {recommendation.summary?.confidence ? `${(recommendation.summary.confidence * 100).toFixed(0)}%` : "-"}
          </h2>
        </div>
      </div>

      {/* Recommendation */}
      <div className="clinical-card p-6">
        <h2 className="text-lg font-bold text-slate-800">
          AI Clinical Reasoning
        </h2>
        <div className="mt-4 text-xs font-semibold leading-relaxed text-slate-600 whitespace-pre-wrap">
          {recommendation.summary?.clinical_reasoning}
        </div>
      </div>

      {/* Sources */}
      <div className="clinical-card p-6">
        <div className="flex items-center gap-2 border-b border-slate-50 pb-3">
          <BookOpen className="text-cyan-650" size={18} />
          <h2 className="text-lg font-bold text-slate-800">
            Evidence-Based Actions
          </h2>
        </div>

        <div className="mt-4 space-y-3">
          {recommendation.recommendations?.map((rec, index) => (
            <motion.div
              key={index}
              whileHover={{ y: -2 }}
              className="rounded-xl border border-slate-100 bg-slate-50/60 p-4"
            >
              <h3 className="font-bold text-slate-850 text-sm">
                {rec.title}
              </h3>
              <p className="mt-1.5 text-xs font-medium text-slate-500 leading-relaxed">
                {rec.description}
              </p>
              <div className="mt-3">
                <span className="rounded-lg bg-cyan-100/70 px-2.5 py-1 text-[10px] font-extrabold text-cyan-800 uppercase tracking-wide">
                  {rec.priority} Priority
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

    </motion.div>
  );
}