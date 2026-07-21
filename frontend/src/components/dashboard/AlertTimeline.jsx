import { AlertTriangle } from "lucide-react";
import { alerts } from "../../assets/data/alertsData";

export default function AlertTimeline() {
  const badge = {
    Critical: "bg-red-100 text-red-700",
    High: "bg-orange-100 text-orange-700",
    Medium: "bg-yellow-100 text-yellow-700",
    Low: "bg-emerald-100 text-emerald-700",
  };

  return (
    <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6">

      <h2 className="text-xl font-bold mb-6">
        Alert Timeline
      </h2>

      <div className="space-y-5">

        {alerts.map(alert => (

          <div
            key={alert.id}
            className="flex gap-4"
          >

            <div className="h-10 w-10 rounded-xl bg-red-50 flex items-center justify-center">

              <AlertTriangle
                size={18}
                className="text-red-600"
              />

            </div>

            <div className="flex-1">

              <div className="flex justify-between">

                <span className="font-semibold">

                  {alert.patient}

                </span>

                <span className="text-slate-400 text-sm">

                  {alert.time}

                </span>

              </div>

              <p className="text-slate-500 text-sm mt-1">

                {alert.message}

              </p>

              <span className={`inline-block mt-3 px-3 py-1 rounded-full text-xs font-semibold ${badge[alert.severity]}`}>

                {alert.severity}

              </span>

            </div>

          </div>

        ))}

      </div>

    </div>
  );
}