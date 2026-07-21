import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  Heart,
  Thermometer,
  Wind,
  AlertCircle,
  FileText,
  Pill,
  Clock,
  Brain,
  User,
  Calendar,
  ShieldAlert,
  CheckCircle,
  Info as InfoIcon,
  X,
  Droplet,
  Stethoscope
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

import { patientService } from "../../services/patientService";
import usePatientStream from "../../hooks/usePatientStream";
// ====================================================
// REUSABLE COMPONENTS
// ====================================================

const Section = ({ title, icon: Icon, children, className = '' }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden ${className}`}>
    <div className="flex items-center px-5 py-4 border-b border-slate-100 bg-slate-50/50">
      {Icon && <Icon className="w-5 h-5 text-slate-500 mr-2" />}
      <h3 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">{title}</h3>
    </div>
    <div className="p-5">
      {children}
    </div>
  </div>
);

const VitalCard = ({ title, value, unit, icon: Icon, colorClass, trend }) => (
  <div className={`p-4 rounded-lg border ${colorClass} flex flex-col`}>
    <div className="flex items-center justify-between mb-2">
      <span className="text-sm font-medium text-slate-600">{title}</span>
      <Icon className="w-5 h-5 opacity-70" />
    </div>
    <div className="flex items-baseline gap-1">
      <span className="text-2xl font-bold">{value || '-'}</span>
      <span className="text-xs font-medium opacity-80">{unit}</span>
    </div>
    {trend && (
      <div className="mt-2 text-xs font-medium opacity-80">
        {trend}
      </div>
    )}
  </div>
);

const Info = ({ label, value }) => (
  <div className="flex flex-col mb-3">
    <span className="text-xs text-slate-500 font-medium">{label}</span>
    <span className="text-sm text-slate-900 font-medium">{value || '-'}</span>
  </div>
);

const EmptyMessage = ({ text }) => (
  <div className="flex items-center justify-center p-6 text-slate-400 text-sm italic">
    {text}
  </div>
);

// ====================================================
// MAIN COMPONENT
// ====================================================

export default function PatientDrawer({ open, patientId, onClose }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [profile, setProfile] = useState(null);
  const {
    connected,
    currentPatient,
    latestVitals,
    latestRisk,
    lastUpdated,
} = usePatientStream(patientId);

  useEffect(() => {
    if (open && patientId) {
      loadPatient();
    }
  }, [open, patientId]);

  const loadPatient = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await patientService.getPatient(patientId);
      setProfile(data);
    } catch (err) {
      setError('Failed to load patient data');
    } finally {
      setLoading(false);
    }
  };

  const getTimelineIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'admission': return <User className="w-4 h-4 text-blue-600" />;
      case 'medication': return <Pill className="w-4 h-4 text-purple-600" />;
      case 'alert': return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'laboratory': return <Droplet className="w-4 h-4 text-cyan-600" />;
      case 'ai': return <Brain className="w-4 h-4 text-indigo-600" />;
      default: return <Clock className="w-4 h-4 text-slate-600" />;
    }
  };

  const getTimelineColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'admission': return 'bg-blue-100 border-blue-200';
      case 'medication': return 'bg-purple-100 border-purple-200';
      case 'alert': return 'bg-red-100 border-red-200';
      case 'laboratory': return 'bg-cyan-100 border-cyan-200';
      case 'ai': return 'bg-indigo-100 border-indigo-200';
      default: return 'bg-slate-100 border-slate-200';
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-40"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed inset-y-0 right-0 w-full max-w-6xl bg-slate-50 shadow-2xl z-50 overflow-hidden flex flex-col border-l border-slate-200"
          >
            {loading && (
              <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
                <div className="flex flex-col items-center">
                  <Activity className="w-8 h-8 text-blue-600 animate-pulse mb-4" />
                  <span className="text-slate-600 font-medium">Loading clinical profile...</span>
                </div>
              </div>
            )}

            {error && (
              <div className="absolute inset-0 bg-white z-50 flex items-center justify-center">
                <div className="text-center p-6 bg-red-50 rounded-xl border border-red-100">
                  <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-3" />
                  <h3 className="text-lg font-bold text-red-800 mb-1">Error Loading Patient</h3>
                  <p className="text-red-600 text-sm mb-4">{error}</p>
                  <button onClick={loadPatient} className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700">
                    Retry
                  </button>
                </div>
              </div>
            )}

            {profile && (
              <>
                {/* Enterprise Header */}
                <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shrink-0 shadow-sm z-10">
                  <div className="flex items-center gap-6">
                    <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-inner">
                      {profile.patient?.name?.charAt(0) || 'P'}
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-slate-900 leading-tight">
                        {profile.patient?.name}
                      </h2>
                      <div className="flex items-center gap-4 text-sm text-slate-500 mt-1">
    <span className="flex items-center gap-1">
        <InfoIcon className="w-4 h-4" />
        ID: {profile.patient?.id}
    </span>

    <span className="flex items-center gap-1">
        <Calendar className="w-4 h-4" />
        Age: {profile.patient?.age}y
    </span>

    <span className="flex items-center gap-1">
        <User className="w-4 h-4" />
        Gender: {profile.patient?.gender}
    </span>

    <span className="flex items-center gap-1">
        <Activity className="w-4 h-4" />
        Bed: {profile.patient?.bed}
    </span>

    <div className="flex items-center gap-2">
        <span
            className={`w-2 h-2 rounded-full ${
                connected ? "bg-emerald-500" : "bg-slate-400"
            }`}
        />

        <span className="text-xs font-medium">
            {connected ? "Live" : "Offline"}
        </span>

        {lastUpdated && (
            <span className="text-xs text-slate-400">
                ({lastUpdated})
            </span>
        )}
    </div>
</div>
                    </div>
                    <button
                      onClick={onClose}
                      className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
                    >
                      <X className="w-6 h-6" />
                    </button>
                  </div>
                </header>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
                  <div className="grid grid-cols-12 gap-6">
                    
                    {/* LEFT COLUMN - Core Clinical (8 cols) */}
                    <div className="col-span-12 xl:col-span-8 space-y-6">

                      {/* Active Alerts */}
                      {profile.alerts?.length > 0 && (
                        <div className="space-y-3">
                          {profile.alerts.map((alert, idx) => {
                            const severity = alert.severity?.toUpperCase();
                            
                            let colorTheme = { bg: 'bg-amber-50', border: 'border-amber-500', icon: 'text-amber-500', title: 'text-amber-900', text: 'text-amber-800' };
                            
                            if (severity === 'HIGH') {
                              colorTheme = { bg: 'bg-red-50', border: 'border-red-600', icon: 'text-red-600', title: 'text-red-900', text: 'text-red-800' };
                            } else if (severity === 'LOW') {
                              colorTheme = { bg: 'bg-blue-50', border: 'border-blue-500', icon: 'text-blue-500', title: 'text-blue-900', text: 'text-blue-800' };
                            }

                            return (
                              <div key={idx} className={`${colorTheme.bg} border-l-4 ${colorTheme.border} p-4 rounded-r-xl shadow-sm flex gap-3 items-start`}>
                                <AlertCircle className={`w-5 h-5 shrink-0 mt-0.5 ${colorTheme.icon}`} />
                                <div>
                                  <h4 className={`text-sm font-bold ${colorTheme.title}`}>
                                    {alert.title}
                                  </h4>
                                  <p className={`text-sm mt-1 ${colorTheme.text}`}>
                                    {alert.message}
                                  </p>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {/* Live Vitals */}
                      <Section title="Live Vitals" icon={Activity}>
                        {profile.vitals ? (
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <VitalCard
                              title="Heart Rate"
                              value={profile.vitals.heart_rate}
                              unit="bpm"
                              icon={Heart}
                              colorClass="bg-rose-50 border-rose-100 text-rose-700"
                            />
                            <VitalCard
                              title="SpO₂"
                              value={profile.vitals.spo2}
                              unit="%"
                              icon={Wind}
                              colorClass="bg-sky-50 border-sky-100 text-sky-700"
                            />
                            <VitalCard
                              title="MAP"
                              value={profile.vitals.mean_arterial_pressure}
                              unit="mmHg"
                              icon={Activity}
                              colorClass="bg-amber-50 border-amber-100 text-amber-700"
                            />
                            <VitalCard
                              title="BP"
                              value={`${profile.vitals.blood_pressure?.systolic || '-'}/${profile.vitals.blood_pressure?.diastolic || '-'}`}
                              unit="mmHg"
                              icon={Activity}
                              colorClass="bg-indigo-50 border-indigo-100 text-indigo-700"
                            />
                            <VitalCard
                              title="Temp"
                              value={profile.vitals.temperature}
                              unit="°C"
                              icon={Thermometer}
                              colorClass="bg-orange-50 border-orange-100 text-orange-700"
                            />
                            <VitalCard
                              title="Resp Rate"
                              value={profile.vitals.respiratory_rate}
                              unit="bpm"
                              icon={Wind}
                              colorClass="bg-teal-50 border-teal-100 text-teal-700"
                            />
                          </div>
                        ) : (
                          <EmptyMessage text="No current vitals available." />
                        )}
                      </Section>

                      {/* Enterprise Vital Trends */}
                      <Section title="Enterprise Vital Trends" icon={Activity}>
                        {profile.history && profile.history.length > 0 ? (
                          <div className="space-y-6">
                            <div className="h-64">
                              <h4 className="text-xs font-semibold text-slate-500 mb-2">Heart Rate & SpO₂</h4>
                              <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={profile.history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                  <XAxis dataKey="time" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                                  <YAxis yAxisId="left" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                                  <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} domain={[80, 100]} />
                                  <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                                  <Line yAxisId="left" type="monotone" dataKey="heart_rate" name="HR (bpm)" stroke="#e11d48" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
                                  <Line yAxisId="right" type="monotone" dataKey="spo2" name="SpO₂ (%)" stroke="#0284c7" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
                                </LineChart>
                              </ResponsiveContainer>
                            </div>
                            <div className="h-64">
                              <h4 className="text-xs font-semibold text-slate-500 mb-2">MAP, Temp & Respiration</h4>
                              <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={profile.history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                  <XAxis dataKey="time" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                                  <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                                  <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                                  <Line type="monotone" dataKey="mean_arterial_pressure" name="MAP (mmHg)" stroke="#d97706" strokeWidth={2} dot={{ r: 3 }} />
                                  <Line type="monotone" dataKey="temperature" name="Temp (°C)" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
                                  <Line type="monotone" dataKey="respiratory_rate" name="RR (bpm)" stroke="#0d9488" strokeWidth={2} dot={{ r: 3 }} />
                                </LineChart>
                              </ResponsiveContainer>
                            </div>
                          </div>
                        ) : (
                          <EmptyMessage text="No historical vitals data." />
                        )}
                      </Section>

                      {/* Labs & Medications (Split Row) */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <Section title="Laboratory Results" icon={Droplet}>
                          {profile.labs && Object.keys(profile.labs).length > 0 ? (
                            <div className="space-y-3">
                              {Object.entries(profile.labs).map(([testName, labValue], idx) => (
                                <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100">
                                  <div className="text-sm font-semibold text-slate-800">{testName}</div>
                                  <div className="text-right">
                                    <div className="text-sm font-bold text-slate-700">
                                      {typeof labValue === 'object' ? JSON.stringify(labValue) : labValue}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <EmptyMessage text="No recent laboratory results." />
                          )}
                        </Section>

                        <Section title="Active Medications" icon={Pill}>
                          {profile.medications?.length > 0 ? (
                            <div className="space-y-3">
                              {profile.medications.map((med, idx) => (
                                <div key={idx} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                  <Pill className="w-4 h-4 text-slate-400 mt-0.5" />
                                  <div>
                                    <div className="text-sm font-semibold text-slate-800">{med.name}</div>
                                    <div className="text-xs text-slate-600 mt-0.5">{med.dose} • {med.route} • {med.frequency}</div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <EmptyMessage text="No active medications." />
                          )}
                        </Section>
                      </div>

                      {/* Clinical Notes */}
                      <Section title="Clinical Notes" icon={FileText}>
                        {profile.clinical_notes?.length > 0 ? (
                          <div className="space-y-4">
                            {profile.clinical_notes.map((noteItem, idx) => (
                              <div key={idx} className="p-4 rounded-lg bg-slate-50 border border-slate-100">
                                <div className="flex justify-between items-center mb-2">
                                  <span className="text-sm font-bold text-slate-700">{noteItem.author}</span>
                                  <span className="text-xs text-slate-500">{noteItem.time}</span>
                                </div>
                                <p className="text-sm text-slate-600 whitespace-pre-line">{noteItem.note}</p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <EmptyMessage text="No clinical notes available." />
                        )}
                      </Section>

                    </div>

                    {/* RIGHT COLUMN - Intelligence & Timeline (4 cols) */}
                    <div className="col-span-12 xl:col-span-4 space-y-6">
                      
                      {/* Admission Information */}
                      <Section title="Admission Details" icon={InfoIcon}>
                        <div className="grid grid-cols-2 gap-4">
                          <Info label="Admit Date" value={profile.admission?.admission_date} />
                          <Info label="ICU Day" value={profile.admission?.icu_day} />
                          <div className="col-span-2">
                            <Info label="Primary Diagnosis" value={profile.admission?.diagnosis} />
                          </div>
                          <div className="col-span-2">
                            <Info label="Attending Physician" value={profile.admission?.attending_physician} />
                          </div>
                          <Info label="Unit" value={profile.admission?.unit} />
                          <Info label="Code Status" value={profile.admission?.code_status} />
                        </div>
                      </Section>

                      {/* AI Recommendations */}
                      <Section title="AI Recommendations" icon={CheckCircle} className="border-indigo-100">
                        {profile.recommendations?.length > 0 ? (
                          <div className="space-y-3">
                            {profile.recommendations.map((rec, idx) => (
                              <div key={idx} className="p-3 bg-indigo-50/50 rounded-lg border border-indigo-100 flex gap-3 items-start">
                                <div className="bg-indigo-100 text-indigo-700 p-1.5 rounded-md mt-0.5">
                                  <Stethoscope className="w-4 h-4" />
                                </div>
                                <div>
                                  <div className="flex justify-between items-center mb-1">
                                    <div className="text-sm font-semibold text-slate-800">{rec.title}</div>
                                    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${rec.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
                                      {rec.priority}
                                    </span>
                                  </div>
                                  <div className="text-xs text-slate-600">{rec.description}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <EmptyMessage text="No current recommendations." />
                        )}
                      </Section>

                      {/* AI Clinical Summary */}
                      {profile.ai?.summary && (
                        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-xl p-5 shadow-sm">
                          <div className="flex items-center gap-2 mb-3">
                            <Brain className="w-5 h-5 text-indigo-600" />
                            <h3 className="text-sm font-bold text-indigo-900 uppercase tracking-wider">AI Clinical Summary</h3>
                          </div>
                          <p className="text-indigo-900/80 leading-relaxed text-sm">
                            {profile.ai.summary}
                          </p>
                        </div>
                      )}

                      {/* Explainable AI */}
                      <Section title="Explainable AI" icon={Brain}>
                        {profile.ai?.explainability && profile.ai.explainability.length > 0 ? (
                          <div className="space-y-4">
                            {profile.ai.explainability.map((item, idx) => (
                              <div key={idx} className="relative">
                                <div className="flex justify-between text-xs mb-1">
                                  <span className="font-medium text-slate-700">{item.feature}</span>
                                  <span className={`font-bold ${item.risk === 'High' ? 'text-red-600' : 'text-emerald-600'}`}>
                                    {item.contribution}
                                  </span>
                                </div>
                                <div className="w-full bg-slate-100 rounded-full h-1.5">
                                  <div
                                    className={`h-1.5 rounded-full ${item.risk === 'High' ? 'bg-red-500' : 'bg-emerald-500'}`}
                                    style={{ width: `${item.importance * 100}%` }}
                                  ></div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <EmptyMessage text="Explainability metrics unavailable." />
                        )}
                      </Section>

                      {/* Risk Progress */}
                      <Section title="Risk Progress" icon={Activity}>
                        {profile.ai?.risk_progress && profile.ai.risk_progress.length > 0 ? (
                          <div className="h-48">
                            <ResponsiveContainer width="100%" height="100%">
                              <AreaChart data={profile.ai.risk_progress} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                                <defs>
                                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                                  </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                                <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} domain={[0, 100]} />
                                <RechartsTooltip contentStyle={{ fontSize: '12px', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                <Area type="monotone" dataKey="riskScore" stroke="#ef4444" fillOpacity={1} fill="url(#colorRisk)" />
                              </AreaChart>
                            </ResponsiveContainer>
                          </div>
                        ) : (
                          <EmptyMessage text="Risk trajectory unavailable." />
                        )}
                      </Section>

                      {/* Clinical Timeline */}
                      <Section title="Clinical Timeline" icon={Clock}>
                        {profile.timeline && profile.timeline.length > 0 ? (
                          <div className="relative pl-4 border-l-2 border-slate-200 space-y-6 py-2 ml-2">
                            {profile.timeline.map((event, idx) => (
                              <div key={idx} className="relative">
                                <div className={`absolute -left-[25px] w-8 h-8 rounded-full flex items-center justify-center border-2 bg-white ${getTimelineColor(event.type)} shadow-sm z-10`}>
                                  {getTimelineIcon(event.type)}
                                </div>
                                <div className="pl-6 pt-1">
                                  <div className="flex flex-col">
                                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">{event.timestamp || event.time}</span>
                                    <span className="text-sm font-semibold text-slate-800 mt-0.5">{event.description}</span>
                                  </div>
                                  {event.details && (
                                    <p className="text-xs text-slate-600 mt-1 bg-slate-50 p-2 rounded border border-slate-100">
                                      {event.details}
                                    </p>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <EmptyMessage text="No timeline events recorded." />
                        )}
                      </Section>

                    </div>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}