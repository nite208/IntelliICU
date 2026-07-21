import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Users,
  AlertTriangle,
  BedDouble,
  BrainCircuit,
  ArrowUpRight,
} from "lucide-react";

import { dashboardService } from "../../services/dashboardService";
import useWebSocket from "../../hooks/useWebSocket";

import { useClinicalAI } from "../../context/ClinicalAIContext";

export default function KPISection() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  // NEW
  const { dashboardData } = useWebSocket();
  const { alertCount } = useClinicalAI();

  useEffect(() => {
    loadDashboard();
  }, []);

  useEffect(() => {
    if (dashboardData) {
      setDashboard(dashboardData);
      setLoading(false);
    }
  }, [dashboardData]);

  async function loadDashboard() {
    try {
      const data = await dashboardService.getDashboard();
      setDashboard(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading || !dashboard) {
    return (
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-40 animate-pulse rounded-3xl bg-slate-200"
          />
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: "Patients",
      value: dashboard.total_patients,
      icon: Users,
      color: "from-cyan-500 to-blue-600",
    },
    {
      title: "Critical",
      value: dashboard.critical_patients,
      icon: AlertTriangle,
      color: "from-red-500 to-red-700",
    },
    {
      title: "Occupancy",
      value: `${dashboard.bed_occupancy}%`,
      icon: BedDouble,
      color: "from-green-500 to-emerald-600",
    },
    {
      title: "AI Alerts",
      value: alertCount ?? dashboard.active_alerts,
      icon: BrainCircuit,
      color: "from-violet-500 to-indigo-600",
    },
  ];

  return (
    <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((item) => {
        const Icon = item.icon;

        return (
          <motion.div
            key={item.title}
            whileHover={{ y: -3 }}
            className="clinical-card p-6"
          >
            <div className="flex justify-between items-start">
              <div>
                <span className="clinical-label">{item.title}</span>

                <motion.h2
                  key={item.value}
                  initial={{ scale: 0.9, opacity: 0.6 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.25 }}
                  className="mt-3 text-4xl font-black text-slate-800 tracking-tight"
                >
                  {item.value}
                </motion.h2>
              </div>

              <div
                className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${item.color} shadow-sm`}
              >
                <Icon className="text-white" size={20} />
              </div>
            </div>

            <div className="mt-6 flex items-center justify-between border-t border-slate-50 pt-4">
              <div className="flex items-center gap-1.5 text-[10px] font-extrabold text-emerald-600 uppercase tracking-wider">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />
                Live Streaming
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}