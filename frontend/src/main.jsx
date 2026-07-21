import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";

import { AuthProvider } from "./context/AuthContext";
import { PatientProvider } from "./context/PatientContext";
import { AlertProvider } from "./context/AlertContext";
import { DashboardProvider } from "./context/DashboardContext";
import { TimelineProvider } from "./context/TimelineContext";
import { ClinicalAIProvider } from "./context/ClinicalAIContext";

import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <PatientProvider>
          <DashboardProvider>
            <AlertProvider>
              <TimelineProvider>
                <ClinicalAIProvider>
                  <App />
                </ClinicalAIProvider>
              </TimelineProvider>
            </AlertProvider>
          </DashboardProvider>
        </PatientProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);