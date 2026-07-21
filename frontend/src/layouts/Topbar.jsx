import { useState } from "react";
import { Bell, Search, LogOut } from "lucide-react";
import { useClinicalAI } from "../context/ClinicalAIContext";
import NotificationDrawer from "../components/dashboardV2/NotificationDrawer";
import { useAuth } from "../context/AuthContext";

export default function Topbar() {
  const { criticalCount } = useClinicalAI();
  const { user, logout } = useAuth();
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <header className="bg-white border-b h-20 flex items-center justify-between px-8">

      <div className="relative w-[420px]">

        <Search
          className="absolute left-4 top-3.5 text-gray-400"
          size={20}
        />

        <input
          placeholder="Search patients, beds, protocols..."
          className="w-full rounded-xl border bg-gray-50 py-3 pl-12 outline-none"
        />

      </div>

      <div className="flex items-center gap-6">

        <div
          onClick={() => setDrawerOpen(true)}
          className="relative cursor-pointer"
        >
          <Bell className="text-gray-600" />
          {criticalCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-black text-white animate-bounce animate-duration-1000">
              {criticalCount}
            </span>
          )}
        </div>
        
        <NotificationDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />

        <div className="flex items-center gap-4 border-l border-slate-100 pl-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-sm uppercase">
              {user ? user.username.slice(0, 2) : "DR"}
            </div>

            <div>
              <p className="font-semibold text-slate-800 leading-tight">
                {user ? user.username.charAt(0).toUpperCase() + user.username.slice(1) : "Dr. Reyes"}
              </p>
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">
                {user ? user.role : "Intensivist"}
              </p>
            </div>
          </div>

          <button
            onClick={logout}
            className="flex items-center justify-center h-9 w-9 rounded-xl text-gray-400 hover:text-red-500 hover:bg-red-50 transition border border-transparent hover:border-red-100"
            title="Secure Logout"
          >
            <LogOut size={18} />
          </button>
        </div>

      </div>

    </header>
  );
}