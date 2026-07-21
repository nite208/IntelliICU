import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  ShieldAlert,
  Activity,
  Clock,
} from "lucide-react";

import { useClinicalAI } from "../../context/ClinicalAIContext";
import AlertDrawer from "./AlertDrawer";

const severityStyles = {
  CRITICAL: {
    icon: ShieldAlert,
    badge: "bg-red-100 text-red-700",
    border: "border-red-500",
  },
  HIGH: {
    icon: AlertTriangle,
    badge: "bg-orange-100 text-orange-700",
    border: "border-orange-500",
  },
  MEDIUM: {
    icon: Activity,
    badge: "bg-yellow-100 text-yellow-700",
    border: "border-yellow-500",
  },
};

export default function LiveAlerts() {

  const { activeAlerts, patientsList } = useClinicalAI();

  const alertsData = activeAlerts || [];
  const patientsData = patientsList || [];

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);

  function openDrawer(alert) {
    setSelectedAlert(alert);
    setDrawerOpen(true);
  }

  const selectedPatient =
    patientsData.find(
      (patient) =>
        patient.id === selectedAlert?.patient_id
    ) || null;

  return (
    <div className="clinical-card shadow-xl">
      <div className="border-b p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">
              Live ICU Alerts
            </h2>

            <p className="mt-1 text-slate-500">
              Real-time clinical events
            </p>
          </div>

          <div className="flex items-center gap-2 text-red-600">
            <div className="h-3 w-3 animate-pulse rounded-full bg-red-500"></div>
            Live
          </div>
        </div>
      </div>

      <div className="max-h-[520px] overflow-y-auto p-5">
        <AnimatePresence>
          {alertsData.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="py-12 text-center"
            >
              <ShieldAlert
                size={48}
                className="mx-auto text-emerald-500"
              />

              <h3 className="mt-4 text-xl font-bold">
                No Active Alerts
              </h3>

              <p className="mt-2 text-slate-500">
                All monitored patients are currently stable.
              </p>
            </motion.div>
          ) : (
            alertsData.map((alert, index) => {
              const config =
                severityStyles[alert.severity] ??
                severityStyles.MEDIUM;

              const Icon = config.icon;

              return (
                <motion.div
                onClick={() => openDrawer(alert)}
                  key={`${alert.patient_id}-${index}`}
                  initial={{
                    opacity: 0,
                    x: 20,
                  }}
                  animate={{
                    opacity: 1,
                    x: 0,
                  }}
                  exit={{
                    opacity: 0,
                  }}
                  className={`mb-4 cursor-pointer rounded-2xl border-l-4 bg-slate-50 p-5 transition hover:shadow-lg ${config.border}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex gap-4">
                      <div
                        className={`flex h-12 w-12 items-center justify-center rounded-xl ${config.badge}`}
                      >
                        <Icon size={22} />
                      </div>

                      <div>
                        <h3 className="font-bold">
                          {alert.patient_name}
                        </h3>

                        <p className="text-sm text-slate-500">
                          {alert.bed}
                        </p>

                        <p className="mt-2">
                          {alert.message}
                        </p>
                      </div>
                    </div>

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-bold ${config.badge}`}
                    >
                      {alert.severity}
                    </span>
                  </div>

                  <div className="mt-4 flex items-center gap-2 text-sm text-slate-500">
                    <Clock size={16} />
                    {alert.timestamp}
                  </div>
                  <AlertDrawer
                   open={drawerOpen}
                   alert={selectedAlert}
                   patient={selectedPatient}
                   onClose={() => setDrawerOpen(false)}
                    />
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}