import React, { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

export default function LoadingBubble() {
  const [step, setStep] = useState(0);
  const steps = [
    "Analyzing patient vitals and telemetry charts...",
    "Consulting electronic health records and lab draws...",
    "Running sepsis prediction and explainability engine...",
    "Formulating clinical recommendations and evidence basis..."
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % steps.length);
    }, 1800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex justify-start items-start gap-3 max-w-[85%]">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-cyan-50 border border-cyan-100 text-cyan-600">
        <Loader2 className="animate-spin" size={14} />
      </div>
      <div className="bg-white border border-slate-150 rounded-2xl p-4.5 shadow-sm space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">Clinical Copilot</span>
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-cyan-500 animate-ping"></span>
        </div>
        <p className="text-xs text-slate-500 italic animate-pulse">{steps[step]}</p>
      </div>
    </div>
  );
}
