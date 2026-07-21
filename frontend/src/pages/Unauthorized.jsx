import React from "react";
import { Link } from "react-router-dom";
import { ShieldAlert, ArrowLeft } from "lucide-react";

export default function Unauthorized() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] p-8 text-center max-w-md mx-auto space-y-6">
      <div className="h-16 w-16 bg-red-50 rounded-2xl flex items-center justify-center border border-red-100 shadow-sm animate-pulse">
        <ShieldAlert size={36} className="text-red-500" />
      </div>

      <div className="space-y-2">
        <h1 className="text-2xl font-black text-slate-800">Access Denied</h1>
        <p className="text-xs leading-relaxed text-slate-500 font-semibold">
          Your credentials do not possess the required RBAC security clearance to view this clinical section. 
          Please contact your administrator for role adjustments.
        </p>
      </div>

      <div className="pt-4 w-full">
        <Link
          to="/dashboard"
          className="btn-clinical-primary w-full justify-center gap-2 py-3"
        >
          <ArrowLeft size={14} />
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}
