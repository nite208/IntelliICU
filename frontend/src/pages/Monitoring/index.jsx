import { Activity, Radio } from "lucide-react";

import LiveAnalytics from "../../components/dashboardV2/LiveAnalytics";
import AlertsSection from "../../components/dashboardV2/AlertsSection";
import VitalsOverview from "../../components/patientProfile/VitalsOverview";

export default function Monitoring() {
  return (
    <div className="space-y-8">
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-[#0B2942] to-cyan-950 p-6 text-white shadow-md">
        <div className="flex items-center gap-4">
          <div className="rounded-xl bg-white/10 p-3">
            <Radio size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-black">Live Monitoring</h1>
            <p className="mt-1 text-xs text-slate-350">
              Real-time ICU vitals, alerts, and streaming analytics
            </p>
          </div>
          <div className="ml-auto flex items-center gap-2 rounded-full bg-emerald-500/20 px-3.5 py-1.5 text-xs">
            <Activity className="text-emerald-300" size={14} />
            <span className="font-semibold text-emerald-255">Stream Active</span>
          </div>
        </div>
      </div>

      <VitalsOverview />

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-8">
          <LiveAnalytics />
        </div>
        <div className="col-span-12 xl:col-span-4">
          <AlertsSection />
        </div>
      </div>
    </div>
  );
}
