"""
app/clinical_reasoning/laboratory_engine.py

Laboratory Interpretation Engine for IntelliICU (Phase 13.4).
Analyzes patient lab parameters across CBC, Renal, Electrolytes, Liver,
Inflammatory, Coagulation, and ABG panels, flagging abnormalities and generating clinical commentary.
"""

from typing import Dict, Any, List

class LaboratoryEngine:
    """
    Analyzes lab values, tags abnormalities, determines severities, and recommends actions.
    """

    @staticmethod
    def generate(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes laboratory values from the patient context.
        
        Returns:
        {
          "laboratory_interpretation": [
              {
                "name": str,
                "value": float/int/str,
                "normal_range": str,
                "status": str ("ELEVATED" | "LOW"),
                "severity": str ("NORMAL" | "MILD" | "MODERATE" | "SEVERE" | "CRITICAL"),
                "interpretation": str,
                "possible_causes": list[str],
                "clinical_significance": str,
                "recommended_actions": list[str]
              }
          ],
          "summary": {
              "abnormal_count": int,
              "critical_count": int,
              "highest_priority": str ("NORMAL" | "MILD" | "MODERATE" | "SEVERE" | "CRITICAL")
          }
        }
        """
        # Safely extract labs, vitals, and admission info from context
        labs = context.get("labs", {}) or {}
        vitals = context.get("vitals", {}) or {}
        
        # Merge keys so that case-insensitive matches work
        merged_labs = {k.lower(): v for k, v in labs.items()}
        merged_vitals = {k.lower(): v for k, v in vitals.items()}

        interpretations = []

        # Helper to define standard definitions
        # Format: (key, display_name, normal_range_str, low_limit, high_limit, logic_fn)
        # logic_fn returns (is_abnormal, status, severity, interpretation, causes_list, significance, actions_list)
        
        def check_val(val_name: str):
            # Check lab keys
            val = merged_labs.get(val_name.lower())
            # Fallback to vitals if urine output or similar
            if val is None:
                val = merged_vitals.get(val_name.lower())
            return val

        # ----------------------------------------------------
        # Define Interpretation Logic for each lab
        # ----------------------------------------------------
        
        # 1. Hemoglobin
        hb = check_val("hemoglobin") or check_val("hb")
        if hb is not None:
            try:
                val = float(hb)
                if val < 12.0:
                    status = "LOW"
                    if val < 7.0:
                        sev = "CRITICAL"
                        interp = "Critical anemia risking systemic tissue hypoxia."
                        causes = ["Active acute hemorrhage", "Severe chronic anemia", "Hemolysis", "Bone marrow suppression"]
                        sig = "Critical risk of tissue hypoxia, myocardial ischemia, and high-output cardiovascular failure."
                        acts = ["Notify attending physician immediately.", "Prepare for urgent packed red blood cell (PRBC) transfusion.", "Draw type and cross-match.", "Identify active bleeding source."]
                    elif val < 8.0:
                        sev = "SEVERE"
                        interp = "Severe anemia."
                        causes = ["Hemorrhage", "Hemolysis", "Renal failure (reduced erythropoietin)"]
                        sig = "Significant risk of tissue perfusion failure, especially in patients with coronary artery disease."
                        acts = ["Monitor hemodynamics closely.", "Consider transfusion depending on cardiac status/symptoms."]
                    elif val < 10.0:
                        sev = "MODERATE"
                        interp = "Moderate anemia."
                        causes = ["Anemia of chronic disease", "Nutritional deficiencies", "Occult blood loss"]
                        sig = "Decreased oxygen carrying capacity; generally tolerated if hemodynamics are stable."
                        acts = ["Monitor CBC daily.", "Investigate occult sources of blood loss (e.g., GI tract)."]
                    else:
                        sev = "MILD"
                        interp = "Mild anemia."
                        causes = ["Hemodilution", "Mild chronic anemia"]
                        sig = "Minimal immediate risk; represents baseline physiologic status in many ICU patients."
                        acts = ["Monitor standard laboratory cycles."]
                    
                    interpretations.append({
                        "name": "Hemoglobin", "value": val, "normal_range": "12.0 - 17.5 g/dL",
                        "status": status, "severity": sev, "interpretation": interp,
                        "possible_causes": causes, "clinical_significance": sig, "recommended_actions": acts
                    })
                elif val > 17.5:
                    interpretations.append({
                        "name": "Hemoglobin", "value": val, "normal_range": "12.0 - 17.5 g/dL",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Mild polycythemia.",
                        "possible_causes": ["Dehydration / hemoconcentration", "Chronic hypoxia (COPD)", "Erythropoietin-producing tumors"],
                        "clinical_significance": "Increases blood viscosity, slightly raising thrombotic risk.",
                        "recommended_actions": ["Assess hydration status.", "Monitor perfusion and systemic hydration metrics."]
                    })
            except ValueError:
                pass

        # 2. Hematocrit
        hct = check_val("hematocrit") or check_val("hct")
        if hct is not None:
            try:
                val = float(hct)
                if val < 36.0:
                    status = "LOW"
                    sev = "CRITICAL" if val < 21.0 else ("SEVERE" if val < 24.0 else ("MODERATE" if val < 30.0 else "MILD"))
                    interpretations.append({
                        "name": "Hematocrit", "value": val, "normal_range": "36 - 50%",
                        "status": status, "severity": sev, "interpretation": "Decreased proportion of red blood cells in blood.",
                        "possible_causes": ["Blood loss", "Hemodilution", "Anemia"],
                        "clinical_significance": "Directly correlates with hemoglobin levels and oxygen delivery capacity.",
                        "recommended_actions": ["Correlate with hemoglobin levels.", "Evaluate clinical hydration and hemorrhage status."]
                    })
                elif val > 50.0:
                    interpretations.append({
                        "name": "Hematocrit", "value": val, "normal_range": "36 - 50%",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Elevated hematocrit.",
                        "possible_causes": ["Severe dehydration", "Polycythemia vera"],
                        "clinical_significance": "Indicates hemoconcentration or excess RBC production.",
                        "recommended_actions": ["Evaluate hydration status.", "Consider volume replacement."]
                    })
            except ValueError:
                pass

        # 3. WBC
        wbc = check_val("wbc")
        if wbc is not None:
            try:
                val = float(wbc)
                if val > 11.0:
                    status = "ELEVATED"
                    if val > 30.0:
                        sev = "CRITICAL"
                        interp = "Critical leukocytosis."
                        causes = ["Severe systemic infection / septic shock", "Leukemoid reaction", "Hematologic malignancy"]
                        sig = "Highly suggestive of extreme inflammatory response or severe underlying infection."
                        acts = ["Check urgent blood and sputum cultures.", "Evaluate for source control of infection.", "Initiate or broaden empiric antibiotics.", "Check peripheral smear."]
                    elif val > 20.0:
                        sev = "SEVERE"
                        interp = "Severe leukocytosis."
                        causes = ["Active systemic infection", "Severe tissue necrosis", "High-dose corticosteroid therapy"]
                        sig = "Significant inflammatory response, likely infectious."
                        acts = ["Evaluate infectious sources.", "Correlate with temperature, heart rate, and lactate."]
                    elif val > 15.0:
                        sev = "MODERATE"
                        interp = "Moderate leukocytosis."
                        causes = ["Infection", "Post-surgical stress", "Steroid use"]
                        sig = "Reflects acute physiological stress or localized infection."
                        acts = ["Monitor WBC trend daily.", "Correlate with localized physical findings."]
                    else:
                        sev = "MILD"
                        interp = "Mild leukocytosis."
                        causes = ["Mild stress response", "Steroids", "Early infection"]
                        sig = "Non-specific elevation common in hospitalized patients."
                        acts = ["Monitor standard laboratory cycles."]

                    interpretations.append({
                        "name": "WBC", "value": val, "normal_range": "4.0 - 11.0 K/uL",
                        "status": status, "severity": sev, "interpretation": interp,
                        "possible_causes": causes, "clinical_significance": sig, "recommended_actions": acts
                    })
                elif val < 4.0:
                    status = "LOW"
                    sev = "CRITICAL" if val < 1.0 else ("SEVERE" if val < 2.0 else "MODERATE")
                    interpretations.append({
                        "name": "WBC", "value": val, "normal_range": "4.0 - 11.0 K/uL",
                        "status": status, "severity": sev, "interpretation": "Leukopenia, suggesting high vulnerability to infection.",
                        "possible_causes": ["Sepsis (overwhelming infection)", "Bone marrow suppression", "Chemotherapy / immunosuppression"],
                        "clinical_significance": "Severely compromised immune defense; high risk for opportunistic infections.",
                        "recommended_actions": ["Initiate neutropenic precautions if neutrophil count is also low.", "Monitor for early signs of fever/chills.", "Perform infectious workup if febrile."]
                    })
            except ValueError:
                pass

        # 4. Platelets
        plt = check_val("platelets") or check_val("plt")
        if plt is not None:
            try:
                val = float(plt)
                if val < 150.0:
                    status = "LOW"
                    if val < 20.0:
                        sev = "CRITICAL"
                        interp = "Critical thrombocytopenia with high risk of spontaneous bleeding."
                        causes = ["Disseminated Intravascular Coagulation (DIC)", "Heparin-Induced Thrombocytopenia (HIT)", "Immune Thrombocytopenia (ITP)", "Severe sepsis"]
                        sig = "High danger of spontaneous intracranial or gastrointestinal hemorrhage."
                        acts = ["Notify attending immediately.", "Transfuse platelets immediately.", "Hold all antiplatelet and anticoagulant medications.", "Investigate for HIT or DIC."]
                    elif val < 50.0:
                        sev = "SEVERE"
                        interp = "Severe thrombocytopenia."
                        causes = ["Sepsis", "DIC", "HIT", "Drug-induced platelet destruction"]
                        sig = "Increased bleeding risk, especially during invasive procedures."
                        acts = ["Avoid invasive procedures (lumbar puncture, central lines unless ultrasound guided).", "Prepare platelet transfusion if active bleeding or procedure planned."]
                    elif val < 100.0:
                        sev = "MODERATE"
                        interp = "Moderate thrombocytopenia."
                        causes = ["Sepsis", "Splenic sequestration", "Liver disease"]
                        sig = "Tolerated unless surgical interventions are required."
                        acts = ["Monitor platelet counts daily.", "Review medication list for drug-induced causes."]
                    else:
                        sev = "MILD"
                        interp = "Mild thrombocytopenia."
                        causes = ["Early sepsis", "Hemodilution"]
                        sig = "Common in ICU; indicates mild bone marrow suppression or consumption."
                        acts = ["Monitor standard laboratory cycles."]

                    interpretations.append({
                        "name": "Platelets", "value": val, "normal_range": "150 - 450 K/uL",
                        "status": status, "severity": sev, "interpretation": interp,
                        "possible_causes": causes, "clinical_significance": sig, "recommended_actions": acts
                    })
                elif val > 450.0:
                    interpretations.append({
                        "name": "Platelets", "value": val, "normal_range": "150 - 450 K/uL",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Thrombocytosis.",
                        "possible_causes": ["Reactive (inflammation/infection)", "Iron deficiency", "Myeloproliferative disorders"],
                        "clinical_significance": "Secondary reactiveness; rarely causes hypercoagulability unless extreme (> 1000).",
                        "recommended_actions": ["Monitor trends.", "Identify inflammatory source."]
                    })
            except ValueError:
                pass

        # 5. Neutrophils
        neut = check_val("neutrophils") or check_val("neut")
        if neut is not None:
            try:
                val = float(neut)
                if val > 75.0:
                    interpretations.append({
                        "name": "Neutrophils", "value": val, "normal_range": "40 - 75 %",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Neutrophilia / neutrophilic shift.",
                        "possible_causes": ["Acute bacterial infection", "Tissue necrosis", "Steroid administration"],
                        "clinical_significance": "Reflects acute inflammatory response, typical in bacterial infections.",
                        "recommended_actions": ["Monitor for fever or local signs of infection."]
                    })
                elif val < 40.0:
                    interpretations.append({
                        "name": "Neutrophils", "value": val, "normal_range": "40 - 75 %",
                        "status": "LOW", "severity": "MODERATE", "interpretation": "Neutropenia.",
                        "possible_causes": ["Viral infection", "Chemotherapy", "Severe sepsis"],
                        "clinical_significance": "Impaired ability to fight bacterial infections.",
                        "recommended_actions": ["Monitor for fever.", "Consider neutropenic precautions if absolute count is < 1.0."]
                    })
            except ValueError:
                pass

        # 6. Lymphocytes
        lymph = check_val("lymphocytes") or check_val("lymph")
        if lymph is not None:
            try:
                val = float(lymph)
                if val < 20.0:
                    interpretations.append({
                        "name": "Lymphocytes", "value": val, "normal_range": "20 - 45 %",
                        "status": "LOW", "severity": "MILD", "interpretation": "Lymphopenia.",
                        "possible_causes": ["Acute physiologic stress response", "Corticosteroids", "Sepsis"],
                        "clinical_significance": "Common reactive state under severe stress; prognostic indicator in sepsis.",
                        "recommended_actions": ["Monitor trends."]
                    })
            except ValueError:
                pass

        # 7. Creatinine
        creat = check_val("creatinine") or check_val("creat")
        if creat is not None:
            try:
                val = float(creat)
                if val > 1.2:
                    status = "ELEVATED"
                    if val > 3.0:
                        sev = "CRITICAL"
                        interp = "Critical kidney injury or severe chronic kidney disease."
                        causes = ["Acute Kidney Injury (AKI) Stage 3", "Severe dehydration / prerenal azotemia", "Acute tubular necrosis (ATN)", "End-stage renal disease (ESRD)"]
                        sig = "Impending renal failure; high risk of severe metabolic acidosis, hyperkalemia, and fluid overload."
                        acts = ["Consult Nephrology immediately.", "Adjust all medication doses for renal impairment.", "Hold all nephrotoxins.", "Strict urine output monitoring.", "Prepare for potential dialysis (RRT/CRRT)."]
                    elif val > 2.0:
                        sev = "SEVERE"
                        interp = "Severe renal impairment / AKI Stage 2."
                        causes = ["Prerenal hypoperfusion", "Nephrotoxic drugs", "ATN"]
                        sig = "Marked loss of filtration capacity; high probability of drug toxicity if doses are not adjusted."
                        acts = ["Adjust antimicrobial and other drug dosages.", "Hold non-essential nephrotoxic medications.", "Assess fluid responsiveness."]
                    elif val > 1.5:
                        sev = "MODERATE"
                        interp = "Moderate renal impairment / AKI Stage 1."
                        causes = ["Dehydration", "Contrast-induced nephropathy", "Hypotension"]
                        sig = "Early organ dysfunction, requiring close follow-up to prevent progression."
                        acts = ["Optimize hemodynamics and hydration.", "Check serum potassium and bicarbonate levels."]
                    else:
                        sev = "MILD"
                        interp = "Mild renal impairment."
                        causes = ["Dehydration", "Baseline chronic kidney disease"]
                        sig = "Mild decrease in GCS / filtration."
                        acts = ["Monitor creatinine daily."]

                    interpretations.append({
                        "name": "Creatinine", "value": val, "normal_range": "0.6 - 1.2 mg/dL",
                        "status": status, "severity": sev, "interpretation": interp,
                        "possible_causes": causes, "clinical_significance": sig, "recommended_actions": acts
                    })
            except ValueError:
                pass

        # 8. BUN
        bun = check_val("bun")
        if bun is not None:
            try:
                val = float(bun)
                if val > 20.0:
                    status = "ELEVATED"
                    sev = "CRITICAL" if val > 60.0 else ("SEVERE" if val > 40.0 else ("MODERATE" if val > 30.0 else "MILD"))
                    interpretations.append({
                        "name": "BUN", "value": val, "normal_range": "7 - 20 mg/dL",
                        "status": status, "severity": sev, "interpretation": "Elevated Blood Urea Nitrogen, suggesting azotemia.",
                        "possible_causes": ["Dehydration / prerenal state", "Renal failure", "GI bleeding (increased protein breakdown)"],
                        "clinical_significance": "Reflects decreased renal clearance or elevated urea production.",
                        "recommended_actions": ["Correlate with creatinine to compute BUN/Creatinine ratio.", "Evaluate hydration and volume status."]
                    })
            except ValueError:
                pass

        # 9. eGFR
        egfr = check_val("egfr")
        if egfr is not None:
            try:
                val = float(egfr)
                if val < 90.0:
                    status = "LOW"
                    sev = "CRITICAL" if val < 15.0 else ("SEVERE" if val < 30.0 else ("MODERATE" if val < 60.0 else "MILD"))
                    interpretations.append({
                        "name": "eGFR", "value": val, "normal_range": ">= 90 mL/min/1.73m²",
                        "status": status, "severity": sev, "interpretation": "Reduced estimated glomerular filtration rate.",
                        "possible_causes": ["Acute kidney injury", "Chronic kidney disease"],
                        "clinical_significance": "Measures renal function stage and guides dosing of critical drugs.",
                        "recommended_actions": ["Review renal medication dosage guidelines.", "Maintain adequate renal perfusion pressures."]
                    })
            except ValueError:
                pass

        # 10. Urine Output
        uo = check_val("urine_output_ml") or check_val("urine_output") or check_val("uo")
        if uo is not None:
            try:
                val = float(uo)
                # Assume urine output in mL/hour. Normal for a standard 70kg patient is >= 35 mL/h (0.5 mL/kg/h)
                if val < 35.0:
                    status = "LOW"
                    if val < 15.0:
                        sev = "CRITICAL"
                        interp = "Severe oliguria or anuria."
                        causes = ["Acute tubular necrosis", "Severe hypovolemic or septic shock", "Urinary catheter obstruction", "Post-renal obstruction"]
                        sig = "Extremely high risk of rapid azotemia, hyperkalemia, and volume overload."
                        acts = ["Check patency of Foley catheter immediately (flush catheter).", "Assess fluid responsiveness (passive leg raise).", "Obtain urgent renal ultrasound.", "Hold nephrotoxic medications."]
                    else:
                        sev = "SEVERE"
                        interp = "Oliguria."
                        causes = ["Renal hypoperfusion", "Dehydration", "Early acute kidney injury"]
                        sig = "Inadequate renal perfusion, indicating physiological distress."
                        acts = ["Evaluate hydration and fluid balance.", "Monitor creatinine and electrolytes."]

                    interpretations.append({
                        "name": "Urine Output", "value": val, "normal_range": ">= 35 mL/hour (0.5 mL/kg/h)",
                        "status": status, "severity": sev, "interpretation": interp,
                        "possible_causes": causes, "clinical_significance": sig, "recommended_actions": acts
                    })
            except ValueError:
                pass

        # 11. Sodium
        na = check_val("sodium") or check_val("na")
        if na is not None:
            try:
                val = float(na)
                if val < 135.0:
                    status = "LOW"
                    sev = "CRITICAL" if val < 125.0 else ("SEVERE" if val < 130.0 else "MILD")
                    interpretations.append({
                        "name": "Sodium", "value": val, "normal_range": "135 - 145 mEq/L",
                        "status": status, "severity": sev, "interpretation": "Hyponatremia.",
                        "possible_causes": ["SIADH", "Fluid overload / excess free water", "Heart failure", "Adrenal insufficiency"],
                        "clinical_significance": "Can cause cerebral edema, leading to confusion, seizures, and coma if critical.",
                        "recommended_actions": ["Restrict free water intake if hypervolemic.", "Monitor neurological status closely.", "Check urine sodium and osmolarity.", "Avoid rapid correction (risk of central pontine myelinolysis)."]
                    })
                elif val > 145.0:
                    status = "ELEVATED"
                    sev = "CRITICAL" if val > 155.0 else ("SEVERE" if val > 150.0 else "MILD")
                    interpretations.append({
                        "name": "Sodium", "value": val, "normal_range": "135 - 145 mEq/L",
                        "status": status, "severity": sev, "interpretation": "Hypernatremia.",
                        "possible_causes": ["Dehydration / free water deficit", "Diabetes insipidus", "Excessive hypertonic saline infusion"],
                        "clinical_significance": "Intracellular dehydration, particularly impacting brain cells.",
                        "recommended_actions": ["Administer free water enterally or D5W intravenously.", "Slowly lower sodium (target < 10 mEq/L per 24 hours)."]
                    })
            except ValueError:
                pass

        # 12. Potassium
        k = check_val("potassium") or check_val("k")
        if k is not None:
            try:
                val = float(k)
                if val < 3.5:
                    status = "LOW"
                    sev = "CRITICAL" if val < 2.8 else ("SEVERE" if val < 3.2 else "MILD")
                    interpretations.append({
                        "name": "Potassium", "value": val, "normal_range": "3.5 - 5.0 mEq/L",
                        "status": status, "severity": sev, "interpretation": "Hypokalemia.",
                        "possible_causes": ["Diuretic therapy (Furosemide)", "Gastrointestinal loss (vomiting/diarrhea)", "Inadequate replenishment"],
                        "clinical_significance": "Cardiac excitability, muscle weakness, risk of lethal ventricular arrhythmias.",
                        "recommended_actions": ["Administer oral or IV potassium chloride replacement.", "Check and replenish magnesium (hypomagnesemia prevents potassium correction).", "Monitor telemetry for QTc prolongation or U waves."]
                    })
                elif val > 5.0:
                    status = "ELEVATED"
                    if val > 6.0:
                        sev = "CRITICAL"
                        interp = "Critical hyperkalemia requiring emergent therapy."
                        causes = ["Acute Kidney Injury", "Metabolic acidosis", "Cell lysis (rhabdomyolysis/tumor lysis)", "Potassium-sparing diuretics"]
                        sig = "Lethal danger of cardiac arrest (PEA, ventricular fibrillation or asystole)."
                        acts = ["Obtain urgent EKG (check for peaked T waves, PR prolongation, wide QRS).", "Administer Calcium Gluconate (10 mL of 10% solution) IV immediately to stabilize myocardium.", "Administer Insulin + Dextrose (10 units regular insulin + 50 mL D50W) IV to shift potassium intracellularly.", "Administer Sodium Bicarbonate or Albuterol inhalations.", "Consider emergent hemodysterialysis."]
                    elif val > 5.5:
                        sev = "SEVERE"
                        interp = "Severe hyperkalemia."
                        causes = ["Renal insufficiency", "Metabolic acidosis", "Potassium supplements"]
                        sig = "High risk of cardiac conduction abnormalities."
                        acts = ["Monitor EKG and repeat potassium in 2-4 hours.", "Restrict dietary potassium.", "Consider loop diuretics or exchange resins."]
                    else:
                        sev = "MILD"
                        interp = "Mild hyperkalemia."
                        causes = ["Mild renal dysfunction", "Hemolyzed blood sample (artifact)"]
                        sig = "Low immediate risk; monitor trend."
                        acts = ["Repeat potassium to rule out hemolysis.", "Monitor BMP daily."]

                    interpretations.append({
                        "name": "Potassium", "value": val, "normal_range": "3.5 - 5.0 mEq/L",
                        "status": status, "severity": sev, "interpretation": interp,
                        "possible_causes": causes, "clinical_significance": sig, "recommended_actions": acts
                    })
            except ValueError:
                pass

        # 13. Chloride
        cl = check_val("chloride") or check_val("cl")
        if cl is not None:
            try:
                val = float(cl)
                if val < 96.0 or val > 106.0:
                    status = "LOW" if val < 96.0 else "ELEVATED"
                    interpretations.append({
                        "name": "Chloride", "value": val, "normal_range": "96 - 106 mEq/L",
                        "status": status, "severity": "MILD", "interpretation": "Chloride imbalance.",
                        "possible_causes": ["Excessive normal saline (0.9% NaCl) infusion (causes hyperchloremia)", "Vomiting or NG tube suction (causes hypochloremic alkalosis)"],
                        "clinical_significance": "Can contribute to acid-base disturbance (hyperchloremic metabolic acidosis).",
                        "recommended_actions": ["Review IV fluid choice; consider switching to balanced crystalloids (Lactated Ringer's or Plasma-Lyte)."]
                    })
            except ValueError:
                pass

        # 14. Calcium
        ca = check_val("calcium") or check_val("ca")
        if ca is not None:
            try:
                val = float(ca)
                if val < 8.5 or val > 10.5:
                    status = "LOW" if val < 8.5 else "ELEVATED"
                    interpretations.append({
                        "name": "Calcium", "value": val, "normal_range": "8.5 - 10.5 mg/dL",
                        "status": status, "severity": "MILD", "interpretation": "Calcium deviation.",
                        "possible_causes": ["Hypoalbuminemia (causes pseudohypocalcemia)", "Critical illness", "Hyperparathyroidism", "Malignancy"],
                        "clinical_significance": "Affects neuromuscular excitability and cardiac contractility.",
                        "recommended_actions": ["Check ionized calcium level for accurate active fraction.", "Replenish calcium gluconate if ionized fraction is low and symptomatic."]
                    })
            except ValueError:
                pass

        # 15. Magnesium
        mg = check_val("magnesium") or check_val("mg")
        if mg is not None:
            try:
                val = float(mg)
                if val < 1.7:
                    status = "LOW"
                    sev = "CRITICAL" if val < 1.0 else ("SEVERE" if val < 1.4 else "MILD")
                    interpretations.append({
                        "name": "Magnesium", "value": val, "normal_range": "1.7 - 2.2 mg/dL",
                        "status": status, "severity": sev, "interpretation": "Hypomagnesemia.",
                        "possible_causes": ["Diuretic therapy", "Chronic alcoholism", "Malabsorption", "Malnutrition"],
                        "clinical_significance": "Predisposes to cardiac arrhythmias (Torsades de Pointes) and refractory hypokalemia.",
                        "recommended_actions": ["Administer Magnesium Sulfate IV (1-2 g over 30-60 mins).", "Monitor telemetry for prolonged QT interval."]
                    })
                elif val > 2.2:
                    interpretations.append({
                        "name": "Magnesium", "value": val, "normal_range": "1.7 - 2.2 mg/dL",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Hypermagnesemia.",
                        "possible_causes": ["Renal failure", "Excessive replacement infusions"],
                        "clinical_significance": "Depresses neuromuscular function; low reflexes at higher levels.",
                        "recommended_actions": ["Hold magnesium-containing medications and infusions."]
                    })
            except ValueError:
                pass

        # 16. Phosphate
        phos = check_val("phosphate") or check_val("phos")
        if phos is not None:
            try:
                val = float(phos)
                if val < 2.5 or val > 4.5:
                    status = "LOW" if val < 2.5 else "ELEVATED"
                    interpretations.append({
                        "name": "Phosphate", "value": val, "normal_range": "2.5 - 4.5 mg/dL",
                        "status": status, "severity": "MILD", "interpretation": "Phosphate imbalance.",
                        "possible_causes": ["Refeeding syndrome (causes critical hypophosphatemia)", "Renal failure (causes hyperphosphatemia)"],
                        "clinical_significance": "Hypophosphatemia leads to diaphragm weakness and failure to wean from mechanical ventilation.",
                        "recommended_actions": ["Replenish phosphate IV if severe (< 1.5 mg/dL).", "Hold replacement and check renal function if hyperphosphatemic."]
                    })
            except ValueError:
                pass

        # 17. AST
        ast = check_val("ast")
        if ast is not None:
            try:
                val = float(ast)
                if val > 40.0:
                    status = "ELEVATED"
                    sev = "CRITICAL" if val > 1000.0 else ("SEVERE" if val > 300.0 else ("MODERATE" if val > 100.0 else "MILD"))
                    interpretations.append({
                        "name": "AST", "value": val, "normal_range": "10 - 40 U/L",
                        "status": status, "severity": sev, "interpretation": "Elevated aspartate aminotransferase, indicating hepatocellular injury.",
                        "possible_causes": ["Shock liver / ischemic hepatitis", "Drug-induced liver injury (acetaminophen)", "Biliary obstruction", "Alcoholic/viral hepatitis"],
                        "clinical_significance": "Reflects acute or chronic liver tissue damage.",
                        "recommended_actions": ["Monitor liver function panel daily.", "Review and discontinue potentially hepatotoxic drugs.", "Evaluate biliary tract with ultrasound if biliary symptoms present."]
                    })
            except ValueError:
                pass

        # 18. ALT
        alt = check_val("alt")
        if alt is not None:
            try:
                val = float(alt)
                if val > 56.0:
                    status = "ELEVATED"
                    interpretations.append({
                        "name": "ALT", "value": val, "normal_range": "7 - 56 U/L",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Elevated alanine aminotransferase.",
                        "possible_causes": ["Liver injury", "Fatty liver", "Medications"],
                        "clinical_significance": "Specific marker for hepatocellular damage.",
                        "recommended_actions": ["Monitor liver enzyme panel."]
                    })
            except ValueError:
                pass

        # 19. Bilirubin
        bili = check_val("bilirubin") or check_val("bili")
        if bili is not None:
            try:
                val = float(bili)
                if val > 1.2:
                    status = "ELEVATED"
                    sev = "SEVERE" if val > 6.0 else ("MODERATE" if val > 3.0 else "MILD")
                    interpretations.append({
                        "name": "Bilirubin", "value": val, "normal_range": "0.2 - 1.2 mg/dL",
                        "status": status, "severity": sev, "interpretation": "Hyperbilirubinemia.",
                        "possible_causes": ["Biliary obstruction / cholecystitis", "Shock liver / liver failure", "Hemolysis", "Gilbert's syndrome"],
                        "clinical_significance": "Indicates impaired biliary clearance or massive erythrocyte breakdown.",
                        "recommended_actions": ["Obtain biliary tract ultrasound.", "Check direct vs. indirect fractions.", "Assess for signs of jaundice."]
                    })
            except ValueError:
                pass

        # 20. Albumin
        alb = check_val("albumin") or check_val("alb")
        if alb is not None:
            try:
                val = float(alb)
                if val < 3.5:
                    status = "LOW"
                    interpretations.append({
                        "name": "Albumin", "value": val, "normal_range": "3.5 - 5.0 g/dL",
                        "status": "LOW", "severity": "MILD", "interpretation": "Hypoalbuminemia.",
                        "possible_causes": ["Systemic inflammatory response (capillary leak)", "Malnutrition", "Hepatic synthetic dysfunction", "Nephrotic syndrome"],
                        "clinical_significance": "Decreases plasma oncotic pressure, leading to peripheral edema and third-spacing.",
                        "recommended_actions": ["Avoid albumin transfusions solely for low numbers; optimize nutritional intake."]
                    })
            except ValueError:
                pass

        # 21. ALP
        alp = check_val("alp")
        if alp is not None:
            try:
                val = float(alp)
                if val > 147.0:
                    interpretations.append({
                        "name": "ALP", "value": val, "normal_range": "44 - 147 U/L",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Elevated Alkaline Phosphatase.",
                        "possible_causes": ["Cholestasis / biliary obstruction", "Bone remodeling or fracture"],
                        "clinical_significance": "Suggestive of biliary tract obstruction when elevated alongside bilirubin or GGT.",
                        "recommended_actions": ["Correlate with right upper quadrant ultrasound."]
                    })
            except ValueError:
                pass

        # 22. CRP
        crp = check_val("crp")
        if crp is not None:
            try:
                val = float(crp)
                if val > 0.8:
                    status = "ELEVATED"
                    sev = "SEVERE" if val > 10.0 else ("MODERATE" if val > 3.0 else "MILD")
                    interpretations.append({
                        "name": "CRP", "value": val, "normal_range": "< 0.8 mg/dL",
                        "status": status, "severity": sev, "interpretation": "Elevated C-Reactive Protein.",
                        "possible_causes": ["Severe bacterial or viral infection", "Systemic inflammatory response syndrome (SIRS)", "Post-operative tissue injury", "Autoimmune flare"],
                        "clinical_significance": "Non-specific but sensitive indicator of acute systemic inflammation.",
                        "recommended_actions": ["Correlate with procalcitonin and WBC trends.", "Investigate active infectious sources."]
                    })
            except ValueError:
                pass

        # 23. Procalcitonin
        pct = check_val("procalcitonin") or check_val("pct")
        if pct is not None:
            try:
                val = float(pct)
                if val > 0.15:
                    status = "ELEVATED"
                    if val > 10.0:
                        sev = "CRITICAL"
                        interp = "Critical systemic bacterial infection / septic shock."
                        causes = ["Severe bacterial sepsis", "Severe septic shock", "Severe localized infection (e.g. peritonitis, pneumonia)"]
                        sig = "Highly specific indicator of severe systemic bacterial infection with high risk of organ failure."
                        acts = ["Broaden or optimize antimicrobial therapy immediately.", "Perform source control evaluations.", "Monitor serum lactate clearance.", "Repeat PCT in 24-48 hours to assess response."]
                    elif val > 2.0:
                        sev = "SEVERE"
                        interp = "High risk of systemic bacterial infection."
                        causes = ["Bacterial sepsis", "Severe localized bacterial infection"]
                        sig = "Strongly supportive of systemic infectious etiology."
                        acts = ["Ensure adequate culture-directed antibiotic coverage.", "Optimize hemodynamics."]
                    elif val > 0.5:
                        sev = "MODERATE"
                        interp = "Moderate risk of systemic infection."
                        causes = ["Localized bacterial infection", "Severe non-infectious inflammatory stress"]
                        sig = "Borderline sepsis indicator."
                        acts = ["Evaluate for localized infection.", "Monitor PCT trend daily."]
                    else:
                        sev = "MILD"
                        interp = "Mild elevation."
                        causes = ["Early localized infection", "Severe systemic trauma", "Major surgery"]
                        sig = "Infection possible; low immediate risk of systemic shock."
                        acts = ["Re-evaluate in 24 hours if clinically concerned."]

                    interpretations.append({
                        "name": "Procalcitonin", "value": val, "normal_range": "< 0.15 ng/mL",
                        "status": status, "severity": sev, "interpretation": interp,
                        "possible_causes": causes, "clinical_significance": sig, "recommended_actions": acts
                    })
            except ValueError:
                pass

        # 24. Lactate
        lact = check_val("lactate") or check_val("lact")
        if lact is not None:
            try:
                val = float(lact)
                if val > 2.0:
                    status = "ELEVATED"
                    if val > 6.0:
                        sev = "CRITICAL"
                        interp = "Critical hyperlactatemia suggesting profound systemic tissue hypoperfusion."
                        causes = ["Septic shock", "Hypovolemic / cardiogenic shock", "Mesenteric ischemia", "Severe cellular hypoxia"]
                        sig = "Profound anaerobic metabolism; associated with extremely high hospital mortality."
                        acts = ["Notify attending immediately.", "Optimize oxygen delivery and systemic perfusion.", "Assess fluid responsiveness.", "Titrate vasopressors (Norepinephrine) to target MAP >= 65 mmHg.", "Repeat lactate in 2 hours."]
                    elif val > 4.0:
                        sev = "SEVERE"
                        interp = "Severe hyperlactatemia."
                        causes = ["Systemic hypoperfusion", "Sepsis", "Active tissue ischemia"]
                        sig = "Indicates significant systemic tissue hypoxia."
                        acts = ["Initiate aggressive fluid resuscitation (30 mL/kg Balanced Crystalloid) if hypovolemic/septic.", "Ensure serial measurements are scheduled every 2-4 hours."]
                    elif val > 3.0:
                        sev = "MODERATE"
                        interp = "Moderate hyperlactatemia."
                        causes = ["Hypoperfusion", "Metformin toxicity", "Liver dysfunction (decreased clearance)"]
                        sig = "Signifies early or occult tissue hypoperfusion."
                        acts = ["Obtain serial lactate trends.", "Optimize cardiovascular hemodynamics."]
                    else:
                        sev = "MILD"
                        interp = "Mild hyperlactatemia."
                        causes = ["Beta-agonist (albuterol) therapy", "Mild dehydration", "Strenuous physical effort"]
                        sig = "Minimal immediate risk; represents stress state."
                        acts = ["Monitor lactate trend."]

                    interpretations.append({
                        "name": "Lactate", "value": val, "normal_range": "0.5 - 2.0 mmol/L",
                        "status": status, "severity": sev, "interpretation": interp,
                        "possible_causes": causes, "clinical_significance": sig, "recommended_actions": acts
                    })
            except ValueError:
                pass

        # 25. INR
        inr = check_val("inr")
        if inr is not None:
            try:
                val = float(inr)
                if val > 1.2:
                    status = "ELEVATED"
                    sev = "CRITICAL" if val > 5.0 else ("SEVERE" if val > 3.0 else ("MODERATE" if val > 2.0 else "MILD"))
                    interpretations.append({
                        "name": "INR", "value": val, "normal_range": "0.8 - 1.2",
                        "status": status, "severity": sev, "interpretation": "Elevated international normalized ratio.",
                        "possible_causes": ["Warfarin therapy", "Liver failure", "Disseminated Intravascular Coagulation (DIC)", "Vitamin K deficiency"],
                        "clinical_significance": "Impaired coagulation pathway; elevated hemorrhage risk.",
                        "recommended_actions": ["Hold all anticoagulants.", "Administer Vitamin K IV/PO or Fresh Frozen Plasma (FFP) if active bleeding or emergency procedure scheduled.", "Avoid intramuscular injections."]
                    })
            except ValueError:
                pass

        # 26. PT
        pt = check_val("pt")
        if pt is not None:
            try:
                val = float(pt)
                if val > 13.5:
                    interpretations.append({
                        "name": "PT", "value": val, "normal_range": "11.0 - 13.5 seconds",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Prolonged Prothrombin Time.",
                        "possible_causes": ["Warfarin use", "Liver disease", "DIC"],
                        "clinical_significance": "Indicates deficiency or blockade of extrinsic pathway coagulation factors.",
                        "recommended_actions": ["Correlate with INR value."]
                    })
            except ValueError:
                pass

        # 27. aPTT
        aptt = check_val("aptt")
        if aptt is not None:
            try:
                val = float(aptt)
                if val > 35.0:
                    interpretations.append({
                        "name": "aPTT", "value": val, "normal_range": "25 - 35 seconds",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Prolonged activated partial thromboplastin time.",
                        "possible_causes": ["Unfractionated heparin therapy", "Coagulation factor deficiencies (hemophilia)", "Lupus anticoagulant"],
                        "clinical_significance": "Indicates blockade or deficiency of intrinsic/common coagulation pathways.",
                        "recommended_actions": ["Correlate with heparin infusion status.", "Obtain mixing study if unexplained."]
                    })
            except ValueError:
                pass

        # 28. D-Dimer
        ddimer = check_val("ddimer") or check_val("d-dimer")
        if ddimer is not None:
            try:
                val = float(ddimer)
                if val > 500.0:
                    interpretations.append({
                        "name": "D-Dimer", "value": val, "normal_range": "< 500 ng/mL",
                        "status": "ELEVATED", "severity": "MILD", "interpretation": "Elevated D-Dimer.",
                        "possible_causes": ["Disseminated Intravascular Coagulation (DIC)", "Deep Vein Thrombosis (DVT) / Pulmonary Embolism (PE)", "Systemic inflammation", "Active malignancy"],
                        "clinical_significance": "Suggests active intravascular fibrin division; highly non-specific in critical illness.",
                        "recommended_actions": ["Correlate with clinical suspicion of venous thromboembolism (Wells score).", "Perform lower extremity duplex ultrasound or CT pulmonary angiogram if highly suspicious."]
                    })
            except ValueError:
                pass

        # 29. pH
        ph = check_val("ph")
        if ph is not None:
            try:
                val = float(ph)
                if val < 7.35:
                    status = "LOW"
                    sev = "CRITICAL" if val < 7.20 else ("SEVERE" if val < 7.30 else "MILD")
                    interpretations.append({
                        "name": "pH", "value": val, "normal_range": "7.35 - 7.45",
                        "status": status, "severity": sev, "interpretation": "Acidemia.",
                        "possible_causes": ["Metabolic acidosis (lactic acidosis, DKA, renal failure)", "Respiratory acidosis (hypoventilation, severe COPD, ARDS)"],
                        "clinical_significance": "Reduces cardiac contractility, impairs drug efficacy, and predisposes to arrhythmias.",
                        "recommended_actions": ["Assess PaCO2 and HCO3 to identify acid-base etiology.", "Ensure adequate ventilation.", "Consider sodium bicarbonate only if pH < 7.15 and metabolic etiology is refractory."]
                    })
                elif val > 7.45:
                    status = "ELEVATED"
                    sev = "CRITICAL" if val > 7.55 else ("SEVERE" if val > 7.50 else "MILD")
                    interpretations.append({
                        "name": "pH", "value": val, "normal_range": "7.35 - 7.45",
                        "status": status, "severity": sev, "interpretation": "Alkalemia.",
                        "possible_causes": ["Metabolic alkalosis (contraction, severe vomiting)", "Respiratory alkalosis (hyperventilation, pain, anxiety, early sepsis)"],
                        "clinical_significance": "Can cause hypokalemia, hypocalcemia, and reduce cerebral blood flow.",
                        "recommended_actions": ["Determine respiratory vs. metabolic cause.", "Optimize ventilator settings if intubated."]
                    })
            except ValueError:
                pass

        # 30. PaO2
        pao2_val = check_val("pao2") or check_val("pa-o2")
        if pao2_val is not None:
            try:
                val = float(pao2_val)
                if val < 75.0:
                    status = "LOW"
                    if val < 45.0:
                        sev = "CRITICAL"
                        interp = "Critical hypoxemia representing respiratory failure."
                        causes = ["Severe ARDS", "Massive pulmonary embolism", "Pulmonary edema / CHF", "Severe pneumonia"]
                        sig = "Lethal threat of immediate organ damage or cardiac arrest due to severe hypoxia."
                        acts = ["Increase FiO2 to 100% immediately.", "Ensure patient airway; check ventilator circuit.", "Prepare for urgent intubation if not mechanical ventilated.", "Consult pulmonology / respiratory therapy."]
                    elif val < 55.0:
                        sev = "SEVERE"
                        interp = "Severe hypoxemia."
                        causes = ["ARDS", "Pneumonia", "Atelectasis"]
                        sig = "Significant compromise in oxygen delivery; risk of tissue injury."
                        acts = ["Increase supplemental oxygen (HFNO/NIV).", "Obtain chest X-ray.", "Optimize ventilator positive end-expiratory pressure (PEEP)."]
                    elif val < 65.0:
                        sev = "MODERATE"
                        interp = "Moderate hypoxemia."
                        causes = ["Atelectasis", "Fluid overload", "COPD exacerbation"]
                        sig = "Mild to moderate ventilation-perfusion mismatch."
                        acts = ["Titrate supplemental oxygen to target SpO2 92-96%.", "Encourage pulmonary hygiene (coughing, deep breathing)."]
                    else:
                        sev = "MILD"
                        interp = "Mild hypoxemia."
                        causes = ["Hypoventilation", "Mild atelectasis"]
                        sig = "Generally tolerated; monitor trend."
                        acts = ["Monitor pulse oximetry."]

                    interpretations.append({
                        "name": "PaO2", "value": val, "normal_range": "75 - 100 mmHg",
                        "status": status, "severity": sev, "interpretation": interp,
                        "possible_causes": causes, "clinical_significance": sig, "recommended_actions": acts
                    })
            except ValueError:
                pass

        # 31. PaCO2
        paco2_val = check_val("paco2") or check_val("pa-co2")
        if paco2_val is not None:
            try:
                val = float(paco2_val)
                if val > 45.0:
                    status = "ELEVATED"
                    sev = "CRITICAL" if val > 60.0 else ("SEVERE" if val > 55.0 else ("MODERATE" if val > 50.0 else "MILD"))
                    interpretations.append({
                        "name": "PaCO2", "value": val, "normal_range": "35 - 45 mmHg",
                        "status": status, "severity": sev, "interpretation": "Hypercapnia.",
                        "possible_causes": ["Hypoventilation / respiratory depression", "COPD exacerbation", "Ventilatory muscle fatigue"],
                        "clinical_significance": "Causes respiratory acidosis, cerebral vasodilation (increased ICP), and somnolence.",
                        "recommended_actions": ["Increase ventilator minute ventilation (increase respiratory rate or tidal volume).", "Consider non-invasive ventilation (BiPAP) if not intubated."]
                    })
                elif val < 35.0:
                    interpretations.append({
                        "name": "PaCO2", "value": val, "normal_range": "35 - 45 mmHg",
                        "status": "LOW", "severity": "MILD", "interpretation": "Hypocapnia.",
                        "possible_causes": ["Hyperventilation (pain, anxiety, fever)", "Early septic shock response", "Excessive ventilator support"],
                        "clinical_significance": "Causes respiratory alkalosis; vasoconstriction of cerebral vessels.",
                        "recommended_actions": ["Address underlying pain/anxiety.", "De-escalate ventilator settings if appropriate."]
                    })
            except ValueError:
                pass

        # 32. HCO3
        hco3 = check_val("hco3")
        if hco3 is not None:
            try:
                val = float(hco3)
                if val < 22.0 or val > 26.0:
                    status = "LOW" if val < 22.0 else "ELEVATED"
                    interpretations.append({
                        "name": "HCO3", "value": val, "normal_range": "22 - 26 mEq/L",
                        "status": status, "severity": "MILD", "interpretation": "Bicarbonate deviation.",
                        "possible_causes": ["Renal compensation for respiratory alkalosis/acidosis", "Metabolic acidosis (low HCO3)", "Metabolic alkalosis (high HCO3)"],
                        "clinical_significance": "Reflects the metabolic component of acid-base buffer system.",
                        "recommended_actions": ["Correlate with pH and arterial blood gas values."]
                    })
            except ValueError:
                pass

        # 33. Base Excess
        be = check_val("base_excess") or check_val("be")
        if be is not None:
            try:
                val = float(be)
                if val < -2.0 or val > 2.0:
                    status = "LOW" if val < -2.0 else "ELEVATED"
                    interpretations.append({
                        "name": "Base Excess", "value": val, "normal_range": "-2 to +2 mEq/L",
                        "status": status, "severity": "MILD", "interpretation": "Base excess deviation.",
                        "possible_causes": ["Metabolic acidosis (negative/low value)", "Metabolic alkalosis (positive/high value)"],
                        "clinical_significance": "Measures the pure metabolic deviation of acid-base balance.",
                        "recommended_actions": ["Correlate with pH and serum lactate."]
                    })
            except ValueError:
                pass

        # 34. SaO2
        sao2 = check_val("sao2")
        if sao2 is not None:
            try:
                val = float(sao2)
                if val < 95.0:
                    status = "LOW"
                    sev = "CRITICAL" if val < 85.0 else ("SEVERE" if val < 90.0 else "MILD")
                    interpretations.append({
                        "name": "SaO2", "value": val, "normal_range": "95 - 100 %",
                        "status": status, "severity": sev, "interpretation": "Oxygen saturation deficit.",
                        "possible_causes": ["Gas exchange impairment", "Hypoventilation", "Ventilation-perfusion mismatch"],
                        "clinical_significance": "Indicates arterial hemoglobin oxygen saturation status.",
                        "recommended_actions": ["Optimize oxygen therapy delivery.", "Correlate with PaO2 and SpO2."]
                    })
            except ValueError:
                pass

        # ----------------------------------------------------
        # Compile Summary statistics
        # ----------------------------------------------------
        abnormal_count = len(interpretations)
        critical_count = sum(1 for item in interpretations if item["severity"] == "CRITICAL")
        
        severity_order = ["CRITICAL", "SEVERE", "MODERATE", "MILD", "NORMAL"]
        highest_priority = "NORMAL"
        for s in severity_order:
            if any(item["severity"] == s for item in interpretations):
                highest_priority = s
                break

        return {
            "laboratory_interpretation": interpretations,
            "summary": {
                "abnormal_count": abnormal_count,
                "critical_count": critical_count,
                "highest_priority": highest_priority
            }
        }
