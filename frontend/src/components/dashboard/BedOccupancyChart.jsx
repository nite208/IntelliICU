import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { occupancyData } from "../../assets/data/chartData";

const COLORS = ["#06b6d4", "#e2e8f0"];

export default function BedOccupancyChart() {
  return (
    <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6">

      <div className="mb-6">

        <h2 className="text-2xl font-bold">
          Bed Occupancy
        </h2>

      </div>

      <div className="h-72">

        <ResponsiveContainer width="100%" height="100%">

          <PieChart>

            <Pie
              data={occupancyData}
              innerRadius={60}
              outerRadius={95}
              dataKey="value"
            >

              {occupancyData.map((entry,index)=>

                <Cell
                  key={index}
                  fill={COLORS[index]}
                />

              )}

            </Pie>

            <Tooltip/>

          </PieChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}