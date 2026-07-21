"""
app/clinical_reasoning/differential_engine.py

Differential Diagnosis Engine for ICU patients (Phase 13.0).
Evaluates 8 critical ICU conditions using expert clinical rule scoring,
incorporating vital signs, laboratory metrics, active alerts, and RAG contexts.
"""

from typing import Dict, Any, List

class DifferentialEngine:
    """
    Expert clinical rule engine to score and rank ICU differential diagnoses.
    """

    INITIAL_DIAGNOSES = [
        "Septic Shock",
        "Hypovolemic Shock",
        "Cardiogenic Shock",
        "Obstructive Shock",
        "AKI",
        "ARDS",
        "Acute Respiratory Failure",
        "Multi Organ Dysfunction"
    ]

    @staticmethod
    def evaluate(
        context: Dict[str, Any],
        abnormal_vitals: List[str],
        abnormal_labs: List[str],
        admission_diagnosis: str,
        retrieved_sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Scans patient clinical parameters and computes a likelihood score (0.0 to 1.0)
        and evidence lists for the 8 core ICU diagnoses.

        Returns a sorted list of dicts:
        [
            {
                "diagnosis": str,
                "likelihood": float (0.0 - 1.0),
                "supporting_evidence": list[str],
                "contradicting_evidence": list[str]
            }
        ]
        """
        # Extract clinical parameters from context
        vitals = context.get("vitals", {}) or {}
        labs = context.get("labs", {}) or {}
        alerts = context.get("alerts", []) or []
        meds = context.get("medications", []) or []

        # Normalise strings for robust matching
        abn_vitals_lower = [v.lower() for v in abnormal_vitals]
        abn_labs_lower = [l.lower() for l in abnormal_labs]
        adm_diag_lower = admission_diagnosis.lower() if admission_diagnosis else ""
        alert_titles = [a.get("title", "").lower() for a in alerts]
        meds_lower = [m.lower() for m in meds]

        results = []

        # ----------------------------------------------------
        # 1. Septic Shock
        # ----------------------------------------------------
        septic_shock = {
            "diagnosis": "Septic Shock",
            "score": 0.0,
            "supporting_evidence": [],
            "contradicting_evidence": []
        }
        # Supporting indicators
        if "sepsis" in adm_diag_lower or "septic" in adm_diag_lower:
            septic_shock["score"] += 0.4
            septic_shock["supporting_evidence"].append("Admission diagnosis indicates Sepsis/Septic Shock.")
        if any("sepsis" in t or "infection" in t for t in alert_titles):
            septic_shock["score"] += 0.2
            septic_shock["supporting_evidence"].append("Active sepsis or infection alert present.")
        
        # Vasoactive usage in hypotension
        has_vasopressors = any(m in meds_lower for m in ["norepinephrine", "vasopressin", "epinephrine", "levophed"])
        if has_vasopressors:
            septic_shock["score"] += 0.3
            septic_shock["supporting_evidence"].append("Patient requires vasopressor therapy (norepinephrine/vasopressin).")
            
        # Vitals/Labs indicators
        lactate = labs.get("lactate")
        if lactate is not None:
            if lactate > 2.0:
                septic_shock["score"] += 0.2
                septic_shock["supporting_evidence"].append(f"Elevated serum lactate ({lactate} mmol/L) suggests tissue hypoperfusion.")
            else:
                septic_shock["contradicting_evidence"].append(f"Normal serum lactate ({lactate} mmol/L) makes shock less likely.")
        
        temp = vitals.get("temperature")
        if temp is not None:
            if temp > 38.0:
                septic_shock["score"] += 0.1
                septic_shock["supporting_evidence"].append(f"Fever (temp {temp} °C) suggests inflammatory host response.")
            elif temp < 36.0:
                septic_shock["score"] += 0.1
                septic_shock["supporting_evidence"].append(f"Hypothermia (temp {temp} °C) is a risk driver in severe infection.")
        
        wbc = labs.get("wbc")
        if wbc is not None:
            if wbc > 12.0 or wbc < 4.0:
                septic_shock["score"] += 0.1
                septic_shock["supporting_evidence"].append(f"Abnormal leukocyte count (WBC {wbc} K/uL) points to immunologic activity.")

        # Contradicting indicators
        if not has_vasopressors and any("map" not in v for v in abn_vitals_lower):
            septic_shock["contradicting_evidence"].append("Patient is normotensive without vasopressor support.")

        results.append(septic_shock)

        # ----------------------------------------------------
        # 2. Hypovolemic Shock
        # ----------------------------------------------------
        hypo_shock = {
            "diagnosis": "Hypovolemic Shock",
            "score": 0.0,
            "supporting_evidence": [],
            "contradicting_evidence": []
        }
        if "hypovolemic" in adm_diag_lower or "hemorrhage" in adm_diag_lower or "dehydration" in adm_diag_lower:
            hypo_shock["score"] += 0.4
            hypo_shock["supporting_evidence"].append("Admission diagnosis suggests volume depletion or hemorrhage.")
            
        hr = vitals.get("heart_rate")
        sbp = vitals.get("systolic_bp")
        if hr is not None and sbp is not None:
            if hr > 100 and sbp < 90:
                hypo_shock["score"] += 0.3
                hypo_shock["supporting_evidence"].append(f"Tachycardia ({hr} bpm) and hypotension (SBP {sbp} mmHg) match hypovolemic profile.")
                
        # Renal hypoperfusion / fluid status
        urine = vitals.get("urine_output_ml") or vitals.get("urine_output")
        if urine is not None and isinstance(urine, (int, float)) and urine < 30:
            hypo_shock["score"] += 0.2
            hypo_shock["supporting_evidence"].append(f"Oliguria ({urine} mL/hour) suggests renal hypoperfusion or fluid deficit.")

        if lactate is not None and lactate > 2.0:
            hypo_shock["score"] += 0.1
            hypo_shock["supporting_evidence"].append("Serum lactate elevated due to peripheral hypoperfusion.")

        # Contradicting
        if any("sepsis" in t for t in alert_titles):
            hypo_shock["contradicting_evidence"].append("Infection parameters point more towards distributive/septic shock.")
            
        results.append(hypo_shock)

        # ----------------------------------------------------
        # 3. Cardiogenic Shock
        # ----------------------------------------------------
        cardio_shock = {
            "diagnosis": "Cardiogenic Shock",
            "score": 0.0,
            "supporting_evidence": [],
            "contradicting_evidence": []
        }
        if "cardiogenic" in adm_diag_lower or "infarction" in adm_diag_lower or "heart failure" in adm_diag_lower:
            cardio_shock["score"] += 0.4
            cardio_shock["supporting_evidence"].append("Admission diagnosis lists cardiac injury or failure.")
        if any(m in meds_lower for m in ["dobutamine", "milrinone", "epinephrine"]):
            cardio_shock["score"] += 0.3
            cardio_shock["supporting_evidence"].append("Patient requires inotropic support (dobutamine).")
        if hr is not None and hr > 110:
            cardio_shock["score"] += 0.1
            cardio_shock["supporting_evidence"].append(f"Persistent tachycardia ({hr} bpm) to compensate for low stroke volume.")
            
        # Contradicting
        if not any(m in meds_lower for m in ["dobutamine", "milrinone"]):
            cardio_shock["contradicting_evidence"].append("No active inotropic support prescribed.")
            
        results.append(cardio_shock)

        # ----------------------------------------------------
        # 4. Obstructive Shock
        # ----------------------------------------------------
        obstructive_shock = {
            "diagnosis": "Obstructive Shock",
            "score": 0.0,
            "supporting_evidence": [],
            "contradicting_evidence": []
        }
        if any(k in adm_diag_lower for k in ["embolism", "tamponade", "pneumothorax"]):
            obstructive_shock["score"] += 0.5
            obstructive_shock["supporting_evidence"].append("Mechanical obstruction identified in admission history.")
            
        spo2 = vitals.get("spo2")
        if spo2 is not None and spo2 < 92:
            obstructive_shock["score"] += 0.2
            obstructive_shock["supporting_evidence"].append(f"Hypoxemia (SpO2 {spo2}%) matches pulmonary embolism/mechanical profiles.")

        # Contradicting
        if not any(k in adm_diag_lower for k in ["embolism", "tamponade", "pneumothorax"]):
            obstructive_shock["contradicting_evidence"].append("No structural or mechanical thoracic pathology reported.")
            
        results.append(obstructive_shock)

        # ----------------------------------------------------
        # 5. AKI (Acute Kidney Injury)
        # ----------------------------------------------------
        aki = {
            "diagnosis": "AKI",
            "score": 0.0,
            "supporting_evidence": [],
            "contradicting_evidence": []
        }
        if "aki" in adm_diag_lower or "renal failure" in adm_diag_lower or "kidney" in adm_diag_lower:
            aki["score"] += 0.3
            aki["supporting_evidence"].append("Acute Kidney Injury noted in history.")
            
        creat = labs.get("creatinine")
        if creat is not None:
            if creat > 1.5:
                aki["score"] += 0.4
                aki["supporting_evidence"].append(f"Elevated serum creatinine ({creat} mg/dL) indicates impaired filtration.")
            else:
                aki["contradicting_evidence"].append(f"Normal serum creatinine ({creat} mg/dL) makes significant AKI less likely.")
                
        bun = labs.get("bun")
        if bun is not None and bun > 20:
            aki["score"] += 0.2
            aki["supporting_evidence"].append(f"Elevated BUN ({bun} mg/dL) suggests azotemia.")

        if urine is not None and isinstance(urine, (int, float)) and urine < 30:
            aki["score"] += 0.2
            aki["supporting_evidence"].append(f"Decreased urine output ({urine} mL/hour) supports KDIGO oliguria criteria.")

        results.append(aki)

        # ----------------------------------------------------
        # 6. ARDS
        # ----------------------------------------------------
        ards = {
            "diagnosis": "ARDS",
            "score": 0.0,
            "supporting_evidence": [],
            "contradicting_evidence": []
        }
        if "ards" in adm_diag_lower or "respiratory distress" in adm_diag_lower:
            ards["score"] += 0.3
            ards["supporting_evidence"].append("Respiratory distress syndrome noted in admission.")
            
        pao2 = labs.get("pao2")
        # Assume standard FiO2 of 0.4 - 0.5 in ventilated patients if not specified
        if pao2 is not None:
            pf_ratio = pao2 / 0.5 # estimation
            if pf_ratio < 300:
                ards["score"] += 0.4
                ards["supporting_evidence"].append(f"Estimated PaO2/FiO2 ratio ({pf_ratio:.0f}) satisfies Berlin definition for ARDS.")
            else:
                ards["contradicting_evidence"].append(f"Satisfactory PaO2/FiO2 ratio ({pf_ratio:.0f}) rules out severe ARDS.")
                
        if spo2 is not None and spo2 < 90:
            ards["score"] += 0.2
            ards["supporting_evidence"].append(f"Persistent hypoxemia (SpO2 {spo2}%) despite supplemental oxygen.")

        results.append(ards)

        # ----------------------------------------------------
        # 7. Acute Respiratory Failure
        # ----------------------------------------------------
        resp_failure = {
            "diagnosis": "Acute Respiratory Failure",
            "score": 0.0,
            "supporting_evidence": [],
            "contradicting_evidence": []
        }
        if "respiratory failure" in adm_diag_lower or "pneumonia" in adm_diag_lower or "copd" in adm_diag_lower:
            resp_failure["score"] += 0.3
            resp_failure["supporting_evidence"].append("Admission diagnosis reflects pulmonary compromise.")
            
        rr = vitals.get("respiratory_rate")
        if rr is not None and rr > 24:
            resp_failure["score"] += 0.3
            resp_failure["supporting_evidence"].append(f"Tachypnea ({rr} breaths/min) suggests increased work of breathing.")
            
        if spo2 is not None and spo2 < 92:
            resp_failure["score"] += 0.3
            resp_failure["supporting_evidence"].append(f"Severe hypoxemia (SpO2 {spo2}%) indicates gas exchange failure.")

        if spo2 is not None and spo2 >= 96 and (rr is not None and rr < 20):
            resp_failure["contradicting_evidence"].append("Adequate oxygen saturation on minimal or no support.")

        results.append(resp_failure)

        # ----------------------------------------------------
        # 8. Multi Organ Dysfunction
        # ----------------------------------------------------
        mods = {
            "diagnosis": "Multi Organ Dysfunction",
            "score": 0.0,
            "supporting_evidence": [],
            "contradicting_evidence": []
        }
        
        failure_count = 0
        # Check Cardiovascular failure
        if has_vasopressors or (sbp is not None and sbp < 90):
            failure_count += 1
            mods["supporting_evidence"].append("Cardiovascular system compromise (hypotension/vasopressors).")
        # Check Renal failure
        if creat is not None and creat > 1.8:
            failure_count += 1
            mods["supporting_evidence"].append("Renal system compromise (severe azotemia/elevated creatinine).")
        # Check Respiratory failure
        if spo2 is not None and spo2 < 90:
            failure_count += 1
            mods["supporting_evidence"].append("Respiratory system compromise (severe hypoxemia).")

        if failure_count >= 2:
            mods["score"] = 0.4 + (failure_count * 0.2)
            mods["supporting_evidence"].append(f"Sequential dysfunction identified across {failure_count} organ systems.")
        else:
            mods["contradicting_evidence"].append("System dysfunctions are localized; multiorgan criteria not met.")
            
        results.append(mods)

        # ----------------------------------------------------
        # Normalise and Format Output
        # ----------------------------------------------------
        formatted_results = []
        for r in results:
            # Clean empty lists if any
            if not r["supporting_evidence"]:
                r["supporting_evidence"].append("No specific supporting clinical signs identified.")
            if not r["contradicting_evidence"]:
                r["contradicting_evidence"].append("No significant opposing clinical metrics observed.")
                
            # Clamp score between 0.0 and 1.0
            likelihood = min(max(r["score"], 0.0), 1.0)
            
            # Map admission diagnosis exact matches to higher baseline
            if r["diagnosis"].lower() in adm_diag_lower:
                likelihood = max(likelihood, 0.90)

            formatted_results.append({
                "diagnosis": r["diagnosis"],
                "likelihood": round(likelihood, 2),
                "supporting_evidence": r["supporting_evidence"],
                "contradicting_evidence": r["contradicting_evidence"]
            })

        # Rank diagnoses by likelihood descending, then by whether it matches the admission diagnosis, then by name
        formatted_results.sort(key=lambda x: (-x["likelihood"], not (x["diagnosis"].lower() in adm_diag_lower), x["diagnosis"]))
        return formatted_results
