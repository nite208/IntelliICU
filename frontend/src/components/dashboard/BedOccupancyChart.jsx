import { motion } from "framer-motion";
import {
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
} from "recharts";

import useWebSocket from "../../hooks/useWebSocket";

export default function BedOccupancyChart() {
  const { dashboardData } = useWebSocket();

  const occupancyValue = dashboardData?.bed_occupancy ?? 86;
  const totalPatients = dashboardData?.total_patients ?? 48;
  const icuCapacity = dashboardData?.icu_capacity ?? 56;

  const occupancy = [
    {
      name: "Occupancy",
      value: occupancyValue,
      fill: "#06b6d4",
    },
  ];

  return (
    <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800">
            Bed Occupancy
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            ICU capacity utilization
          </p>
        </div>
        <span className="text-xs font-bold text-slate-400">
          {totalPatients} / {icuCapacity} Beds
        </span>
      </div>

      <div className="relative mt-6 h-64 flex items-center justify-center">
        <div className="w-full h-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="75%"
              outerRadius="95%"
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
                background={{ fill: "#f1f5f9" }}
                dataKey="value"
                cornerRadius={12}
              />
            </RadialBarChart>
          </ResponsiveContainer>
        </div>

        <div className="absolute flex flex-col items-center justify-center text-center pointer-events-none">
          <motion.h1
            key={occupancyValue}
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3 }}
            className="text-4xl font-black text-cyan-600 tracking-tight"
          >
            {occupancyValue}%
          </motion.h1>
          <span className="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider mt-1 block">
            Capacity Filled
          </span>
        </div>
      </div>

      <div className="mt-4 border-t border-slate-100 pt-4 flex justify-between text-xs text-slate-500 font-semibold">
        <span>Available Beds: <strong className="text-slate-800">{icuCapacity - totalPatients}</strong></span>
        <span className="text-emerald-600 font-bold">Active Surveillance</span>
      </div>
    </div>
  );
}