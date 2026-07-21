import { motion } from "framer-motion";
import { BrainCircuit } from "lucide-react";

import { aiActivities } from "../../assets/data/alertsData";

export default function ActivityFeed() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="clinical-card p-6"
    >
      <h2 className="text-2xl font-bold">AI Activity Feed</h2>
      <p className="mt-2 text-slate-500">
        Real-time clinical AI pipeline events
      </p>

      <div className="mt-8 space-y-5">
        {aiActivities.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50 p-4"
          >
            <div className="flex gap-4">
              <BrainCircuit className="text-cyan-600" size={22} />
              <div>
                <p className="font-semibold">{item.title}</p>
                <p className="text-sm text-slate-400">{item.time}</p>
              </div>
            </div>
            <span className="h-3 w-3 animate-pulse rounded-full bg-emerald-500" />
          </div>
        ))}
      </div>
    </motion.div>
  );
}
