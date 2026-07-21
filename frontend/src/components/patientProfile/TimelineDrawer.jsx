import { motion, AnimatePresence } from "framer-motion";
import { X, Clock, User, Clipboard, CheckCircle } from "lucide-react";

export default function TimelineDrawer({ open, event, onClose }) {
  if (!event) return null;

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.4 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black"
          />

          {/* Slide-over Drawer */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 z-50 h-full w-[400px] bg-white shadow-2xl flex flex-col p-6"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <span className="text-[10px] font-black uppercase bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                  {event.type} Log Details
                </span>
                <h3 className="text-lg font-bold text-slate-800 mt-2">{event.title}</h3>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-slate-50 rounded-xl transition text-slate-400 hover:text-slate-600"
              >
                <X size={18} />
              </button>
            </div>

            {/* Content Body */}
            <div className="flex-1 overflow-y-auto mt-6 space-y-6">
              {/* Event Metadata Card */}
              <div className="space-y-4">
                <div>
                  <label className="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider">
                    Event Description
                  </label>
                  <p className="text-sm text-slate-700 leading-relaxed mt-1">
                    {event.description}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">Time</span>
                    <div className="flex items-center gap-1.5 mt-1 font-bold text-xs text-slate-700">
                      <Clock size={12} className="text-slate-500" />
                      {event.time}
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">Actor</span>
                    <div className="flex items-center gap-1.5 mt-1 font-bold text-xs text-slate-700">
                      <User size={12} className="text-slate-500" />
                      {event.actor}
                    </div>
                  </div>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 font-semibold block">Timestamp</span>
                  <span className="text-xs font-semibold text-slate-600">{event.timestamp}</span>
                </div>
              </div>

              {/* Event Structured Metadata Fields */}
              {event.metadata && Object.keys(event.metadata).length > 0 && (
                <div className="border-t border-slate-100 pt-6">
                  <label className="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider flex items-center gap-1.5">
                    <Clipboard size={12} />
                    Structured Payload (Metadata)
                  </label>
                  <div className="mt-3 bg-slate-900 text-slate-300 p-4 rounded-xl text-xs font-mono overflow-x-auto max-h-[220px]">
                    <pre>{JSON.stringify(event.metadata, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="border-t border-slate-100 pt-4 mt-auto">
              <button
                onClick={onClose}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white py-3 text-xs font-bold transition shadow-md"
              >
                <CheckCircle size={14} />
                Done
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
