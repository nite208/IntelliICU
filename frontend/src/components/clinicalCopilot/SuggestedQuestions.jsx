import React from "react";
import { HelpCircle } from "lucide-react";

export default function SuggestedQuestions({ onSelect, disabled }) {
  const questions = [
    "What is the sepsis risk and heart rate for this patient?",
    "Explain the current hemodynamic status and vitals",
    "Analyze the latest lab results (lactate/WBC)",
    "What active clinical alerts are currently firing?"
  ];

  return (
    <div className="space-y-2.5">
      <div className="flex items-center gap-1.5 text-slate-400">
        <HelpCircle size={12} />
        <span className="text-[10px] font-black uppercase tracking-wider">Suggested Queries</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {questions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => !disabled && onSelect(q)}
            disabled={disabled}
            className="text-left text-xs bg-slate-50 hover:bg-slate-100 text-slate-600 font-medium py-2 px-3.5 rounded-xl border border-slate-150 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
