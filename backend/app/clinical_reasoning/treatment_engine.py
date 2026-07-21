"""
app/clinical_reasoning/treatment_engine.py

Treatment Pathway Generator for ICU patients (Phase 13.1).
Synthesizes customized treatment plans based on patient telemetry,
the highest-ranked differential diagnosis, and evidence-based clinical guidelines.
"""

from typing import Dict, Any, List

class TreatmentEngine:
    """
    Expert clinical rules engine generating structured ICU treatment plans.
    """

    @staticmethod
    def generate(
        differential_diagnosis: List[Dict[str, Any]],
        context: Dict[str, Any],
        vitals: Dict[str, Any],
        labs: Dict[str, Any],
        retrieved_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Processes patient metrics and differential diagnoses to compile a structured treatment plan.

        Returns a dictionary:
        {
            "priority": str ("CRITICAL" | "HIGH" | "MEDIUM" | "LOW"),
            "immediate_actions": list[str],
            "medications": list[str],
            "monitoring": list[str],
            "labs_to_repeat": list[str],
            "consults": list[str],
            "expected_goals": list[str]
        }
        """
        # Default fallback pathway
        pathway = {
            "priority": "MEDIUM",
            "immediate_actions": ["Perform comprehensive clinical re-assessment.", "Verify peripheral and central intravenous access lines."],
            "medications": ["Continue current home and maintenance medications.", "Re-evaluate medication list for active drug-drug interactions."],
            "monitoring": ["Continuous telemetry monitoring (ECG, pulse oximetry, non-invasive blood pressure).", "Assess fluid balance twice daily."],
            "labs_to_repeat": ["Serum electrolytes and renal panel in 12-24 hours."],
            "consults": ["ICU Attending Physician review."],
            "expected_goals": ["Maintain hemodynamic and ventilatory stability.", "Maintain vital signs within normal physiological ranges."]
        }

        if not differential_diagnosis:
            return pathway

        # Find the highest ranked diagnosis with significant likelihood
        primary_diag_item = differential_diagnosis[0]
        primary_diag = primary_diag_item.get("diagnosis", "")
        likelihood = primary_diag_item.get("likelihood", 0.0)

        # Retrieve any sources matching the primary category for evidence-based references
        matching_guidelines = [
            s.get("title", "") for s in retrieved_sources
            if s.get("category", "").lower() in [primary_diag.lower(), "sepsis" if "septic" in primary_diag.lower() else ""]
        ]
        guideline_ref = f" (Ref: {matching_guidelines[0]})" if matching_guidelines else ""

        # Clinically match pathways based on top differential diagnosis
        if "septic shock" in primary_diag.lower() and likelihood >= 0.40:
            pathway["priority"] = "CRITICAL"
            pathway["immediate_actions"] = [
                f"Administer rapid IV fluid bolus of 30 mL/kg balanced crystalloid within 3 hours of shock onset{guideline_ref}.",
                "Draw at least 2 sets of blood cultures (one peripheral, one from each central line) BEFORE antimicrobial administration.",
                "Administer broad-spectrum empiric IV antibiotics within 1 hour of septic shock recognition.",
                "Establish central venous access and arterial line for continuous vasoactive titration."
            ]
            pathway["medications"] = [
                "Norepinephrine IV continuous infusion (first-line) to maintain MAP >= 65 mmHg.",
                "Consider adding Vasopressin continuous infusion at a fixed rate of 0.03 units/min as adjunct to reduce norepinephrine requirement.",
                "Empiric antimicrobial coverage: Piperacillin/Tazobactam 4.5 g IV q6h (or Meropenem 1 g IV q8h) + Vancomycin based on renal function.",
                "Hydrocortisone 200 mg/day IV continuous infusion if blood pressure remains refractory to fluids and vasopressors."
            ]
            pathway["monitoring"] = [
                "Continuous arterial line MAP monitoring (target >= 65 mmHg).",
                "Strict hourly urine output monitoring via indwelling catheter (target >= 0.5 mL/kg/h).",
                "Continuous pulse oximetry and ECG.",
                "Assess for fluid responsiveness dynamically (pulse pressure variation, stroke volume variation, passive leg raise)."
            ]
            pathway["labs_to_repeat"] = [
                "Repeat serum lactate every 2 to 4 hours until lactate < 2.0 mmol/L and normal clearance trend established.",
                "Daily Complete Blood Count (CBC) and Basic Metabolic Panel (BMP).",
                "Arterial Blood Gas (ABG) every 6-8 hours while on mechanical ventilation or vasopressors."
            ]
            pathway["consults"] = [
                "Infectious Diseases (ID) consult for antibiotic stewardship.",
                "Critical Care Attending Physician.",
                "Nephrology if CRRT/RRT needed."
            ]
            pathway["expected_goals"] = [
                "Maintain Mean Arterial Pressure (MAP) >= 65 mmHg.",
                "Urine output >= 0.5 mL/kg/hour.",
                "Lactate clearance of >= 10% within 2-4 hours of initiation.",
                "Stabilization of systemic perfusion and heart rate (< 100 bpm)."
            ]

        elif "hypovolemic shock" in primary_diag.lower() and likelihood >= 0.40:
            pathway["priority"] = "CRITICAL"
            pathway["immediate_actions"] = [
                "Establish two large-bore peripheral IV lines (14G or 16G) or central venous access.",
                "Initiate aggressive volume resuscitation using balanced crystalloids (e.g. Lactated Ringer's).",
                "Prepare for blood transfusion (activate massive transfusion protocol if active severe hemorrhage suspected).",
                "Identify and control the source of fluid/blood loss."
            ]
            pathway["medications"] = [
                "Balanced crystalloids IV boluses.",
                "Uncrossed Type O negative packed red blood cells (PRBCs) in emergency, or type-specific blood products.",
                "Anticipate tranexamic acid (TXA) if within 3 hours of trauma/post-partum hemorrhage.",
                "Avoid vasoactive agents until intravascular volume is largely restored."
            ]
            pathway["monitoring"] = [
                "Frequent non-invasive or continuous arterial blood pressure.",
                "Assess fluid responsiveness dynamically (passive leg raise, stroke volume variation).",
                "Daily weight and cumulative fluid balance metrics."
            ]
            pathway["labs_to_repeat"] = [
                "Hemoglobin/Hematocrit every 2 to 4 hours during active resuscitation.",
                "Coagulation panel (PT/INR, PTT, Fibrinogen) every 4 hours.",
                "Electrolyte monitoring ( BMP ) every 12 hours."
            ]
            pathway["consults"] = [
                "Trauma Surgery / General Surgery / Interventional Radiology for hemorrhage control.",
                "Blood Bank notification."
            ]
            pathway["expected_goals"] = [
                "Hemodynamic stabilization (MAP >= 65 mmHg, HR < 100 bpm).",
                "Target Hemoglobin 7.0 - 9.0 g/dL (unless active cardiovascular disease/bleeding).",
                "Reversal of oliguria (urine output > 0.5 mL/kg/h)."
            ]

        elif "cardiogenic shock" in primary_diag.lower() and likelihood >= 0.40:
            pathway["priority"] = "CRITICAL"
            pathway["immediate_actions"] = [
                "Order emergency 12-lead ECG and bedside transthoracic echocardiogram (TTE).",
                "Optimize oxygenation, consider non-invasive ventilation (NIV) to reduce respiratory work and cardiac afterload.",
                "Avoid large fluid boluses unless low filling pressures confirmed."
            ]
            pathway["medications"] = [
                "Dobutamine IV continuous infusion (inotrope) start at 2.5-5.0 mcg/kg/min; titrate to cardiac index goals.",
                "Norepinephrine IV continuous infusion as adjunct if severe hypotension (SBP < 80-90 mmHg) is present to protect coronary perfusion.",
                "Aspirin, Heparin, and antiplatelets if acute myocardial infarction suspected.",
                "Loop diuretics (Furosemide) IV if pulmonary congestion present and hemodynamics permit."
            ]
            pathway["monitoring"] = [
                "Continuous cardiac output/cardiac index monitoring (pulmonary artery catheter or arterial wave-form analysis).",
                "Continuous ECG for arrhythmias.",
                "Arterial line MAP and central venous pressure (CVP)."
            ]
            pathway["labs_to_repeat"] = [
                "Serial Cardiac Troponins every 6 hours.",
                "BNP / NT-proBNP daily.",
                "Daily BMP (renal panel) and arterial blood gases."
            ]
            pathway["consults"] = [
                "Interventional Cardiology for emergent cardiac catheterization.",
                "Cardiothoracic Surgery if mechanical circulatory support (ECMO, Impella, IABP) is indicated."
            ]
            pathway["expected_goals"] = [
                "Maintain Cardiac Index > 2.2 L/min/m².",
                "Mean Arterial Pressure (MAP) >= 65 mmHg.",
                "Resolution of pulmonary congestion and tissue hypoperfusion."
            ]

        elif "aki" in primary_diag.lower() and likelihood >= 0.40:
            pathway["priority"] = "HIGH"
            pathway["immediate_actions"] = [
                f"Discontinue all nephrotoxic medications (NSAIDs, aminoglycosides, ACE inhibitors/ARBs){guideline_ref}.",
                "Assess volume status; avoid fluid depletion and fluid overload.",
                "Re-evaluate all drug dosages for current renal clearance."
            ]
            pathway["medications"] = [
                "Adjust doses of active renal-clearance drugs (Meropenem, Piperacillin/Tazobactam, Vancomycin).",
                "Initiate loop diuretic (Furosemide) 20-40 mg IV bolus only if fluid overload is present (not to treat AKI).",
                "Electrolyte management: administer sodium polystyrene sulfonate or insulin/dextrose for hyperkalemia."
            ]
            pathway["monitoring"] = [
                "Strict hourly urine output monitoring.",
                "Daily weights.",
                "Serial serum potassium and bicarbonate levels."
            ]
            pathway["labs_to_repeat"] = [
                "Serum creatinine and electrolytes (BMP) at least every 12 to 24 hours.",
                "Serum drug levels (e.g. Vancomycin troughs or AUC/MIC) daily."
            ]
            pathway["consults"] = [
                "Nephrology consult for renal replacement therapy (RRT) planning if refractory metabolic acidosis, hyperkalemia, or fluid overload develop."
            ]
            pathway["expected_goals"] = [
                "Stabilization of serum creatinine.",
                "Maintain urine output >= 0.5 mL/kg/h.",
                "Avoidance of metabolic acidosis (pH >= 7.2) and severe hyperkalemia (K+ < 5.5 mmol/L)."
            ]

        elif "ards" in primary_diag.lower() and likelihood >= 0.40:
            pathway["priority"] = "CRITICAL"
            pathway["immediate_actions"] = [
                "Ensure lung-protective mechanical ventilation protocol: low tidal volumes (6 mL/kg predicted body weight).",
                "Limit plateau pressures to < 30 cmH2O.",
                "Set PEEP to maximize alveolar recruitment while avoiding overdistension.",
                "Consider early prone positioning (16 hours/day) in severe ARDS (PF ratio < 150)."
            ]
            pathway["medications"] = [
                "Cisatracurium IV infusion (neuromuscular blockade) if ventilator dyssynchrony.",
                "Consider corticosteroid therapy (Dexamethasone 6 mg daily or Methylprednisolone).",
                "Sedatives and analgesics titrated to target RASS of -3 to -4 during neuromuscular blockade."
            ]
            pathway["monitoring"] = [
                "Continuous ventilator parameters: tidal volume, plateau pressure, driving pressure (< 15 cmH2O), and PEEP.",
                "Continuous pulse oximetry and capnography.",
                "Serial arterial blood gases (ABG)."
            ]
            pathway["labs_to_repeat"] = [
                "ABG every 4-6 hours or 1 hour following ventilator adjustment.",
                "BMP daily."
            ]
            pathway["consults"] = [
                "Pulmonology and Respiratory Therapy.",
                "Physical Therapy for early mobilization if stable."
            ]
            pathway["expected_goals"] = [
                "Maintain SpO2 88% - 95% (or PaO2 55 - 80 mmHg).",
                "Plateau pressure < 30 cmH2O, driving pressure < 15 cmH2O.",
                "Arterial pH 7.30 - 7.45 (permissible hypercapnia)."
            ]

        elif "acute respiratory failure" in primary_diag.lower() and likelihood >= 0.40:
            pathway["priority"] = "HIGH"
            pathway["immediate_actions"] = [
                "Administer titrated supplemental oxygen via nasal cannula, simple mask, or non-rebreather.",
                "Initiate high-flow nasal oxygen (HFNO) or non-invasive ventilation (NIV/BiPAP) for hypoxic/hypercapnic failure.",
                "Ensure emergency airway equipment (intubation kit) is bedside.",
                "Encourage deep breathing, coughing, and incentive spirometry."
            ]
            pathway["medications"] = [
                "Short-acting beta-agonists (Albuterol) and anticholinergics (Ipratropium) nebulized q4-6h if wheezing.",
                "Systemic corticosteroids (Prednisone 40 mg PO or Methylprednisolone 40 mg IV) if COPD/asthma exacerbation.",
                "Empiric antibiotics if acute bacterial pneumonia suspected."
            ]
            pathway["monitoring"] = [
                "Continuous pulse oximetry (target 94-98% for general, 88-92% for COPD).",
                "Respiratory rate, accessory muscle use, work of breathing, and mental status.",
                "Telemetry ECG for tachyarrhythmias."
            ]
            pathway["labs_to_repeat"] = [
                "ABG within 1-2 hours of initiating NIV/HFNO, then as clinically indicated.",
                "Daily electrolytes and renal panel."
            ]
            pathway["consults"] = [
                "Respiratory Therapy.",
                "Pulmonology."
            ]
            pathway["expected_goals"] = [
                "Resolution of severe respiratory distress.",
                "Maintain target SpO2 (94-98% or 88-92% for COPD).",
                "Avoidance of endotracheal intubation.",
                "Stabilization of arterial pH (> 7.35) and pCO2."
            ]

        return pathway
