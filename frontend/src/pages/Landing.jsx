import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Activity,
  ArrowRight,
  Shield,
  Cpu,
  Layers,
  HeartPulse,
  Lock,
  ExternalLink,
  Users,
  LineChart,
  Terminal,
  Brain,
  Stethoscope,
  Building2,
  FileSpreadsheet,
  CheckCircle2,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import DNAHelixCanvas from "../components/common/DNAHelixCanvas";

export default function Landing() {
  const fadeInUp = {
    initial: { opacity: 0, y: 30 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, margin: "-80px" },
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] },
  };

  const staggerContainer = {
    initial: {},
    whileInView: { transition: { staggerChildren: 0.12 } },
    viewport: { once: true },
  };

  return (
    <div className="min-h-screen w-full bg-[#070b14] text-slate-100 font-sans relative selection:bg-amber-500/30 selection:text-amber-200 overflow-x-hidden">
      {/* Inline ECG waveform animation keyframes */}
      <style>{`
        @keyframes ecgSweep {
          0% { stroke-dashoffset: 1000; }
          100% { stroke-dashoffset: 0; }
        }
        .animate-ecg {
          stroke-dasharray: 1000;
          animation: ecgSweep 12s linear infinite;
        }
      `}</style>

      {/* Header / Navbar */}
      <header className="w-full border-b border-slate-800/60 bg-[#070b14]/90 backdrop-blur-xl sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-amber-500/20 via-sky-500/20 to-blue-600/30 border border-amber-500/40 shadow-lg shadow-amber-500/10">
              <Activity className="text-amber-400" size={20} />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-white flex items-center gap-2">
                IntelliICU
                <span className="text-[10px] font-semibold text-amber-400/90 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30 uppercase tracking-widest">
                  v2.0 Enterprise
                </span>
              </span>
              <span className="text-[10px] block font-medium text-slate-400 tracking-wider">
                Clinical Decision Support & Telemetry Platform
              </span>
            </div>
          </div>

          <div className="flex items-center gap-5">
            <span
              className="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 opacity-80 cursor-not-allowed select-none bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800"
              title="API Documentation Endpoint Deployment Coming Soon"
            >
              API Docs (Coming Soon)
            </span>
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 border border-slate-700/80 text-white font-semibold px-4 py-2.5 text-xs transition duration-200 hover:bg-slate-800 hover:border-amber-500/40 active:scale-[0.98] shadow-sm"
            >
              <Lock size={12} className="text-amber-400" />
              Sign In
            </Link>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="relative z-10">
        
        {/* ========================================================================= */}
        {/* HERO SECTION WITH BIOLUMINESCENT DNA HELIX BACKGROUND */}
        {/* ========================================================================= */}
        <section className="relative min-h-[90vh] flex items-center px-6 py-16 md:py-24 border-b border-slate-800/60">
          <DNAHelixCanvas className="opacity-90" />
          
          {/* Subtle Ambient Radial Glow */}
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-amber-500/10 rounded-full blur-[160px] pointer-events-none" />
          <div className="absolute bottom-10 right-1/4 w-[500px] h-[500px] bg-sky-500/10 rounded-full blur-[160px] pointer-events-none" />

          <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 25 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7 }}
              className="lg:col-span-7 space-y-8 text-left"
            >
              <div className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-950/30 px-3.5 py-1.5 backdrop-blur-md">
                <Sparkles size={13} className="text-amber-400" />
                <span className="text-[11px] font-semibold text-amber-300 tracking-wide">
                  Clinical AI Decision Support • Continuous Surveillance
                </span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-[1.12] tracking-tight text-white">
                Real-Time <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-amber-400 to-sky-400">Clinical Intelligence</span> & Patient Surveillance.
              </h1>

              <p className="text-base text-slate-300 leading-relaxed max-w-xl font-normal">
                An enterprise clinical platform empowering intensive care teams with automated sepsis risk stratification, real-time physiological telemetry analysis, and context-aware RAG decision support.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 pt-2">
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-bold px-7 py-3.5 text-xs transition duration-200 hover:brightness-110 hover:shadow-lg hover:shadow-amber-500/20 active:scale-[0.98]"
                >
                  Access Command Center
                  <ArrowRight size={14} />
                </Link>
                <a
                  href="#surveillance"
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-800 bg-slate-900/60 text-slate-300 font-semibold px-6 py-3.5 text-xs transition hover:bg-slate-800 hover:text-white"
                >
                  Explore Capabilities
                  <ChevronRight size={14} className="text-slate-500" />
                </a>
              </div>

              {/* Trust Indicators */}
              <div className="pt-6 border-t border-slate-800/80 grid grid-cols-3 gap-6 max-w-lg">
                <div>
                  <div className="text-2xl font-bold text-white font-mono">2s</div>
                  <div className="text-xs text-slate-400 mt-0.5">WebSocket Telemetry</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-amber-400 font-mono">96%</div>
                  <div className="text-xs text-slate-400 mt-0.5">AI Confidence Index</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-white font-mono">8 Roles</div>
                  <div className="text-xs text-slate-400 mt-0.5">Granular RBAC Security</div>
                </div>
              </div>
            </motion.div>

            {/* Hero Live Telemetry Preview Widget */}
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="lg:col-span-5 relative w-full flex justify-center"
            >
              <div className="w-full max-w-[440px] rounded-2xl border border-slate-800 bg-slate-900/80 p-6 backdrop-blur-xl shadow-2xl space-y-6 border-t-2 border-t-amber-500/60">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div className="flex items-center gap-2.5">
                    <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-xs font-semibold text-slate-300 tracking-wide uppercase">
                      MICU Live Stream
                    </span>
                  </div>
                  <span className="text-[11px] font-mono font-medium text-amber-400 bg-amber-950/50 px-2.5 py-1 rounded border border-amber-500/30">
                    BED 04 • ICU-10248
                  </span>
                </div>

                {/* ECG Waveform Screen */}
                <div className="h-28 bg-[#04070f] rounded-xl border border-slate-800 p-3 flex items-center justify-center relative overflow-hidden">
                  <svg viewBox="0 0 400 100" className="w-full h-full text-sky-400 drop-shadow-[0_0_8px_rgba(56,189,248,0.5)]">
                    <path
                      d="M 0 50 L 80 50 L 90 40 L 95 65 L 105 20 L 115 80 L 125 50 L 200 50 L 210 40 L 215 65 L 225 20 L 235 80 L 245 50 L 320 50 L 330 40 L 335 65 L 345 20 L 355 80 L 365 50 L 400 50"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="animate-ecg"
                    />
                  </svg>
                  <div className="absolute top-3 right-3 text-right">
                    <div className="text-2xl font-bold text-sky-400 font-mono">132</div>
                    <div className="text-[9px] font-semibold text-slate-400 uppercase tracking-wider font-mono">BPM (HR)</div>
                  </div>
                </div>

                {/* Patient Telemetry Cards */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3.5">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">BP / MAP</span>
                    <div className="text-base font-bold text-white font-mono mt-1">82/48 <span className="text-xs text-amber-400 font-normal">(59)</span></div>
                    <span className="text-[10px] font-semibold text-red-400 mt-1 block">Hypotensive</span>
                  </div>
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3.5">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Sepsis AI Risk</span>
                    <div className="text-base font-bold text-red-400 font-mono mt-1">93% <span className="text-xs text-slate-400 font-normal">HIGH</span></div>
                    <span className="text-[10px] font-semibold text-amber-400 mt-1 block">Lactate 4.6 mmol/L</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>


        {/* ========================================================================= */}
        {/* GROUP 1: REAL-TIME PHYSIOLOGICAL SURVEILLANCE GROUP */}
        {/* ========================================================================= */}
        <section id="surveillance" className="py-20 px-6 border-b border-slate-800/60 bg-[#060a12]">
          <div className="max-w-7xl mx-auto space-y-12">
            
            {/* Group 1 Mini-Hero Header */}
            <motion.div {...fadeInUp} className="max-w-2xl space-y-3">
              <div className="inline-flex items-center gap-2 text-xs font-bold text-sky-400 uppercase tracking-widest">
                <Activity size={15} />
                <span>01. Real-Time Surveillance Group</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                Continuous Physiological Signals & Waveforms
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                Stream real-time vital metrics, multi-parameter trend diagnostics, and instant patient deterioration alerts across active ICU wards.
              </p>
            </motion.div>

            {/* Group 1 Component Cards Grid */}
            <motion.div {...staggerContainer} className="grid grid-cols-1 md:grid-cols-2 gap-8">
              
              {/* Feature 1.1: Live Monitoring */}
              <motion.div {...fadeInUp} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-8 space-y-6 transition hover:border-slate-700">
                <div className="h-12 w-12 rounded-xl bg-sky-950/60 border border-sky-500/30 flex items-center justify-center text-sky-400">
                  <Activity size={24} />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-white">Live Monitoring (`/monitoring`)</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Single-patient high-acuity bedside surveillance feed. Features real-time parameter cards for Heart Rate, SpO2, MAP, Temperature, and Respiratory Rate, with auto-resolving alarm engine.
                  </p>
                </div>
                <div className="pt-2 border-t border-slate-800/80 flex items-center gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1.5"><CheckCircle2 size={14} className="text-emerald-400" /> 2s Dynamic Telemetry</span>
                  <span className="flex items-center gap-1.5"><CheckCircle2 size={14} className="text-emerald-400" /> Alarm Suppression</span>
                </div>
              </motion.div>

              {/* Feature 1.2: Telemetry Trends */}
              <motion.div {...fadeInUp} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-8 space-y-6 transition hover:border-slate-700">
                <div className="h-12 w-12 rounded-xl bg-amber-950/60 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <LineChart size={24} />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-white">Telemetry Trends (`/telemetry`)</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Multi-patient parameter trend surveillance. Monitors 7 physiological biomarkers across all ICU beds to detect sub-acute physiological deterioration before clinical crisis.
                  </p>
                </div>
                <div className="pt-2 border-t border-slate-800/80 flex items-center gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1.5"><CheckCircle2 size={14} className="text-emerald-400" /> 7 Biomarker Matrices</span>
                  <span className="flex items-center gap-1.5"><CheckCircle2 size={14} className="text-emerald-400" /> Trend Summary Log</span>
                </div>
              </motion.div>

            </motion.div>

          </div>
        </section>


        {/* ========================================================================= */}
        {/* GROUP 2: CLINICAL AI INTELLIGENCE GROUP */}
        {/* ========================================================================= */}
        <section id="ai-intelligence" className="py-20 px-6 border-b border-slate-800/60 bg-[#070b14]">
          <div className="max-w-7xl mx-auto space-y-12">
            
            {/* Group 2 Mini-Hero Header */}
            <motion.div {...fadeInUp} className="max-w-2xl space-y-3">
              <div className="inline-flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-widest">
                <Brain size={15} />
                <span>02. AI Intelligence Group</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                Context-Aware Clinical Copilot & RAG Engine
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                Evidence-grounded clinical decision support powered by patient context synthesis, guideline vector retrieval, and automated sepsis risk calculation.
              </p>
            </motion.div>

            {/* Group 2 Component Cards Grid */}
            <motion.div {...staggerContainer} className="grid grid-cols-1 md:grid-cols-3 gap-8">
              
              {/* Feature 2.1: Clinical Copilot */}
              <motion.div {...fadeInUp} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-7 space-y-5 transition hover:border-slate-700">
                <div className="h-11 w-11 rounded-xl bg-amber-950/60 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <Stethoscope size={22} />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-white">Clinical Copilot (`/copilot`)</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Per-patient RAG assistant. Retrieves EHR context, lab findings, and clinical guidelines to generate evidence-based treatment suggestions and PDF summary notes.
                  </p>
                </div>
                <div className="pt-3 border-t border-slate-800/80 text-xs text-slate-400 flex items-center gap-2">
                  <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                  <span>RAG Vector Search + PDF Report Generator</span>
                </div>
              </motion.div>

              {/* Feature 2.2: Hospital Assistant */}
              <motion.div {...fadeInUp} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-7 space-y-5 transition hover:border-slate-700">
                <div className="h-11 w-11 rounded-xl bg-sky-950/60 border border-sky-500/30 flex items-center justify-center text-sky-400">
                  <Building2 size={22} />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-white">Hospital Assistant (`/hospital-assistant`)</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Hospital-wide AI triage command center. Processes natural language queries across all active ICU beds, summarizing unit occupancy and critical alerts.
                  </p>
                </div>
                <div className="pt-3 border-t border-slate-800/80 text-xs text-slate-400 flex items-center gap-2">
                  <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                  <span>Natural Language Triage Queries</span>
                </div>
              </motion.div>

              {/* Feature 2.3: Sepsis Risk Engine */}
              <motion.div {...fadeInUp} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-7 space-y-5 transition hover:border-slate-700">
                <div className="h-11 w-11 rounded-xl bg-indigo-950/60 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <Cpu size={22} />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-white">Sepsis ML Risk Engine</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Continuous machine learning risk scoring. Computes SOFA, qSOFA, and NEWS2 clinical severity indexes to flag sepsis probability in real-time.
                  </p>
                </div>
                <div className="pt-3 border-t border-slate-800/80 text-xs text-slate-400 flex items-center gap-2">
                  <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                  <span>SOFA / qSOFA / NEWS2 Calculations</span>
                </div>
              </motion.div>

            </motion.div>

          </div>
        </section>


        {/* ========================================================================= */}
        {/* GROUP 3: OPERATIONS & GOVERNANCE GROUP */}
        {/* ========================================================================= */}
        <section id="operations" className="py-20 px-6 border-b border-slate-800/60 bg-[#060a12]">
          <div className="max-w-7xl mx-auto space-y-12">
            
            {/* Group 3 Mini-Hero Header */}
            <motion.div {...fadeInUp} className="max-w-2xl space-y-3">
              <div className="inline-flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-widest">
                <Layers size={15} />
                <span>03. Operations & Governance Group</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                ICU Operations, Population Analytics & RBAC Security
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                Centralized hospital administration, population-level risk trend metrics, and audit-logged role-based access management across 8 clinical tiers.
              </p>
            </motion.div>

            {/* Group 3 Component Cards Grid */}
            <motion.div {...staggerContainer} className="grid grid-cols-1 md:grid-cols-3 gap-8">
              
              {/* Feature 3.1: Operations Dashboard */}
              <motion.div {...fadeInUp} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-7 space-y-5 transition hover:border-slate-700">
                <div className="h-11 w-11 rounded-xl bg-emerald-950/60 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <Layers size={22} />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-white">Admin Operations (`/dashboard`)</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Hospital-wide ICU census snapshot. Displays total patients, critical counts, bed occupancy, department unit status, and active alert feeds.
                  </p>
                </div>
                <div className="pt-3 border-t border-slate-800/80 text-xs text-slate-400 flex items-center gap-2">
                  <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                  <span>Hospital-Wide Census & Unit Status</span>
                </div>
              </motion.div>

              {/* Feature 3.2: Analytics */}
              <motion.div {...fadeInUp} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-7 space-y-5 transition hover:border-slate-700">
                <div className="h-11 w-11 rounded-xl bg-sky-950/60 border border-sky-500/30 flex items-center justify-center text-sky-400">
                  <FileSpreadsheet size={22} />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-white">Population Analytics (`/analytics`)</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Aggregate clinical statistics. Tracks 24h/7d population risk progression trends, admission/discharge volumes, and AI prediction accuracy metrics.
                  </p>
                </div>
                <div className="pt-3 border-t border-slate-800/80 text-xs text-slate-400 flex items-center gap-2">
                  <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                  <span>24h/7d Progression & AUROC Metrics</span>
                </div>
              </motion.div>

              {/* Feature 3.3: User Directory & RBAC */}
              <motion.div {...fadeInUp} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-7 space-y-5 transition hover:border-slate-700">
                <div className="h-11 w-11 rounded-xl bg-purple-950/60 border border-purple-500/30 flex items-center justify-center text-purple-400">
                  <Users size={22} />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-white">User Directory & RBAC (`/users`)</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Granular permission management across 8 roles (SuperAdmin, HospitalAdmin, ICUManager, Doctor, Nurse, LabTechnician, Receptionist, Viewer).
                  </p>
                </div>
                <div className="pt-3 border-t border-slate-800/80 text-xs text-slate-400 flex items-center gap-2">
                  <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                  <span>8-Role Security Clearances</span>
                </div>
              </motion.div>

            </motion.div>

          </div>
        </section>


        {/* ========================================================================= */}
        {/* INTERACTIVE DEMO SANDBOX ACCESSIBILITY SECTION */}
        {/* ========================================================================= */}
        <section className="py-20 px-6 border-b border-slate-800/60 max-w-5xl mx-auto">
          <motion.div {...fadeInUp} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-8 sm:p-12 backdrop-blur-xl text-center space-y-8 shadow-2xl relative overflow-hidden border-t-2 border-t-amber-500/50">
            <div className="space-y-3">
              <span className="text-xs font-bold text-amber-400 uppercase tracking-widest block">
                Sandbox Environment
              </span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                Try Pre-Configured Role Accounts
              </h2>
              <p className="text-xs sm:text-sm text-slate-300 max-w-lg mx-auto leading-relaxed">
                Log in directly using pre-seeded accounts to experience specific clinical workflows and clearance views.
              </p>
            </div>

            {/* Sandbox Credentials Table */}
            <div className="max-w-2xl mx-auto rounded-xl border border-slate-800 bg-slate-950/80 p-5 text-left space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                  <Terminal size={14} className="text-amber-400" />
                  Pre-Seeded Clinical Roles
                </span>
                <span className="text-[10px] text-slate-400 font-mono">Environment: Demo Sandbox</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3.5 rounded-lg border border-purple-500/30 bg-purple-950/20 space-y-1">
                  <div className="text-xs font-bold text-purple-300">HospitalAdmin</div>
                  <div className="text-[11px] text-slate-300 font-mono">admin / admin123</div>
                  <div className="text-[10px] text-purple-400 font-medium">Full Governance</div>
                </div>

                <div className="p-3.5 rounded-lg border border-sky-500/30 bg-sky-950/20 space-y-1">
                  <div className="text-xs font-bold text-sky-300">ICUManager</div>
                  <div className="text-[11px] text-slate-300 font-mono">reyes / intensivist123</div>
                  <div className="text-[10px] text-sky-400 font-medium">Ward Surveillance</div>
                </div>

                <div className="p-3.5 rounded-lg border border-emerald-500/30 bg-emerald-950/20 space-y-1">
                  <div className="text-xs font-bold text-emerald-300">Doctor</div>
                  <div className="text-[11px] text-slate-300 font-mono">miller / miller123</div>
                  <div className="text-[10px] text-emerald-400 font-medium">Clinical Workspaces</div>
                </div>
              </div>
            </div>

            <div>
              <Link
                to="/login"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-bold px-8 py-3.5 text-xs transition duration-200 hover:brightness-110 shadow-lg shadow-amber-500/20 active:scale-[0.98]"
              >
                <Lock size={13} />
                Launch Portal Sign In
              </Link>
            </div>
          </motion.div>
        </section>

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/60 bg-[#04070e] py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
              <Activity size={14} />
            </div>
            <span className="text-xs font-bold text-slate-300 tracking-wider uppercase">
              INTELLIICU CLINICAL SYSTEM • 2026
            </span>
          </div>

          <div className="text-center text-xs text-slate-400 font-medium space-y-1">
            <p>Licensed under the MIT License.</p>
            <p>Maintained & Extended by <span className="text-white font-semibold">Nitesh Kumawat (nite208)</span>. Originally created as a collaborative clinical project.</p>
          </div>

          <div className="flex items-center gap-4">
            <a
              href="https://github.com/nite208/IntelliICU"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition"
            >
              <svg
                viewBox="0 0 24 24"
                width="14"
                height="14"
                stroke="currentColor"
                strokeWidth="2.5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
              </svg>
              GitHub Repository <ExternalLink size={10} />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
