import { motion } from "framer-motion";
import {
  BedDouble,
  Users,
  Ambulance,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import {
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
} from "recharts";

import useWebSocket from "../../hooks/useWebSocket";

export default function HospitalAnalytics() {
  // New WebSocket Hook
  const { dashboardData } = useWebSocket();

  const occupancyValue = dashboardData?.bed_occupancy ?? 86;
  const totalPatients = dashboardData?.total_patients ?? 48;
  const icuCapacity = dashboardData?.icu_capacity ?? 56;
  const activeAlerts = dashboardData?.active_alerts ?? 6;

  const occupancy = [
    {
      name: "Occupancy",
      value: occupancyValue,
      fill: "#06b6d4",
    },
  ];

  const resources = [
    {
      title: "ICU Beds",
      value: `${totalPatients} / ${icuCapacity}`,
      icon: BedDouble,
      color: "bg-cyan-100 text-cyan-600",
    },
    {
      title: "Doctors On Duty",
      value: "18",
      icon: Users,
      color: "bg-violet-100 text-violet-600",
    },
    {
      title: "Emergency Admissions",
      value: activeAlerts,
      icon: Ambulance,
      color: "bg-red-100 text-red-600",
    },
    {
      title: "System Health",
      value: "99.8%",
      icon: ShieldCheck,
      color: "bg-emerald-100 text-emerald-600",
    },
  ];

  return (
    <section className="space-y-6">
      {/* Occupancy */}
      <motion.div
        whileHover={{ y: -3 }}
        className="clinical-card p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-800">
              Hospital Analytics
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Operational Intelligence
            </p>
          </div>

          <TrendingUp className="text-cyan-600" size={18} />
        </div>

        <div className="relative mt-8 h-72 flex items-center justify-center">
          <div className="w-full h-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                innerRadius="80%"
                outerRadius="100%"
                data={occupancy}
                startAngle={90}
                endAngle={-270}
              >
                <PolarAngleAxis
                  type="number"
                  domain={[0, 100]}
                  tick={false}
                />

                <RadialBar
                  background
                  dataKey="value"
                  cornerRadius={12}
                />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>

          <div className="absolute flex flex-col items-center justify-center text-center">
            <motion.h1
              key={occupancyValue}
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3 }}
              className="text-4xl font-black text-cyan-600 tracking-tight"
            >
              {occupancyValue}%
            </motion.h1>

            <span className="clinical-label mt-1 block">
              Bed Occupancy
            </span>
          </div>
        </div>
      </motion.div>

      {/* Resource Cards */}
      <div className="space-y-4">
        {resources.map((item, index) => {
          const Icon = item.icon;

          return (
            <motion.div
              key={index}
              whileHover={{ y: -1 }}
              className="clinical-card p-4.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4.5">
                  <div
                    className={`flex h-11 w-11 items-center justify-center rounded-xl ${item.color}`}
                  >
                    <Icon size={20} />
                  </div>

                  <div>
                    <span className="clinical-label text-[10px]">
                      {item.title}
                    </span>

                    <motion.h3
                      key={item.value}
                      initial={{ opacity: 0.5 }}
                      animate={{ opacity: 1 }}
                      className="text-lg font-black text-slate-800 tracking-tight mt-0.5"
                    >
                      {item.value}
                    </motion.h3>
                  </div>
                </div>

                <span className="block h-2 w-2 animate-pulse rounded-full bg-emerald-500"></span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Footer */}
      <motion.div
        whileHover={{ y: -2 }}
        className="rounded-2xl bg-gradient-to-br from-slate-900 via-[#0B2942] to-cyan-950 p-6 text-white shadow-md border border-slate-950"
      >
        <span className="text-[10px] text-cyan-400 font-extrabold uppercase tracking-wider block">
          AI Operational Insight
        </span>

        <h3 className="mt-2 text-base font-bold">
          ICU Bed Utilization Notice
        </h3>

        <p className="mt-3 text-xs leading-relaxed text-slate-350">
          The platform predicts occupancy levels may reach 90% within the next 8 hours. Active discharge planning is advised for clinically stable recovery cases.
        </p>
      </motion.div>
    </section>
  );
}