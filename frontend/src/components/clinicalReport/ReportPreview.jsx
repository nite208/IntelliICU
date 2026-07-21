import React, { useState, useEffect } from "react";
import { X, FileText, User, Activity, FlaskConical, Bell, CheckCircle2, Gauge, AlertTriangle, AlertOctagon } from "lucide-react";
import ReportSection from "./ReportSection";
import ReportToolbar from "./ReportToolbar";
import api from "../../api/axios";

export default function ReportPreview({ patientId, onClose }) {
  const [reportType, setReportType] = useState("ICU Progress Note");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    generateReport();
  }, [reportType]);

  const generateReport = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.post("/clinical-copilot/report", {
        patient_id: patientId,
        report_type: reportType
      });
      setReport(response.data);
    } catch (err) {
      console.error("Failed to generate clinical report:", err);
      setError("Failed to compile clinical metrics. Please verify patient registry status.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyReport = () => {
    if (!report) return;
    const { content, report_type, created_at, patient_name, patient_id } = report;
    const text = `
INTELLIICU CLINICAL REPORT
Report Type: ${report_type}
Generated At: ${created_at}
Patient Name: ${patient_name} (${patient_id})
Diagnosis: ${content.admission?.diagnosis || "N/A"}
Bed: ${content.admission?.bed_number || "N/A"}
Physician: ${content.admission?.doctor_name || "N/A"}

AI CLINICAL REASONING SUMMARY
${content.ai_reasoning}

CLINICAL RECOMMENDATIONS & PATHWAYS
${content.clinical_recommendations?.map((r) => `- ${r}`).join("\n")}

PHYSIOLOGICAL VITALS & TRENDS
- Heart Rate: ${content.vitals?.heart_rate} bpm (Trend: ${content.vital_trends?.heart_rate?.direction})
- Blood Pressure: ${content.vitals?.systolic_bp}/${content.vitals?.diastolic_bp} mmHg (Trend: ${content.vital_trends?.systolic_bp?.direction})
- SpO2: ${content.vitals?.spo2}% (Trend: ${content.vital_trends?.spo2?.direction})
- Temp: ${content.vitals?.temperature}°C (Trend: ${content.vital_trends?.temperature?.direction})

ABNORMAL LAB METRICS
${content.abnormal_labs?.map((l) => `- ${l.metric}: ${l.value} (Ref: ${l.reference}) - ${l.status} [${l.severity}]`).join("\n") || "None"}

ACTIVE TELEMETRY ALERTS
${content.active_alerts?.map((a) => `- [${a.severity}] ${a.title}: ${a.message}`).join("\n") || "None"}
`.trim();

    navigator.clipboard.writeText(text);
    alert("Structured report text copied to clipboard!");
  };

  const handleDownloadPDF = async () => {
    if (!report?.report_id) return;
    try {
      setDownloading(true);
      const response = await api.get(`/clinical-copilot/report/${report.report_id}/pdf`, {
        responseType: "blob"
      });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `clinical_report_${report.report_id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF download failed:", err);
      alert("Failed to build clinical PDF document.");
    } finally {
      setDownloading(false);
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case "CRITICAL":
        return "bg-red-50 text-red-600 border border-red-100";
      case "HIGH":
        return "bg-amber-50 text-amber-600 border border-amber-100";
      default:
        return "bg-blue-50 text-blue-600 border border-blue-100";
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl w-full max-w-4xl h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-fadeIn">
        
        {/* Header Title block */}
        <div className="flex items-center justify-between px-6 py-4.5 border-b border-slate-150 bg-slate-50/50 shrink-0">
          <div className="flex items-center gap-2">
            <FileText className="text-cyan-600" size={18} />
            <h2 className="text-sm font-black uppercase tracking-wider text-slate-800">AI Clinical Report Workspace</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-655 hover:bg-slate-100 rounded-xl transition"
          >
            <X size={16} />
          </button>
        </div>

        {/* Toolbar Section */}
        <ReportToolbar
          reportType={reportType}
          onTypeChange={setReportType}
          onDownloadPDF={handleDownloadPDF}
          onCopyReport={handleCopyReport}
          generating={loading}
          downloading={downloading}
        />

        {/* Content Preview Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-64 gap-3 text-slate-400">
              <div className="h-7 w-7 animate-spin rounded-full border-2 border-cyan-600 border-t-transparent"></div>
              <span className="text-xs font-bold uppercase tracking-wider">Compiling EHR charts & building RAG summary...</span>
            </div>
          ) : error ? (
            <div className="text-center p-8 bg-red-50 border border-red-100 rounded-2xl max-w-md mx-auto mt-12 text-red-600 text-xs font-semibold">
              {error}
            </div>
          ) : report ? (
            <div className="space-y-6 max-w-3xl mx-auto">
              
              {/* Demographics Card */}
              <div className="bg-white border border-slate-150 rounded-2xl p-5 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">Patient File</span>
                    <span className={`text-[8.5px] px-2 py-0.5 rounded-lg border font-black uppercase tracking-wider ${getPriorityBadge(report.content.clinical_priority)}`}>
                      {report.content.clinical_priority} PRIORITY
                    </span>
                  </div>
                  <span className="text-[9px] text-slate-400 font-bold uppercase">REP ID: {report.report_id.toUpperCase()}</span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="space-y-1">
                    <div className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">Demographics</div>
                    <div className="font-extrabold text-slate-700">
                      {report.patient_name} ({report.content.demographics?.age}yo {report.content.demographics?.gender})
                    </div>
                    <div className="text-slate-500">ID: {patientId}</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">Admission Registry</div>
                    <div className="font-extrabold text-slate-700">
                      {report.content.admission?.diagnosis}
                    </div>
                    <div className="text-slate-500">
                      Bed {report.content.admission?.bed_number} ({report.content.admission?.ward}) &bull; Attending: {report.content.admission?.doctor_name}
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Clinical reasoning */}
              <ReportSection title="AI Clinical Note / Reasoning" icon={Activity}>
                <p className="text-xs text-slate-700 leading-relaxed font-semibold">
                  {report.content.ai_reasoning}
                </p>
              </ReportSection>

              {/* Vitals Trends */}
              <ReportSection title="Telemetry & Vital Sign Trends" icon={Activity}>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {[
                    { name: "Heart Rate", val: report.content.vitals?.heart_rate, unit: "bpm", trend: report.content.vital_trends?.heart_rate?.direction },
                    { name: "Blood Pressure", val: `${report.content.vitals?.systolic_bp}/${report.content.vitals?.diastolic_bp}`, unit: "mmHg", trend: report.content.vital_trends?.systolic_bp?.direction },
                    { name: "SpO₂", val: report.content.vitals?.spo2, unit: "%", trend: report.content.vital_trends?.spo2?.direction },
                    { name: "Temperature", val: report.content.vitals?.temperature, unit: "°C", trend: report.content.vital_trends?.temperature?.direction }
                  ].map((v, i) => (
                    <div key={i} className="border border-slate-100 rounded-xl p-3 bg-slate-50/20">
                      <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">{v.name}</span>
                      <div className="font-extrabold text-slate-800 text-sm mt-1">{v.val} <span className="text-[9px] font-normal text-slate-400">{v.unit}</span></div>
                      <div className="text-[9px] text-slate-500 capitalize mt-0.5">Trend: {v.trend || "stable"}</div>
                    </div>
                  ))}
                </div>
              </ReportSection>

              {/* Abnormal Labs */}
              <ReportSection title={`Abnormal Labs (${report.content.abnormal_labs?.length || 0})`} icon={FlaskConical}>
                {report.content.abnormal_labs?.length > 0 ? (
                  <div className="space-y-2">
                    {report.content.abnormal_labs.map((lab, i) => (
                      <div key={i} className="flex justify-between items-center p-2.5 border border-slate-50 rounded-lg">
                        <div>
                          <span className="font-bold text-slate-700">{lab.metric}</span>
                          <span className="text-slate-400 text-[10px] ml-2">({lab.reference})</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="font-extrabold text-slate-800">{lab.value}</span>
                          <span className={`px-2 py-0.5 text-[8.5px] font-black uppercase tracking-wider rounded-lg ${
                            lab.severity === "CRITICAL" ? "bg-red-50 text-red-600 border border-red-100" : "bg-amber-50 text-amber-600 border border-amber-100"
                          }`}>
                            {lab.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400 italic">No abnormal chemical panel biomarkers logged.</p>
                )}
              </ReportSection>

              {/* Active alerts */}
              <ReportSection title={`Active Alerts (${report.content.active_alerts?.length || 0})`} icon={Bell}>
                {report.content.active_alerts?.length > 0 ? (
                  <div className="space-y-2">
                    {report.content.active_alerts.map((alert, i) => (
                      <div key={i} className="flex items-start gap-2.5 p-3 border border-slate-100 bg-slate-50/20 rounded-xl">
                        <span className={`h-1.5 w-1.5 rounded-full mt-1.5 ${
                          alert.severity === "CRITICAL" ? "bg-red-500" : "bg-amber-500"
                        }`}></span>
                        <div>
                          <div className="font-bold text-slate-700 text-[11px]">{alert.title}</div>
                          <div className="text-[10px] text-slate-500 mt-0.5">{alert.message}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400 italic">No active alarms firing.</p>
                )}
              </ReportSection>

              {/* Recommendations */}
              <ReportSection title="Recommendations & Care Pathways" icon={CheckCircle2}>
                {report.content.clinical_recommendations?.length > 0 ? (
                  <ul className="space-y-2.5">
                    {report.content.clinical_recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-slate-655 font-medium">
                        <CheckCircle2 size={13} className="text-emerald-500 mt-0.5 shrink-0" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-400 italic">No care guidelines created.</p>
                )}
              </ReportSection>

              {/* Confidence Indicator */}
              <div className="space-y-1.5 bg-slate-50 border border-slate-150 rounded-xl p-3.5">
                <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-wider text-slate-400">
                  <span className="flex items-center gap-1"><Gauge size={11} /> Copilot Report Confidence</span>
                  <span className="font-extrabold text-slate-700">{Math.round(report.content.confidence * 100)}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-cyan-600 rounded-full transition-all duration-500" 
                    style={{ width: `${report.content.confidence * 100}%` }}
                  ></div>
                </div>
              </div>

            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
