import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function Layout() {
  return (
    <div className="flex h-screen bg-[#F5F7FA]">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Navigation */}
        <Topbar />

        {/* Routed Pages */}
        <main className="flex-1 overflow-auto bg-[#F5F7FA] p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}