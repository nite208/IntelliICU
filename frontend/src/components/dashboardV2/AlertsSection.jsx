import { useState } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  Clock3,
  ChevronRight,
  Siren,
  ShieldAlert,
  Activity,
} from "lucide-react";

import useWebSocket from "../../hooks/useWebSocket";
import AlertDrawer from "./AlertDrawer";

const severityStyles = {
  CRITICAL: {
    color: "bg-red-500",
    badge: "bg-red-100 text-red-700",
    icon: Siren,
  },
  HIGH: {
    color: "bg-orange-500",
    badge: "bg-orange-100 text-orange-700",
    icon: ShieldAlert,
  },
  MEDIUM: {
    color: "bg-yellow-500",
    badge: "bg-yellow-100 text-yellow-700",
    icon: Activity,
  },
  LOW: {
    color: "bg-emerald-500",
    badge: "bg-emerald-100 text-emerald-700",
    icon: AlertTriangle,
  },
};

export default function AlertsSection() {
  const { alertsData, patientsData } = useWebSocket();

  const [selectedAlert, setSelectedAlert] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  function openAlert(alert) {
    setSelectedAlert(alert);
    setDrawerOpen(true);
  }

  const selectedPatient =
    patientsData.find(
      (patient) => patient.id === selectedAlert?.patient_id
    ) || null;

  return (
    <>
      <section className="overflow-hidden rounded-[30px] border border-slate-200 bg-white shadow-xl">
        {/* Header */}

        <div className="flex items-center justify-between border-b p-7">
          <div>
            <h2 className="text-3xl font-black">
              Live Alert Center
            </h2>

            <p className="mt-2 text-slate-500">
              AI continuously monitors every ICU patient.
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-full bg-red-50 px-4 py-2">
            <span className="h-3 w-3 animate-pulse rounded-full bg-red-500" />

            <span className="font-semibold text-red-700">
              {alertsData.length} Active Alerts
            </span>
          </div>
        </div>

        {/* Timeline */}

        <div className="max-h-[650px] overflow-y-auto">
          {alertsData.length === 0 && (
            <div className="p-10 text-center text-slate-500">
              No active clinical alerts.
            </div>
          )}

          {alertsData.map((alert, index) => {
            const style =
              severityStyles[
                alert.severity?.toUpperCase()
              ] || severityStyles.LOW;

            const Icon = style.icon;

            return (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{
                  delay: index * 0.05,
                }}
                whileHover={{
                  x: 6,
                }}
                onClick={() => openAlert(alert)}
                className="group cursor-pointer border-b p-6 transition hover:bg-slate-50 last:border-none"
              >
                <div className="flex gap-5">
                  {/* Timeline */}

                  <div className="flex flex-col items-center">
                    <div
                      className={`flex h-14 w-14 items-center justify-center rounded-2xl ${style.color}`}
                    >
                      <Icon
                        className="text-white"
                        size={24}
                      />
                    </div>

                    {index !== alertsData.length - 1 && (
                      <div className="mt-2 h-full w-1 rounded-full bg-slate-200" />
                    )}
                  </div>

                  {/* Content */}

                  <div className="flex-1">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <h3 className="text-xl font-bold">
                          {alert.patient_name}
                        </h3>

                        <div className="mt-2 flex items-center gap-2 text-sm text-slate-500">
                          <Clock3 size={15} />
                          {alert.time}
                        </div>
                      </div>

                      <span
                        className={`rounded-full px-4 py-2 text-sm font-bold ${style.badge}`}
                      >
                        {alert.severity}
                      </span>
                    </div>

                    <p className="mt-5 leading-7 text-slate-600">
                      {alert.message}
                    </p>

                    <button className="mt-5 flex items-center gap-2 font-semibold text-cyan-600 transition group-hover:translate-x-1">
                      View Clinical Details

                      <ChevronRight size={18} />
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      <AlertDrawer
        open={drawerOpen}
        alert={selectedAlert}
        patient={selectedPatient}
        onClose={() => setDrawerOpen(false)}
      />
    </>
  );
}