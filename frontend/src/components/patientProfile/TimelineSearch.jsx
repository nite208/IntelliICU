import { Search, X } from "lucide-react";

export default function TimelineSearch({ value, onChange }) {
  return (
    <div className="relative w-full">
      <Search
        className="absolute left-3.5 top-3 text-slate-400"
        size={16}
      />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search timeline events..."
        className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-10 text-xs outline-none transition focus:border-slate-400 focus:bg-white text-slate-800 font-semibold"
      />
      {value && (
        <button
          onClick={() => onChange("")}
          className="absolute right-3 top-2.5 p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition"
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
}
