import { Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";

import Layout from "./layouts/Layout";

import AuthGuard from "./components/auth/AuthGuard";
import RoleGuard from "./components/auth/RoleGuard";

// Lazy Loaded Pages
const Dashboard = lazy(() => import("./pages/DashboardV2"));
const PatientProfile = lazy(() => import("./pages/PatientProfile"));
const Monitoring = lazy(() => import("./pages/Monitoring"));
const Analytics = lazy(() => import("./pages/Analytics"));
const Settings = lazy(() => import("./pages/Settings"));
const Login = lazy(() => import("./pages/Login"));
const UserManagement = lazy(() => import("./pages/UserManagement"));
const UserProfile = lazy(() => import("./pages/UserProfile"));
const Telemetry = lazy(() => import("./pages/Telemetry"));
const HospitalAssistant = lazy(() => import("./pages/HospitalAssistant"));
const ClinicalCopilot = lazy(() => import("./pages/ClinicalCopilot"));
const Unauthorized = lazy(() => import("./pages/Unauthorized"));
const Landing = lazy(() => import("./pages/Landing"));

export default function App() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-slate-950">
          <div className="flex flex-col items-center gap-4">
            <div className="h-10 w-10 rounded-full border-4 border-cyan-500 border-t-transparent animate-spin"></div>

            <p className="text-cyan-400 font-semibold tracking-wide">
              Loading IntelliICU...
            </p>
          </div>
        </div>
      }
    >
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />

        <Route
          element={
            <AuthGuard>
              <Layout />
            </AuthGuard>
          }
        >
          {/* Dashboard (Admin, HospitalAdmin, ICUManager, Doctor, Nurse) */}
          <Route
            path="/dashboard"
            element={
              <RoleGuard allowedRoles={["superadmin", "hospitaladmin", "icumanager", "doctor", "nurse"]}>
                <Dashboard />
              </RoleGuard>
            }
          />

          {/* Patient Details Profile */}
          <Route
            path="/patients/:patientId"
            element={
              <RoleGuard allowedRoles={["superadmin", "hospitaladmin", "icumanager", "doctor", "nurse", "labtechnician", "viewer"]}>
                <PatientProfile />
              </RoleGuard>
            }
          />

          {/* Live Monitoring */}
          <Route
            path="/monitoring"
            element={
              <RoleGuard allowedRoles={["superadmin", "hospitaladmin", "icumanager", "doctor", "nurse", "viewer"]}>
                <Monitoring />
              </RoleGuard>
            }
          />

          {/* Telemetry Trends */}
          <Route
            path="/telemetry"
            element={
              <RoleGuard allowedRoles={["superadmin", "hospitaladmin", "icumanager", "doctor", "nurse", "labtechnician", "viewer"]}>
                <Telemetry />
              </RoleGuard>
            }
          />

          {/* Analytics */}
          <Route
            path="/analytics"
            element={
              <RoleGuard allowedRoles={["superadmin", "hospitaladmin", "icumanager"]}>
                <Analytics />
              </RoleGuard>
            }
          />

          {/* Hospital Assistant */}
          <Route
            path="/hospital-assistant"
            element={
              <RoleGuard allowedRoles={["superadmin", "hospitaladmin", "icumanager", "doctor", "nurse", "receptionist"]}>
                <HospitalAssistant />
              </RoleGuard>
            }
          />

          {/* User Directory */}
          <Route
            path="/users"
            element={
              <RoleGuard allowedRoles={["superadmin", "hospitaladmin"]}>
                <UserManagement />
              </RoleGuard>
            }
          />

          {/* Settings (AI Config) */}
          <Route
            path="/settings"
            element={
              <RoleGuard allowedRoles={["superadmin", "hospitaladmin"]}>
                <Settings />
              </RoleGuard>
            }
          />

          {/* My Profile */}
          <Route
            path="/profile"
            element={
              <RoleGuard allowedRoles={["superadmin", "hospitaladmin", "icumanager", "doctor", "nurse", "labtechnician", "receptionist", "viewer"]}>
                <UserProfile />
              </RoleGuard>
            }
          />

          <Route
            path="/unauthorized"
            element={<Unauthorized />}
          />
        </Route>
      </Routes>
    </Suspense>
  );
}