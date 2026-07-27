import { NavLink, Link } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Activity,
  BarChart3,
  Settings,
  Shield,
  User,
  TrendingUp,
  Building2,
  MessageSquare,
  Sparkles,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";

export default function Sidebar({ mobileOpen = false, setMobileOpen = () => {} }) {
  const { user } = useAuth();
  const role = user?.role?.toLowerCase();

  let menu = [];

  if (role === "hospitaladmin" || role === "superadmin") {
    menu = [
      { icon: LayoutDashboard, title: "Admin Dashboard", path: "/dashboard" },
      { icon: Activity, title: "Live Monitoring", path: "/monitoring" },
      { icon: TrendingUp, title: "Telemetry Trends", path: "/telemetry" },
      { icon: BarChart3, title: "Analytics", path: "/analytics" },
      { icon: Building2, title: "Hospital Assistant", path: "/hospital-assistant" },
      { icon: Shield, title: "User Directory", path: "/users" },
      { icon: Settings, title: "Settings", path: "/settings" },
      { icon: User, title: "My Profile", path: "/profile" },
    ];
  } else if (role === "icumanager") {
    menu = [
      { icon: LayoutDashboard, title: "Operations Dashboard", path: "/dashboard" },
      { icon: Activity, title: "Live Monitoring", path: "/monitoring" },
      { icon: TrendingUp, title: "Telemetry Trends", path: "/telemetry" },
      { icon: BarChart3, title: "Analytics", path: "/analytics" },
      { icon: Building2, title: "Hospital Assistant", path: "/hospital-assistant" },
      { icon: User, title: "My Profile", path: "/profile" },
    ];
  } else if (role === "doctor") {
    menu = [
      { icon: LayoutDashboard, title: "Doctor Dashboard", path: "/dashboard" },
      { icon: Activity, title: "Live Monitoring", path: "/monitoring" },
      { icon: TrendingUp, title: "Telemetry Trends", path: "/telemetry" },
      { icon: Building2, title: "Hospital Assistant", path: "/hospital-assistant" },
      { icon: User, title: "My Profile", path: "/profile" },
    ];
  } else if (role === "nurse") {
    menu = [
      { icon: LayoutDashboard, title: "Nursing Dashboard", path: "/dashboard" },
      { icon: Activity, title: "Live Monitoring", path: "/monitoring" },
      { icon: TrendingUp, title: "Telemetry Trends", path: "/telemetry" },
      { icon: Building2, title: "Hospital Assistant", path: "/hospital-assistant" },
      { icon: User, title: "My Profile", path: "/profile" },
    ];
  } else if (role === "labtechnician") {
    menu = [
      { icon: TrendingUp, title: "Telemetry Trends", path: "/telemetry" },
      { icon: User, title: "My Profile", path: "/profile" },
    ];
  } else if (role === "receptionist") {
    menu = [
      { icon: Building2, title: "Hospital Assistant", path: "/hospital-assistant" },
      { icon: User, title: "My Profile", path: "/profile" },
    ];
  } else if (role === "viewer") {
    menu = [
      { icon: Activity, title: "Live Monitoring", path: "/monitoring" },
      { icon: TrendingUp, title: "Telemetry Trends", path: "/telemetry" },
      { icon: User, title: "My Profile", path: "/profile" },
    ];
  } else {
    // Default fallback
    menu = [
      { icon: LayoutDashboard, title: "Dashboard", path: "/dashboard" },
      { icon: User, title: "My Profile", path: "/profile" },
    ];
  }

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-[#091220] text-slate-100 transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 flex flex-col border-r border-slate-800/80 ${
        mobileOpen ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      {/* Header */}
      <Link
        to="/"
        className="flex h-16 items-center gap-3 border-b border-slate-800/80 px-6 shrink-0 transition hover:opacity-90 cursor-pointer"
        title="View IntelliICU Overview (Landing Page)"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-tr from-amber-500/20 to-sky-500/20 border border-amber-500/40">
          <Activity size={16} className="text-amber-400" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
            IntelliICU
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          </h1>
          <p className="text-[10px] font-medium text-slate-400 tracking-wide">Enterprise Clinical Platform</p>
        </div>
      </Link>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Clinical Navigation
        </div>
        {menu.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.title}
              to={item.path}
              onClick={() => setMobileOpen(false)}
              end={item.path === "/dashboard"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-medium transition duration-150 ${
                  isActive
                    ? "bg-slate-800/90 text-white font-semibold border-l-2 border-amber-400 shadow-sm"
                    : "text-slate-400 hover:bg-slate-900/80 hover:text-slate-200"
                }`
              }
            >
              <Icon size={17} className="shrink-0" />
              <span>{item.title}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Role Info */}
      <div className="border-t border-slate-800/80 p-4 shrink-0">
        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3.5 space-y-1">
          <div className="flex items-center justify-between text-[11px]">
            <span className="font-semibold text-slate-200">Role Clearance</span>
            <span className="font-mono text-[9px] font-bold text-amber-400 bg-amber-950/60 px-1.5 py-0.5 rounded border border-amber-500/30 uppercase">
              {user ? user.role : "User"}
            </span>
          </div>
          <p className="text-[10px] text-slate-400 leading-tight">
            Audited JWT Session • Real-Time Telemetry Active
          </p>
        </div>
      </div>
    </aside>
  );
}
