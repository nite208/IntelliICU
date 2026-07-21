import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { vitalsData } from "../../assets/data/chartData";

export default function VitalsChart() {
  return (
    <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6">

      <div className="mb-6">

        <h2 className="text-2xl font-bold">
          Live ICU Vitals
        </h2>

        <p className="text-slate-500">
          Heart Rate Trend
        </p>

      </div>

      <div className="h-80">

        <ResponsiveContainer width="100%" height="100%">

          <LineChart data={vitalsData}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="time"/>

            <YAxis/>

            <Tooltip/>

            <Line
              dataKey="hr"
              stroke="#2563eb"
              strokeWidth={4}
              dot={{ r:5 }}
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}