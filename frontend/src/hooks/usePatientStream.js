import { useEffect, useMemo, useState } from "react";
import websocketService from "../services/websocketService";

export default function usePatientStream(patientId) {
    const [connected, setConnected] = useState(false);
    const [currentPatient, setCurrentPatient] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);

    const channel = useMemo(() => {
        return patientId ? `patient_${patientId}` : "patient";
    }, [patientId]);

    useEffect(() => {
        if (!patientId) return;

        const handleConnected = () => {
            setConnected(true);
        };

        const handleDisconnected = () => {
            setConnected(false);
        };

        const handlePatientUpdate = (message) => {
            if (!message?.data) return;

            setCurrentPatient(message.data);
            setLastUpdated(message.timestamp ?? new Date().toLocaleTimeString());
        };

        setConnected(websocketService.isConnected(channel));

        websocketService.on(
            channel,
            "connected",
            handleConnected
        );

        websocketService.on(
            channel,
            "disconnected",
            handleDisconnected
        );

        websocketService.on(
            channel,
            "patient_update",
            handlePatientUpdate
        );

        return () => {
            websocketService.off(
                channel,
                "connected",
                handleConnected
            );

            websocketService.off(
                channel,
                "disconnected",
                handleDisconnected
            );

            websocketService.off(
                channel,
                "patient_update",
                handlePatientUpdate
            );
        };
    }, [patientId, channel]);

    return {
        connected,

        currentPatient,

        latestVitals: currentPatient
            ? {
                  heart_rate: currentPatient.heart_rate,
                  spo2: currentPatient.spo2,
                  temperature: currentPatient.temperature,
                  respiratory_rate: currentPatient.respiratory_rate,
                  systolic_bp: currentPatient.systolic_bp,
                  diastolic_bp: currentPatient.diastolic_bp,
                  lactate: currentPatient.lactate,
              }
            : null,

        latestRisk: currentPatient
            ? {
                  risk_score: currentPatient.risk_score,
                  risk_level: currentPatient.risk_level,
                  status: currentPatient.status,
              }
            : null,

        lastUpdated,
    };
}