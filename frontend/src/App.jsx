import { Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";

import Layout from "./layouts/Layout";

import AuthGuard from "./components/auth/AuthGuard";
import PermissionGuard from "./components/auth/PermissionGuard";

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

          <Route
            path="/dashboard"
            element={
              <PermissionGuard requiredPermission="Dashboard" showFallback>
                <Dashboard />
              </PermissionGuard>
            }
          />

          <Route
            path="/patients/:patientId"
            element={
              <PermissionGuard requiredPermission="Patients" showFallback>
                <PatientProfile />
              </PermissionGuard>
            }
          />

          <Route
            path="/monitoring"
            element={
              <PermissionGuard requiredPermission="Patients" showFallback>
                <Monitoring />
              </PermissionGuard>
            }
          />

          <Route
            path="/analytics"
            element={
              <PermissionGuard requiredPermission="Analytics" showFallback>
                <Analytics />
              </PermissionGuard>
            }
          />

          <Route
            path="/settings"
            element={
              <PermissionGuard requiredPermission="Settings" showFallback>
                <Settings />
              </PermissionGuard>
            }
          />

          <Route
            path="/users"
            element={
              <PermissionGuard requiredPermission="UserManagement" showFallback>
                <UserManagement />
              </PermissionGuard>
            }
          />

          <Route
            path="/profile"
            element={<UserProfile />}
          />

          <Route
            path="/telemetry"
            element={
              <PermissionGuard requiredPermission="Patients" showFallback>
                <Telemetry />
              </PermissionGuard>
            }
          />

          <Route
            path="/hospital-assistant"
            element={
              <PermissionGuard requiredPermission="ClinicalAI" showFallback>
                <HospitalAssistant />
              </PermissionGuard>
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