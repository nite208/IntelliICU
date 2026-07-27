import { useState } from "react";
import { Bell, Search, LogOut, Menu } from "lucide-react";
import { useClinicalAI } from "../context/ClinicalAIContext";
import NotificationDrawer from "../components/dashboardV2/NotificationDrawer";
import { useAuth } from "../context/AuthContext";

export default function Topbar({ onMenuClick = () => {} }) {
  const { criticalCount } = useClinicalAI();
  const { user, logout } = useAuth();
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <header className="bg-white border-b border-slate-200/80 h-16 flex items-center justify-between px-6 shrink-0 z-30">
      
      {/* Mobile Menu Toggle & Search Bar */}
      <div className="flex items-center gap-4 flex-1">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100 transition"
          aria-label="Toggle Navigation Menu"
        >
          <Menu size={20} />
        </button>

        <div className="relative w-full max-w-md">
          <Search
            className="absolute left-3.5 top-2.5 text-slate-400"
            size={16}
          />
          <input
            placeholder="Search patient ID, ward beds, protocols..."
            className="w-full rounded-xl border border-slate-200 bg-slate-50/80 py-2 pl-9 pr-4 text-xs font-medium outline-none transition focus:border-slate-400 focus:bg-white text-slate-800"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-5">
        
        {/* Notification Bell */}
        <div
          onClick={() => setDrawerOpen(true)}
          className="relative cursor-pointer p-2 rounded-xl text-slate-600 hover:bg-slate-100 transition"
          title="Active Alarm Feed"
        >
          <Bell size={18} />
          {criticalCount > 0 && (
            <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-600 text-[9px] font-bold text-white shadow-xs">
              {criticalCount}
            </span>
          )}
        </div>
        
        <NotificationDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />

        {/* User Info & Logout */}
        <div className="flex items-center gap-3 border-l border-slate-200 pl-5">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-full bg-slate-900 flex items-center justify-center text-white text-xs font-bold uppercase shadow-xs">
              {user ? user.username.slice(0, 2) : "DR"}
            </div>

            <div className="hidden sm:block text-left">
              <p className="text-xs font-bold text-slate-900 leading-tight">
                {user ? user.username.charAt(0).toUpperCase() + user.username.slice(1) : "Dr. Reyes"}
              </p>
              <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">
                {user ? user.role : "Intensivist"}
              </p>
            </div>
          </div>

          <button
            onClick={logout}
            className="flex items-center justify-center h-8 w-8 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition border border-transparent hover:border-red-100"
            title="Secure Session Logout"
          >
            <LogOut size={16} />
          </button>
        </div>

      </div>

    </header>
  );
}