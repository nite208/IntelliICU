import { BrainCircuit, ShieldAlert, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { aiSummary } from "../../assets/data/dashboardData";

export default function AIRecommendationCard() {
  return (
    <motion.div
      whileHover={{ y: -6 }}
      className="rounded-3xl overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-cyan-900 text-white shadow-xl"
    >
      <div className="p-8">

        <div className="flex justify-between items-start">

          <div>

            <p className="uppercase tracking-widest text-cyan-300 text-xs">
              AI Clinical Summary
            </p>

            <h2 className="text-3xl font-bold mt-2">
              High Risk Detected
            </h2>

          </div>

          <div className="h-16 w-16 rounded-2xl bg-white/10 flex items-center justify-center backdrop-blur">
            <BrainCircuit size={30} />
          </div>

        </div>

        <div className="mt-8 grid md:grid-cols-2 gap-8">

          <div>

            <div className="flex items-center gap-2">
              <ShieldAlert className="text-red-400" size={20} />

              <span className="font-semibold">
                AI Prediction
              </span>
            </div>

            <p className="mt-4 leading-7 text-slate-200">
              {aiSummary.prediction}
            </p>

            <div className="mt-8">

              <p className="text-sm text-slate-300">
                Confidence
              </p>

              <div className="mt-2 h-3 rounded-full bg-white/10">

                <div
                  className="h-full rounded-full bg-cyan-400"
                  style={{ width: `${aiSummary.confidence}%` }}
                />

              </div>

              <p className="mt-2 font-semibold text-cyan-300">
                {aiSummary.confidence}%
              </p>

            </div>

          </div>

          <div>

            <p className="font-semibold">
              Immediate Recommendation
            </p>

            <div className="mt-4 rounded-2xl bg-white/10 p-5 leading-7 text-slate-200">
              {aiSummary.recommendation}
            </div>

            <button className="mt-6 flex items-center gap-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 transition px-5 py-3 font-semibold">
              View Evidence
              <ArrowRight size={18} />
            </button>

          </div>

        </div>

      </div>
    </motion.div>
  );
}