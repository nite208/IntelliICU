import { useState, useEffect } from "react";
import HeroBanner from "../../components/dashboardV2/HeroBanner";
import KPISection from "../../components/dashboardV2/KPISection";
import LiveAnalytics from "../../components/dashboardV2/LiveAnalytics";
import PatientsSection from "../../components/dashboardV2/PatientsSection";
import AIRecommendation from "../../components/dashboardV2/AIRecommendation";
import ActivityFeed from "../../components/dashboardV2/ActivityFeed";
import HospitalAnalytics from "../../components/dashboardV2/HospitalAnalytics";
import FloatingAI from "../../components/dashboardV2/FloatingAI";
import LiveAlerts from "../../components/dashboardV2/LiveAlerts";
import ClinicalTasks from "../../components/dashboard/ClinicalTasks";
import BedOccupancyChart from "../../components/dashboard/BedOccupancyChart";
import { useAuth } from "../../context/AuthContext";
import { userService } from "../../services/userService";
import { timelineService } from "../../services/timelineService";
import { ShieldCheck, Cpu, Database, Activity, Lock, Users } from "lucide-react";

// Admin Dashboard Component
function AdminDashboard() {
  const [totalUsers, setTotalUsers] = useState(0);
  const [systemLogs, setSystemLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAdminData() {
      try {
        const userData = await userService.getUsers("", "all", "all", 1, 1);
        setTotalUsers(userData.total || 0);
        
        const logs = await timelineService.getTimeline("SYSTEM");
        setSystemLogs(logs || []);
      } catch (err) {
        console.error("Failed to load admin dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadAdminData();
  }, []);

  return (
    <div className="space-y-8">
      <HeroBanner />
      
      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6 flex items-center gap-4">
          <div className="p-4 rounded-2xl bg-emerald-50 text-emerald-600">
            <Cpu size={24} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-500">API Status</h3>
            <p className="text-lg font-black text-slate-800">Online</p>
            <span className="text-xs text-slate-400">FastAPI • Latency &lt; 5ms</span>
          </div>
        </div>

        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6 flex items-center gap-4">
          <div className="p-4 rounded-2xl bg-cyan-50 text-cyan-600">
            <Database size={24} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-500">Database Connection</h3>
            <p className="text-lg font-black text-slate-800">Connected</p>
            <span className="text-xs text-slate-400">PostgreSQL • Port 5433</span>
          </div>
        </div>

        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6 flex items-center gap-4">
          <div className="p-4 rounded-2xl bg-blue-50 text-blue-600">
            <Activity size={24} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-500">ICU Telemetry Simulator</h3>
            <p className="text-lg font-black text-slate-800">Active</p>
            <span className="text-xs text-slate-400">Tick interval: 2 seconds</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* User directory summary card */}
        <div className="col-span-12 xl:col-span-4 rounded-3xl bg-white border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 rounded-xl bg-slate-100 text-slate-700">
                <Users size={20} />
              </div>
              <h2 className="text-xl font-bold">User Directory</h2>
            </div>
            <p className="text-slate-500 text-sm leading-relaxed mb-6">
              Manage accounts, roles, access rights, and passwords for hospital administrative staff and clinical staff members.
            </p>
            <div className="border-t border-slate-100 pt-4 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 font-bold">Total Accounts</span>
                <span className="font-extrabold text-slate-800">{totalUsers}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 font-bold">Directories Active</span>
                <span className="text-emerald-600 font-extrabold">100% Active</span>
              </div>
            </div>
          </div>
          <a
            href="/users"
            className="mt-6 w-full text-center py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition"
          >
            Manage Accounts
          </a>
        </div>

        {/* Admin System Logs (System timeline) */}
        <div className="col-span-12 xl:col-span-8 rounded-3xl bg-white border border-slate-200 shadow-sm p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-xl bg-slate-100 text-slate-700">
              <Lock size={20} />
            </div>
            <h2 className="text-xl font-bold">Administrative System Logs</h2>
          </div>

          <div className="h-[280px] overflow-y-auto space-y-4 pr-2">
            {loading ? (
              <p className="text-slate-400 text-xs">Loading logs...</p>
            ) : systemLogs.length > 0 ? (
              systemLogs.map((log) => (
                <div key={log.id} className="flex gap-4 p-3 hover:bg-slate-50 rounded-xl transition border border-slate-100/50">
                  <div className="text-[10px] text-slate-400 font-bold self-start mt-0.5 whitespace-nowrap bg-slate-100 px-2 py-0.5 rounded">
                    {log.time || new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-800">{log.title}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">{log.description}</p>
                    <span className="text-[10px] text-cyan-600 mt-1 block font-black uppercase">Actor: {log.actor}</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-xs py-8 text-center">No recent administrative logs.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Doctor Dashboard Component
function DoctorDashboard() {
  return (
    <div className="space-y-8">
      <HeroBanner />
      <KPISection />
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-8">
          <LiveAnalytics />
        </div>
        <div className="col-span-12 xl:col-span-4">
          <HospitalAnalytics />
        </div>
      </div>
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-8">
          <PatientsSection />
        </div>
        <div className="col-span-12 xl:col-span-4">
          <AIRecommendation />
        </div>
      </div>
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-7">
          <LiveAlerts />
        </div>
        <div className="col-span-12 xl:col-span-5">
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}

// Nurse Dashboard Component
function NurseDashboard() {
  return (
    <div className="space-y-8">
      <HeroBanner />
      <KPISection />
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-8">
          <PatientsSection />
        </div>
        <div className="col-span-12 xl:col-span-4">
          <ClinicalTasks />
        </div>
      </div>
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12">
          <LiveAlerts />
        </div>
      </div>
    </div>
  );
}

// ICU Manager Dashboard Component
function ICUManagerDashboard() {
  return (
    <div className="space-y-8">
      <HeroBanner />
      <KPISection />
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-8">
          <LiveAnalytics />
        </div>
        <div className="col-span-12 xl:col-span-4">
          <BedOccupancyChart />
        </div>
      </div>
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-7">
          <LiveAlerts />
        </div>
        <div className="col-span-12 xl:col-span-5">
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}

export default function DashboardV2() {
  const { user } = useAuth();
  const role = user?.role?.toLowerCase();

  return (
    <>
      {role === "hospitaladmin" || role === "superadmin" ? (
        <AdminDashboard />
      ) : role === "nurse" ? (
        <NurseDashboard />
      ) : role === "icumanager" ? (
        <ICUManagerDashboard />
      ) : (
        <DoctorDashboard />
      )}

      {/* Floating AI Assistant */}
      {role !== "doctor" && <FloatingAI />}
    </>
  );
}