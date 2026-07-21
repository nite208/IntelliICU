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
  Database,
  Users,
  LineChart,
  Terminal
} from "lucide-react";

export default function Landing() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
  };

  return (
    <div className="min-h-screen w-full bg-[#0a0e1a] text-slate-100 font-sans relative overflow-x-hidden">
      {/* Inline styles for custom animations like ECG trace */}
      <style>{`
        @keyframes ecgSweep {
          0% { stroke-dashoffset: 1000; }
          100% { stroke-dashoffset: 0; }
        }
        .animate-ecg {
          stroke-dasharray: 1000;
          animation: ecgSweep 15s linear infinite;
        }
        @keyframes pulseGlow {
          0%, 100% { opacity: 0.15; transform: scale(1); }
          50% { opacity: 0.25; transform: scale(1.1); }
        }
        .glow-pulse {
          animation: pulseGlow 8s ease-in-out infinite;
        }
      `}</style>

      {/* Background ambient glowing nodes */}
      <div className="absolute top-[-10%] left-[-10%] h-[600px] w-[600px] rounded-full bg-cyan-500/10 blur-[180px] glow-pulse pointer-events-none" />
      <div className="absolute top-[40%] right-[-10%] h-[650px] w-[650px] rounded-full bg-purple-600/10 blur-[180px] glow-pulse pointer-events-none" style={{ animationDelay: "-3s" }} />
      <div className="absolute bottom-[-5%] left-[20%] h-[500px] w-[500px] rounded-full bg-indigo-500/10 blur-[150px] glow-pulse pointer-events-none" style={{ animationDelay: "-5s" }} />

      {/* Header / Navbar */}
      <header className="w-full border-b border-slate-900 bg-[#0a0e1a]/85 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 shadow-md shadow-cyan-500/20">
              <Activity className="text-white" size={20} />
            </div>
            <div>
              <span className="text-md font-black tracking-wider uppercase text-white">
                IntelliICU
              </span>
              <span className="text-[9px] block font-bold text-cyan-400 tracking-widest uppercase">
                Clinical AI Command Center
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://intelliicu-production.up.railway.app/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-slate-200 transition"
            >
              API Docs <ExternalLink size={12} />
            </a>
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 font-bold px-4 py-2 text-xs transition duration-300 hover:border-cyan-500/50 hover:bg-slate-950 active:scale-[0.98]"
            >
              Sign In
            </Link>
          </div>
        </div>
      </header>

      {/* Main Section */}
      <main className="max-w-7xl mx-auto px-6 relative z-10">
        
        {/* 1. HERO SECTION */}
        <section className="py-20 md:py-28 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-7 space-y-8 text-left">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/20 px-3.5 py-1.5">
              <HeartPulse size={12} className="text-cyan-400 animate-pulse" />
              <span className="font-mono text-[9px] font-bold text-cyan-400 uppercase tracking-widest">
                AI Decision Support • Active Surveillance
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-tight tracking-tight text-white">
              Real-Time <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-400">Clinical Intelligence</span> & Patient Surveillance.
            </h1>

            <p className="text-base text-slate-400 leading-relaxed max-w-xl">
              An enterprise-grade clinical decision support platform. Supporting ICU clinicians with automated sepsis risk predictions, real-time physiological telemetry, alert auditing, and structured patient timelines.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 pt-2">
              <Link
                to="/login"
                className="inline-flex items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-extrabold px-6 py-4 text-xs transition duration-300 hover:shadow-lg hover:shadow-cyan-500/25 active:scale-[0.98]"
              >
                Enter Command Center
                <ArrowRight size={14} />
              </Link>
              <a
                href="https://intelliicu-production.up.railway.app/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-800 bg-slate-900/30 text-slate-300 font-extrabold px-6 py-4 text-xs transition hover:bg-slate-900/60 hover:text-white"
              >
                View API Docs
                <ExternalLink size={13} className="text-slate-500" />
              </a>
            </div>
          </div>

          {/* Decorative Live Telemetry Mockup */}
          <div className="lg:col-span-5 relative w-full flex justify-center">
            <div className="w-full max-w-[420px] rounded-3xl border border-slate-800/80 bg-slate-900/20 p-6 backdrop-blur-2xl shadow-[0_0_50px_rgba(6,182,212,0.06)] space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800/50 pb-4">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-cyan-500 animate-ping" />
                  <span className="font-mono text-[10px] font-black uppercase text-slate-400 tracking-wider">
                    ICU TELEMETRY STREAM
                  </span>
                </div>
                <span className="font-mono text-[9px] font-semibold text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/30">
                  BED 04
                </span>
              </div>

              {/* Dynamic Waveform Panel */}
              <div className="h-24 bg-slate-950/60 rounded-2xl border border-slate-900 p-2 flex items-center justify-center relative overflow-hidden">
                <svg viewBox="0 0 400 100" className="w-full h-full text-cyan-500 drop-shadow-[0_0_6px_rgba(6,182,212,0.4)]">
                  <path
                    d="M 0 50 L 80 50 L 90 40 L 95 65 L 105 20 L 115 80 L 125 50 L 200 50 L 210 40 L 215 65 L 225 20 L 235 80 L 245 50 L 320 50 L 330 40 L 335 65 L 345 20 L 355 80 L 365 50 L 400 50"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="animate-ecg"
                  />
                </svg>
                <div className="absolute top-2 right-3 flex items-baseline gap-1 text-right">
                  <span className="text-2xl font-black text-cyan-400 font-mono">78</span>
                  <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest font-mono">BPM</span>
                </div>
              </div>

              {/* Patient Vitals Micro Widgets */}
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl border border-slate-900 bg-slate-950/30 p-3 flex flex-col justify-between">
                  <span className="text-[8px] font-black text-slate-500 uppercase tracking-wider">SPO2 SATURATION</span>
                  <div className="flex items-baseline gap-1 mt-1">
                    <span className="text-lg font-black text-indigo-400 font-mono">98%</span>
                    <span className="text-[7px] text-slate-500 font-bold">NORMAL</span>
                  </div>
                </div>
                <div className="rounded-xl border border-slate-900 bg-slate-950/30 p-3 flex flex-col justify-between">
                  <span className="text-[8px] font-black text-slate-500 uppercase tracking-wider">SEPSIS ML RISK</span>
                  <div className="flex items-baseline gap-1 mt-1">
                    <span className="text-lg font-black text-emerald-400 font-mono">12%</span>
                    <span className="text-[7px] text-slate-500 font-bold">LOW</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 2. PROBLEM / VALUE SECTION */}
        <section className="py-20 border-t border-slate-900/60">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-4">
            <span className="font-mono text-[10px] font-black text-cyan-400 uppercase tracking-widest">
              CLINICAL IMPACT
            </span>
            <h2 className="text-3xl font-black tracking-tight text-white">
              Solving Critical Care Challenges
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              IntelliICU addresses communication overhead and information overload in busy intensive care environments.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-2xl border border-slate-900 bg-slate-900/10 p-8 backdrop-blur-md shadow-md transition hover:border-slate-800">
              <div className="h-10 w-10 rounded-xl bg-cyan-950/50 border border-cyan-800/30 flex items-center justify-center text-cyan-400 mb-6">
                <Cpu size={18} />
              </div>
              <h3 className="text-lg font-bold text-white mb-3">Early Sepsis Detection</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Utilizes structured physiological algorithms to monitor trends in real-time, helping clinicians anticipate septic shock before physical onset.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-900 bg-slate-900/10 p-8 backdrop-blur-md shadow-md transition hover:border-slate-800">
              <div className="h-10 w-10 rounded-xl bg-indigo-950/50 border border-indigo-800/30 flex items-center justify-center text-indigo-400 mb-6">
                <Layers size={18} />
              </div>
              <h3 className="text-lg font-bold text-white mb-3">Reduced Alert Fatigue</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Aggregates and audits live patient vitals, filter out noise, and highlights critical alarms so you can focus on patients requiring urgent attention.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-900 bg-slate-900/10 p-8 backdrop-blur-md shadow-md transition hover:border-slate-800">
              <div className="h-10 w-10 rounded-xl bg-purple-950/50 border border-purple-800/30 flex items-center justify-center text-purple-400 mb-6">
                <Shield size={18} />
              </div>
              <h3 className="text-lg font-bold text-white mb-3">Granular Access Controls</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Enforces secure Role-Based Access Controls (RBAC) to segment clinical interfaces, audit user operations, and ensure patient privacy records are protected.
              </p>
            </div>
          </div>
        </section>

        {/* 3. FEATURE GRID */}
        <section className="py-20 border-t border-slate-900/60">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-4">
            <span className="font-mono text-[10px] font-black text-indigo-400 uppercase tracking-widest">
              PLATFORM CAPABILITIES
            </span>
            <h2 className="text-3xl font-black tracking-tight text-white">
              Clinical Command Infrastructure
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Explore the core components engineered inside the IntelliICU ecosystem.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Feature 1 */}
            <div className="flex gap-6 rounded-2xl border border-slate-900 bg-slate-900/10 p-6 backdrop-blur-md">
              <div className="shrink-0 h-10 w-10 rounded-xl bg-slate-950 flex items-center justify-center border border-slate-800 text-cyan-400">
                <Users size={16} />
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-black text-white uppercase tracking-wider">Role-Based Dashboard Portals</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Tailored interfaces for clinicians (patient vitals overview, clinical copilot support) and platform administrators (user control, audit logs, system stats).
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="flex gap-6 rounded-2xl border border-slate-900 bg-slate-900/10 p-6 backdrop-blur-md">
              <div className="shrink-0 h-10 w-10 rounded-xl bg-slate-950 flex items-center justify-center border border-slate-800 text-indigo-400">
                <Activity size={16} />
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-black text-white uppercase tracking-wider">WebSocket Live Monitoring</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Real-time streaming pipelines driving instant vital logs updates, alert states, and active ward patient maps without manual browser reloads.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="flex gap-6 rounded-2xl border border-slate-900 bg-slate-900/10 p-6 backdrop-blur-md">
              <div className="shrink-0 h-10 w-10 rounded-xl bg-slate-950 flex items-center justify-center border border-slate-800 text-purple-400">
                <Cpu size={16} />
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-black text-white uppercase tracking-wider">AI Clinical Copilot & RAG</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  AI-assisted decision support offering contextual risk interpretations, hospital operational queries, and medical knowledge suggestions.
                </p>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="flex gap-6 rounded-2xl border border-slate-900 bg-slate-900/10 p-6 backdrop-blur-md">
              <div className="shrink-0 h-10 w-10 rounded-xl bg-slate-950 flex items-center justify-center border border-slate-800 text-emerald-400">
                <LineChart size={16} />
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-black text-white uppercase tracking-wider">Telemetry Diagnostics</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Comprehensive telemetry views detailing historical charts for vital signs like SpO2, Heart Rate, Blood Pressure, and Respiratory rates.
                </p>
              </div>
            </div>

          </div>
        </section>

        {/* 4. TECH STACK STRIP */}
        <section className="py-12 border-t border-slate-900/60 text-center space-y-6">
          <span className="font-mono text-[9px] font-black text-slate-500 uppercase tracking-widest block">
            BUILT WITH ENTERPRISE TECHNOLOGIES
          </span>
          <div className="flex flex-wrap justify-center items-center gap-3 sm:gap-6">
            <span className="font-mono text-xs text-slate-300 bg-slate-900/40 border border-slate-800/80 px-3 py-1.5 rounded-lg flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              FastAPI
            </span>
            <span className="font-mono text-xs text-slate-300 bg-slate-900/40 border border-slate-800/80 px-3 py-1.5 rounded-lg flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
              React & Vite
            </span>
            <span className="font-mono text-xs text-slate-300 bg-slate-900/40 border border-slate-800/80 px-3 py-1.5 rounded-lg flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
              PostgreSQL
            </span>
            <span className="font-mono text-xs text-slate-300 bg-slate-900/40 border border-slate-800/80 px-3 py-1.5 rounded-lg flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
              WebSockets
            </span>
            <span className="font-mono text-xs text-slate-300 bg-slate-900/40 border border-slate-800/80 px-3 py-1.5 rounded-lg flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-purple-400" />
              LLM Integration
            </span>
          </div>
        </section>

        {/* 5. LIVE DEMO SECTION */}
        <section className="py-20 border-t border-slate-900/60 max-w-4xl mx-auto">
          <div className="rounded-3xl border border-slate-800 bg-gradient-to-tr from-slate-900/40 via-slate-900/25 to-[#0b2942]/10 p-8 sm:p-12 backdrop-blur-2xl text-center space-y-8 relative overflow-hidden shadow-xl">
            <div className="absolute top-[-100px] right-[-100px] h-[300px] w-[300px] rounded-full bg-cyan-500/5 blur-[80px] pointer-events-none" />
            
            <div className="space-y-3">
              <span className="font-mono text-[10px] font-black text-cyan-400 uppercase tracking-widest block">
                IMMEDIATE DEMO ACCESS
              </span>
              <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                Try the Command Center Instantly
              </h2>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                Log in directly using pre-seeded sandbox credentials to experience full Clinician and Administrator capabilities.
              </p>
            </div>

            {/* Credentials Card */}
            <div className="max-w-md mx-auto rounded-2xl border border-slate-800/60 bg-slate-950/50 p-6 text-left space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-800/50">
                <Terminal size={14} className="text-slate-500" />
                <span className="font-mono text-[9px] font-bold text-slate-400 uppercase tracking-widest">
                  SANDBOX CLEARANCE LOGS
                </span>
              </div>
              <div className="space-y-3.5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-1">
                  <span className="font-bold text-slate-300 flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                    Administrator Account
                  </span>
                  <span className="font-mono text-slate-400 bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800 text-[11px] self-start sm:self-auto">
                    admin / admin123
                  </span>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-1">
                  <span className="font-bold text-slate-300 flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-cyan-500" />
                    Intensivist / MD Account
                  </span>
                  <span className="font-mono text-slate-400 bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800 text-[11px] self-start sm:self-auto">
                    reyes / intensivist123
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <Link
                to="/login"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-extrabold px-8 py-4 text-xs transition duration-300 hover:shadow-lg hover:shadow-cyan-500/25 active:scale-[0.98]"
              >
                <Lock size={12} />
                Access Command Center
              </Link>
            </div>
          </div>
        </section>

      </main>

      {/* 6. FOOTER */}
      <footer className="w-full border-t border-slate-900/60 bg-slate-950/80 py-12 px-6 mt-20">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <Activity className="text-cyan-500" size={16} />
            <span className="font-mono text-[10px] font-black uppercase text-slate-400 tracking-wider">
              INTELLIICU CLINICAL SYSTEM • 2026
            </span>
          </div>

          <div className="text-center text-[10px] text-slate-500 font-medium space-y-1">
            <p>Licensed under the MIT License.</p>
            <p>Built for clinical portfolio demonstrations by <span className="text-slate-400 font-bold">Sumeet Sonar</span>.</p>
          </div>

          <div className="flex items-center gap-4">
            <a
              href="https://github.com/Sumeet2005/IntelliICU"
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
                className="inline-block"
              >
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
              </svg>
              GitHub Repo <ExternalLink size={10} />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
