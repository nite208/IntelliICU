import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  BrainCircuit,
  Download,
  Printer,
  HeartPulse,
  Activity,
  Thermometer,
  Clock3,
  Loader2,
} from "lucide-react";

import { useClinicalAI } from "../../context/ClinicalAIContext";

function buildAnalysisPayload(selectedPatient) {
  const patient = selectedPatient?.patient || {};
  const admission = selectedPatient?.admission || {};
  const vitals = selectedPatient?.vitals || {};
  const labs = selectedPatient?.labs || {};

  return {
    patient: {
      id: patient.id,
      name: patient.name,
      age: patient.age,
      gender: patient.gender,
    },
    admission: {
      bed: admission.bed || patient.bed,
      diagnosis: admission.diagnosis || "Septic Shock",
    },
    vitals: {
      heart_rate: vitals.heart_rate ?? 132,
      systolic_bp: vitals.blood_pressure?.systolic ?? vitals.systolic_bp ?? 82,
      diastolic_bp: vitals.blood_pressure?.diastolic ?? vitals.diastolic_bp ?? 48,
      respiratory_rate: vitals.respiratory_rate ?? 31,
      spo2: vitals.spo2 ?? 89,
      temperature: vitals.temperature ?? 39.2,
    },
    labs: {
      lactate: parseFloat(labs.Lactate || labs.lactate) || 4.6,
      wbc: parseFloat(labs.WBC || labs.wbc) || 18.2,
      creatinine: parseFloat(labs.Creatinine || labs.creatinine) || 2.1,
    },
    prediction: {
      risk_score: patient.risk_score,
      risk_level: patient.risk_level,
    },
  };
}

export default function PatientHeader() {
  const navigate = useNavigate();
  const { selectedPatient, analyzePatient, loading } = useClinicalAI();
  const patient = selectedPatient?.patient;

  const rawRisk = selectedPatient?.risk_level ?? patient?.risk_level ?? selectedPatient?.ai?.summary?.overall_condition;

  const getNormalizedRisk = (val) => {
    if (!val) return "LOW";
    const v = String(val).toUpperCase();
    if (v === "CRITICAL" || v === "HIGH") return "HIGH";
    if (v === "SERIOUS" || v === "MEDIUM") return "MEDIUM";
    if (v === "STABLE" || v === "LOW") return "LOW";
    return "LOW";
  };

  const riskLevel = getNormalizedRisk(rawRisk);
  const riskScore = selectedPatient?.risk_score ?? patient?.risk_score ?? selectedPatient?.ai?.risk_progress?.current_risk ?? 0;
  const bed = selectedPatient?.admission?.bed ?? patient?.bed ?? "-";

  if (!patient) {
    return (
      <div className="rounded-[30px] bg-white p-8 shadow-xl border border-slate-200">
        <h2 className="text-3xl font-bold">
          No Patient Selected
        </h2>

        <p className="mt-3 text-slate-500">
          Select a patient from the Dashboard to view the Clinical Workspace.
        </p>
      </div>
    );
  }

  const riskColor = {
    HIGH: "bg-red-100 text-red-700 border-red-200",
    MEDIUM: "bg-orange-100 text-orange-700 border-orange-200",
    LOW: "bg-emerald-100 text-emerald-700 border-emerald-200",
  };

  return (
    <div className="rounded-[32px] bg-white border border-slate-200 shadow-xl overflow-hidden">

      {/* Top Banner */}

      <div className="bg-gradient-to-r from-slate-900 via-cyan-900 to-blue-900 p-8 text-white">

        <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-8">

          {/* Left */}

          <div className="flex items-center gap-6">

            <button
              onClick={() => navigate("/dashboard")}
              className="rounded-xl bg-white/10 p-3 transition hover:bg-white/20"
            >
              <ArrowLeft />
            </button>

            <div className="flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 text-4xl font-black">

              {(patient?.name ?? "P").charAt(0)}

            </div>

            <div>

              <h1 className="text-4xl font-black">

                {patient?.name}

              </h1>

              <div className="mt-3 flex flex-wrap items-center gap-3 text-cyan-100">

                <span>{patient?.id}</span>

                <span>•</span>

                <span>{patient?.age} Years</span>

                <span>•</span>

                <span>{patient?.gender}</span>

                <span>•</span>

                <span>{bed}</span>

              </div>

            </div>

          </div>

          {/* Right */}

          <div className="flex flex-wrap gap-3">

            <button
              onClick={() => analyzePatient(buildAnalysisPayload(selectedPatient))}
              disabled={loading}
              className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 font-semibold transition hover:bg-cyan-400 disabled:opacity-60"
            >
              {loading ? (
                <Loader2 className="animate-spin" size={18} />
              ) : (
                <BrainCircuit size={18} />
              )}
              Analyze Again
            </button>

            <button className="rounded-xl bg-white/10 px-5 py-3 hover:bg-white/20 transition">

              <Download size={18} />

            </button>

            <button className="rounded-xl bg-white/10 px-5 py-3 hover:bg-white/20 transition">

              <Printer size={18} />

            </button>

          </div>

        </div>

      </div>

      {/* Live Status */}

      <div className="grid grid-cols-2 xl:grid-cols-5 gap-6 p-8">

        <div className="rounded-2xl bg-red-50 border border-red-100 p-5">

          <HeartPulse className="text-red-500" />

          <h2 className="mt-4 text-4xl font-black">

            {selectedPatient?.vitals?.heart_rate ?? "-"}

          </h2>

          <p className="text-slate-500">

            Heart Rate

          </p>

        </div>

        <div className="rounded-2xl bg-cyan-50 border border-cyan-100 p-5">

          <Activity className="text-cyan-600" />

          <h2 className="mt-4 text-4xl font-black">

            {selectedPatient?.vitals?.spo2 ? `${selectedPatient.vitals.spo2}%` : "-"}

          </h2>

          <p className="text-slate-500">

            SpO₂

          </p>

        </div>

        <div className="rounded-2xl bg-orange-50 border border-orange-100 p-5">

          <Thermometer className="text-orange-600" />

          <h2 className="mt-4 text-4xl font-black">

            {selectedPatient?.vitals?.temperature ? `${selectedPatient.vitals.temperature}°` : "-"}

          </h2>

          <p className="text-slate-500">

            Temperature

          </p>

        </div>

        <div className="rounded-2xl border p-5">

          <h2
            className={`inline-flex rounded-full border px-4 py-2 text-sm font-bold ${
              riskColor[riskLevel]
            }`}
          >
            {riskLevel}
          </h2>

          <h3 className="mt-5 text-3xl font-black">

            {((riskScore) * 100).toFixed(0)}%

          </h3>

          <p className="text-slate-500">

            AI Risk Score

          </p>

        </div>

        <div className="rounded-2xl border p-5">

          <Clock3 className="text-emerald-600" />

          <h2 className="mt-4 text-xl font-black">

            Updated Now

          </h2>

          <p className="mt-2 text-slate-500">

            Live Monitoring Active

          </p>

        </div>

      </div>

    </div>
  );
}