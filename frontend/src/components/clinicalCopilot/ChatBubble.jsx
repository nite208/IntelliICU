import React, { useState } from "react";
import { 
  User, Activity, AlertTriangle, AlertOctagon, CheckCircle2, BookOpen, 
  ChevronDown, ChevronUp, Pill, FlaskConical, Bell, Gauge, Heart, FileText, Stethoscope 
} from "lucide-react";
import StreamingMarkdown from "./StreamingMarkdown";

export default function ChatBubble({ message }) {
  const { sender, content, timestamp } = message;
  const isUser = sender === "user";

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 max-w-[85%] ml-auto">
        <div className="flex flex-col items-end">
          <div className="bg-slate-900 text-white rounded-2xl p-4 text-xs font-medium shadow-sm leading-relaxed">
            {content}
          </div>
          <span className="text-[9px] text-slate-400 mt-1">{timestamp}</span>
        </div>
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-slate-100 border border-slate-200 text-slate-600">
          <User size={14} />
        </div>
      </div>
    );
  }

  // Handle streaming placeholders
  if (message.isStreaming) {
    return (
      <div className="flex justify-start gap-3 w-full animate-fadeIn">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-cyan-50 border border-cyan-100 text-cyan-600 shadow-sm">
          <Activity className="animate-pulse" size={14} />
        </div>

        <div className="flex flex-col space-y-1.5 w-full">
          <div className="bg-white border border-slate-150 rounded-2xl p-5 shadow-sm space-y-3">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
              <span className="text-[10px] font-black uppercase tracking-wider text-cyan-600">Clinical Copilot</span>
              <span className="text-[9px] px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-700 font-bold border border-cyan-100 flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-500 animate-pulse"></span>
                Streaming
              </span>
            </div>
            <div className="min-h-[30px]">
              <StreamingMarkdown
                text={content?.summary || content?.reasoning || ""}
                isStreaming={true}
              />
            </div>
          </div>
          <span className="text-[9px] text-slate-400 self-start pl-1">{timestamp}</span>
        </div>
      </div>
    );
  }

  // Clinical Copilot message layout
  const { 
    reasoning, risk_drivers, abnormal_vitals, abnormal_labs, 
    recommendations, evidence, confidence, context,
    answer, guideline, source, publication_year,
    retrieved_sources, differential_diagnosis, treatment_pathway, medication_plan, risk_scores, laboratory_interpretation, trend_analysis
  } = content || {};

  // Toggles for collapsible sections
  const [showReasoning, setShowReasoning] = useState(true);
  const [showRiskDrivers, setShowRiskDrivers] = useState(true);
  const [showVitals, setShowVitals] = useState(true);
  const [showLabs, setShowLabs] = useState(true);
  const [showRecommendations, setShowRecommendations] = useState(true);
  const [showEvidence, setShowEvidence] = useState(true);
  const [showRAGEvidence, setShowRAGEvidence] = useState(true);
  const [showCitations, setShowCitations] = useState(true);
  const [showDifferential, setShowDifferential] = useState(true);
  const [showTreatment, setShowTreatment] = useState(true);
  const [showMedications, setShowMedications] = useState(true);
  const [showRiskScores, setShowRiskScores] = useState(true);
  const [showLabsInterpretation, setShowLabsInterpretation] = useState(true);
  const [showTrends, setShowTrends] = useState(true);

  // Helper to parse severity tags from string content
  const parseSeverity = (text) => {
    let cleanText = text;
    let severity = "INFO";

    if (text.includes("[CRITICAL]")) {
      cleanText = text.replace("[CRITICAL]", "").trim();
      severity = "CRITICAL";
    } else if (text.includes("[WARNING]")) {
      cleanText = text.replace("[WARNING]", "").trim();
      severity = "WARNING";
    }
    return { cleanText, severity };
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case "CRITICAL":
        return "bg-red-50 text-red-600 border border-red-100";
      case "WARNING":
        return "bg-amber-50 text-amber-600 border border-amber-100";
      default:
        return "bg-blue-50 text-blue-600 border border-blue-100";
    }
  };

  // Helper for priority styling
  const getPriorityStyle = (priority) => {
    switch (priority) {
      case "CRITICAL":
        return { bg: "bg-red-50 border-red-150", text: "text-red-700", label: "CRITICAL PRIORITY", icon: AlertOctagon };
      case "HIGH":
        return { bg: "bg-amber-50 border-amber-150", text: "text-amber-700", label: "HIGH PRIORITY", icon: AlertTriangle };
      default:
        return { bg: "bg-blue-50 border-blue-150", text: "text-blue-700", label: "STABLE", icon: Activity };
    }
  };

  const priorityInfo = getPriorityStyle(context?.clinical_priority);
  const PriorityIcon = priorityInfo.icon;

  // Render RAG Guideline layout
  if (answer) {
    return (
      <div className="flex justify-start gap-3 w-full">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-blue-50 border border-blue-100 text-blue-600">
          <BookOpen size={14} />
        </div>

        <div className="flex flex-col space-y-1.5 w-full">
          <div className="bg-white border border-slate-150 rounded-2xl p-5 shadow-sm space-y-5">
            
            {/* RAG Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-3.5 gap-2">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-black uppercase tracking-wider text-blue-600">Clinical RAG Engine</span>
                <span className="text-[9px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-bold border border-blue-100">Guideline Retrieval</span>
              </div>
              
              {source && (
                <div className="flex items-center gap-1.5 text-[9px] font-black text-slate-500 uppercase tracking-wider bg-slate-100 px-2.5 py-0.5 rounded-lg border border-slate-150">
                  <span>{source}</span>
                  {publication_year && <span>({publication_year})</span>}
                </div>
              )}
            </div>

            {/* Guideline Name Block */}
            {guideline && (
              <div className="flex items-start gap-2.5 p-3.5 rounded-xl bg-blue-50/30 border border-blue-100 text-xs">
                <FileText size={14} className="text-blue-500 shrink-0 mt-0.5" />
                <div>
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Reference Guideline</span>
                  <span className="font-bold text-slate-700">{guideline}</span>
                </div>
              </div>
            )}

            {/* Answer Content */}
            <div className="space-y-1.5">
              <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">Clinical Guideline Advisory</span>
              <p className="text-xs text-slate-800 leading-relaxed font-medium bg-slate-50 border border-slate-100 rounded-xl p-4">
                {answer}
              </p>
            </div>

            {/* Guideline Evidence Collapsible */}
            {evidence && evidence.length > 0 && (
              <div className="border border-slate-150 rounded-xl overflow-hidden">
                <button
                  onClick={() => setShowRAGEvidence(!showRAGEvidence)}
                  className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
                >
                  <div className="flex items-center gap-2">
                    <BookOpen size={13} className="text-blue-500" />
                    <span className="text-[10px] font-black uppercase tracking-wider">Supporting Clinical Evidence</span>
                  </div>
                  {showRAGEvidence ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                </button>

                {showRAGEvidence && (
                  <div className="p-4 border-t border-slate-100 bg-white text-xs">
                    <ul className="space-y-3">
                      {evidence.map((ev, i) => (
                        <li key={i} className="flex items-start gap-2.5 text-slate-655 font-medium leading-relaxed">
                          <CheckCircle2 size={13} className="text-blue-500 mt-0.5 shrink-0" />
                          <span>{ev}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Confidence Score Bar */}
            {confidence !== undefined && (
              <div className="space-y-1.5 bg-slate-50 border border-slate-150 rounded-xl p-3.5">
                <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-wider text-slate-400">
                  <span className="flex items-center gap-1"><Gauge size={11} /> Retrieval Match Confidence</span>
                  <span className="font-extrabold text-slate-700">{Math.round(confidence * 100)}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-600 rounded-full transition-all duration-500" 
                    style={{ width: `${confidence * 100}%` }}
                  ></div>
                </div>
              </div>
            )}

          </div>
          <span className="text-[9px] text-slate-400 self-start pl-1">{timestamp}</span>
        </div>
      </div>
    );
  }

  // Fallback to Explainable AI layout
  return (
    <div className="flex justify-start gap-3 w-full">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-cyan-50 border border-cyan-100 text-cyan-600">
        <Activity size={14} />
      </div>

      <div className="flex flex-col space-y-1.5 w-full">
        <div className="bg-white border border-slate-150 rounded-2xl p-5 shadow-sm space-y-5">
          
          {/* Header Banner & Clinical Priority */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-3.5 gap-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-black uppercase tracking-wider text-cyan-600">Clinical Copilot</span>
              <span className="text-[9px] px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-700 font-bold border border-cyan-100">Explainable AI</span>
            </div>
            
            {context?.clinical_priority && (
              <div className={`flex items-center gap-1.5 px-3 py-1 rounded-xl border text-[9px] font-black tracking-wider uppercase ${priorityInfo.bg} ${priorityInfo.text}`}>
                <PriorityIcon size={12} />
                <span>{priorityInfo.label}</span>
              </div>
            )}
          </div>

          {/* 1. AI Reasoning Section */}
          <div className="border border-slate-150 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
            >
              <div className="flex items-center gap-2">
                <Activity size={13} className="text-cyan-600" />
                <span className="text-[10px] font-black uppercase tracking-wider">AI Clinical Reasoning</span>
              </div>
              {showReasoning ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>

            {showReasoning && (
              <div className="p-4 border-t border-slate-100 bg-white">
                {reasoning
                  ? <StreamingMarkdown text={reasoning} isStreaming={false} />
                  : <p className="text-xs text-slate-400 italic">No clinical explanations generated.</p>
                }
              </div>
            )}
          </div>

          {/* 2. Risk Drivers Section */}
          {risk_drivers && risk_drivers.length > 0 && (
            <div className="border border-slate-150 rounded-xl overflow-hidden">
              <button
                onClick={() => setShowRiskDrivers(!showRiskDrivers)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <AlertTriangle size={13} className="text-amber-500" />
                  <span className="text-[10px] font-black uppercase tracking-wider">AI Risk Drivers</span>
                </div>
                {showRiskDrivers ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showRiskDrivers && (
                <div className="p-4 border-t border-slate-100 bg-white text-xs space-y-2.5">
                  {risk_drivers.map((driver, i) => {
                    const { cleanText, severity } = parseSeverity(driver);
                    return (
                      <div key={i} className="flex items-start justify-between gap-3 p-3 rounded-xl border border-slate-100 bg-slate-50/30">
                        <span className="text-slate-655 font-medium leading-relaxed">{cleanText}</span>
                        {severity !== "INFO" && (
                          <span className={`px-2 py-0.5 text-[8.5px] font-black uppercase tracking-wider rounded-lg shrink-0 ${getSeverityBadge(severity)}`}>
                            {severity}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* 3. Abnormal Vitals Section */}
          {abnormal_vitals && abnormal_vitals.length > 0 && (
            <div className="border border-slate-150 rounded-xl overflow-hidden">
              <button
                onClick={() => setShowVitals(!showVitals)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <Heart size={13} className="text-red-500" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Abnormal Vitals ({abnormal_vitals.length})</span>
                </div>
                {showVitals ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showVitals && (
                <div className="p-4 border-t border-slate-100 bg-white text-xs space-y-2">
                  {abnormal_vitals.map((vital, i) => {
                    const { cleanText, severity } = parseSeverity(vital);
                    return (
                      <div key={i} className="flex items-center justify-between gap-3 p-2.5 border border-slate-50 rounded-lg">
                        <span className="text-slate-655 font-medium">{cleanText}</span>
                        {severity !== "INFO" && (
                          <span className={`px-2 py-0.5 text-[8px] font-black uppercase tracking-wider rounded-lg ${getSeverityBadge(severity)}`}>
                            {severity}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* 4. Abnormal Labs Section */}
          {abnormal_labs && abnormal_labs.length > 0 && (
            <div className="border border-slate-150 rounded-xl overflow-hidden">
              <button
                onClick={() => setShowLabs(!showLabs)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <FlaskConical size={13} className="text-blue-500" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Abnormal Labs ({abnormal_labs.length})</span>
                </div>
                {showLabs ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showLabs && (
                <div className="p-4 border-t border-slate-100 bg-white text-xs space-y-2">
                  {abnormal_labs.map((lab, i) => {
                    const { cleanText, severity } = parseSeverity(lab);
                    return (
                      <div key={i} className="flex items-center justify-between gap-3 p-2.5 border border-slate-50 rounded-lg">
                        <span className="text-slate-655 font-semibold">{cleanText}</span>
                        <span className={`px-2 py-0.5 text-[8.5px] font-black uppercase tracking-wider rounded-lg shrink-0 ${getSeverityBadge(severity)}`}>
                          {severity}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* 5. Recommendations Section */}
          {recommendations && recommendations.length > 0 && (
            <div className="border border-slate-150 rounded-xl overflow-hidden">
              <button
                onClick={() => setShowRecommendations(!showRecommendations)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={13} className="text-emerald-500" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Stabilization Pathway</span>
                </div>
                {showRecommendations ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showRecommendations && (
                <div className="p-4 border-t border-slate-100 bg-white text-xs">
                  <ul className="space-y-2.5">
                    {recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-slate-655 font-medium leading-relaxed">
                        <CheckCircle2 size={13} className="text-emerald-500 mt-0.5 shrink-0" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Differential Diagnosis Collapsible Section */}
          {differential_diagnosis && differential_diagnosis.length > 0 && (
            <div className="border border-slate-150 rounded-xl overflow-hidden animate-fadeIn">
              <button
                onClick={() => setShowDifferential(!showDifferential)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <Activity size={13} className="text-cyan-600 animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Differential Diagnoses</span>
                </div>
                {showDifferential ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showDifferential && (
                <div className="p-4 border-t border-slate-100 bg-white space-y-4">
                  {differential_diagnosis.map((diag, idx) => {
                    const likelihoodPct = Math.round(diag.likelihood * 100);
                    // Color code based on likelihood percentage
                    let colorClass = "text-emerald-600 bg-emerald-50 border-emerald-100";
                    let barColor = "bg-emerald-500";
                    if (likelihoodPct < 40) {
                      colorClass = "text-slate-500 bg-slate-50 border-slate-150";
                      barColor = "bg-slate-400";
                    } else if (likelihoodPct < 70) {
                      colorClass = "text-amber-600 bg-amber-50 border-amber-100";
                      barColor = "bg-amber-500";
                    }

                    return (
                      <div key={idx} className="p-3.5 border border-slate-100 rounded-xl bg-slate-50/20 hover:bg-slate-50/50 transition-colors space-y-2.5">
                        <div className="flex items-center justify-between gap-3">
                          <span className="font-bold text-slate-800 text-xs">{diag.diagnosis}</span>
                          <span className={`px-2 py-0.5 rounded-full border text-[9px] font-black tracking-wider uppercase ${colorClass}`}>
                            {likelihoodPct}% Likelihood
                          </span>
                        </div>

                        {/* Tiny progress bar representing likelihood */}
                        <div className="w-full h-1 bg-slate-100 rounded-full overflow-hidden">
                          <div className={`h-full ${barColor} rounded-full`} style={{ width: `${likelihoodPct}%` }} />
                        </div>

                        {/* Evidence breakdown */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[10px]">
                          {/* Supporting */}
                          <div className="space-y-1.5 p-2 rounded-lg bg-emerald-50/10 border border-emerald-500/10">
                            <span className="font-bold text-emerald-700 uppercase tracking-wide block">Supporting Evidence</span>
                            <ul className="space-y-1 text-slate-655 font-medium pl-3 list-disc">
                              {diag.supporting_evidence.map((se, i) => (
                                <li key={i}>{se}</li>
                              ))}
                            </ul>
                          </div>

                          {/* Contradicting */}
                          <div className="space-y-1.5 p-2 rounded-lg bg-red-50/10 border border-red-500/10">
                            <span className="font-bold text-red-700 uppercase tracking-wide block">Contradicting Evidence</span>
                            <ul className="space-y-1 text-slate-655 font-medium pl-3 list-disc">
                              {diag.contradicting_evidence.map((ce, i) => (
                                <li key={i}>{ce}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Treatment Pathway Collapsible Section */}
          {treatment_pathway && (
            <div className="border border-slate-150 rounded-xl overflow-hidden animate-fadeIn">
              <button
                onClick={() => setShowTreatment(!showTreatment)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <Stethoscope size={13} className="text-emerald-600 animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Clinical Treatment Pathway</span>
                </div>
                {showTreatment ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showTreatment && (
                <div className="p-5 border-t border-slate-100 bg-white space-y-5 text-xs">
                  {/* Priority Header */}
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="font-extrabold uppercase tracking-wide text-slate-400 text-[10px]">Pathway Care Level</span>
                    <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-wider border ${
                      treatment_pathway.priority === "CRITICAL"
                        ? "text-red-700 bg-red-50 border-red-100 animate-pulse"
                        : "text-amber-700 bg-amber-50 border-amber-100"
                    }`}>
                      {treatment_pathway.priority} priority
                    </span>
                  </div>

                  {/* 1. Immediate Actions */}
                  {treatment_pathway.immediate_actions && treatment_pathway.immediate_actions.length > 0 && (
                    <div className="space-y-2">
                      <span className="font-bold text-red-700 uppercase tracking-wide text-[10px] block">1. Immediate Resuscitative Actions</span>
                      <ul className="space-y-1.5 pl-3 text-slate-655 font-medium list-disc">
                        {treatment_pathway.immediate_actions.map((act, i) => (
                          <li key={i}>{act}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 2. Medications */}
                  {treatment_pathway.medications && treatment_pathway.medications.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-50">
                      <span className="font-bold text-cyan-700 uppercase tracking-wide text-[10px] block">2. Directed Pharmacotherapy</span>
                      <div className="grid grid-cols-1 gap-2 pl-1">
                        {treatment_pathway.medications.map((med, i) => (
                          <div key={i} className="flex items-start gap-2 p-2 border border-slate-100 rounded-lg bg-slate-50/20">
                            <Pill size={13} className="text-cyan-500 mt-0.5 shrink-0" />
                            <span className="text-slate-655 font-medium">{med}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 3. Monitoring */}
                  {treatment_pathway.monitoring && treatment_pathway.monitoring.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-50">
                      <span className="font-bold text-amber-700 uppercase tracking-wide text-[10px] block">3. Hemodynamic & Vitals Monitoring</span>
                      <ul className="space-y-1.5 pl-3 text-slate-655 font-medium list-disc">
                        {treatment_pathway.monitoring.map((mon, i) => (
                          <li key={i}>{mon}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 4. Repeat Labs */}
                  {treatment_pathway.labs_to_repeat && treatment_pathway.labs_to_repeat.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-50">
                      <span className="font-bold text-indigo-700 uppercase tracking-wide text-[10px] block">4. Laboratory Re-evaluation Schedule</span>
                      <div className="grid grid-cols-1 gap-2 pl-1">
                        {treatment_pathway.labs_to_repeat.map((lab, i) => (
                          <div key={i} className="flex items-start gap-2 p-2 border border-slate-100 rounded-lg bg-slate-50/20">
                            <FlaskConical size={13} className="text-indigo-500 mt-0.5 shrink-0" />
                            <span className="text-slate-655 font-medium">{lab}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 5. Consults */}
                  {treatment_pathway.consults && treatment_pathway.consults.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-50">
                      <span className="font-bold text-slate-700 uppercase tracking-wide text-[10px] block">5. Specialty Consultations</span>
                      <ul className="space-y-1.5 pl-3 text-slate-655 font-medium list-disc">
                        {treatment_pathway.consults.map((con, i) => (
                          <li key={i}>{con}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 6. Expected Goals */}
                  {treatment_pathway.expected_goals && treatment_pathway.expected_goals.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-50 bg-emerald-50/10 p-3 rounded-xl border border-emerald-500/10">
                      <span className="font-bold text-emerald-700 uppercase tracking-wide text-[10px] block">6. Targeted Therapeutic Goals</span>
                      <div className="grid grid-cols-1 gap-2 pl-1">
                        {treatment_pathway.expected_goals.map((goal, i) => (
                          <div key={i} className="flex items-start gap-2 text-slate-655 font-medium">
                            <CheckCircle2 size={13} className="text-emerald-500 mt-0.5 shrink-0" />
                            <span>{goal}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Medication Recommendations Collapsible Section */}
          {medication_plan && medication_plan.recommended_drugs && medication_plan.recommended_drugs.length > 0 && (
            <div className="border border-slate-150 rounded-xl overflow-hidden animate-fadeIn">
              <button
                onClick={() => setShowMedications(!showMedications)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <Pill size={13} className="text-cyan-600 animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Medication Recommendations ({medication_plan.recommended_drugs.length})</span>
                </div>
                {showMedications ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showMedications && (
                <div className="p-4 border-t border-slate-100 bg-white space-y-4 text-xs">
                  {medication_plan.recommended_drugs.map((drug, idx) => {
                    const confidencePct = Math.round(drug.confidence * 100);
                    let confidenceColor = "text-emerald-700 bg-emerald-50 border-emerald-100";
                    if (confidencePct < 80) {
                      confidenceColor = "text-amber-700 bg-amber-50 border-amber-100";
                    }

                    return (
                      <div key={idx} className="p-3.5 border border-slate-100 rounded-xl bg-slate-50/20 hover:bg-slate-50/50 transition-colors space-y-3">
                        {/* Drug Name & Confidence */}
                        <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-2">
                          <span className="font-extrabold text-slate-800 text-sm flex items-center gap-1.5">
                            <Pill size={14} className="text-cyan-600" />
                            {drug.name}
                          </span>
                          <span className={`px-2 py-0.5 rounded-full border text-[9px] font-black tracking-wider uppercase ${confidenceColor}`}>
                            {confidencePct}% Confidence
                          </span>
                        </div>

                        {/* Details grid */}
                        <div className="space-y-2 text-slate-655 font-medium text-[11px]">
                          <div>
                            <span className="font-bold text-slate-400 uppercase text-[9px] block">Indication</span>
                            <span className="text-slate-755">{drug.indication}</span>
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                            <div>
                              <span className="font-bold text-slate-400 uppercase text-[9px] block">Suggested Dose</span>
                              <span className="text-slate-755">{drug.suggested_dose} ({drug.route}, {drug.frequency})</span>
                            </div>
                            <div>
                              <span className="font-bold text-slate-400 uppercase text-[9px] block">Renal Adjustment Status</span>
                              <span className="text-slate-755">{drug.renal_adjustment}</span>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                            {/* Monitoring */}
                            {drug.monitoring && drug.monitoring.length > 0 && (
                              <div className="space-y-1">
                                <span className="font-bold text-slate-400 uppercase text-[9px] block">Clinical Monitoring</span>
                                <ul className="list-disc pl-3.5 space-y-0.5 text-slate-655">
                                  {drug.monitoring.map((m, i) => (
                                    <li key={i}>{m}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Contraindications */}
                            {drug.contraindications && drug.contraindications.length > 0 && (
                              <div className="space-y-1">
                                <span className="font-bold text-red-400 uppercase text-[9px] block">Contraindications / Precautions</span>
                                <ul className="list-disc pl-3.5 space-y-0.5 text-red-700/80">
                                  {drug.contraindications.map((c, i) => (
                                    <li key={i}>{c}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Clinical Risk Scores Collapsible Section */}
          {risk_scores && (
            <div className="border border-slate-150 rounded-xl overflow-hidden animate-fadeIn">
              <button
                onClick={() => setShowRiskScores(!showRiskScores)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <Gauge size={13} className="text-cyan-600 animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Clinical Risk Scores</span>
                </div>
                {showRiskScores ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showRiskScores && (
                <div className="p-4 border-t border-slate-100 bg-white space-y-4 text-xs">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(risk_scores).map(([key, item]) => {
                      const title = key.toUpperCase() === "APACHE2" ? "APACHE II" : key.toUpperCase();
                      let scoreColor = "text-slate-700 bg-slate-50 border-slate-150";
                      let badgeColor = "text-slate-600 bg-slate-50 border-slate-100";
                      
                      if (item.risk === "CRITICAL" || item.risk === "HIGH" || item.risk === "POSITIVE") {
                        scoreColor = "text-red-700 bg-red-50 border-red-150";
                        badgeColor = "text-red-700 bg-red-50 border-red-100";
                      } else if (item.risk === "MEDIUM") {
                        scoreColor = "text-amber-700 bg-amber-50 border-amber-150";
                        badgeColor = "text-amber-700 bg-amber-50 border-amber-100";
                      } else if (item.risk === "LOW" || item.risk === "NEGATIVE") {
                        scoreColor = "text-emerald-700 bg-emerald-50 border-emerald-150";
                        badgeColor = "text-emerald-700 bg-emerald-50 border-emerald-100";
                      }

                      return (
                        <div key={key} className="p-3.5 border border-slate-100 rounded-xl bg-slate-50/20 hover:bg-slate-50/50 transition-colors flex flex-col justify-between space-y-3">
                          <div>
                            {/* Score & Badge */}
                            <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-2">
                              <span className="font-extrabold text-slate-800 text-xs">{title} Score</span>
                              <span className={`px-2.5 py-0.5 rounded-full border text-[9px] font-black tracking-wider uppercase ${badgeColor}`}>
                                {item.risk} Risk
                              </span>
                            </div>

                            {/* Scoring details */}
                            <div className="mt-2.5 space-y-2">
                              <div className="flex items-baseline gap-2">
                                <span className={`px-2 py-0.5 rounded-md border font-extrabold text-xs ${scoreColor}`}>
                                  Score: {item.score}
                                </span>
                              </div>
                              
                              <p className="text-[10px] text-slate-655 font-medium leading-relaxed">
                                {item.explanation}
                              </p>
                            </div>
                          </div>

                          {/* Parameters used list */}
                          {item.parameters && item.parameters.length > 0 && (
                            <div className="pt-2 border-t border-slate-50">
                              <span className="font-bold text-slate-400 uppercase text-[9px] tracking-wider block mb-1">Triggered Indicators</span>
                              <ul className="list-disc pl-3 text-[9.5px] text-slate-500 font-medium space-y-0.5">
                                {item.parameters.map((p, i) => (
                                  <li key={i}>{p}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Laboratory Interpretation Collapsible Section */}
          {laboratory_interpretation && laboratory_interpretation.laboratory_interpretation && laboratory_interpretation.laboratory_interpretation.length > 0 && (
            <div className="border border-slate-150 rounded-xl overflow-hidden animate-fadeIn">
              <button
                onClick={() => setShowLabsInterpretation(!showLabsInterpretation)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <FlaskConical size={13} className="text-cyan-600 animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Laboratory Interpretation ({laboratory_interpretation.summary.abnormal_count} abnormal)</span>
                </div>
                {showLabsInterpretation ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showLabsInterpretation && (
                <div className="p-4 border-t border-slate-100 bg-white space-y-4 text-xs">
                  {/* Summary Bar */}
                  <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-50 border border-slate-150 rounded-xl font-bold text-[10px] text-slate-500 uppercase tracking-wide">
                    <div>
                      Abnormal Parameters: <span className="text-slate-800 font-black">{laboratory_interpretation.summary.abnormal_count}</span>
                    </div>
                    <div>
                      Critical Flags: <span className="text-red-600 font-black">{laboratory_interpretation.summary.critical_count}</span>
                    </div>
                    <div>
                      Highest Severity: <span className={`px-2 py-0.5 rounded-md border text-[9px] font-black ${
                        laboratory_interpretation.summary.highest_priority === "CRITICAL"
                          ? "text-red-700 bg-red-50 border-red-100 animate-pulse"
                          : "text-amber-700 bg-amber-50 border-amber-100"
                      }`}>{laboratory_interpretation.summary.highest_priority}</span>
                    </div>
                  </div>

                  {/* Labs List */}
                  <div className="space-y-3">
                    {laboratory_interpretation.laboratory_interpretation.map((lab, idx) => {
                      let severityBadge = "text-slate-600 bg-slate-50 border-slate-100";
                      if (lab.severity === "CRITICAL") {
                        severityBadge = "text-red-700 bg-red-50 border-red-200 animate-pulse";
                      } else if (lab.severity === "SEVERE") {
                        severityBadge = "text-red-600 bg-red-50 border-red-100";
                      } else if (lab.severity === "MODERATE") {
                        severityBadge = "text-amber-700 bg-amber-50 border-amber-100";
                      } else if (lab.severity === "MILD") {
                        severityBadge = "text-slate-500 bg-slate-50 border-slate-100";
                      }

                      return (
                        <div key={idx} className="p-3.5 border border-slate-100 rounded-xl bg-slate-50/20 hover:bg-slate-50/50 transition-colors space-y-2.5">
                          {/* Title & Severity */}
                          <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-2">
                            <span className="font-extrabold text-slate-800 text-xs flex items-center gap-1">
                              <span className={`w-1.5 h-1.5 rounded-full ${lab.severity === "CRITICAL" ? "bg-red-500 animate-ping" : "bg-cyan-500"}`}></span>
                              {lab.name}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] text-slate-400 font-bold">Val: <strong className="text-slate-700">{lab.value}</strong> (Ref: {lab.normal_range})</span>
                              <span className={`px-2 py-0.5 rounded-full border text-[9px] font-black uppercase tracking-wider ${severityBadge}`}>
                                {lab.severity}
                              </span>
                            </div>
                          </div>

                          {/* Details */}
                          <div className="space-y-2 text-[10.5px] text-slate-655 font-medium leading-relaxed">
                            <p>
                              <strong className="text-slate-800">Interpretation:</strong> {lab.interpretation}
                            </p>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                              {/* Causes */}
                              <div className="space-y-1">
                                <span className="font-bold text-slate-400 uppercase text-[9px] tracking-wide block">Possible Causes</span>
                                <ul className="list-disc pl-3.5 text-slate-500 text-[10px] space-y-0.5">
                                  {lab.possible_causes.map((c, i) => (
                                    <li key={i}>{c}</li>
                                  ))}
                                </ul>
                              </div>

                              {/* Significance */}
                              <div className="space-y-1">
                                <span className="font-bold text-slate-400 uppercase text-[9px] tracking-wide block">Clinical Significance</span>
                                <p className="text-[10px] text-slate-655 font-medium leading-relaxed">
                                  {lab.clinical_significance}
                                </p>
                              </div>
                            </div>

                            {/* Recommended Actions */}
                            {lab.recommended_actions && lab.recommended_actions.length > 0 && (
                              <div className="space-y-1 pt-1.5 border-t border-slate-50">
                                <span className="font-bold text-cyan-700 uppercase text-[9px] tracking-wide block">Recommended Clinical Actions</span>
                                <ul className="list-disc pl-3.5 text-slate-655 text-[10px] space-y-0.5 font-semibold">
                                  {lab.recommended_actions.map((act, i) => (
                                    <li key={i}>{act}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Clinical Trends Collapsible Section */}
          {trend_analysis && (
            <div className="border border-slate-150 rounded-xl overflow-hidden animate-fadeIn">
              <button
                onClick={() => setShowTrends(!showTrends)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <Activity size={13} className="text-cyan-600 animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Clinical Trends & Deterioration Risk</span>
                </div>
                {showTrends ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showTrends && (
                <div className="p-5 border-t border-slate-100 bg-white space-y-5 text-xs">
                  {/* Status header & Deterioration Probability */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 border-b border-slate-100 pb-4">
                    <div className="space-y-1">
                      <span className="text-[9px] font-black uppercase tracking-wider text-slate-400">Overall Patient Trajectory</span>
                      <div className="flex items-center gap-2">
                        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border ${
                          trend_analysis.overall_trend === "DETERIORATING"
                            ? "text-red-700 bg-red-50 border-red-155 animate-pulse"
                            : trend_analysis.overall_trend === "IMPROVING"
                            ? "text-emerald-700 bg-emerald-50 border-emerald-155"
                            : "text-slate-600 bg-slate-50 border-slate-155"
                        }`}>
                          {trend_analysis.overall_trend}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-[9px] font-black uppercase tracking-wider text-slate-400">
                        <span>Deterioration Probability</span>
                        <span className="font-extrabold text-slate-700">{Math.round(trend_analysis.deterioration_probability * 100)}%</span>
                      </div>
                      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-500 ${
                            trend_analysis.deterioration_probability >= 0.60
                              ? "bg-red-500"
                              : trend_analysis.deterioration_probability >= 0.30
                              ? "bg-amber-500"
                              : "bg-emerald-500"
                          }`}
                          style={{ width: `${trend_analysis.deterioration_probability * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Parameter Lists */}
                  <div className="space-y-4">
                    {/* 1. Worsening Parameters */}
                    {trend_analysis.worsening_parameters && trend_analysis.worsening_parameters.length > 0 && (
                      <div className="space-y-2">
                        <span className="font-bold text-red-700 uppercase tracking-wide text-[10px] block">Worsening Telemetry / Labs</span>
                        <div className="grid grid-cols-1 gap-2.5">
                          {trend_analysis.worsening_parameters.map((p, i) => (
                            <div key={i} className="p-3 border border-red-100 rounded-xl bg-red-50/10 text-[10.5px] space-y-1">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-red-800">{p.name}</span>
                                <span className="px-2 py-0.5 rounded-full bg-red-50 border border-red-100 text-red-700 font-extrabold text-[9px]">
                                  {p.rate_of_change} {p.direction === "RISING" ? "↑" : "↓"}
                                </span>
                              </div>
                              <p className="text-slate-655 font-medium text-[10px]">
                                <strong className="text-slate-700">Interpretation:</strong> {p.interpretation} <br />
                                <strong className="text-slate-700">Clinical Impact:</strong> {p.clinical_significance}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 2. Improving Parameters */}
                    {trend_analysis.improving_parameters && trend_analysis.improving_parameters.length > 0 && (
                      <div className="space-y-2 pt-2 border-t border-slate-50">
                        <span className="font-bold text-emerald-700 uppercase tracking-wide text-[10px] block">Improving Telemetry / Labs</span>
                        <div className="grid grid-cols-1 gap-2.5">
                          {trend_analysis.improving_parameters.map((p, i) => (
                            <div key={i} className="p-3 border border-emerald-100 rounded-xl bg-emerald-50/10 text-[10.5px] space-y-1">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-emerald-800">{p.name}</span>
                                <span className="px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-700 font-extrabold text-[9px]">
                                  {p.rate_of_change} {p.direction === "RISING" ? "↑" : "↓"}
                                </span>
                              </div>
                              <p className="text-slate-655 font-medium text-[10px]">
                                <strong className="text-slate-700">Interpretation:</strong> {p.interpretation} <br />
                                <strong className="text-slate-700">Clinical Impact:</strong> {p.clinical_significance}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 3. Stable Parameters */}
                    {trend_analysis.stable_parameters && trend_analysis.stable_parameters.length > 0 && (
                      <div className="space-y-2 pt-2 border-t border-slate-50">
                        <span className="font-bold text-slate-400 uppercase tracking-wide text-[10px] block">Stable Parameters</span>
                        <div className="flex flex-wrap gap-2">
                          {trend_analysis.stable_parameters.map((p, i) => (
                            <span key={i} className="px-2 py-1 rounded-lg border border-slate-100 bg-slate-50/50 text-[10px] text-slate-500 font-semibold">
                              • {p.name}: {p.current_value}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Recommendations */}
                  {trend_analysis.recommendations && trend_analysis.recommendations.length > 0 && (
                    <div className="space-y-2 pt-3 border-t border-slate-100">
                      <span className="font-bold text-cyan-700 uppercase tracking-wide text-[10px] block">Trend Recommendations</span>
                      <ul className="space-y-1.5 pl-3 text-slate-655 font-medium list-disc">
                        {trend_analysis.recommendations.map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                </div>
              )}
            </div>
          )}

          {/* 6. Evidence Section */}
          {evidence && evidence.length > 0 && (
            <div className="border border-slate-150 rounded-xl overflow-hidden">
              <button
                onClick={() => setShowEvidence(!showEvidence)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <BookOpen size={13} className="text-slate-500" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Clinical Evidence Basis</span>
                </div>
                {showEvidence ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showEvidence && (
                <div className="p-4 border-t border-slate-100 bg-white text-xs">
                  <ul className="space-y-2 pl-4 list-disc text-slate-500 leading-relaxed">
                    {evidence.map((ev, i) => (
                      <li key={i}>{ev}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* 7. Evidence & References Section */}
          {retrieved_sources && retrieved_sources.length > 0 && (
            <div className="border border-slate-150 rounded-xl overflow-hidden">
              <button
                onClick={() => setShowCitations(!showCitations)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50/50 hover:bg-slate-50 transition text-slate-700"
              >
                <div className="flex items-center gap-2">
                  <FileText size={13} className="text-cyan-600" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Evidence & References ({retrieved_sources.length})</span>
                </div>
                {showCitations ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {showCitations && (
                <div className="p-4 border-t border-slate-100 bg-white space-y-3">
                  {retrieved_sources.map((cit, i) => {
                    const score = cit.similarity_score;
                    const pct = score ? (score > 1 ? score : score * 100).toFixed(0) + "%" : "N/A";
                    return (
                      <div key={i} className="p-3 border border-slate-100 rounded-xl bg-slate-50/30 text-xs space-y-1.5 hover:bg-slate-50/50 transition-colors">
                        <div className="flex items-start justify-between gap-3">
                          <span className="font-bold text-slate-800 leading-snug">{cit.title}</span>
                          {score && (
                            <span className="px-2 py-0.5 rounded-full bg-cyan-50 border border-cyan-100 text-cyan-700 font-extrabold text-[9px] shrink-0">
                              {pct} Match
                            </span>
                          )}
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-x-4 gap-y-1 text-[10px] text-slate-500 font-medium">
                          <div>
                            <span className="font-semibold text-slate-400">Source:</span> {cit.source || "N/A"}
                          </div>
                          <div>
                            <span className="font-semibold text-slate-400">Category:</span> {cit.category || "N/A"}
                          </div>
                          <div>
                            <span className="font-semibold text-slate-400">Section:</span> {cit.section || "N/A"}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Confidence Score Gauge Progress Bar */}
          {confidence !== undefined && (
            <div className="space-y-1.5 bg-slate-50 border border-slate-150 rounded-xl p-3.5">
              <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-wider text-slate-400">
                <span className="flex items-center gap-1"><Gauge size={11} /> AI Decision Confidence</span>
                <span className="font-extrabold text-slate-700">{Math.round(confidence * 100)}%</span>
              </div>
              <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-cyan-600 rounded-full transition-all duration-500" 
                  style={{ width: `${confidence * 100}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Performance Metrics Panel */}
          {content?.performance_metrics && (
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 pt-3 border-t border-slate-100 text-[9.5px] font-bold text-slate-400">
              <span className="flex items-center gap-1">
                <span className={`h-1.5 w-1.5 rounded-full ${content.performance_metrics.cache === 'HIT' ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
                Cache {content.performance_metrics.cache}
              </span>
              <span>•</span>
              <span>Total: {(content.performance_metrics.total_response_time_ms / 1000).toFixed(1)}s</span>
              <span>•</span>
              <span>Eval: {(content.performance_metrics.prompt_evaluation_time_ms / 1000).toFixed(1)}s</span>
              <span>•</span>
              <span>Gen: {(content.performance_metrics.generation_time_ms / 1000).toFixed(1)}s</span>
              <span>•</span>
              <span>Speed: {content.performance_metrics.tokens_per_sec} tok/s</span>
            </div>
          )}

        </div>
        <span className="text-[9px] text-slate-400 self-start pl-1">{timestamp}</span>
      </div>
    </div>
  );
}
