import { CalendarDays, Clock3, BrainCircuit } from "lucide-react";
import { motion } from "framer-motion";

export default function DashboardHeader() {
  return (
    <motion.div
      initial={{ opacity: 0, y: -25 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: .5 }}
      className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-6"
    >
      <div>

        <div className="flex items-center gap-2 text-slate-500 text-sm">

          <span>Clinical</span>

          <span>/</span>

          <span className="font-semibold text-cyan-700">
            Dashboard
          </span>

        </div>

        <h1 className="mt-3 text-5xl font-black tracking-tight text-slate-900">

          AI Clinical Command Center

        </h1>

        <p className="mt-2 text-slate-500 max-w-3xl">

          Real-time monitoring, AI-assisted diagnosis,
          predictive analytics and clinical recommendations
          across all ICU units.

        </p>

      </div>

      <div className="flex flex-wrap gap-4">

        <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-5 w-56">

          <div className="flex items-center gap-3">

            <CalendarDays
              size={18}
              className="text-cyan-600"
            />

            <span className="text-slate-500 text-sm">

              Today

            </span>

          </div>

          <h2 className="mt-3 font-semibold text-lg">

            Wednesday

          </h2>

          <p className="text-slate-500">

            July 8, 2026

          </p>

        </div>

        <div className="rounded-2xl bg-gradient-to-r from-cyan-600 to-blue-700 text-white shadow-lg p-5 w-72">

          <div className="flex justify-between">

            <div>

              <p className="text-cyan-100">

                Current Shift

              </p>

              <h2 className="text-2xl font-bold">

                Day Shift

              </h2>

            </div>

            <Clock3 />

          </div>

          <div className="mt-5 flex items-center justify-between">

            <span>

              07:00 — 19:00

            </span>

            <span>

              Dr. Reyes

            </span>

          </div>

        </div>

      </div>

    </motion.div>
  );
}