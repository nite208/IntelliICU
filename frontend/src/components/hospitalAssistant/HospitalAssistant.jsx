/**
 * HospitalAssistant.jsx
 *
 * Enterprise Hospital-Wide AI Assistant — Phase 13.6.
 *
 * Layout:
 * ┌──────────────────────────────────────────────────────────────────┐
 * │  Header banner (Hospital AI Command Centre)                      │
 * ├─────────────────────────┬────────────────────────────────────────┤
 * │  LEFT PANEL             │  RIGHT PANEL                           │
 * │  ─ Hospital KPI cards   │  ─ AI Chat interface (SSE streaming)   │
 * │  ─ Critical patient list│    ─ Suggested prompt chips            │
 * │  ─ Active alerts        │    ─ Conversation history              │
 * │  ─ AI Insights          │    ─ Streaming response + sources      │
 * │  ─ Recommended Actions  │                                        │
 * └─────────────────────────┴────────────────────────────────────────┘
 *
 * Uses existing: clinical-card, badge-clinical-*, btn-clinical-* CSS classes.
 * Reuses websocketService for live KPI polling via existing dashboard channel.
 * Does NOT duplicate Clinical Copilot UI or logic.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BrainCircuit, Building2, AlertTriangle, Activity,
  Users, BedDouble, Send, Loader2, Sparkles,
  TrendingDown, ShieldAlert, Siren, CheckCircle,
  ChevronRight, RefreshCw, Zap, BookOpen,
} from "lucide-react";
import { hospitalAssistantService } from "../../services/hospitalAssistantService";
import StreamingMarkdown from "../clinicalCopilot/StreamingMarkdown";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SUGGESTED_PROMPTS = [
  "Which patients need immediate attention?",
  "Show highest risk ICU patients.",
  "Which patients have worsening vital trends?",
  "Give me an ICU summary right now.",
  "Sepsis overview — which patients are at risk?",
  "What is the current bed utilisation?",
  "Patients with abnormal labs?",
  "List patients requiring urgent review.",
];

const RISK_COLORS = {
  HIGH:   "text-red-600 bg-red-50 border-red-200",
  MEDIUM: "text-orange-600 bg-orange-50 border-orange-200",
  LOW:    "text-emerald-700 bg-emerald-50 border-emerald-200",
};

const STATUS_DOT = {
  Critical: "bg-red-500 animate-pulse",
  Serious:  "bg-orange-400",
  Stable:   "bg-emerald-400",
};

const PRIORITY_BADGE = {
  URGENT: "badge-clinical-danger",
  HIGH:   "badge-clinical-warning",
  MEDIUM: "badge-clinical-info",
};

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function KPICard({ label, value, sub, icon: Icon, colorClass = "text-slate-700" }) {
  return (
    <motion.div whileHover={{ y: -2 }} className="clinical-card p-4">
      <div className="flex items-center justify-between mb-2">
        <Icon size={16} className={`${colorClass} opacity-80`} />
      </div>
      <p className={`text-2xl font-black tracking-tight ${colorClass}`}>{value ?? "—"}</p>
      <p className="text-[9px] font-black uppercase tracking-widest text-slate-400 mt-0.5">{label}</p>
      {sub && <p className="text-[10px] text-slate-400 font-semibold mt-1">{sub}</p>}
    </motion.div>
  );
}

function CriticalPatientRow({ patient, index }) {
  const dotC = STATUS_DOT[patient.status] || "bg-slate-300";
  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-slate-50 last:border-0">
      <span className="text-[10px] font-black text-slate-300 w-4">{index + 1}</span>
      <span className={`h-2 w-2 rounded-full shrink-0 ${dotC}`} />
      <div className="flex-1 min-w-0">
        <p className="text-[11px] font-black text-slate-800 truncate">{patient.name}</p>
        <p className="text-[9px] text-slate-400 font-semibold">
          {patient.id} · Bed {patient.bed} · {patient.gender}
        </p>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <span className={`text-[10px] font-black px-2 py-0.5 rounded-full border ${RISK_COLORS[patient.risk_level] || RISK_COLORS.LOW}`}>
          {Math.round((patient.risk_score || 0) * 100)}%
        </span>
      </div>
    </div>
  );
}

function AlertRow({ alert }) {
  const isCrit = alert.risk_level === "HIGH";
  return (
    <div className={`rounded-xl border p-3 mb-2 ${isCrit ? "bg-red-50/60 border-red-200" : "bg-orange-50/40 border-orange-200"}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <AlertTriangle size={11} className={isCrit ? "text-red-500 animate-pulse" : "text-orange-500"} />
          <span className="text-[10px] font-black text-slate-800">{alert.patient_name}</span>
          <span className="text-[9px] text-slate-400 font-semibold">Bed {alert.bed}</span>
        </div>
        <span className={`text-[8px] font-black px-1.5 py-0.5 rounded-full border ${RISK_COLORS[alert.risk_level] || RISK_COLORS.LOW}`}>
          {alert.risk_level}
        </span>
      </div>
      <div className="mt-1.5 flex flex-wrap gap-1">
        {alert.flags.slice(0, 4).map((f, i) => (
          <span key={i} className="text-[8px] font-bold bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded-md">
            {f}
          </span>
        ))}
        {alert.flags.length > 4 && (
          <span className="text-[8px] font-bold text-slate-400">+{alert.flags.length - 4} more</span>
        )}
      </div>
    </div>
  );
}

function InsightItem({ text, index }) {
  return (
    <div className="flex items-start gap-2 py-2 border-b border-slate-50 last:border-0">
      <Sparkles size={11} className="text-cyan-500 mt-0.5 shrink-0" />
      <p className="text-[10px] font-semibold text-slate-700 leading-relaxed">{text}</p>
    </div>
  );
}

function ActionItem({ action }) {
  const badge = PRIORITY_BADGE[action.priority] || "badge-clinical-info";
  return (
    <div className="flex items-start gap-2.5 py-2.5 border-b border-slate-50 last:border-0">
      <span className={`shrink-0 mt-0.5 ${badge}`}>{action.priority}</span>
      <div>
        <p className="text-[10px] font-black text-slate-800">{action.patient_name || action.patient_id}</p>
        <p className="text-[10px] text-slate-600 font-semibold">{action.action}</p>
        {action.rationale && (
          <p className="text-[9px] text-slate-400 mt-0.5">{action.rationale}</p>
        )}
      </div>
    </div>
  );
}

function ChatMessage({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      {!isUser && (
        <div className="mr-2 mt-0.5 h-6 w-6 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shrink-0">
          <BrainCircuit size={12} className="text-white" />
        </div>
      )}
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-xs font-medium leading-relaxed shadow-sm ${
          isUser
            ? "bg-slate-900 text-white rounded-tr-sm"
            : "bg-white border border-slate-100 text-slate-800 rounded-tl-sm"
        }`}
      >
        {isUser ? msg.content : <StreamingMarkdown text={msg.content} />}
      </div>
    </div>
  );
}

function StreamingCursor() {
  return (
    <span
      className="inline-block h-3.5 w-0.5 rounded-full bg-cyan-500 ml-0.5 align-middle"
      style={{ animation: "blink 1s step-end infinite" }}
    />
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function HospitalAssistant() {
  // Snapshot state
  const [snapshot,    setSnapshot]    = useState(null);
  const [loading,     setLoading]     = useState(true);
  const [refreshing,  setRefreshing]  = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Chat state
  const [messages,        setMessages]        = useState([]);
  const [inputValue,      setInputValue]       = useState("");
  const [streaming,       setStreaming]         = useState(false);
  const [streamingText,   setStreamingText]    = useState("");
  const [pendingFinal,    setPendingFinal]     = useState(null);

  // Active left panel tab
  const [activeTab, setActiveTab] = useState("critical");

  const chatEndRef  = useRef(null);
  const inputRef    = useRef(null);
  const pollingRef  = useRef(null);

  // ---------- Data loading ----------
  const loadSnapshot = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    else          setRefreshing(true);
    try {
      const data = await hospitalAssistantService.getSnapshot();
      setSnapshot(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("[HospitalAssistant] Snapshot error:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadSnapshot();
    // Refresh snapshot every 10 seconds
    pollingRef.current = setInterval(() => loadSnapshot(true), 10000);
    return () => clearInterval(pollingRef.current);
  }, [loadSnapshot]);

  // Scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  // ---------- Chat ----------
  const sendMessage = useCallback(async (question) => {
    if (!question.trim() || streaming) return;

    const q = question.trim();
    setInputValue("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setStreaming(true);
    setStreamingText("");

    try {
      await hospitalAssistantService.chatStream(
        q,
        (token) => setStreamingText((prev) => prev + token),
        (final) => {
          const reasoning = final?.reasoning || final?.answer || "Analysis complete.";
          setMessages((prev) => [...prev, { role: "assistant", content: reasoning }]);
          setStreamingText("");
          setPendingFinal(final);
          setStreaming(false);
        },
      );
    } catch (err) {
      // Fallback: try batch
      try {
        const res = await hospitalAssistantService.chat(q);
        const text = res?.reasoning || res?.answer || "Analysis complete.";
        setMessages((prev) => [...prev, { role: "assistant", content: text }]);
      } catch {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Unable to process request. Please try again." },
        ]);
      }
      setStreamingText("");
      setStreaming(false);
    }
  }, [streaming]);

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const handlePromptClick = (prompt) => sendMessage(prompt);

  // ---------- Derived data ----------
  const summary    = snapshot?.summary    || {};
  const critical   = snapshot?.critical_patients   || [];
  const alerts     = snapshot?.active_alerts       || [];
  const insights   = snapshot?.ai_insights         || [];
  const actions    = snapshot?.recommended_actions || [];
  const telemetry  = snapshot?.telemetry_insights  || [];

  const criticalCount  = summary.critical_patients    || 0;
  const alertCount     = summary.active_alert_count   || 0;
  const worsening      = summary.worsening_trend_count || 0;

  const tabs = [
    { id: "critical",  label: "Critical",  count: critical.length,  icon: ShieldAlert  },
    { id: "alerts",    label: "Alerts",    count: alerts.length,    icon: Siren        },
    { id: "insights",  label: "Insights",  count: insights.length,  icon: Sparkles     },
    { id: "actions",   label: "Actions",   count: actions.length,   icon: Zap          },
    { id: "telemetry", label: "Telemetry", count: telemetry.length, icon: TrendingDown },
  ];

  return (
    <div className="space-y-6">

      {/* ── Header ── */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-[#071B35] to-[#0B2942] p-6 text-white shadow-lg">
        <div className="flex items-center gap-4">
          <div className="rounded-xl bg-white/10 p-3 border border-white/10">
            <Building2 size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-black">IntelliAI Hospital Command Centre</h1>
            <p className="mt-1 text-xs text-slate-400">
              Hospital-wide AI clinical intelligence · All ICU patients · Real-time
            </p>
          </div>
          <div className="ml-auto flex items-center gap-3">
            {lastUpdated && (
              <p className="text-[10px] text-slate-500">
                Updated {lastUpdated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
              </p>
            )}
            <button
              onClick={() => loadSnapshot(true)}
              disabled={refreshing}
              className="flex items-center gap-1.5 rounded-xl bg-white/10 hover:bg-white/20 px-3 py-2 text-xs font-bold transition cursor-pointer"
            >
              <RefreshCw size={12} className={refreshing ? "animate-spin" : ""} />
              Refresh
            </button>
          </div>
        </div>

        {/* KPI strip */}
        {!loading && (
          <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
            {[
              { label: "Total Patients",   value: summary.total_patients,       colorClass: "text-white"          },
              { label: "Critical",         value: summary.critical_patients,     colorClass: "text-red-400"        },
              { label: "Active Alerts",    value: summary.active_alert_count,    colorClass: "text-orange-400"     },
              { label: "Sepsis Suspects",  value: summary.sepsis_suspects,       colorClass: "text-rose-400"       },
              { label: "Bed Occupancy",    value: `${summary.bed_occupancy_pct}%`, colorClass: "text-cyan-400"    },
              { label: "Worsening Trends", value: summary.worsening_trend_count, colorClass: "text-yellow-400"    },
            ].map(({ label, value, colorClass }) => (
              <div key={label} className="rounded-xl bg-white/5 border border-white/10 px-4 py-3">
                <p className={`text-xl font-black ${colorClass}`}>{value ?? "—"}</p>
                <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-0.5">{label}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Main grid ── */}
      <div className="grid grid-cols-12 gap-6">

        {/* ── LEFT PANEL ── */}
        <div className="col-span-12 lg:col-span-5 space-y-4">

          {loading ? (
            <div className="clinical-card p-8 flex flex-col items-center justify-center text-slate-400">
              <Loader2 size={24} className="animate-spin mb-3" />
              <p className="text-sm font-bold">Aggregating hospital data…</p>
            </div>
          ) : (
            <>
              {/* Tab navigation */}
              <div className="flex gap-1.5 overflow-x-auto pb-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center gap-1.5 shrink-0 rounded-xl px-3 py-2 text-xs font-bold transition cursor-pointer ${
                        activeTab === tab.id
                          ? "bg-slate-900 text-white"
                          : "bg-white border border-slate-200 text-slate-600 hover:bg-slate-50"
                      }`}
                    >
                      <Icon size={11} />
                      {tab.label}
                      {tab.count > 0 && (
                        <span className={`rounded-full px-1.5 py-0.5 text-[8px] font-black ${
                          activeTab === tab.id ? "bg-white/20 text-white" : "bg-slate-100 text-slate-500"
                        }`}>
                          {tab.count}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>

              <AnimatePresence mode="wait">
                {/* Critical Patients */}
                {activeTab === "critical" && (
                  <motion.div key="critical"
                    initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                    className="clinical-card p-5"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <ShieldAlert size={14} className="text-red-500" />
                        <h3 className="text-sm font-black text-slate-800">Critical Patients</h3>
                      </div>
                      <span className="badge-clinical-danger">{critical.length} patients</span>
                    </div>
                    {critical.length === 0 ? (
                      <p className="text-xs text-slate-400 font-semibold text-center py-6">
                        No critical patients at this time.
                      </p>
                    ) : (
                      <div className="max-h-96 overflow-y-auto">
                        {critical.map((p, i) => (
                          <CriticalPatientRow key={p.id} patient={p} index={i} />
                        ))}
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Active Alerts */}
                {activeTab === "alerts" && (
                  <motion.div key="alerts"
                    initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                    className="clinical-card p-5"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <Siren size={14} className="text-orange-500 animate-pulse" />
                        <h3 className="text-sm font-black text-slate-800">Active Alerts</h3>
                      </div>
                      {alerts.length > 0 && (
                        <span className="badge-clinical-warning">{alerts.length} patients</span>
                      )}
                    </div>
                    {alerts.length === 0 ? (
                      <div className="flex items-center gap-2 justify-center py-6 text-emerald-600 text-xs font-bold">
                        <CheckCircle size={16} /> No active alerts
                      </div>
                    ) : (
                      <div className="max-h-96 overflow-y-auto">
                        {alerts.map((a) => <AlertRow key={a.patient_id} alert={a} />)}
                      </div>
                    )}
                  </motion.div>
                )}

                {/* AI Insights */}
                {activeTab === "insights" && (
                  <motion.div key="insights"
                    initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                    className="clinical-card p-5"
                  >
                    <div className="flex items-center gap-2 mb-4">
                      <Sparkles size={14} className="text-cyan-500" />
                      <h3 className="text-sm font-black text-slate-800">AI Insights</h3>
                    </div>
                    {insights.map((text, i) => <InsightItem key={i} text={text} index={i} />)}
                  </motion.div>
                )}

                {/* Recommended Actions */}
                {activeTab === "actions" && (
                  <motion.div key="actions"
                    initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                    className="clinical-card p-5"
                  >
                    <div className="flex items-center gap-2 mb-4">
                      <Zap size={14} className="text-amber-500" />
                      <h3 className="text-sm font-black text-slate-800">Recommended Actions</h3>
                    </div>
                    {actions.length === 0 ? (
                      <p className="text-xs text-slate-400 font-semibold text-center py-6">
                        No actions required at this time.
                      </p>
                    ) : (
                      <div className="max-h-96 overflow-y-auto">
                        {actions.map((a, i) => <ActionItem key={i} action={a} />)}
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Telemetry Insights */}
                {activeTab === "telemetry" && (
                  <motion.div key="telemetry"
                    initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                    className="clinical-card p-5"
                  >
                    <div className="flex items-center gap-2 mb-4">
                      <TrendingDown size={14} className="text-rose-500" />
                      <h3 className="text-sm font-black text-slate-800">Worsening Telemetry Trends</h3>
                    </div>
                    {telemetry.length === 0 ? (
                      <div className="flex items-center gap-2 justify-center py-6 text-emerald-600 text-xs font-bold">
                        <CheckCircle size={16} /> All telemetry trends stable
                      </div>
                    ) : (
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {telemetry.map((ti) => (
                          <div key={ti.patient_id} className={`rounded-xl border p-3 ${
                            ti.overall_alert_level === "CRITICAL" ? "bg-red-50/60 border-red-200" : "bg-orange-50/40 border-orange-200"
                          }`}>
                            <div className="flex items-start justify-between gap-2 mb-1">
                              <span className="text-[10px] font-black text-slate-800">
                                {ti.patient_name || ti.patient_id}
                              </span>
                              <span className={`text-[8px] font-black px-1.5 py-0.5 rounded-full border ${
                                ti.overall_alert_level === "CRITICAL"
                                  ? "bg-red-100 border-red-300 text-red-700"
                                  : "bg-orange-100 border-orange-300 text-orange-700"
                              }`}>
                                {ti.overall_alert_level}
                              </span>
                            </div>
                            <p className="text-[9px] text-slate-600 leading-relaxed">
                              {ti.clinical_narrative}
                            </p>
                            {ti.critical_parameters?.length > 0 && (
                              <div className="mt-1.5 flex gap-1 flex-wrap">
                                {ti.critical_parameters.map((p, i) => (
                                  <span key={i} className="text-[8px] font-bold bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded-md">
                                    {p}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </>
          )}
        </div>

        {/* ── RIGHT PANEL — AI Chat ── */}
        <div className="col-span-12 lg:col-span-7">
          <div className="clinical-card flex flex-col overflow-hidden" style={{ height: "calc(100vh - 280px)", minHeight: "540px" }}>

            {/* Chat header */}
            <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
              <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-700 flex items-center justify-center">
                <BrainCircuit size={16} className="text-white" />
              </div>
              <div>
                <h2 className="text-sm font-black text-slate-800">IntelliAI Hospital Assistant</h2>
                <p className="text-[9px] text-slate-400 font-semibold">
                  Ask anything about your ICU · Powered by {summary.total_patients || "—"} patients
                </p>
              </div>
              <div className="ml-auto flex items-center gap-1.5 rounded-full bg-emerald-100 px-3 py-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[9px] font-bold text-emerald-700">LIVE</span>
              </div>
            </div>

            {/* Suggested prompts — only when chat is empty */}
            {messages.length === 0 && !streaming && (
              <div className="px-5 pt-5 pb-3">
                <p className="text-[9px] font-black uppercase tracking-widest text-slate-400 mb-3">
                  Suggested Queries
                </p>
                <div className="flex flex-wrap gap-2">
                  {SUGGESTED_PROMPTS.slice(0, 6).map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => handlePromptClick(prompt)}
                      className="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50/80 px-3 py-2 text-[10px] font-semibold text-slate-600 hover:bg-slate-100 hover:border-slate-300 transition cursor-pointer text-left"
                    >
                      <ChevronRight size={10} className="shrink-0 text-slate-400" />
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-5 py-4 space-y-1">
              {messages.length === 0 && !streaming && (
                <div className="flex flex-col items-center justify-center h-full text-slate-400 text-center">
                  <Building2 size={32} className="mb-3 opacity-20" />
                  <p className="text-sm font-black text-slate-500">Hospital AI Command Centre</p>
                  <p className="text-xs mt-1 max-w-xs">
                    Ask any hospital-level clinical question. I have access to all active ICU patients.
                  </p>
                </div>
              )}

              {messages.map((msg, i) => <ChatMessage key={i} msg={msg} />)}

              {/* Streaming response */}
              {(streaming || streamingText) && (
                <div className="flex justify-start mb-3">
                  <div className="mr-2 mt-0.5 h-6 w-6 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shrink-0">
                    <BrainCircuit size={12} className="text-white" />
                  </div>
                  <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-white border border-slate-100 px-4 py-2.5 text-xs font-medium leading-relaxed text-slate-800 shadow-sm">
                    {streamingText ? (
                      <StreamingMarkdown text={streamingText} isStreaming={streaming} />
                    ) : (
                      <Loader2 size={14} className="animate-spin text-slate-300" />
                    )}
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-slate-100 px-5 py-4">
              <form onSubmit={handleSubmit} className="flex items-center gap-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask about your hospital… e.g. 'Which patients need attention?'"
                  disabled={streaming}
                  className="input-clinical flex-1"
                />
                <button
                  type="submit"
                  disabled={streaming || !inputValue.trim()}
                  className="btn-clinical-primary shrink-0 gap-2"
                >
                  {streaming ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Send size={14} />
                  )}
                  {streaming ? "Thinking…" : "Ask"}
                </button>
              </form>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
