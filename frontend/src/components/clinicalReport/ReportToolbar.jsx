import React from "react";
import { Download, Copy, Loader2 } from "lucide-react";

export default function ReportToolbar({ 
  reportType, 
  onTypeChange, 
  onDownloadPDF, 
  onCopyReport, 
  generating,
  downloading
}) {
  const reportTypes = [
    "ICU Progress Note",
    "Daily Clinical Summary",
    "Shift Handover",
    "Discharge Summary"
  ];

  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 border-b border-slate-150 bg-white px-5 py-4 shrink-0">
      {/* Report Type Selector */}
      <div className="flex items-center gap-2">
        <label className="text-[10px] font-black uppercase tracking-wider text-slate-400">Format</label>
        <select
          value={reportType}
          onChange={(e) => onTypeChange(e.target.value)}
          disabled={generating}
          className="text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-700 font-bold focus:outline-none focus:border-cyan-600 focus:bg-white transition disabled:opacity-50"
        >
          {reportTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2">
        {/* Copy Report */}
        <button
          onClick={onCopyReport}
          disabled={generating}
          className="flex items-center justify-center gap-1.5 px-3.5 py-2 border border-slate-200 hover:bg-slate-50 text-slate-600 font-bold text-xs rounded-xl transition disabled:opacity-50"
          title="Copy report details to clipboard"
        >
          <Copy size={13} />
          <span>Copy Text</span>
        </button>

        {/* Download PDF */}
        <button
          onClick={onDownloadPDF}
          disabled={generating || downloading}
          className="flex items-center justify-center gap-1.5 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl transition disabled:opacity-50 shadow-sm"
          title="Download hospital-styled PDF report"
        >
          {downloading ? (
            <Loader2 className="animate-spin" size={13} />
          ) : (
            <Download size={13} />
          )}
          <span>{downloading ? "Building PDF..." : "Download PDF"}</span>
        </button>
      </div>
    </div>
  );
}
