import { BrainCircuit } from "lucide-react";
import { aiActivities } from "../../assets/data/alertsData";

export default function AIActivityFeed() {

  return (

    <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6">

      <h2 className="text-xl font-bold mb-6">

        AI Activity Feed

      </h2>

      <div className="space-y-4">

        {aiActivities.map(item => (

          <div
            key={item.id}
            className="flex items-center justify-between"
          >

            <div className="flex gap-3">

              <BrainCircuit className="text-cyan-600"/>

              <div>

                <p className="font-medium">

                  {item.title}

                </p>

                <p className="text-slate-400 text-sm">

                  {item.time}

                </p>

              </div>

            </div>

            <span className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse"/>

          </div>

        ))}

      </div>

    </div>

  );

}