import { BarChart3 } from "lucide-react";

import LiveAnalytics from "../../components/dashboardV2/LiveAnalytics";
import HospitalAnalytics from "../../components/dashboardV2/HospitalAnalytics";
import KPISection from "../../components/dashboardV2/KPISection";

export default function Analytics() {
  return (
    <div className="space-y-8">
      <div className="clinical-card p-6">
        <div className="flex items-center gap-4">
          <div className="rounded-xl bg-cyan-50 p-3">
            <BarChart3 className="text-cyan-600" size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-800">Hospital Analytics</h1>
            <p className="mt-1 text-xs text-slate-500">
              ICU occupancy, outcomes, and AI-assisted clinical metrics
            </p>
          </div>
        </div>
      </div>

      <KPISection />

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-8">
          <LiveAnalytics />
        </div>
        <div className="col-span-12 xl:col-span-4">
          <HospitalAnalytics />
        </div>
      </div>
    </div>
  );
}
