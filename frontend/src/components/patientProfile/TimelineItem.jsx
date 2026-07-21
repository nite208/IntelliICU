import { motion } from "framer-motion";
import {
  Pill,
  FlaskConical,
  AlertTriangle,
  Stethoscope,
  ClipboardCheck,
  Brain,
  User,
  Lightbulb,
} from "lucide-react";

export default function TimelineItem({ event, isLast, onOpenDetails }) {
  const getEventConfig = (type) => {
    const t = type?.toLowerCase() || "";
    if (t.includes("admission") || t.includes("clipboard")) {
      return { icon: ClipboardCheck, color: "bg-emerald-500 text-white" };
    }
    if (t.includes("medication") || t.includes("pill")) {
      return { icon: Pill, color: "bg-blue-500 text-white" };
    }
    if (t.includes("lab") || t.includes("laboratory") || t.includes("flask")) {
      return { icon: FlaskConical, color: "bg-orange-500 text-white" };
    }
    if (t.includes("alert") || t.includes("critical")) {
      return { icon: AlertTriangle, color: "bg-red-500 text-white" };
    }
    if (t.includes("ai") || t.includes("analysis") || t.includes("brain")) {
      return { icon: Brain, color: "bg-violet-500 text-white" };
    }
    if (t.includes("recommendation") || t.includes("lightbulb") || t.includes("priority")) {
      return { icon: Lightbulb, color: "bg-amber-500 text-white" };
    }
    if (t.includes("user") || t.includes("person") || t.includes("doctor")) {
      return { icon: User, color: "bg-slate-500 text-white" };
    }
    return { icon: Stethoscope, color: "bg-cyan-600 text-white" };
  };

  const config = getEventConfig(event.type);
  const Icon = config.icon;

  return (
    <motion.div
      whileHover={{ x: 3 }}
      className="flex gap-4 pb-6 last:pb-0"
    >
      <div className="flex flex-col items-center">
        <div className={`flex h-11 w-11 items-center justify-center rounded-xl shadow-md ${config.color}`}>
          <Icon size={20} />
        </div>
        {!isLast && (
          <div className="mt-2 h-full w-0.5 bg-slate-100"></div>
        )}
      </div>

      <div className="flex-1 rounded-xl border border-slate-100 bg-white p-4 shadow-sm hover:shadow-md transition">
        <div className="flex items-center justify-between gap-4">
          <div>
            <span className="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider">
              {event.type}
            </span>
            <h4 className="text-sm font-bold text-slate-800 mt-0.5">
              {event.title}
            </h4>
          </div>
          <span className="rounded-lg bg-slate-50 px-2 py-0.5 text-xs font-semibold text-slate-500">
            {event.time}
          </span>
        </div>

        <p className="text-xs text-slate-600 mt-2 leading-relaxed">
          {event.description}
        </p>

        <div className="mt-3 flex items-center justify-between border-t border-slate-50 pt-2.5">
          <span className="text-[10px] text-slate-400 font-medium">
            Actor: <strong className="text-slate-600">{event.actor}</strong>
          </span>
          <button
            onClick={() => onOpenDetails(event)}
            className="text-[10px] font-bold text-cyan-600 hover:text-cyan-700 transition"
          >
            View Details &rarr;
          </button>
        </div>
      </div>
    </motion.div>
  );
}
