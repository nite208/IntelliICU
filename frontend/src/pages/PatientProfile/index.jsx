import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Loader2, AlertCircle, Download, FileText, Database } from "lucide-react";

import PatientHeader from "../../components/patientProfile/PatientHeader";
import VitalsOverview from "../../components/patientProfile/VitalsOverview";
import AIRecommendationPanel from "../../components/patientProfile/AIRecommendation";
import ClinicalTimeline from "../../components/patientProfile/ClinicalTimeline";
import EvidencePanel from "../../components/patientProfile/EvidencePanel";
import ExplainabilityPanel from "../../components/patientProfile/ExplainabilityPanel";
import LabResults from "../../components/patientProfile/LabResults";
import ChatPanel from "../../components/clinicalCopilot/ChatPanel";

import { patientService } from "../../services/patientService";
import { timelineService } from "../../services/timelineService";
import { useClinicalAI } from "../../context/ClinicalAIContext";

// Reports component sub-tab
const ReportsTab = ({ patientId }) => {
  const [format, setFormat] = useState("pdf");
  const [exporting, setExporting] = useState(false);

  const handleDownload = async () => {
    if (!patientId) return;
    try {
      setExporting(true);
      await timelineService.downloadExport(patientId, format, "all", "");
    } catch (err) {
      console.error("Timeline export failed:", err);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="clinical-card p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Export Clinical Reports</h2>
        <p className="text-xs text-slate-500 mt-1">
          Generate structured clinical summaries, timeline audit logs, and diagnostic files
        </p>
      </div>

      <div className="space-y-4">
        <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Report Format</label>
        <div className="grid grid-cols-3 gap-4">
          {[
            { id: "pdf", label: "PDF Document", icon: FileText, desc: "Clinician Signoff" },
            { id: "csv", label: "CSV Dataset", icon: Download, desc: "Data Analytics" },
            { id: "json", label: "JSON Raw Data", icon: Database, desc: "Developer Feed" },
          ].map((item) => (
            <div
              key={item.id}
              onClick={() => setFormat(item.id)}
              className={`cursor-pointer rounded-2xl border p-4.5 transition text-center flex flex-col items-center justify-center ${
                format === item.id
                  ? "border-cyan-600 bg-cyan-50/30 text-cyan-700"
                  : "border-slate-150 hover:bg-slate-50 text-slate-500"
              }`}
            >
              <item.icon size={20} className="mb-2" />
              <span className="text-xs font-bold block">{item.label}</span>
              <span className="text-[9px] opacity-75 mt-0.5 block">{item.desc}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-4 border-t border-slate-50">
        <button
          onClick={handleDownload}
          disabled={exporting || !patientId}
          className="w-full flex items-center justify-center gap-2 rounded-2xl bg-slate-900 hover:bg-slate-850 text-white font-bold py-3.5 text-xs shadow-md transition disabled:opacity-50"
        >
          {exporting ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
          ) : (
            <>
              <Download size={14} />
              Export Patient File
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default function PatientProfile() {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const { setSelectedPatient } = useClinicalAI();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview"); // overview, timeline, evidence, explainability, reports

  useEffect(() => {
    loadPatient();
  }, [patientId]);

  async function loadPatient() {
    try {
      setLoading(true);
      setError(null);

      const patient = await patientService.getPatientById(patientId);

      if (!patient) {
        setError("Patient not found.");
        setSelectedPatient(null);
        return;
      }

      setSelectedPatient(patient);
    } catch (err) {
      console.error(err);
      setError("Failed to load patient details.");
      setSelectedPatient(null);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="flex items-center gap-3 text-slate-600">
          <Loader2 className="animate-spin" size={28} />
          <span className="text-lg font-semibold">Loading patient profile...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="clinical-card p-10 text-center max-w-md mx-auto mt-16">
        <AlertCircle className="mx-auto text-red-500" size={48} />
        <h2 className="mt-4 text-xl font-bold text-slate-800">{error}</h2>
        <button
          onClick={() => navigate("/dashboard")}
          className="mt-6 rounded-xl bg-slate-900 px-6 py-3 font-semibold text-white hover:bg-slate-850 transition"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PatientHeader />

      {/* Tabs Selector Navigation */}
      <div className="flex border-b border-slate-200">
        {[
          { id: "overview", label: "Overview" },
          { id: "timeline", label: "Timeline" },
          { id: "evidence", label: "Evidence" },
          { id: "explainability", label: "Explainability" },
          { id: "reports", label: "Reports" },
          { id: "copilot", label: "Clinical Copilot" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-6 py-3.5 text-xs font-black uppercase tracking-wider transition-all border-b-2 -mb-[1px] ${
              activeTab === tab.id
                ? "border-cyan-600 text-cyan-600"
                : "border-transparent text-slate-400 hover:text-slate-655"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-12 gap-6 items-start">
        {/* Left Column - Active Tab Component */}
        <div className="col-span-12 xl:col-span-8 space-y-6">
          {activeTab === "overview" && (
            <>
              <VitalsOverview />
              <LabResults />
            </>
          )}

          {activeTab === "timeline" && (
            <ClinicalTimeline />
          )}

          {activeTab === "evidence" && (
            <EvidencePanel />
          )}

          {activeTab === "explainability" && (
            <ExplainabilityPanel />
          )}

          {activeTab === "reports" && (
            <ReportsTab patientId={patientId} />
          )}

          {activeTab === "copilot" && (
            <ChatPanel patientId={patientId} />
          )}
        </div>

        {/* Right Column - Pinned Sticky AI Recommendation */}
        <div className="col-span-12 xl:col-span-4 xl:sticky xl:top-6">
          <AIRecommendationPanel />
        </div>
      </div>
    </div>
  );
}
