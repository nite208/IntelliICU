import {
  createContext,
  useContext,
  useMemo,
  useState,
  useCallback,
} from "react";

import { patientService } from "../services/patientService";

const PatientContext = createContext(null);

export function PatientProvider({ children }) {
  const [patientsList, setPatientsList] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [loadingPatients, setLoadingPatients] = useState(false);

  const loadPatients = useCallback(async () => {
    try {
      setLoadingPatients(true);

      const data = await patientService.getPatients();

      setPatientsList(data || []);
    } catch (err) {
      console.error("Failed to load patients:", err);
    } finally {
      setLoadingPatients(false);
    }
  }, []);

  const clearSelectedPatient = useCallback(() => {
    setSelectedPatient(null);
  }, []);

  const value = useMemo(
    () => ({
      patientsList,
      selectedPatient,
      loadingPatients,

      setPatientsList,
      setSelectedPatient,

      loadPatients,
      clearSelectedPatient,
    }),
    [
      patientsList,
      selectedPatient,
      loadingPatients,
      loadPatients,
      clearSelectedPatient,
    ]
  );

  return (
    <PatientContext.Provider value={value}>
      {children}
    </PatientContext.Provider>
  );
}

export function usePatient() {
  const context = useContext(PatientContext);

  if (!context) {
    throw new Error("usePatient must be used inside PatientProvider.");
  }

  return context;
}