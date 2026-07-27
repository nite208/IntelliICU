import React, { useState, useEffect } from "react";
import { useClinicalAI } from "../../context/ClinicalAIContext";
import ChatPanel from "../../components/clinicalCopilot/ChatPanel";
import { MessageSquare, Users, Activity, Loader2 } from "lucide-react";
import { patientService } from "../../services/patientService";

export default function ClinicalCopilotPage() {
  const { selectedPatient, setSelectedPatient, patientsList } = useClinicalAI();
  const [loading, setLoading] = useState(false);

  const patientId = selectedPatient?.patient?.id;

  // Auto select first patient if none selected
  useEffect(() => {
    if (!selectedPatient && patientsList && patientsList.length > 0) {
      handleSelectPatient(patientsList[0].id);
    }
  }, [selectedPatient, patientsList]);

  const handleSelectPatient = async (id) => {
    if (!id) return;
    try {
      setLoading(true);
      const fullPatient = await patientService.getPatientById(id);
      if (fullPatient) {
        setSelectedPatient(fullPatient);
      }
    } catch (err) {
      console.error("Failed to load patient for copilot:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="rounded-2xl bg-gradient-to-r from-[#070b14] via-[#091220] to-[#0c192e] p-6 text-white shadow-xl border border-slate-800/80">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="rounded-xl bg-amber-500/10 border border-amber-500/20 p-3 text-amber-400">
              <MessageSquare size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight">Clinical Copilot</h1>
              <p className="mt-1 text-xs text-slate-400">
                EHR-aware conversational AI assistant with per-patient RAG context & guideline retrieval
              </p>
            </div>
          </div>

          {/* Patient Selector */}
          {patientsList && patientsList.length > 0 && (
            <div className="flex items-center gap-3 bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl border border-white/10">
              <Users size={16} className="text-cyan-400" />
              <span className="text-xs font-bold text-slate-200">Patient:</span>
              <select
                value={patientId || ""}
                onChange={(e) => handleSelectPatient(e.target.value)}
                disabled={loading}
                className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-bold text-white outline-none focus:border-cyan-500 transition cursor-pointer"
              >
                {patientsList.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name || `${p.first_name} ${p.last_name}`} ({p.id})
                  </option>
                ))}
              </select>
              {loading && <Loader2 className="animate-spin text-cyan-400" size={14} />}
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Panel Container */}
      {patientId ? (
        <ChatPanel patientId={patientId} />
      ) : (
        <div className="clinical-card p-12 text-center text-slate-500 space-y-3">
          <Activity size={32} className="mx-auto text-slate-400 animate-pulse" />
          <h3 className="text-base font-bold text-slate-700">Select a Patient</h3>
          <p className="text-xs">Please select an active ICU patient above to open Clinical Copilot chat context.</p>
        </div>
      )}
    </div>
  );
}
