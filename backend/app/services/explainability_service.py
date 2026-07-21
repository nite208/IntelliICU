"""
Explainability Engine Service
"""

class ExplainabilityEngine:
    """
    Enterprise Explainability Engine.
    Analyzes clinical metrics from patient data to extract SHAP-like contributors and impact scores.
    """

    @staticmethod
    def generate(patient_data: dict) -> dict:
        """
        Generates positive and negative risk contributors based on clinical rules.
        """
        positive_contributors = []
        negative_contributors = []

        # Helper to safely parse numeric values (handling optional nesting and string units)
        def get_value(keys, default=None):
            for key_path in keys if isinstance(keys[0], list) else [keys]:
                val = patient_data
                for k in key_path:
                    if isinstance(val, dict):
                        val = val.get(k)
                    else:
                        val = None
                        break
                if val is not None:
                    # Clean and parse value
                    if isinstance(val, (int, float)):
                        return float(val)
                    if isinstance(val, str):
                        import re
                        match = re.search(r"[-+]?\d*\.\d+|\d+", val)
                        if match:
                            return float(match.group())
            return default

        # Extract values
        risk_score = get_value([["patient", "risk_score"], ["prediction", "risk_score"], ["risk_score"]], None)
        spo2 = get_value([["vitals", "spo2"], ["spo2"]], None)
        temp = get_value([["vitals", "temperature"], ["temperature"]], None)
        hr = get_value([["vitals", "heart_rate"], ["vitals", "hr"], ["heart_rate"]], None)
        rr = get_value([["vitals", "respiratory_rate"], ["vitals", "rr"], ["respiratory_rate"]], None)
        map_val = get_value([["vitals", "mean_arterial_pressure"], ["vitals", "map"], ["mean_arterial_pressure"]], None)
        platelets = get_value([["labs", "Platelets"], ["labs", "platelets"], ["platelets"]], None)
        sbp = get_value([["vitals", "blood_pressure", "systolic"], ["vitals", "systolic_bp"], ["systolic_bp"]], None)
        lactate = get_value([["labs", "Lactate"], ["labs", "lactate"], ["lactate"]], None)

        # ----------------------------------------------------
        # Positive Contributors Rules
        # ----------------------------------------------------

        # 1. Lactate > 4
        if lactate is not None and lactate > 4.0:
            impact = round(min(0.40, max(0.05, 0.15 + (lactate - 4.0) * 0.05)), 2)
            positive_contributors.append({
                "feature": "Lactate",
                "impact": impact,
                "reason": f"Elevated blood lactate level ({lactate} mmol/L) suggests tissue hypoperfusion and anaerobic metabolism."
            })

        # 2. HR > 120
        if hr is not None and hr > 120.0:
            impact = round(min(0.40, max(0.05, 0.10 + (hr - 120.0) * 0.01)), 2)
            positive_contributors.append({
                "feature": "Heart Rate",
                "impact": impact,
                "reason": f"Tachycardia ({hr:.0f} bpm) indicates systemic response to physiological stress or infection."
            })

        # 3. Temp > 39
        if temp is not None and temp > 39.0:
            impact = round(min(0.40, max(0.05, 0.15 + (temp - 39.0) * 0.10)), 2)
            positive_contributors.append({
                "feature": "Temperature",
                "impact": impact,
                "reason": f"Severe hyperthermia ({temp}°C) suggests an active systemic inflammatory response syndrome (SIRS)."
            })

        # 4. RR > 30
        if rr is not None and rr > 30.0:
            impact = round(min(0.40, max(0.05, 0.15 + (rr - 30.0) * 0.02)), 2)
            positive_contributors.append({
                "feature": "Respiratory Rate",
                "impact": impact,
                "reason": f"Tachypnea ({rr:.0f} breaths/min) indicates acute respiratory distress or metabolic compensation."
            })

        # 5. Risk Score > 0.8
        if risk_score is not None and risk_score > 0.80:
            impact = round(min(0.40, max(0.05, 0.20 + (risk_score - 0.80) * 0.50)), 2)
            positive_contributors.append({
                "feature": "Sepsis Risk Score",
                "impact": impact,
                "reason": f"High predictive model risk score ({risk_score * 100:.1f}%) suggests imminent risk of sepsis progression."
            })

        # ----------------------------------------------------
        # Negative Contributors Rules
        # ----------------------------------------------------

        # 1. SpO2 < 92
        if spo2 is not None and spo2 < 92.0:
            impact = round(min(0.40, max(0.05, 0.15 + (92.0 - spo2) * 0.03)), 2)
            negative_contributors.append({
                "feature": "SpO₂",
                "impact": impact,
                "reason": f"Hypoxemia (SpO₂ {spo2:.0f}%) indicates impaired gas exchange or respiratory dysfunction."
            })

        # 2. MAP < 65
        if map_val is not None and map_val < 65.0:
            impact = round(min(0.40, max(0.05, 0.15 + (65.0 - map_val) * 0.02)), 2)
            negative_contributors.append({
                "feature": "Mean Arterial Pressure",
                "impact": impact,
                "reason": f"Low mean arterial pressure ({map_val:.0f} mmHg) suggests inadequate systemic perfusion pressure."
            })

        # 3. Platelets < 150
        if platelets is not None and platelets < 150.0:
            impact = round(min(0.40, max(0.05, 0.10 + (150.0 - platelets) * 0.003)), 2)
            negative_contributors.append({
                "feature": "Platelets",
                "impact": impact,
                "reason": f"Thrombocytopenia (Platelets {platelets:.0f} x10⁹/L) suggests potential consumption or coagulopathy."
            })

        # 4. SBP < 90
        if sbp is not None and sbp < 90.0:
            impact = round(min(0.40, max(0.05, 0.20 + (90.0 - sbp) * 0.02)), 2)
            negative_contributors.append({
                "feature": "Systolic BP",
                "impact": impact,
                "reason": f"Hypotension (Systolic BP {sbp:.0f} mmHg) indicates acute circulatory failure or shock state."
            })

        return {
            "positive_contributors": positive_contributors,
            "negative_contributors": negative_contributors
        }
