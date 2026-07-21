import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
  LineChart,
  Line,
} from "recharts";

import {
  Activity,
  HeartPulse,
  BrainCircuit,
  TrendingUp,
} from "lucide-react";

import { motion } from "framer-motion";

const heartRate = [
  { t: "08", hr: 82 },
  { t: "10", hr: 91 },
  { t: "12", hr: 88 },
  { t: "14", hr: 101 },
  { t: "16", hr: 111 },
  { t: "18", hr: 118 },
];

const prediction = [
  { t: "08", p: 21 },
  { t: "10", p: 33 },
  { t: "12", p: 46 },
  { t: "14", p: 60 },
  { t: "16", p: 79 },
  { t: "18", p: 96 },
];

export default function LiveAnalytics() {
  return (
    <section className="space-y-6">

      {/* Header */}

      <div className="flex items-center justify-between">

        <div>

          <h2 className="text-2xl font-bold">

            Live ICU Analytics

          </h2>

          <p className="text-slate-500">

            AI monitoring every patient in real time

          </p>

        </div>

        <div className="flex items-center gap-2 rounded-full bg-emerald-100 px-4 py-2">

          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"/>

          <span className="font-semibold text-emerald-700">

            LIVE

          </span>

        </div>

      </div>

      {/* Charts */}

      {/* Charts */}

      <div className="grid grid-cols-12 gap-6">

        {/* Heart Rate */}

        <motion.div

          whileHover={{ y: -3 }}

          className="col-span-12 xl:col-span-8 clinical-card p-6"

        >

          <div className="flex items-center justify-between">

            <div>

              <div className="flex items-center gap-2">

                <HeartPulse className="text-red-500"/>

                <h3 className="font-bold text-xl text-slate-800">

                  Heart Rate Trend

                </h3>

              </div>

              <p className="mt-2 text-xs text-slate-500">

                Live streaming ICU telemetry (last 6h)

              </p>

            </div>

            <div className="rounded-xl bg-red-50 px-4 py-2">

              <span className="font-bold text-red-600 text-sm">

                118 BPM

              </span>

            </div>

          </div>

          <div className="mt-8 h-80">

            <ResponsiveContainer width="100%" height="100%">

              <AreaChart data={heartRate}>

                <defs>

                  <linearGradient id="hrGradient" x1="0" y1="0" x2="0" y2="1">

                    <stop offset="0%" stopColor="#ef4444" stopOpacity={0.2}/>

                    <stop offset="100%" stopColor="#ef4444" stopOpacity={0}/>

                  </linearGradient>

                </defs>

                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9"/>

                <XAxis dataKey="t" stroke="#94a3b8" fontSize={11}/>

                <YAxis stroke="#94a3b8" fontSize={11}/>

                <Tooltip/>

                <Area

                  type="monotone"

                  dataKey="hr"

                  stroke="#ef4444"

                  strokeWidth={3}

                  fill="url(#hrGradient)"

                />

              </AreaChart>

            </ResponsiveContainer>

          </div>

        </motion.div>

        {/* Right Column - Sepsis Prediction */}

        <div className="col-span-12 xl:col-span-4 flex flex-col">

          <motion.div

            whileHover={{ y: -3 }}

            className="clinical-card p-6 flex-1 flex flex-col justify-between"

          >

            <div>

              <div className="flex items-center gap-2">

                <TrendingUp className="text-cyan-650"/>

                <h3 className="font-bold text-slate-800 text-lg">

                  Sepsis AI Risk Trend

                </h3>

              </div>

              <p className="mt-2 text-xs text-slate-500">

                Real-time AI probability index

              </p>

            </div>

            <div className="mt-6 h-64">

              <ResponsiveContainer width="100%" height="100%">

                <LineChart data={prediction}>

                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9"/>

                  <XAxis dataKey="t" stroke="#94a3b8" fontSize={11}/>

                  <YAxis stroke="#94a3b8" fontSize={11}/>

                  <Tooltip/>

                  <Line

                    type="monotone"

                    dataKey="p"

                    stroke="#0284c7"

                    strokeWidth={3}

                    dot={{ r: 4, strokeWidth: 2, fill: "#fff" }}

                  />

                </LineChart>

              </ResponsiveContainer>

            </div>

          </motion.div>

        </div>

      </div>

      {/* Bottom Stats */}

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-6">

        {[
          ["SpO₂", "98%", "text-cyan-600"],
          ["Respiration", "18 bpm", "text-emerald-600"],
          ["Temperature", "37.1°C", "text-orange-600"],
          ["AI Events", "124", "text-violet-600"],
        ].map(([title, value, color]) => (

          <motion.div

            whileHover={{ y: -2 }}

            key={title}

            className="clinical-card p-6"

          >

            <Activity className={color} size={18}/>

            <h2 className="mt-4 text-3xl font-black text-slate-800">

              {value}

            </h2>

            <p className="mt-1 text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">

              {title}

            </p>

          </motion.div>

        ))}

      </div>

    </section>
  );
}