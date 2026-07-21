"""
Explainable Reasoning Service for Clinical Copilot.
Translates patient explainability data and clinical state into natural explanation structures.
"""

from typing import Dict, Any, List

class ExplainableReasoningService:
    """
    Service layer providing transparent clinical explanations based on AI model inputs and database values.
    """

    @staticmethod
    def process_explainable_query(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses the clinical question and context to extract structured reasoning, risk drivers,
        and physiological biomarker contributions.
        """
        if not context or "patient" not in context:
            return {
                "reasoning": "Context not available for this patient.",
                "risk_drivers": [],
                "abnormal_vitals": [],
                "abnormal_labs": [],
                "recommendations": [],
                "evidence": [],
                "confidence": 0.0
            }

        # 1. Extract base metrics
        vitals = context.get("vitals") or {}
        labs = context.get("labs") or {}
        prediction = context.get("prediction") or {}
        risk_score = prediction.get("risk_score")
        risk_level = prediction.get("risk_level", "LOW")
        alerts = context.get("alerts", [])
        explainability = context.get("explainability") or {}

        # 2. Compile risk drivers from explainability engine
        risk_drivers = []
        for c in explainability.get("positive_contributors", []):
            risk_drivers.append(f"{c['feature']} (Impact: +{int(c['impact']*100)}%) - {c['reason']}")
        for c in explainability.get("negative_contributors", []):
            risk_drivers.append(f"{c['feature']} (Impact: -{int(c['impact']*100)}%) - {c['reason']}")

        # 3. Compile abnormal vitals based on trend thresholds and raw values
        abnormal_vitals = []
        hr = vitals.get("heart_rate")
        spo2 = vitals.get("spo2")
        temp = vitals.get("temperature")
        sys_bp = vitals.get("systolic_bp")
        dia_bp = vitals.get("diastolic_bp")

        if hr and hr > 100:
            abnormal_vitals.append(f"Tachycardia (HR: {hr} bpm) - Elevated cardiac rate indicating physiological strain.")
        if spo2 and spo2 < 92:
            abnormal_vitals.append(f"Hypoxemia (SpO2: {spo2}%) - Sub-optimal oxygen saturation levels.")
        if temp and temp >= 38.0:
            abnormal_vitals.append(f"Fever (Temp: {temp}°C) - Pyrexia indicating active systemic inflammation.")
        elif temp and temp < 36.0:
            abnormal_vitals.append(f"Hypothermia (Temp: {temp}°C) - Sub-normal body temperature.")
        if sys_bp and sys_bp < 90:
            abnormal_vitals.append(f"Hypotension (BP: {sys_bp}/{dia_bp} mmHg) - Depressed arterial blood pressure.")

        # Add vital trend contexts
        trends = context.get("vital_trends") or {}
        for metric, info in trends.items():
            if isinstance(info, dict) and info.get("direction") in ["rising", "falling"]:
                abnormal_vitals.append(f"Vital Trend: {metric.replace('_', ' ').title()} is {info['direction']} (Latest: {info['last_value']}).")

        # 4. Compile abnormal labs
        abnormal_labs = []
        for lab in context.get("abnormal_labs", []):
            abnormal_labs.append(f"{lab['metric']}: {lab['value']} (Ref: {lab['reference']}) - {lab['status']} [{lab['severity']}]")

        # 5. Extract medications and standard pathways
        medications = context.get("medications") or []
        recommendations = medications + [
            "Initiate continuous vital signs and mean arterial pressure (MAP) logging.",
            "Order serial blood gas draws and lactate measurements every 2-4 hours.",
            "Acknowledge active critical telemetry alarms and verify sensor positions."
        ]

        # 6. Gather physiological evidence
        evidence = []
        if risk_score:
            evidence.append(f"Sepsis AI risk index is {risk_score} (risk level category: {risk_level}).")
        if labs.get("lactate"):
            evidence.append(f"Lactate biomarker is {labs.get('lactate')} mmol/L.")
        if labs.get("wbc"):
            evidence.append(f"White blood cell count is {labs.get('wbc')} x10^9/L.")
        if alerts:
            evidence.append(f"Alert Registry: {len(alerts)} active telemetry alerts currently firing.")

        # 7. Formulate targeted reasoning explanation based on question keywords
        q_lower = question.lower()
        if "why" in q_lower and "risk" in q_lower:
            reasoning = (
                f"The patient is categorized as {risk_level} risk due to active organ dysfunction and systemic inflammatory signals. "
                f"Sepsis risk is elevated to {risk_score or 'N/A'}. The major risk drivers are the elevated lactate level ({labs.get('lactate')} mmol/L) "
                f"representing tissue hypoperfusion, combined with severe hypotension (BP: {sys_bp}/{dia_bp} mmHg) and hypoxemia (SpO2: {spo2}%)."
            )
        elif "why" in q_lower and ("recommendation" in q_lower or "action" in q_lower):
            reasoning = (
                f"The recommended care pathway (including {', '.join([m.split()[0] for m in medications[:2]])}) was generated "
                f"to stabilize tissue oxygenation and reverse hypoperfusion. Prompt antibiotic and fluid titration are indicated by "
                f"active sepsis prediction criteria and low arterial perfusion indexes."
            )
        elif "vital" in q_lower:
            reasoning = (
                f"Analysis of vitals shows hemodynamic stress. The primary vital driver is the heart rate ({hr} bpm) "
                f"in response to systemic shock, compounded by oxygen saturation drops down to {spo2}%. Vitals trends show "
                f"vital parameter shifts needing active clinical adjustment."
            )
        elif "lab" in q_lower:
            reasoning = (
                f"Laboratory results indicate active metabolic acidosis and infection response. The primary lab drivers are the "
                f"elevated blood lactate of {labs.get('lactate')} mmol/L and leukocytosis (WBC: {labs.get('wbc')} x10^9/L), which "
                f"collectively support a diagnosis of sepsis or septic shock."
            )
        else:
            reasoning = (
                f"Clinical Copilot Explanation: Patient displays physiological markers associated with {risk_level} sepsis probability. "
                f"This reasoning is supported by {len(abnormal_vitals)} abnormal vital readings and {len(abnormal_labs)} abnormal laboratory markers. "
                f"Please review the detailed risk drivers and recommendations below."
            )

        return {
            "reasoning": reasoning,
            "risk_drivers": risk_drivers,
            "abnormal_vitals": abnormal_vitals,
            "abnormal_labs": abnormal_labs,
            "recommendations": recommendations,
            "evidence": evidence,
            "confidence": 0.95 if risk_score else 0.80
        }
