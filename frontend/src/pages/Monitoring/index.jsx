import { Activity, Radio } from "lucide-react";

import AlertsSection from "../../components/dashboardV2/AlertsSection";
import VitalsOverview from "../../components/patientProfile/VitalsOverview";

export default function Monitoring() {
  return (
    <div className="space-y-8">
      <div className="rounded-2xl bg-gradient-to-r from-[#070b14] via-[#091220] to-[#0c192e] p-6 text-white shadow-xl border border-slate-800/80">
        <div className="flex items-center gap-4">
          <div className="rounded-xl bg-amber-500/10 border border-amber-500/20 p-3 text-amber-400">
            <Radio size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight">Live Monitoring</h1>
            <p className="mt-1 text-xs text-slate-400">
              Real-time ICU vitals, physiological trends, and patient-level alerts
            </p>
          </div>
          <div className="ml-auto flex items-center gap-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-3.5 py-1.5 text-xs text-emerald-400 font-bold">
            <Activity className="text-emerald-400" size={14} />
            <span>Telemetry Stream Active</span>
          </div>
        </div>
      </div>

      <VitalsOverview />

      <AlertsSection />
    </div>
  );
}
