import { motion } from "framer-motion";
import {
  BrainCircuit,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function HeroBanner() {
  const { user } = useAuth();
  const role = user?.role?.toLowerCase();

  let label = "AI Clinical Decision Support System";
  let title = "IntelliICU";
  let coloredTitle = "Clinical Command Center";
  let subtitle = "Monitor ICU patients in real time, predict clinical deterioration, receive explainable AI recommendations, and support evidence-based medical decisions.";
  let cardTitle = "Real-Time Clinical Status";
  let cardBody = "The AI Decision Support Engine has identified 3 high-risk patients with elevated probability of sepsis. Broad-spectrum protocol checklists are currently outstanding on beds MICU-04 and MICU-07.";
  let footerLeft = "Next scheduled AI analysis: Under 2 mins";
  let footerRight = "100% telemetry online";

  if (role === "hospitaladmin" || role === "superadmin") {
    label = "AI Clinical Decision Support System | Administrative Portal";
    title = "System Control";
    coloredTitle = "IntelliICU Control Center";
    subtitle = "Manage administrative users, update system settings, verify clinical limits and configuration thresholds, and audit system performance metrics.";
    cardTitle = "System Control Summary";
    cardBody = "All REST endpoints and WebSocket relays are online. System health check completed successfully. No critical database failures reported.";
    footerLeft = "System uptime: 99.98%";
    footerRight = "All services operational";
  } else if (role === "nurse") {
    label = "AI Clinical Decision Support System | Nursing Workspace";
    title = "Nursing Suite";
    coloredTitle = "Care & Monitoring";
    subtitle = "View your assigned patient charts, track active nursing tasks, track live alert logs, and receive nursing care assistant recommendations.";
    cardTitle = "Active Care Summary";
    cardBody = "Currently monitoring active patient beds. Next vitals checks are scheduled. 2 alerts require active verification on bed MICU-04.";
    footerLeft = "Nursing shift: 12-hour AM/PM";
    footerRight = "Care protocols online";
  } else if (role === "icumanager") {
    label = "AI Clinical Decision Support System | Operations Portal";
    title = "ICU Operations";
    coloredTitle = "Operations Command";
    subtitle = "Review bed occupancy, track admissions/discharges, evaluate alert response times, and analyze clinical and operational efficiency.";
    cardTitle = "Operational Status";
    cardBody = "Bed occupancy is currently at 80% (8/10 beds filled). Average alert response time is 45 seconds. Analytics report is ready for export.";
    footerLeft = "Census: 8 active patients";
    footerRight = "80% Bed utilization";
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 25 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative overflow-hidden rounded-[28px] bg-gradient-to-r from-[#070b14] via-[#091220] to-[#0c192e] py-7 px-8 text-white shadow-xl border border-slate-800/80"
    >
      {/* Subtle Background Glows */}
      <div className="absolute -top-32 -right-20 h-80 w-80 rounded-full bg-amber-500/10 blur-3xl"></div>
      <div className="absolute -bottom-32 -left-20 h-72 w-72 rounded-full bg-indigo-500/10 blur-3xl"></div>

      <div className="relative grid grid-cols-12 gap-8 items-center">

        {/* Left Side */}
        <div className="col-span-12 lg:col-span-7">

          <div className="inline-flex items-center gap-2 rounded-full bg-amber-500/10 border border-amber-500/20 px-4 py-1.5 text-xs font-semibold text-amber-400 backdrop-blur">

            <BrainCircuit size={16} className="text-amber-400" />

            {label}

          </div>

          <h1 className="mt-4 text-4xl font-extrabold tracking-tight leading-tight text-white">

            {title}{" "}

            <span className="block bg-gradient-to-r from-amber-300 via-amber-400 to-amber-500 bg-clip-text text-transparent">

              {coloredTitle}

            </span>

          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-300">

            {subtitle}

          </p>

        </div>

        {/* Right Side - Clinical Summary Box */}
        <div className="col-span-12 lg:col-span-5 flex flex-col justify-center">
          <div className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-6 backdrop-blur shadow-inner">
            <div className="flex items-center gap-3">
              <Sparkles className="text-amber-400 animate-pulse" size={18} />
              <h3 className="font-bold text-sm text-slate-100 uppercase tracking-wider">
                {cardTitle}
              </h3>
            </div>

            <p className="mt-3 text-xs leading-relaxed text-slate-300">
              {cardBody}
            </p>
            
            <div className="mt-5 border-t border-slate-800 pt-3 flex justify-between text-[11px] text-slate-400">
              <span>{footerLeft}</span>
              <span className="text-amber-400 font-bold">{footerRight}</span>
            </div>
          </div>
        </div>

      </div>

    </motion.section>
  );
}