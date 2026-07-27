import { BarChart3 } from "lucide-react";

import AnalyticsAggregateSection from "../../components/dashboardV2/AnalyticsAggregateSection";
import HospitalAnalytics from "../../components/dashboardV2/HospitalAnalytics";
import KPISection from "../../components/dashboardV2/KPISection";

export default function Analytics() {
  return (
    <div className="space-y-8">
      <div className="rounded-2xl bg-gradient-to-r from-[#070b14] via-[#091220] to-[#0c192e] p-6 text-white shadow-xl border border-slate-800/80">
        <div className="flex items-center gap-4">
          <div className="rounded-xl bg-amber-500/10 border border-amber-500/20 p-3 text-amber-400">
            <BarChart3 size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight">Hospital Analytics & Outcomes</h1>
            <p className="mt-1 text-xs text-slate-400">
              ICU occupancy, outcomes, and AI-assisted clinical metrics
            </p>
          </div>
        </div>
      </div>

      <KPISection />

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-8">
          <AnalyticsAggregateSection />
        </div>
        <div className="col-span-12 xl:col-span-4">
          <HospitalAnalytics />
        </div>
      </div>
    </div>
  );
}
