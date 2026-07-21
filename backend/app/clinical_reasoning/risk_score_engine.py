"""
app/clinical_reasoning/risk_score_engine.py

Clinical Risk Score Engine for ICU patients (Phase 13.3).
Calculates validated clinical scores: SOFA, qSOFA, NEWS2, SIRS, and Simplified APACHE II.
"""

from typing import Dict, Any, List

class RiskScoreEngine:
    """
    Computes validated physiological risk scores for critical care telemetry.
    """

    @staticmethod
    def calculate(
        vitals: Dict[str, Any],
        labs: Dict[str, Any],
        gcs: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Computes 5 critical care risk indices based on real-time metrics.

        Returns a dictionary:
        {
            "sofa": {"score": int, "risk": str, "explanation": str, "parameters": list[str]},
            "qsofa": {"score": int, "risk": str, "explanation": str, "parameters": list[str]},
            "news2": {"score": int, "risk": str, "explanation": str, "parameters": list[str]},
            "sirs": {"score": int, "risk": str, "explanation": str, "parameters": list[str]},
            "apache2": {"score": int, "risk": str, "explanation": str, "parameters": list[str]}
        }
        """
        # Safely extract metrics
        hr = vitals.get("heart_rate") or vitals.get("hr")
        sbp = vitals.get("systolic_bp")
        dbp = vitals.get("diastolic_bp")
        temp = vitals.get("temperature")
        rr = vitals.get("respiratory_rate") or vitals.get("rr")
        spo2 = vitals.get("spo2")
        map_val = vitals.get("mean_arterial_pressure") or vitals.get("map")

        # Fallback MAP calculation if missing
        if map_val is None and sbp is not None and dbp is not None:
            map_val = dbp + (sbp - dbp) / 3.0

        lactate = labs.get("lactate") or labs.get("Lactate")
        creat = labs.get("creatinine") or labs.get("Creatinine")
        wbc = labs.get("wbc") or labs.get("WBC")
        pao2 = labs.get("pao2") or labs.get("PaO2")
        platelets = labs.get("platelets") or labs.get("Platelets")
        potassium = labs.get("potassium") or labs.get("Potassium")
        bilirubin = labs.get("bilirubin") or labs.get("Bilirubin")

        meds = context.get("medications", [])
        meds_lower = [m.lower() for m in meds]
        has_vasopressors = any(m in meds_lower for m in ["norepinephrine", "vasopressin", "epinephrine", "levophed"])

        alert_titles = [a.get("title", "").lower() for a in context.get("alerts", [])]
        has_altered_mental = gcs < 15 or any("mental" in t or "consciousness" in t or "gcs" in t for t in alert_titles)

        # ----------------------------------------------------
        # 1. qSOFA Calculation
        # ----------------------------------------------------
        q_score = 0
        q_params = []
        if rr is not None and rr >= 22:
            q_score += 1
            q_params.append(f"Respiratory Rate >= 22 ({rr} bpm)")
        if sbp is not None and sbp <= 100:
            q_score += 1
            q_params.append(f"Systolic BP <= 100 mmHg ({sbp} mmHg)")
        if has_altered_mental:
            q_score += 1
            q_params.append(f"Altered Mentation / GCS < 15 (GCS: {gcs})")

        q_risk = "LOW"
        q_exp = "Normal clinical risk. Monitor standard vitals."
        if q_score >= 2:
            q_risk = "HIGH"
            q_exp = f"Score of {q_score} indicates high risk of poor clinical outcomes / sepsis death. Urgent review indicated."

        # ----------------------------------------------------
        # 2. SIRS Calculation
        # ----------------------------------------------------
        s_score = 0
        s_params = []
        if temp is not None:
            if temp > 38.0 or temp < 36.0:
                s_score += 1
                s_params.append(f"Temperature outside 36-38 °C ({temp} °C)")
        if hr is not None and hr > 90:
            s_score += 1
            s_params.append(f"Heart Rate > 90 bpm ({hr} bpm)")
        if rr is not None and rr > 20:
            s_score += 1
            s_params.append(f"Respiratory Rate > 20 bpm ({rr} bpm)")
        if wbc is not None:
            if wbc > 12.0 or wbc < 4.0:
                s_score += 1
                s_params.append(f"WBC outside 4.0-12.0 K/uL ({wbc} K/uL)")

        s_risk = "NEGATIVE"
        s_exp = "Systemic Inflammatory Response Syndrome criteria negative."
        if s_score >= 2:
            s_risk = "POSITIVE"
            s_exp = f"SIRS criteria positive ({s_score} points). Reflects systemic inflammatory response."

        # ----------------------------------------------------
        # 3. SOFA Calculation
        # ----------------------------------------------------
        sofa_score = 0
        sofa_params = []

        # Cardiovascular
        cv_pts = 0
        if has_vasopressors:
            cv_pts = 3 # Norepinephrine/Epinephrine <= 0.1 standard baseline
            sofa_params.append("Cardiovascular: Vasoactive infusion active (+3 pts)")
        elif map_val is not None and map_val < 70:
            cv_pts = 1
            sofa_params.append(f"Cardiovascular: MAP < 70 mmHg ({map_val:.1f} mmHg) (+1 pt)")
        sofa_score += cv_pts

        # Renal
        renal_pts = 0
        if creat is not None:
            if creat >= 5.0:
                renal_pts = 4
            elif creat >= 3.5:
                renal_pts = 3
            elif creat >= 2.0:
                renal_pts = 2
            elif creat >= 1.2:
                renal_pts = 1
            
            if renal_pts > 0:
                sofa_params.append(f"Renal: Creatinine {creat} mg/dL (+{renal_pts} pts)")
        sofa_score += renal_pts

        # Respiratory
        resp_pts = 0
        # Estimate PaO2/FiO2 ratio from SpO2 if PaO2 is not available
        pf_ratio = None
        if pao2 is not None:
            pf_ratio = pao2 / 0.4 # assume standard FiO2 40% if not set
        elif spo2 is not None:
            # Simple conversion: SpO2 90% is roughly PaO2 60 -> P/F = 150
            pf_ratio = (spo2 / 100.0) * 250

        if pf_ratio is not None:
            if pf_ratio < 100:
                resp_pts = 4
            elif pf_ratio < 200:
                resp_pts = 3
            elif pf_ratio < 300:
                resp_pts = 2
            elif pf_ratio < 400:
                resp_pts = 1

            if resp_pts > 0:
                sofa_params.append(f"Respiratory: P/F ratio estimated at {pf_ratio:.0f} (+{resp_pts} pts)")
        sofa_score += resp_pts

        # Coagulation
        coag_pts = 0
        if platelets is not None:
            if platelets < 20:
                coag_pts = 4
            elif platelets < 50:
                coag_pts = 3
            elif platelets < 100:
                coag_pts = 2
            elif platelets < 150:
                coag_pts = 1
            
            if coag_pts > 0:
                sofa_params.append(f"Coagulation: Platelets {platelets} K/uL (+{coag_pts} pts)")
        sofa_score += coag_pts

        # Neurological
        neuro_pts = 0
        if gcs < 15:
            if gcs < 6:
                neuro_pts = 4
            elif gcs <= 9:
                neuro_pts = 3
            elif gcs <= 12:
                neuro_pts = 2
            elif gcs <= 14:
                neuro_pts = 1
            
            if neuro_pts > 0:
                sofa_params.append(f"Neurological: GCS {gcs} (+{neuro_pts} pts)")
        sofa_score += neuro_pts

        # Liver
        liv_pts = 0
        if bilirubin is not None:
            if bilirubin >= 12.0:
                liv_pts = 4
            elif bilirubin >= 6.0:
                liv_pts = 3
            elif bilirubin >= 2.0:
                liv_pts = 2
            elif bilirubin >= 1.2:
                liv_pts = 1
            
            if liv_pts > 0:
                sofa_params.append(f"Hepatic: Bilirubin {bilirubin} mg/dL (+{liv_pts} pts)")
        sofa_score += liv_pts

        sofa_risk = "LOW"
        if sofa_score >= 12:
            sofa_risk = "CRITICAL"
        elif sofa_score >= 7:
            sofa_risk = "HIGH"
        elif sofa_score >= 3:
            sofa_risk = "MEDIUM"

        sofa_exp = f"SOFA Score is {sofa_score}. "
        if sofa_score >= 12:
            sofa_exp += "Mortality risk is high (>50%). Severe multi-system organ failure."
        elif sofa_score >= 7:
            sofa_exp += "Mortality risk is moderate (15-30%). Multi-system organ dysfunction."
        else:
            sofa_exp += "Mortality risk is low (<10%). Organ systems stable."

        # ----------------------------------------------------
        # 4. NEWS2 Calculation
        # ----------------------------------------------------
        n_score = 0
        n_params = []

        # RR
        if rr is not None:
            if rr <= 8 or rr >= 25:
                n_score += 3
                n_params.append(f"Resp Rate abnormal ({rr} bpm) (+3 pts)")
            elif 21 <= rr <= 24:
                n_score += 2
                n_params.append(f"Resp Rate elevated ({rr} bpm) (+2 pts)")
            elif 9 <= rr <= 11:
                n_score += 1
                n_params.append(f"Resp Rate low ({rr} bpm) (+1 pt)")

        # SpO2
        if spo2 is not None:
            if spo2 <= 91:
                n_score += 3
                n_params.append(f"SpO2 low ({spo2}%) (+3 pts)")
            elif 92 <= spo2 <= 93:
                n_score += 2
                n_params.append(f"SpO2 low ({spo2}%) (+2 pts)")
            elif 94 <= spo2 <= 95:
                n_score += 1
                n_params.append(f"SpO2 low ({spo2}%) (+1 pt)")

        # SBP
        if sbp is not None:
            if sbp <= 90 or sbp >= 220:
                n_score += 3
                n_params.append(f"Systolic BP extreme ({sbp} mmHg) (+3 pts)")
            elif 91 <= sbp <= 100:
                n_score += 2
                n_params.append(f"Systolic BP low ({sbp} mmHg) (+2 pts)")
            elif 101 <= sbp <= 110:
                n_score += 1
                n_params.append(f"Systolic BP low ({sbp} mmHg) (+1 pt)")

        # HR
        if hr is not None:
            if hr <= 40 or hr >= 131:
                n_score += 3
                n_params.append(f"Heart Rate extreme ({hr} bpm) (+3 pts)")
            elif 111 <= hr <= 130:
                n_score += 2
                n_params.append(f"Heart Rate high ({hr} bpm) (+2 pts)")
            elif 41 <= hr <= 50 or 91 <= hr <= 110:
                n_score += 1
                n_params.append(f"Heart Rate abnormal ({hr} bpm) (+1 pt)")

        # Temp
        if temp is not None:
            if temp <= 35.0:
                n_score += 3
                n_params.append(f"Temp low ({temp} °C) (+3 pts)")
            elif temp >= 39.1:
                n_score += 2
                n_params.append(f"Temp high ({temp} °C) (+2 pts)")
            elif 35.1 <= temp <= 36.0 or 38.1 <= temp <= 39.0:
                n_score += 1
                n_params.append(f"Temp abnormal ({temp} °C) (+1 pt)")

        # Supplemental Oxygen
        # Assume oxygen therapy is active if RAG oxygen category is retrieved or user asks about oxygen
        is_oxygen_active = any("oxygen" in med.lower() for med in meds_lower) or any("oxygen" in t for t in alert_titles)
        if is_oxygen_active:
            n_score += 2
            n_params.append("Supplemental Oxygen active (+2 pts)")

        # Altered Mentation
        if has_altered_mental:
            n_score += 3
            n_params.append("Consciousness: CVPU (Altered Mentation) (+3 pts)")

        n_risk = "LOW"
        if n_score >= 7:
            n_risk = "HIGH"
        elif n_score >= 5:
            n_risk = "MEDIUM"

        n_exp = f"NEWS2 Score is {n_score}. "
        if n_score >= 7:
            n_exp += "High risk. Triggers critical care pathway and continuous monitoring."
        elif n_score >= 5:
            n_exp += "Medium risk. Prompts urgent clinical review."
        else:
            n_exp += "Low risk. Routine ward-level observations."

        # ----------------------------------------------------
        # 5. Simplified APACHE II Calculation
        # ----------------------------------------------------
        ap_score = 0
        ap_params = []

        # Age points based on context (default age 67 if not set)
        pat = context.get("patient", {}) or {}
        age = pat.get("age", 67)
        age_pts = 0
        if age >= 75:
            age_pts = 6
        elif age >= 65:
            age_pts = 5
        elif age >= 55:
            age_pts = 3
        elif age >= 45:
            age_pts = 2
        ap_score += age_pts
        ap_params.append(f"Age: {age} years (+{age_pts} pts)")

        # Temp points
        t_pts = 0
        if temp is not None:
            if temp >= 41.0 or temp <= 29.9:
                t_pts = 4
            elif 39.0 <= temp <= 40.9 or 30.0 <= temp <= 31.9:
                t_pts = 3
            elif 38.5 <= temp <= 38.9 or 32.0 <= temp <= 34.9:
                t_pts = 1
            if t_pts > 0:
                ap_params.append(f"APACHE Temp: {temp} °C (+{t_pts} pts)")
        ap_score += t_pts

        # MAP points
        m_pts = 0
        if map_val is not None:
            if map_val >= 160 or map_val <= 49:
                m_pts = 4
            elif 130 <= map_val <= 159 or 50 <= map_val <= 59:
                m_pts = 3
            elif 110 <= map_val <= 129 or 60 <= map_val <= 69:
                m_pts = 2
            if m_pts > 0:
                ap_params.append(f"APACHE MAP: {map_val:.1f} mmHg (+{m_pts} pts)")
        ap_score += m_pts

        # Heart Rate points
        h_pts = 0
        if hr is not None:
            if hr >= 180 or hr <= 39:
                h_pts = 4
            elif 140 <= hr <= 179 or 40 <= hr <= 54:
                h_pts = 3
            elif 110 <= hr <= 139 or 55 <= hr <= 69:
                h_pts = 2
            if h_pts > 0:
                ap_params.append(f"APACHE Heart Rate: {hr} bpm (+{h_pts} pts)")
        ap_score += h_pts

        # RR points
        r_pts = 0
        if rr is not None:
            if rr >= 50 or rr <= 5:
                r_pts = 4
            elif 35 <= rr <= 49 or 6 <= rr <= 9:
                r_pts = 3
            elif 25 <= rr <= 34:
                r_pts = 1
            if r_pts > 0:
                ap_params.append(f"APACHE Resp Rate: {rr} breaths/min (+{r_pts} pts)")
        ap_score += r_pts

        # Oxygenation points
        ox_pts = 0
        if pf_ratio is not None:
            if pf_ratio < 200:
                ox_pts = 4
            elif pf_ratio < 350:
                ox_pts = 3
            elif pf_ratio < 500:
                ox_pts = 2
            if ox_pts > 0:
                ap_params.append(f"APACHE Oxygenation: P/F ratio {pf_ratio:.0f} (+{ox_pts} pts)")
        ap_score += ox_pts

        # Potassium points
        k_pts = 0
        if potassium is not None:
            if potassium >= 7.0 or potassium < 2.5:
                k_pts = 4
            elif 6.0 <= potassium <= 6.9 or 2.5 <= potassium <= 2.9:
                k_pts = 3
            elif 5.5 <= potassium <= 5.9 or 3.0 <= potassium <= 3.4:
                k_pts = 1
            if k_pts > 0:
                ap_params.append(f"APACHE Potassium: {potassium} mmol/L (+{k_pts} pts)")
        ap_score += k_pts

        # Creatinine points (double if acute kidney injury)
        c_pts = 0
        if creat is not None:
            if creat >= 3.5:
                c_pts = 4
            elif 2.0 <= creat <= 3.4:
                c_pts = 3
            elif 1.5 <= creat <= 1.9:
                c_pts = 2
            
            # Double points for acute renal failure
            is_acute_renal = "aki" in context.get("admission", {}).get("diagnosis", "").lower()
            if is_acute_renal:
                c_pts *= 2
                ap_params.append(f"APACHE Creatinine: {creat} mg/dL (Acute Renal Failure active) (+{c_pts} pts)")
            elif c_pts > 0:
                ap_params.append(f"APACHE Creatinine: {creat} mg/dL (+{c_pts} pts)")
        ap_score += c_pts

        # WBC points
        w_pts = 0
        if wbc is not None:
            if wbc >= 40.0 or wbc < 1.0:
                w_pts = 4
            elif 20.0 <= wbc <= 39.9 or 1.0 <= wbc <= 2.9:
                w_pts = 3
            elif 15.0 <= wbc <= 19.9 or 3.0 <= wbc <= 14.9:
                w_pts = 1
            if w_pts > 0:
                ap_params.append(f"APACHE WBC: {wbc} K/uL (+{w_pts} pts)")
        ap_score += w_pts

        # GCS points
        gcs_pts = 15 - gcs
        if gcs_pts > 0:
            ap_score += gcs_pts
            ap_params.append(f"APACHE GCS deficit (GCS: {gcs}) (+{gcs_pts} pts)")

        # Chronic health points (standard 5 points for non-operative ICU admission)
        ap_score += 5
        ap_params.append("Chronic Health: Non-operative ICU admission (+5 pts)")

        ap_risk = "LOW"
        if ap_score >= 25:
            ap_risk = "HIGH"
        elif ap_score >= 15:
            ap_risk = "MEDIUM"

        ap_exp = f"APACHE II Score is {ap_score}. "
        if ap_score >= 25:
            ap_exp += "Predicts high hospital mortality (>50%). Critical status."
        elif ap_score >= 15:
            ap_exp += "Predicts moderate hospital mortality (15-40%). Moderate risk."
        else:
            ap_exp += "Predicts low hospital mortality (<15%). Hemodynamically stable."

        return {
            "sofa": {"score": sofa_score, "risk": sofa_risk, "explanation": sofa_exp, "parameters": sofa_params},
            "qsofa": {"score": q_score, "risk": q_risk, "explanation": q_exp, "parameters": q_params},
            "news2": {"score": n_score, "risk": n_risk, "explanation": n_exp, "parameters": n_params},
            "sirs": {"score": s_score, "risk": s_risk, "explanation": s_exp, "parameters": s_params},
            "apache2": {"score": ap_score, "risk": ap_risk, "explanation": ap_exp, "parameters": ap_params}
        }
