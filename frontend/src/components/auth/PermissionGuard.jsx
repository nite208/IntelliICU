import { usePermission } from "../../hooks/usePermission";
import { ShieldAlert } from "lucide-react";

export default function PermissionGuard({ requiredPermission, children, showFallback = false }) {
  const { hasPermission } = usePermission();

  if (!hasPermission(requiredPermission)) {
    if (showFallback) {
      return (
        <div className="flex flex-col items-center justify-center p-12 bg-white border border-slate-200 rounded-[30px] shadow-md text-center max-w-md mx-auto mt-20">
          <ShieldAlert size={48} className="text-red-500 mb-4 animate-pulse" />
          <h2 className="text-xl font-bold text-slate-800">Permission Required</h2>
          <p className="text-xs text-slate-500 mt-2 leading-relaxed">
            Your user profile does not possess the '{requiredPermission}' permission capability needed for this view.
          </p>
        </div>
      );
    }
    return null;
  }

  return children;
}
