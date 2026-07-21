import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Search,
  BrainCircuit,
  Loader2,
} from "lucide-react";

import { useClinicalAI } from "../../context/ClinicalAIContext";
import PatientDrawer from "./PatientDrawer";

const riskBadge = {
  HIGH: "bg-red-100 text-red-700",
  MEDIUM: "bg-orange-100 text-orange-700",
  LOW: "bg-green-100 text-green-700",
};

export default function PatientsSection() {
  const navigate = useNavigate();

  const [search, setSearch] = useState("");

  // Drawer State
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerPatientId, setDrawerPatientId] = useState(null);

  const {
    selectedPatient,
    setSelectedPatient,
    analyzePatient,
    loading,
    patientsList,
  } = useClinicalAI();

  const patients = patientsList || [];

  function handlePatientSelect(patient) {
    setSelectedPatient(patient);
    navigate(`/patients/${patient.id}`);
  }

  const filtered = patients.filter((patient) =>
    patient.name.toLowerCase().includes(search.toLowerCase())
  );

  async function handleAnalyze(patient) {
    const payload = {
      patient: {
        id: patient.id,
        name: patient.name,
        age: patient.age,
        gender: patient.gender,
      },
      admission: {
        bed: patient.bed,
        diagnosis: "Septic Shock",
      },
      vitals: {
        heart_rate: 132,
        systolic_bp: 82,
        diastolic_bp: 48,
        respiratory_rate: 31,
        spo2: 89,
        temperature: 39.2,
      },
      labs: {
        lactate: 4.6,
        wbc: 18.2,
        creatinine: 2.1,
      },
      prediction: {
        risk_score: patient.risk_score,
        risk_level: patient.risk_level,
      },
    };

    await analyzePatient(payload);
  }

  return (
    <div className="rounded-[30px] border border-slate-200 bg-white shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b p-6">
        <div>
          <h2 className="text-2xl font-bold">ICU Patients</h2>
          <p className="text-slate-500">
            Select a patient and analyze using AI.
          </p>
        </div>

        <div className="relative">
          <Search
            className="absolute left-3 top-3 text-slate-400"
            size={18}
          />

          <input
            className="rounded-xl border py-2 pl-10 pr-4"
            placeholder="Search patient..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>



      <div className="divide-y">
        {filtered.map((patient) => (
          <motion.div
            key={patient.id}
            whileHover={{ scale: 1.01 }}
            onClick={() => handlePatientSelect(patient)}
            className={`cursor-pointer p-5 transition ${
              selectedPatient?.id === patient.id
                ? "border-l-4 border-cyan-500 bg-cyan-50"
                : ""
            }`}
          >
            <div className="flex items-center justify-between">
              {/* Patient Info */}
              <div>
                <h3 className="text-lg font-bold">{patient.name}</h3>

                <p className="text-slate-500">
                  {patient.id} • {patient.bed}
                </p>

                <p className="mt-1 text-sm text-slate-400">
                  {patient.status}
                </p>
              </div>

              {/* Risk */}
              <div className="text-center">
                <div
                  className={`rounded-full px-3 py-1 text-xs font-bold ${
                    riskBadge[patient.risk_level]
                  }`}
                >
                  {patient.risk_level}
                </div>

                <motion.div
                  key={patient.risk_score}
                  initial={{ scale: 0.9 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.25 }}
                  className="mt-2 text-lg font-bold"
                >
                  {(patient.risk_score * 100).toFixed(0)}%
                </motion.div>
              </div>

              {/* Analyze Button */}
              <button
                onClick={async (e) => {
                  e.stopPropagation();

                  // Run AI Analysis
                  await handleAnalyze(patient);

                  // Open Patient Drawer
                  setDrawerPatientId(patient.id);
                  setDrawerOpen(true);
                }}
                disabled={loading}
                className="rounded-xl bg-cyan-600 px-5 py-3 text-white transition hover:bg-cyan-700 disabled:opacity-60"
              >
                {loading ? (
                  <Loader2
                    className="animate-spin"
                    size={18}
                  />
                ) : (
                  <div className="flex items-center gap-2">
                    <BrainCircuit size={18} />
                    Analyze
                  </div>
                )}
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Patient Drawer */}
      <PatientDrawer
        open={drawerOpen}
        patientId={drawerPatientId}
        onClose={() => {
          setDrawerOpen(false);
          setDrawerPatientId(null);
        }}
      />
    </div>
  );
}