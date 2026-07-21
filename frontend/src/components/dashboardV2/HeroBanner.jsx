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
      className="relative overflow-hidden rounded-[32px] bg-gradient-to-br from-slate-900 via-[#0B2942] to-cyan-900 py-6 px-8 text-white shadow-2xl"
    >
      {/* Background Glow */}
      <div className="absolute -top-32 -right-20 h-80 w-80 rounded-full bg-cyan-400/20 blur-3xl"></div>
      <div className="absolute -bottom-32 -left-20 h-72 w-72 rounded-full bg-blue-500/20 blur-3xl"></div>

      <div className="relative grid grid-cols-12 gap-8">

        {/* Left Side */}
        <div className="col-span-12 lg:col-span-7">

          <div className="inline-flex items-center gap-2 rounded-full bg-cyan-500/20 border border-cyan-400/30 px-4 py-2 text-sm backdrop-blur">

            <BrainCircuit size={18} />

            {label}

          </div>

          <h1 className="mt-4 text-5xl font-black leading-tight">

            {title}

            <span className="block text-cyan-300">

              {coloredTitle}

            </span>

          </h1>

          <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-300">

            {subtitle}

          </p>

        </div>

        {/* Right Side - Clinical Summary Box */}
        <div className="col-span-12 lg:col-span-5 flex flex-col justify-center">
          <div className="rounded-2xl border border-cyan-400/20 bg-black/20 p-6 backdrop-blur">
            <div className="flex items-center gap-3">
              <Sparkles className="text-cyan-300 animate-pulse" />
              <h3 className="font-semibold text-base">
                {cardTitle}
              </h3>
            </div>

            <p className="mt-4 text-sm leading-7 text-slate-300">
              {cardBody}
            </p>
            
            <div className="mt-6 border-t border-white/10 pt-4 flex justify-between text-xs text-slate-400">
              <span>{footerLeft}</span>
              <span className="text-cyan-300 font-bold">{footerRight}</span>
            </div>
          </div>
        </div>

      </div>

    </motion.section>
  );
}