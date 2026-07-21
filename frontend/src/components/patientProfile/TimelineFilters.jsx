import { motion } from "framer-motion";

export default function TimelineFilters({ activeFilter, onChangeFilter }) {
  const filters = [
    { id: "all", label: "All" },
    { id: "clinical", label: "Clinical" },
    { id: "ai", label: "Clinical AI" },
    { id: "alerts", label: "Alerts" },
    { id: "recommendations", label: "Recommendations" },
    { id: "user", label: "User Actions" },
  ];

  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
      {filters.map((f) => {
        const isActive = activeFilter.toLowerCase() === f.id;
        return (
          <button
            key={f.id}
            onClick={() => onChangeFilter(f.id)}
            className={`relative rounded-xl px-3.5 py-1.5 text-xs font-bold transition whitespace-nowrap ${
              isActive
                ? "bg-slate-900 text-white shadow-sm"
                : "bg-slate-50 text-slate-600 hover:bg-slate-100"
            }`}
          >
            {f.label}
          </button>
        );
      })}
    </div>
  );
}
