"""
Clinical Summary Engine Service
"""

class ClinicalSummaryEngine:
    """
    Enterprise Clinical Summary Engine.
    Dynamically generates clinical summary, reasoning, and priority actions based on patient data.
    """

    @staticmethod
    def generate(patient_data: dict, recommendations: list = None) -> dict:
        """
        Generates structured clinical summary:
        - overall_condition
        - confidence
        - clinical_reasoning
        - priority_actions
        """
        # Helper to safely parse numeric values
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
                    if isinstance(val, (int, float)):
                        return float(val)
                    if isinstance(val, str):
                        import re
                        match = re.search(r"[-+]?\d*\.\d+|\d+", val)
                        if match:
                            return float(match.group())
            return default

        risk_score = get_value([["patient", "risk_score"], ["prediction", "risk_score"], ["risk_score"]], 0.0)
        spo2 = get_value([["vitals", "spo2"], ["spo2"]], None)
        temp = get_value([["vitals", "temperature"], ["temperature"]], None)
        hr = get_value([["vitals", "heart_rate"], ["vitals", "hr"], ["heart_rate"]], None)
        sbp = get_value([["vitals", "blood_pressure", "systolic"], ["vitals", "systolic_bp"], ["systolic_bp"]], None)
        lactate = get_value([["labs", "Lactate"], ["labs", "lactate"], ["lactate"]], None)

        # 1. Determine Overall Condition
        if risk_score >= 0.8:
            overall_condition = "Critical"
            confidence = 0.96
        elif risk_score >= 0.5:
            overall_condition = "Serious"
            confidence = 0.92
        else:
            overall_condition = "Stable"
            confidence = 0.88

        # 2. Build Clinical Reasoning Paragraph based on abnormal findings
        abnormal_findings = []
        if risk_score >= 0.5:
            abnormal_findings.append(f"elevated sepsis risk score ({risk_score*100:.0f}%)")
        if hr is not None and hr > 120:
            abnormal_findings.append(f"tachycardia ({hr:.0f} bpm)")
        if spo2 is not None and spo2 < 92:
            abnormal_findings.append(f"hypoxemia (SpO₂ {spo2:.0f}%)")
        if sbp is not None and sbp < 90:
            abnormal_findings.append(f"severe hypotension (Systolic BP {sbp:.0f} mmHg)")
        elif sbp is not None and sbp < 100:
            abnormal_findings.append(f"borderline hypotension (Systolic BP {sbp:.0f} mmHg)")
        if lactate is not None and lactate >= 4.0:
            abnormal_findings.append(f"critical hyperlactatemia ({lactate} mmol/L)")
        elif lactate is not None and lactate >= 2.0:
            abnormal_findings.append(f"elevated lactate ({lactate} mmol/L)")
        if temp is not None and temp >= 39.0:
            abnormal_findings.append(f"hyperthermia ({temp}°C)")
        elif temp is not None and temp < 36.0:
            abnormal_findings.append(f"hypothermia ({temp}°C)")

        if abnormal_findings:
            if len(abnormal_findings) > 1:
                findings_str = ", ".join(abnormal_findings[:-1]) + " and " + abnormal_findings[-1]
            else:
                findings_str = abnormal_findings[0]
            reasoning = (
                "Sepsis assessment indicates significant physiological stress. "
                f"The presence of {findings_str} indicates high risk of "
                "organ hypoperfusion and potential septic progression."
            )
        else:
            reasoning = "All evaluated vital signs and clinical biomarkers are currently within acceptable ranges."

        # 3. Determine Priority Actions
        priority_actions = []
        if recommendations:
            priority_actions = [rec["title"] for rec in recommendations if rec.get("priority") == "HIGH"]
            if not priority_actions:
                priority_actions = [rec["title"] for rec in recommendations[:3]]
        else:
            # Fallback rule-based priorities
            if risk_score >= 0.8:
                priority_actions.append("Initiate full sepsis resuscitation bundle")
            if lactate is not None and lactate >= 2.0:
                priority_actions.append("Repeat blood lactate in 2-4 hours")
            if sbp is not None and sbp < 90:
                priority_actions.append("Optimize vasopressor support")
            if spo2 is not None and spo2 < 92:
                priority_actions.append("Titrate oxygen therapy")
            if not priority_actions:
                priority_actions.append("Continue routine ICU monitoring")

        return {
            "overall_condition": overall_condition,
            "confidence": confidence,
            "clinical_reasoning": reasoning,
            "priority_actions": priority_actions[:4]
        }
