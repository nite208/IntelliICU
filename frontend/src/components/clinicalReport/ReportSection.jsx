import React, { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

export default function ReportSection({ title, icon: Icon, children, defaultOpen = true }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-slate-150 rounded-xl overflow-hidden bg-white shadow-sm">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700 font-bold"
      >
        <div className="flex items-center gap-2">
          {Icon && <Icon size={14} className="text-slate-500" />}
          <span className="text-[10px] font-black uppercase tracking-wider">{title}</span>
        </div>
        {isOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {isOpen && (
        <div className="p-4 border-t border-slate-100 text-xs text-slate-700 leading-relaxed space-y-3">
          {children}
        </div>
      )}
    </div>
  );
}
