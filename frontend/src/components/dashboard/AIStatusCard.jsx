import { BrainCircuit, Database, ShieldCheck, Activity } from "lucide-react";
import { motion } from "framer-motion";
import { aiStatus } from "../../assets/data/dashboardData";

const items = [
  {
    title: "LLM Engine",
    value: aiStatus.llm,
    icon: BrainCircuit,
    color: "text-cyan-600",
  },
  {
    title: "Knowledge Base",
    value: aiStatus.knowledgeBase,
    icon: Database,
    color: "text-blue-600",
  },
  {
    title: "Prediction Engine",
    value: aiStatus.prediction,
    icon: Activity,
    color: "text-emerald-600",
  },
  {
    title: "RAG Retrieval",
    value: aiStatus.rag,
    icon: ShieldCheck,
    color: "text-purple-600",
  },
];

export default function AIStatusCard() {
  return (
    <motion.div
      whileHover={{ y: -6 }}
      className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6 h-full"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-500 uppercase text-xs tracking-wider">
            AI System
          </p>

          <h2 className="text-2xl font-bold mt-2">
            IntelliICU Status
          </h2>
        </div>

        <div className="h-14 w-14 rounded-2xl bg-cyan-100 flex items-center justify-center">
          <BrainCircuit className="text-cyan-700" size={28} />
        </div>
      </div>

      <div className="mt-8 space-y-5">
        {items.map((item, index) => {
          const Icon = item.icon;

          return (
            <div
              key={index}
              className="flex items-center justify-between border-b pb-4 last:border-none"
            >
              <div className="flex items-center gap-4">
                <div className="h-11 w-11 rounded-xl bg-slate-100 flex items-center justify-center">
                  <Icon className={item.color} size={20} />
                </div>

                <div>
                  <p className="text-sm text-slate-500">{item.title}</p>
                  <p className="font-semibold">{item.value}</p>
                </div>
              </div>

              <span className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse"></span>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}