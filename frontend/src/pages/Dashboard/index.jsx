import DashboardHeader from "../../components/dashboard/DashboardHeader";
import KPIGrid from "../../components/dashboard/KPIGrid";
import AIStatusCard from "../../components/dashboard/AIStatusCard";
import AIRecommendationCard from "../../components/dashboard/AIRecommendationCard";
import RecentPatientsTable from "../../components/dashboard/RecentPatientsTable";
import VitalsChart from "../../components/dashboard/VitalsChart";
import BedOccupancyChart from "../../components/dashboard/BedOccupancyChart";
import AlertTimeline from "../../components/dashboard/AlertTimeline";
import AIActivityFeed from "../../components/dashboard/AIActivityFeed";
import ClinicalTasks from "../../components/dashboard/ClinicalTasks";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-slate-100">
      <div className="mx-auto max-w-[1700px] space-y-8 p-8">

        <DashboardHeader />

        <KPIGrid />

        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 xl:col-span-4">
            <AIStatusCard />
          </div>

          <div className="col-span-12 xl:col-span-8">
            <AIRecommendationCard />
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 xl:col-span-8">
            <VitalsChart />
          </div>

          <div className="col-span-12 xl:col-span-4">
            <BedOccupancyChart />
          </div>
        </div>

        <RecentPatientsTable />

        <div className="grid grid-cols-12 gap-6">

          <div className="col-span-12 xl:col-span-4">
            <AlertTimeline />
          </div>

          <div className="col-span-12 xl:col-span-4">
            <AIActivityFeed />
          </div>

          <div className="col-span-12 xl:col-span-4">
            <ClinicalTasks />
          </div>

        </div>

      </div>
    </div>
  );
}