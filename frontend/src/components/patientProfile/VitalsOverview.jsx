import { useClinicalAI } from "../../context/ClinicalAIContext";
import { useEffect, useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  HeartPulse,
  Activity,
  Thermometer,
  Droplets,
  Loader2,
} from "lucide-react";
import { patientService } from "../../services/patientService";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

export default function VitalsOverview() {
  const { selectedPatient, setSelectedPatient, patientsList, recommendation } = useClinicalAI();
  const patientId = selectedPatient?.patient?.id;
  const vitalsData = selectedPatient?.vitals || {};
  const risk = recommendation?.risk_progress;

  const [activeMetric, setActiveMetric] = useState("heartRate");
  const [history, setHistory] = useState([]);
  const [loadingPatient, setLoadingPatient] = useState(false);

  // Auto-select first patient if none is selected
  useEffect(() => {
    if (!selectedPatient && patientsList && patientsList.length > 0) {
      loadPatientDetails(patientsList[0].id);
    }
  }, [selectedPatient, patientsList]);

  async function loadPatientDetails(id) {
    if (!id) return;
    try {
      setLoadingPatient(true);
      const fullPatient = await patientService.getPatientById(id);
      if (fullPatient) {
        setSelectedPatient(fullPatient);
      }
    } catch (err) {
      console.error("Failed to load patient details in VitalsOverview:", err);
    } finally {
      setLoadingPatient(false);
    }
  }

  // Reset history when active patient changes
  useEffect(() => {
    setHistory([]);
  }, [patientId]);

  // Record rolling vital history from live context updates
  useEffect(() => {
    if (!patientId || !vitalsData.heart_rate) return;

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    setHistory(prev => {
      if (prev.length > 0 && prev[prev.length - 1].time === time) {
        return prev;
      }
      
      const newPoint = {
        time,
        heartRate: vitalsData.heart_rate,
        systolic: vitalsData.blood_pressure?.systolic ?? vitalsData.systolic_bp ?? 82,
        diastolic: vitalsData.blood_pressure?.diastolic ?? vitalsData.diastolic_bp ?? 48,
        spo2: vitalsData.spo2 ?? 89,
        respiratoryRate: vitalsData.respiratory_rate ?? 31,
        temperature: vitalsData.temperature ?? 39.2,
        risk: (selectedPatient?.patient?.risk_score ?? selectedPatient?.ai?.risk_progress?.current_risk ?? 0) * 100,
      };

      const updated = [...prev, newPoint];
      if (updated.length > 60) {
        return updated.slice(updated.length - 60);
      }
      return updated;
    });
  }, [vitalsData, patientId, selectedPatient]);

  const systolic = vitalsData.blood_pressure?.systolic ?? vitalsData.systolic_bp;
  const diastolic = vitalsData.blood_pressure?.diastolic ?? vitalsData.diastolic_bp;
  const bpValue = systolic && diastolic ? `${systolic} / ${diastolic}` : "-";

  const vitals = [
    {
      title: "Heart Rate",
      value: vitalsData.heart_rate ?? "-",
      unit: "bpm",
      icon: HeartPulse,
      color: "text-red-500",
      bg: "bg-red-50",
      border: "border-red-100",
    },
    {
      title: "Blood Pressure",
      value: bpValue,
      unit: "mmHg",
      icon: Activity,
      color: "text-cyan-600",
      bg: "bg-cyan-50",
      border: "border-cyan-100",
    },
    {
      title: "SpO₂",
      value: vitalsData.spo2 ? `${vitalsData.spo2}` : "-",
      unit: "%",
      icon: Droplets,
      color: "text-blue-600",
      bg: "bg-blue-50",
      border: "border-blue-100",
    },
    {
      title: "Temperature",
      value: vitalsData.temperature ? `${vitalsData.temperature}` : "-",
      unit: "°C",
      icon: Thermometer,
      color: "text-orange-500",
      bg: "bg-orange-50",
      border: "border-orange-100",
    },
  ];

  const metricColors = {
    heartRate: { stroke: "#ef4444", fill: "#ef4444" },
    bloodPressure: { stroke: "#0891b2", fill: "#0891b2" },
    spo2: { stroke: "#2563eb", fill: "#2563eb" },
    respiratoryRate: { stroke: "#0d9488", fill: "#0d9488" },
    temperature: { stroke: "#ea580c", fill: "#ea580c" },
    risk: { stroke: "#06b6d4", fill: "#06b6d4" },
  };

  const getMetricTitle = () => {
    switch (activeMetric) {
      case "heartRate": return "Heart Rate Trend";
      case "bloodPressure": return "Blood Pressure Trend";
      case "spo2": return "SpO₂ Trend";
      case "respiratoryRate": return "Respiratory Rate Trend";
      case "temperature": return "Temperature Trend";
      case "risk": return "AI Sepsis Risk Trend";
      default: return "Physiological Trend";
    }
  };

  return (
    <div className="space-y-6">
      {/* Patient Selector Dropdown */}
      <div className="flex items-center justify-between bg-white border border-slate-100 rounded-2xl p-5 shadow-sm">
        <div>
          <h2 className="text-sm font-bold text-slate-800">Physiological Telemetry Monitor</h2>
          <p className="text-[10px] text-slate-400 font-semibold mt-0.5">
            {selectedPatient?.patient?.name ? `Currently monitoring ${selectedPatient.patient.name}` : "Please select a patient to start monitoring vitals"}
          </p>
        </div>
        
        {patientsList && patientsList.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-500">Select Patient:</span>
            <select
              value={patientId || ""}
              onChange={(e) => loadPatientDetails(e.target.value)}
              disabled={loadingPatient}
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-black text-slate-700 outline-none focus:border-cyan-500 transition cursor-pointer"
            >
              {patientsList.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name || `${p.first_name} ${p.last_name}`} ({p.id})
                </option>
              ))}
            </select>
            {loadingPatient && <Loader2 className="animate-spin text-slate-400" size={14} />}
          </div>
        )}
      </div>

      {/* Vital Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {vitals.map((item) => {
          const Icon = item.icon;
          return (
            <motion.div
              key={item.title}
              whileHover={{ y: -2 }}
              className="clinical-card p-5"
            >
              <div className="flex items-center justify-between">
                <Icon
                  className={item.color}
                  size={20}
                />
                <span className="rounded-lg bg-slate-50 border border-slate-100 px-2 py-0.5 text-[9px] font-black uppercase text-slate-400">
                  Normal Range
                </span>
              </div>

              <h2 className="mt-4 text-3xl font-black text-slate-800 tracking-tight">
                {item.value}
              </h2>
              <p className="text-[10px] text-slate-450 font-bold uppercase mt-0.5">
                {item.unit} • {item.title}
              </p>

              <div className="mt-4 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full rounded-full bg-cyan-600"
                  style={{ width: "75%" }}
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Physiological Trend Chart */}
      <motion.div
        whileHover={{ y: -2 }}
        className="clinical-card p-6"
      >
        <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-slate-50 pb-4 gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-800">
              {getMetricTitle()}
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Live ICU physiological telemetry stream
            </p>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {[
              { id: "heartRate", label: "HR" },
              { id: "bloodPressure", label: "BP" },
              { id: "spo2", label: "SpO₂" },
              { id: "respiratoryRate", label: "RR" },
              { id: "temperature", label: "Temp" },
              { id: "risk", label: "Risk" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveMetric(tab.id)}
                className={`rounded-lg px-2.5 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                  activeMetric === tab.id
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-655 hover:bg-slate-200"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {history.length === 0 ? (
          <div className="flex h-80 flex-col items-center justify-center rounded-xl bg-slate-50/50 border border-dashed border-slate-200 mt-6">
            <Loader2 className="animate-spin text-slate-400 mb-2" size={24} />
            <p className="text-xs text-slate-450 font-bold">Waiting for stream data telemetry...</p>
          </div>
        ) : (
          <div className="mt-6">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={history}
                  margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                >
                  <defs>
                    <linearGradient
                      id="chartColor"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="0%"
                        stopColor={metricColors[activeMetric]?.stroke}
                        stopOpacity={0.15}
                      />
                      <stop
                        offset="100%"
                        stopColor={metricColors[activeMetric]?.stroke}
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>

                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} />
                  <Tooltip contentStyle={{ background: '#0f172a', borderRadius: '12px', border: 'none', color: '#fff', fontSize: '11px', fontWeight: 'bold' }} />

                  {activeMetric === "bloodPressure" ? (
                    <>
                      <Area
                        type="monotone"
                        dataKey="systolic"
                        name="Systolic BP"
                        stroke="#0ea5e9"
                        fill="url(#chartColor)"
                        strokeWidth={2.5}
                      />
                      <Area
                        type="monotone"
                        dataKey="diastolic"
                        name="Diastolic BP"
                        stroke="#2563eb"
                        fill="none"
                        strokeWidth={1.5}
                      />
                    </>
                  ) : (
                    <Area
                      type="monotone"
                      dataKey={activeMetric}
                      name={getMetricTitle()}
                      stroke={metricColors[activeMetric]?.stroke}
                      fill="url(#chartColor)"
                      strokeWidth={2.5}
                    />
                  )}
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-6 flex justify-between rounded-xl bg-slate-50/70 border border-slate-100 p-4 text-xs font-semibold text-slate-500">
              <div>
                <p className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">
                  Baseline Risk
                </p>
                <p className="text-lg font-black text-slate-800 mt-1">
                  {((risk?.previous_risk ?? 0) * 100).toFixed(0)}%
                </p>
              </div>

              <div>
                <p className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">
                  Current Risk Index
                </p>
                <p className="text-lg font-black text-slate-850 mt-1">
                  {((risk?.current_risk ?? 0) * 100).toFixed(0)}%
                </p>
              </div>

              <div>
                <p className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">
                  Physiological Trend
                </p>
                <p className="text-lg font-black text-slate-800 mt-1 uppercase">
                  {risk?.trend ?? "Stable"}
                </p>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}