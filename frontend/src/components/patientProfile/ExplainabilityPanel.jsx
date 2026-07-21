import { motion } from "framer-motion";
import {
  BrainCircuit,
  TrendingUp,
  TrendingDown,
  HeartPulse,
  Thermometer,
  Droplets,
  Activity,
  Loader2,
} from "lucide-react";

import { useClinicalAI } from "../../context/ClinicalAIContext";

const iconMap = {
  "Heart Rate": HeartPulse,
  Lactate: Droplets,
  Temperature: Thermometer,
  "Respiratory Rate": Activity,
  "SpO₂": Activity,
  "Systolic BP": TrendingDown,
};

const colorMap = {
  "Heart Rate": "bg-red-500",
  Lactate: "bg-orange-500",
  Temperature: "bg-yellow-500",
  "Respiratory Rate": "bg-cyan-500",
  "SpO₂": "bg-blue-500",
  "Systolic BP": "bg-purple-500",
};

export default function ExplainabilityPanel() {
  const { recommendation, loading } = useClinicalAI();

  if (loading) {
    return (
      <div className="rounded-[30px] border border-slate-200 bg-white p-8 shadow-xl">
        <div className="flex items-center gap-3">
          <Loader2 className="animate-spin text-violet-600" size={28} />
          <div>
            <h2 className="text-xl font-bold">Generating Explainability...</h2>
            <p className="text-slate-500">
              Calculating feature importance
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!recommendation?.explainability) {
    return (
      <div className="rounded-[30px] border border-slate-200 bg-white p-8 shadow-xl">
        <div className="flex items-center gap-3">
          <BrainCircuit className="text-violet-600" size={28} />
          <h2 className="text-2xl font-bold">Explainable AI</h2>
        </div>

        <div className="mt-8 text-center text-slate-500">
          Run AI Analysis to generate explainability.
        </div>
      </div>
    );
  }

  const positive =
    recommendation.explainability.positive_contributors || [];

  const negative =
    recommendation.explainability.negative_contributors || [];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-[30px] border border-slate-200 bg-white p-8 shadow-xl"
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <BrainCircuit className="text-violet-600" size={28} />
            <h2 className="text-2xl font-bold">Explainable AI</h2>
          </div>

          <p className="mt-2 text-slate-500">
            Feature contribution to AI prediction
          </p>
        </div>

        <TrendingUp className="text-violet-600" size={28} />
      </div>

      {/* Positive Contributors */}

      <div className="mt-8">
        <h3 className="mb-5 flex items-center gap-2 text-lg font-bold text-emerald-700">
          <TrendingUp size={18} />
          Positive Contributors
        </h3>

        <div className="space-y-5">
          {positive.map((item, index) => {
            const Icon = iconMap[item.feature] || BrainCircuit;
            const color = colorMap[item.feature] || "bg-cyan-500";
            const value = Math.round(item.impact * 100);

            return (
              <div key={index}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-slate-100 p-3">
                      <Icon size={18} />
                    </div>

                    <div>
                      <p className="font-semibold">{item.feature}</p>

                      <p className="text-sm text-slate-500">
                        {item.reason}
                      </p>
                    </div>
                  </div>

                  <span className="font-bold text-emerald-600">
                    {value}%
                  </span>
                </div>

                <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-200">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    transition={{ duration: 1 }}
                    className={`h-full rounded-full ${color}`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Negative Contributors */}

      <div className="mt-10">
        <h3 className="mb-5 flex items-center gap-2 text-lg font-bold text-red-700">
          <TrendingDown size={18} />
          Negative Contributors
        </h3>

        <div className="space-y-5">
          {negative.map((item, index) => {
            const Icon = iconMap[item.feature] || BrainCircuit;
            const color = colorMap[item.feature] || "bg-red-500";
            const value = Math.round(item.impact * 100);

            return (
              <div key={index}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-slate-100 p-3">
                      <Icon size={18} />
                    </div>

                    <div>
                      <p className="font-semibold">{item.feature}</p>

                      <p className="text-sm text-slate-500">
                        {item.reason}
                      </p>
                    </div>
                  </div>

                  <span className="font-bold text-red-600">
                    {value}%
                  </span>
                </div>

                <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-200">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    transition={{ duration: 1 }}
                    className={`h-full rounded-full ${color}`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-10 rounded-2xl border border-violet-100 bg-violet-50 p-5">
        <h3 className="font-bold text-violet-700">
          AI Interpretation
        </h3>

        <p className="mt-3 leading-7 text-slate-600">
          Explainability is generated from the IntelliAI clinical reasoning
          engine. Higher percentages indicate stronger influence on the current
          prediction.
        </p>
      </div>
    </motion.div>
  );
}